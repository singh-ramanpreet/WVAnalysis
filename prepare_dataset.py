#!/usr/bin/env python3

import argparse
import json
import numpy as np
import awkward
import uproot
from pprint import pprint

parser = argparse.ArgumentParser()

parser.add_argument(
    "--datasets", type=str, default="datasets_2016.json",
    help="json file: info of datasets, default=%(default)s"
    )

parser.add_argument(
    "--variables", type=str, default="variables_map.json",
    help="json file: variables central and systematic map, default=%(default)s"
    )

parser.add_argument(
    "--systematic", type=str, default="",
    help="variables point to given systematic, default=%(default)s"
    )

parser.add_argument(
    "--output", type=str, default="df_dataset.awkd",
    help="awkd file output name, default=%(default)s"
    )

args = parser.parse_args()

# map variables to be used
print(f"Preparing data_frames for systematic '{args.systematic}'")

variables_mapped = {}
variables_map = json.load(open(args.variables, "r"))

for name_ in variables_map:
    systematic = args.systematic
    if systematic not in variables_map[name_]:
        print(f"systematic '{systematic}' not available for '{name_}'")
        print(f"using central variable for '{name_}'")
        print("")
        systematic = "central"

    variables_mapped[name_] = variables_map[name_][systematic]

pprint(variables_mapped, width=1)
input("...")

ttree_branches = list(variables_mapped.values())
print(ttree_branches)

# Loop over samples
dfs = {}
samples_dict = json.load(open(args.datasets, "r"))

for key in samples_dict:

    location = samples_dict[key]["location"]
    filelist = samples_dict[key]["filelist"]
    lumi = samples_dict[key]["lumi"]

    for sample in filelist:

        root_file = location + sample["name"]
        xs = sample["xs"]
        nMC = sample["nMC"]
        nMCneg = sample["nMCneg"]

        xs_weight = (lumi * xs) / (nMC - (2 * nMCneg))

        print("loading ... ", key, sample["name"])

        if key in ["data_obs", "WJets"]:
            df = uproot.lazyarrays(root_file, "otree", branches=ttree_branches, persistvirtual=True)
        else:
            df = uproot.lazyarrays(root_file, "otree", branches=ttree_branches + ["isResolved"], persistvirtual=True)

        for new_name, var_name in variables_mapped.items():
            df[new_name] = df[var_name]
            if new_name != var_name:
                del df[var_name]

        # some derived columns
        df["fatjet_n2b1"] = df["fatjet_e3_v2_sdb1"] / (df["fatjet_e2_sdb1"])**2
        df["fatjet_n2b2"] = df["fatjet_e3_v2_sdb2"] / (df["fatjet_e2_sdb2"])**2
        df["ht"] = df["fatjet_pt"] + df["vbf_j1_pt"] + df["vbf_j2_pt"]
        df["zeppenfeld_w_Deta"] = df["zeppenfeld_w"] / df["vbf_jj_Deta"]
        df["zeppenfeld_v_Deta"] = df["zeppenfeld_v"] / df["vbf_jj_Deta"]

        if "isResolved" not in df.columns:
            df["isResolved"] = False

        if "data" in key:
            df["btag0_weight"] = 1.0

        dfs[f"{key}/{sample['name']}"] = {"xs_weight": xs_weight, "dframe": df}

output_filename = args.output

if args.systematic != "":
    output_ = args.output.split(".awkd")[0]
    output_filename = f"{output_}_{args.systematic}.awkd"

awkward.save(output_filename, dfs, mode="w")
