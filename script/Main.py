# -*- coding: utf-8 -*-
import os
import re
import json
from time import time
def execute(command):
    os.system(command)
    
def genFuzzyName(correct_observations):
    return f"dataset-co{correct_observations}.fuzzy_tensor"

def genMultidupehackName(correct_observations, epsilon, size, time):
    return f"-t{time}-co{correct_observations}-e{epsilon}-s{size}.multidupehack"

def genPafName(multidupehack_file, a, time):
    filename = None
    if a == 10000000000000: # dont show a
        filename = f"{multidupehack_file.replace('.multidupehack', '')}.paf"
    else: # show a
        filename = f"{multidupehack_file.replace('.multidupehack', '')}-a{a}.paf"
        
    return re.sub("(-t\d*)", f"-t{time}", filename)
    

def noise(configs):
    correct_obs = configs["correct_obs"]
    dataset_size = configs["dataset_size"]
    tensor_name = configs["tensor_name"]
    for observations in correct_obs: 
        fuzzy_name = genFuzzyName(observations)
        command = f"cat ../tensor/{tensor_name} "
        command += f"| num-noise '{dataset_size[0]} "
        command += f"{dataset_size[1]} "
        command += f"{dataset_size[2]}' "
        command += f"{observations} 0 > ../fuzzy_tensors/{fuzzy_name}"
        print(command)
        execute(command)
        
def fileExists(pattern, folder):
    for filename in os.listdir(folder):
        if re.search(pattern, filename) != None:
            print(f"=> skipped {filename}")
            return True


def multidupehack(configs):
    correct_obs = configs["correct_obs"]
    u_values = configs["u_values"]
    e = configs["epsilon"]
    counter = 0
    total_count = len(correct_obs) * len(u_values)
    for observations in correct_obs:
        for u in u_values:
            counter += 1
            min_size = float(f"{3**2*(1-u): .1f}")
            
            #skips existing files
            pattern = f"(-t.+-co{observations}-e{e}-s{min_size}.multidupehack)"
            if fileExists(pattern, "../multidupehack/"):
                continue
            
            fuzzy_name = genFuzzyName(observations)
            command = f"multidupehack -s'{min_size} {min_size} {min_size}' "
            command += f"-e '{e} {e} {e}' ../fuzzy_tensors/{fuzzy_name} "
            command += "> ../multidupehack/temp.txt"
            print("="*120)
            print(command)
            
            #runs multidupehack and calculate time
            t0 = time()
            execute(command)
            delta = round(time() - t0)
            
            #creates the FINAL file
            multidupehackName = genMultidupehackName(observations, e, min_size, delta)
            command = f"mv ../multidupehack/temp.txt ../multidupehack/{multidupehackName}"
            execute(command)
            
            #prints the progression
            print(f"({counter} of {total_count} done)")
            print("="*120)
            
def paf(a=10000000000000):
    counter = 0
    multidupack_files = os.listdir("../multidupehack/")
    for filename in multidupack_files:
        counter += 1
        if fileExists(filename, "../paf/"):
            continue
        
        # command = f"cat ../multidupehack/{filename} | "
        # command += f"paf -vf -a{a} "
        # command += "> temp.txt"
        
        command += f"paf -vf -a{a} -"
        
        print("="*120)
        print(command)
        #runs paf and calculate time
        t0 = time()
        execute(command)
        delta = round(time() - t0)
        
        #creates the FINAL file
        paf_filename = genPafName(filename, a, delta)
        command = f"mv ../paf/temp.txt ../paf/{paf_filename}"
        print(command)
        execute(command)
        print(f"({counter} of {len(multidupack_files)} done)")
        print("="*120)

configs = None
with open("configs.json", "r") as file:
    configs = json.load(file)

# noise(configs)
multidupehack(configs)
paf()