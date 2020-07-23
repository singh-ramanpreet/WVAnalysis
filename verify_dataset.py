#!/usr/bin/env python3

import subprocess
import json
import argparse


parser = argparse.ArgumentParser()

parser.add_argument("--datasets", type=str, default="datasets_2016.json",
                    help="json file: info of datasets, default=%(default)s")

parser.add_argument("--sample-tag", dest="sample_tag", type=str, default="all",
                    help="sample tag to process from json file, default=%(default)s")

args = parser.parse_args()

samples_dict = json.load(open(args.datasets, "r"))

for key in samples_dict:

    if args.sample_tag != "all" and args.sample_tag != key: continue

    location = samples_dict[key]["location"]
    filelist = samples_dict[key]["filelist"]
    lumi = samples_dict[key]["lumi"]

    print("\n")
    print(location)
    print("====================================================================")
    for i, sample in enumerate(filelist):

        root_file = location + sample["name"]
        xs = sample["xs"]
        nMC = sample["nMC"]
        nMCneg = sample["nMCneg"]
        print(key, sample["name"], xs, nMC, nMCneg)
        ls = subprocess.Popen(["rootls", root_file])
        ls.wait()
    print("====================================================================")