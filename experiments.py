#!/usr/bin/env python3

import subprocess
import json
import matplotlib.pyplot as plt
from cnfencoder import DNAEncoder

BIN_PATH = "bin/"
CNF_PATH_TEMPLATE = "experiments/cnfs/{}/temp_{}.cnf"

SIZES_ALL = "15,20,25,30,35,40,45,50,55,60,65,66,67,68,69,70,71"
SIZES_NO_GLUCOSE = "72,74,75,76,78,80,81,82,83"

SIZES_MERGE = f"{SIZES_ALL},{SIZES_NO_GLUCOSE}"

SOLVERS = {
    "Glucose": "glucose-syrup -model -verb=0",
    "Kissat":  "kissat -q",
    "CaDiCaL": "cadical -q"
}
COLORS = {"Glucose": "darkorange", "Kissat": "teal", "CaDiCaL": "mediumvioletred"}

subprocess.run(["mkdir", "-p", 
    "experiments/cnfs/order", "experiments/cnfs/norder",
    "experiments/logs/order", "experiments/logs/norder",
    "experiments/plots/order", "experiments/plots/norder"
])

def construct_formulas(is_order):
    """ Construct CNF files w/ or w/o order depending on ``is_order``. """
    for n in set(SIZES_MERGE.split(",")):
        with open(CNF_PATH_TEMPLATE.format("order" if is_order else "norder", n), "w") as f:
            f.write(DNAEncoder(int(n), is_order).to_dimacs())

def plot_data(json_out, plot_out, legends, title, mode):
    """ Plot hyperfine output. """
    with open(json_out) as f:
        data = json.load(f)["results"]

    plt.figure(figsize=(7, 9))
    
    grouped_data = {}
    
    for run in data:
        n = int(run["parameters"]["n"])
        time = run["mean"]
        
        if mode == "batch":
            cmd = run["parameters"]["solver"]
            label = next(k for k, v in SOLVERS.items() if v == cmd)
        else:
            direction = run["parameters"]["dir"]
            label = "Ordered" if direction == "order" else "Not ordered"
        
        if label not in grouped_data: 
            grouped_data[label] = []
            
        grouped_data[label].append((n, time))

    for label, points in grouped_data.items():
        pts = sorted(points)
        plt.plot(
            [p[0] for p in pts], 
            [p[1] for p in pts], 
            label=label, 
            marker="o"
        )
    
    plt.title(label=title, fontsize=16)
    plt.xlabel("Set Size (n)", fontsize=14.5)
    plt.ylabel("Runtime (s)", fontsize=14.5)
    
    plt.legend()
    plt.grid(True)
    plt.savefig(plot_out, dpi=300)
    
def run_batch(sizes, solver_names, json_template, plot_template, is_order): 
    """ Run ``hyperfine`` on a number of set sizes and solvers, 
    save and plot the results. """
    cmds = ",".join([SOLVERS[name] for name in solver_names])
    
    dir = "order" if is_order else "norder"
    
    json_out = json_template.format(dir)
    plot_out = plot_template.format(dir)
    
    subprocess.run([
        "hyperfine",
        "--ignore-failure",
        "--warmup", "0",
        "--max-runs", "5",
        "--export-json", json_out,
        "-L", "solver", cmds,
        "-L", "n", sizes,
        BIN_PATH + "{solver} " + CNF_PATH_TEMPLATE.format(dir, "{n}")
    ])
    
    plot_data(json_out, plot_out, solver_names, ("Ordered" if is_order else "Not ordered"), "batch")

def run_single(sizes, solver, json_out, plot_out):
    """ Run ``hyperfine`` on a set of sizes and a solver with and without order, 
    save and plot the results. """
    subprocess.run([
        "hyperfine",
        "--ignore-failure",
        "--warmup", "1",
        "--max-runs", "3",
        "--export-json", json_out,
        "-L", "dir", "order,norder",
        "-L", "n", sizes,
        BIN_PATH + SOLVERS[solver] + " " + CNF_PATH_TEMPLATE.format("{dir}", "{n}")
    ])
    
    plot_data(json_out, plot_out, ["Ordered", "Not ordered"], solver, "single")
    
def run_race(is_order):
    """ Runs two batches of sizes and solvers. """
    run_batch(
        SIZES_ALL, 
        ["Glucose", "Kissat", "CaDiCaL"],
        "experiments/logs/{}/all.json", 
        "experiments/plots/{}/all.png",
        is_order
    )

    run_batch(
        SIZES_NO_GLUCOSE, 
        ["Kissat", "CaDiCaL"],
        "experiments/logs/{}/kissat_and_cadical.json",
        "experiments/plots/{}/kissat_and_cadical.png",
        is_order
    )

for order in [True, False]:
    construct_formulas(order)
    run_race(order)

for k in SOLVERS.keys():
    fname = k.lower()
    run_single(
        SIZES_ALL if k == "Glucose" else SIZES_MERGE,
        k, 
        f"experiments/logs/{fname}.json",
        f"experiments/plots/{fname}.png"
    )