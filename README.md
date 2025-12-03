# Word Design for DNA Computing on Surfaces
This is an experimental project attempting to solve [problem 033](https://www.csplib.org/Problems/prob033/) on [CSPLib](https://www.csplib.org/).

Given a fixed size `n`, I try to find a set of `n` strings satisfying the problem constraints. I introduce a `cnfencoder` package containing `DNAEncoder`, which  reduces the problem of finding a set of a given size to SAT (helps construct a CNF formula to feed the solver and decode the solution). In pursuit of experimentation, I use three different SAT solvers – [Glucose](https://github.com/audemard/glucose), [Kissat](https://github.com/arminbiere/kissat), and [CaDiCaL](https://github.com/arminbiere/cadical) ([paper](https://cca.informatik.uni-freiburg.de/papers/BiereFallerFazekasFleuryFroleyksPollitt-CAV24.pdf)) –  and compare their performance on fixed input sizes.

## Running the code
Usage:
```
word_design.py [-h] [-n NUMBER] [-o OUTPUT] [-s SOLVER] [-q]
```

Options:
```
  -h, --help            show this help message and exit
  -n NUMBER, --number NUMBER
                        desired set size                       (default: 25)
  -o OUTPUT, --output OUTPUT
                        output DIMACS file for the CNF formula (default: formula.cnf)
  -s SOLVER, --solver SOLVER
                        the SAT solver binary name             (default: ./bin/glucose-syrup)
  -q, --quiet           suppress solver output
```

## Examples
1. ```
   % ./word_design.py -q
   ```
   Output:
   ```diff
   + [./bin/glucose-syrup] Runtime: 0.0337 seconds
   CCTCAAAG | CGGTTTCT | GTCTTTGC | CACAAGCA | CAGCCATT | GCGGATAA | CTCCATCT | CGAGTATC | CCCAAAGT | CAGCTTAG | GACATCGT | GGCAACAA | GTAGACTC | GGTGTTTG | GAGGGAAT | GCACGATT | GCGACTTT | GTCTGCTT | GTTTCGGA | GCCATTCA | GTACGCAA | CTATAGCG | GTAAGGGT | GATCTAGG | TTGGATCG
   ```
2. 
