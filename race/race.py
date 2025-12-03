#!/usr/bin/env python3

import subprocess
import json
import matplotlib.pyplot as plt
from cnfencoder import DNAEncoder

BIN_PATH = "bin/"
CURRENT_DIR = "race/"
CNF_PATH_TEMPLATE = CURRENT_DIR + "cnfs/temp_{}.cnf"

SIZES_ALL = [15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 66, 67, 68, 69, 70, 71]
SIZES_NO_GLUCOSE = [72, 74, 75, 76, 78, 80, 81, 82, 83]

SOLVERS = {
    "Glucose": "glucose-syrup -model -verb=0",
    "Kissat":  "kissat -q",
    "CaDiCaL": "cadical -q"
}
COLORS = {"Glucose": "gold", "Kissat": "blue", "CaDiCaL": "deeppink"}

subprocess.run(["mkdir", "-p", CURRENT_DIR + "cnfs", CURRENT_DIR + "logs", CURRENT_DIR + "plots"])

for n in set(SIZES_ALL + SIZES_NO_GLUCOSE):
    with open(CNF_PATH_TEMPLATE.format(n), "w") as f:
        f.write(DNAEncoder(n).to_dimacs())

def run_race(sizes, solver_names, json_out, plot_out): 
    """Run ``hyperfine`` on a number of set sizes and solvers, save and plot the results."""
    cmds = ",".join([SOLVERS[name] for name in solver_names])
    nums = ",".join(map(str, sizes))
    
    print(f"Running {nums} on {cmds} -> {plot_out}")
    subprocess.run([
        "hyperfine",
        "--ignore-failure",
        "--warmup", "1",
        "--max-runs", "4",
        "--export-json", json_out,
        "-L", "solver", cmds,
        "-L", "n", nums,
        BIN_PATH + "{solver} " + CNF_PATH_TEMPLATE.format("{n}")
    ])

    with open(json_out) as f:
        data = json.load(f)["results"]

    plt.figure(figsize=(7, 9))
    
    results = {name: [] for name in solver_names}
    
    for run in data:
        cmds = run["parameters"]["solver"]
        n = int(run["parameters"]["n"])
        time = run["mean"]
        
        for name, val in SOLVERS.items():
            if val == cmds: results[name].append((n, time))

    for name in solver_names:
        pts = sorted(results[name])
        plt.plot(
            [p[0] for p in pts], 
            [p[1] for p in pts], 
            label=name, color=COLORS[name], marker="o"
        )
        
    plt.xlabel("Set Size (n)", fontsize=15)
    plt.ylabel("Runtime (s)", fontsize=15)
    
    plt.legend()
    plt.grid(True)
    plt.savefig(plot_out, dpi=300)

run_race(
    SIZES_ALL, 
    ["Glucose", "Kissat", "CaDiCaL"],
    CURRENT_DIR + "logs/results_all.json", 
    CURRENT_DIR + "plots/plot_all.png"
)

run_race( 
    SIZES_NO_GLUCOSE, 
    ["Kissat", "CaDiCaL"],
    CURRENT_DIR + "logs/results_no_glucose.json",
    CURRENT_DIR + "plots/plot_no_glucose.png"
)