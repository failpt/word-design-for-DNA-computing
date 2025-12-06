import itertools

class DNAEncoder: 
    def __init__(self, size, eliminate_permutations=False):
        """ Encode a set of 8-letter strings {A, C, G, T} of size ``size`` as 
        {10, 00, 01, 11} and construct a CNF formula which enforces problem 033 specific 
        constraints on the set. 
        If you want your set to be ordered, set ``eliminate_permutations`` to ``True`` """
        self.size = size
        self.eliminate_permutations = eliminate_permutations
        self.length = 8 # word length
        self.bpl = 2 # bits per letter
        
        self.code = { (True, False): 'A', (False, False): 'C', 
                     (False, True): 'G', (True, True): 'T' }
        
        self.base_vars = self.size * self.length * self.bpl
        self.total_vars = self.base_vars
        self.clauses = []
        
        self._encode()
        
    def to_dimacs(self):
        """ :returns: A set of clauses corresponding to the current ``DNAEncoder`` instance in DIMACS.
        :rtype: str """
        lines = [f"p cnf {self.total_vars} {len(self.clauses)}"]
        for c in self.clauses:
            lines.append(" ".join(map(str, c)) + " 0")
        return "\n".join(lines)

    def decode_model(self, model):
        """ Decode a ``model`` into a set of corresponding ``words``.
        :param model: A model solving the earlier constructed CFN formula 
        :type model: list of int
        :returns: Decoded model
        :rtype: list of str """
        words = []
        head_var = 1
        for w in range(self.size):
            chars = []
            for p in range(self.length):
                bit0 = model[head_var - 1] > 0
                bit1 = model[head_var] > 0
                chars.append(self.code[(bit0, bit1)])
                head_var += self.bpl
            words.append("".join(chars))
        return words
    
    def decode_output(self, solver_output):
        """ Extract a model out of ``solver_output`` and decode it into a set of corresponding ``words``.
        :param solver_output: Output of a SAT solver 
        :type solver_output: str
        :returns: Decoded model
        :rtype: list of str """
        model = [int(x)
             for line in solver_output.splitlines() if line.startswith('v') 
             for x in line.split()[1:] if x != '0']
        return self.decode_model(model) if model else None

    def _get_var(self, w, p=0, b=0):
        """ :returns: variable ID for word ``w`` at position ``p`` at bit ``b``.
        :rtype: int """
        return 1 + (w * self.length * self.bpl) + (p * self.bpl) + b

    def _allocate_var(self):
        """ Allocate a new auxiliary variable. """
        self.total_vars += 1
        return self.total_vars

    def _add_gc_content_constraint(self, w):
        """ Add clauses corresponding to word ``w`` having exaclty 4 letters from {C, G} """
        head_var = self._get_var(w)
        bit0_vars = [head_var + self.bpl * i for i in range(self.length)]
            
        for combo in itertools.combinations(bit0_vars, 5):
            self.clauses.append(list(combo))
            self.clauses.append([-x for x in combo])
            
    def _add_hamming_constraint(self, w1, w2, is_rc):
        """ Add clauses corresponding to words ``w1`` and ``w2`` having hamming distance of at least 4. 
        ``is_rc`` indicates wether we treat this as an 'RC-constraint' (i.e. third constraint of problem 033) or a normal constraint (i.e. second constraint) between two distinct words. """
        match_vars = []
        
        for p in range(self.length):
            match_var = self._allocate_var()
            match_vars.append(match_var)
            
            u0, v0 = self._get_var(w1, p), self._get_var(w2, (self.length - 1) - p if is_rc else p)
            u1, v1 = u0 + 1, v0 + 1
            
            for b0 in [True, False]:
                for b1 in [True, False]:
                    lits = [
                        -u0 if b0 else u0,
                        -u1 if (b1 ^ is_rc) else u1, 
                        -v0 if b0 else v0, 
                        -v1 if b1 else v1,
                        match_var
                    ]
                    self.clauses.append(lits)
                    
        for combo in itertools.combinations(match_vars, 5):
            self.clauses.append([-x for x in combo])
            
    def _add_order(self, w1, w2):
        """ Add clauses corresponding to order ``w1`` < ``w2`` by MSB. """
        head_u, head_v = self._get_var(w1), self._get_var(w2)
        prev_eq = None 
        
        for _ in range(self.length):
            for b in range(self.bpl):
                u, v = head_u + b, head_v + b
                
                curr_eq = self._allocate_var()
                
                if prev_eq:
                    self.clauses.append([-curr_eq, prev_eq])
                
                # (u XOR v) => !curr_eq = not (u XOR v) or !curr_eq
                #                       = (u <=> v) or !curr_eq
                #                       = ((!u or v) and (u or !v)) or !curr_eq
                #                       = (!curr_eq or !u or v) and (!curr_eq or u or !v)
                self.clauses.append([-curr_eq, -u, v])
                self.clauses.append([-curr_eq, u, -v])
                
                clause = [-u, v]
                if prev_eq:                 # (u and !v) => !prev_eq
                    clause.append(-prev_eq) # = !(!u or v) => !prev_eq
                self.clauses.append(clause) # = !u or v or !prev_eq
                
                prev_eq = curr_eq
                
            head_u += self.bpl
            head_v += self.bpl
            
        self.clauses.append([-prev_eq])

    def _encode(self):
        """ Enforce all the constraints on the words and save the clauses for CNF in a list. """
        for w in range(self.size):
            self._add_gc_content_constraint(w)    
                     
        for i in range(self.size):
            for j in range(i, self.size):
                if (i != j):
                    self._add_hamming_constraint(i, j, is_rc=False)
                self._add_hamming_constraint(i, j, is_rc=True)
            
        if (self.eliminate_permutations):
            for i in range(self.size - 1):
                self._add_order(i, i + 1)