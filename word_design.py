#!/usr/bin/env python3

import subprocess
from argparse import ArgumentParser
from cnfencoder import DNAEncoder
import time

BIN_PATH = "bin/" # path to the compiled SAT solver binaries

DEFAULT_BINARY = "glucose-syrup"
DEFAULT_CNF_OUT_FILE = "formula.cnf"

RUNTIME_LINE_COLOR = "\033[95m"
RESET_COLOR = "\033[0m"

BIN_PATH_LEN = len(BIN_PATH) + len(DEFAULT_BINARY)
DEFAULT_SET_LEN = 25

NO_ERROR_SOLVER_CODES = [10, 20]

def sat_solve(encoder, out_file, binary, is_quiet):
    """ Fill ``out_file`` with the constructed CNF formula from ``encoder``
    in the DIMACS format, run the SAT solver ``binary`` and document the runtime &
    output of the SAT solver. Print the decoded output. """
    with open(out_file, "w") as f:
        f.write(encoder.to_dimacs())

    cmd = [binary]
    if "glucose" in binary: # had to hardwire
        cmd.append("-model")
    if is_quiet: 
        cmd.append("-verb=0" if "glucose" in binary else "-q")
    cmd.append(out_file)
    
    start_time = time.time()
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    end_time = time.time()
    output = result.stdout
    
    if not is_quiet: 
        print(output)
    if result.returncode not in NO_ERROR_SOLVER_CODES: 
        print(result.stderr)
    
    print(f"{RUNTIME_LINE_COLOR}[{binary:<{BIN_PATH_LEN}}] Runtime: {(end_time - start_time):.4f} seconds{RESET_COLOR}")
    
    if "UNSATISFIABLE" in output: 
        print("UNSATISFIABLE")
        return
    words = encoder.decode_output(output)
    if words:
        print(" | ".join(words))
    else: 
        print("Model parsing failed.")

if __name__ == "__main__":
    parser = ArgumentParser()
    
    parser.add_argument(
        "-n", 
        "--number", 
        default=DEFAULT_SET_LEN, 
        type=int, 
        help="desired set size"
    )
    
    parser.add_argument(
        "-of", 
        "--output", 
        default=DEFAULT_CNF_OUT_FILE, 
        type=str, 
        help="output DIMACS file for the CNF formula"
    )
    
    parser.add_argument(
        "-s", 
        "--solver", 
        default=BIN_PATH + DEFAULT_BINARY, 
        type=str, 
        help="the SAT solver binary name"
    )
    
    parser.add_argument(
        "-q", 
        "--quiet", 
        action="store_true", 
        help="suppress solver output"
    )
    
    parser.add_argument( 
        "-ord",
        "--order", 
        action="store_true",
        help="makes sure the words are fully ordered (by bit encoding)"
    )
    
    args = parser.parse_args()
    encoder = DNAEncoder(args.number, args.order)
    sat_solve(encoder, args.output, args.solver, args.quiet)