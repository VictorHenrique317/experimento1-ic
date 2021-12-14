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
    return f"t{time}-co{correct_observations}-e{epsilon}-s{size}.multidupehack"

def genPafName(multidupehack_name, a, time):
    filename = None
    if a == 1000000: # dont show a
        filename = f"{multidupehack_name.replace('.multidupehack', '')}.paf"
    else: # show a
        filename = f"{multidupehack_name.replace('.multidupehack', '')}-a{a}.paf"
        
    return re.sub("(t\d*)", f"t{time}", filename)
    

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
            pattern = f"(t.+-co{observations}-e{e}-s{min_size}.multidupehack)"
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
            
def getTensorPath(multidupehack_name):
    pattern = "-(co\d*)"
    correct_observations = re.search(pattern, multidupehack_name).group()
    return f"../fuzzy_tensors/dataset{correct_observations}.fuzzy_tensor"
    
def paf(a=1000000):
    #t1-co16-e1-s3.6.paf
    # cat ../fuzzy_tensors/dataset-co32.fuzzy_tensor |
    # paf -vf - -a150000 t1-co32-e1-s4.5.multidupehack  
    pattern = "-(co\d*-e\d*\.\d*-s\d*\.\d*)"
    counter = 0
    multidupack_files = os.listdir("../multidupehack/")
    for multidupehack_name in multidupack_files:
        counter += 1
        if fileExists(pattern, "../paf/"):
            continue
        
        tensor_path = getTensorPath(multidupehack_name) 
        command = f"cat {tensor_path} | "
        command += f"paf -o ../paf/temp.txt -vf "
        command += f"- -a{a} ../multidupehack/{multidupehack_name} "
        
        print("="*120)
        print(command)
        #runs paf and calculate time
        t0 = time()
        execute(command)
        delta = round(time() - t0)
        
        #creates the FINAL file
        paf_filename = genPafName(multidupehack_name, a, delta)
        command = f"mv ../paf/temp.txt ../paf/{paf_filename}"
        # print(command)
        execute(command)
        print(f"({counter} of {len(multidupack_files)} done)")
        print("="*120)


def jaccardIndex(found_pattern, planted_pattern): # 1,2 0,1 10,11 | 1,2 1,1 10,11
    found_pattern = [set(numbers.split(",")) for numbers in found_pattern.split(" ")]
    planted_pattern = [set(numbers.split(",")) for numbers in planted_pattern.split(" ")]

    intersection = []
    union = []    
    for i in range(3):
        intersection.append(found_pattern[i].intersection(planted_pattern[i]))
        union.append(found_pattern[i].union(planted_pattern[i]))
        
    intersection = len(intersection[0])*len(intersection[1])*len(intersection[2])
    union = len(union[0])*len(union[1])*len(union[2])
    
    return intersection / union # 0 <= return <= 1
    
def findMostSimilarPlanted(found_pattern, planted_patterns): 
    # returns in conventional notation the most similar planted pattern
    similarities = []
    for planted_pattern in planted_patterns:
        similarities.append(jaccardIndex(found_pattern, planted_pattern))
        
    most_similar_index = similarities.index(max(similarities))
    return planted_patterns[most_similar_index]

def findHigherJaccard(found_pattern, planted_patterns):
    # given a pattern found by paf, this returns the jaccard index
    # of the most similar planted pattern
    most_similar_planted = findMostSimilarPlanted(found_pattern, planted_patterns)
    return jaccardIndex(found_pattern, most_similar_planted)

def getPlantedPatterns():
    # ['pattern','pattern']
    patterns = None
    with open("../tensor/dataset.tensor", "r") as pattern_file:
        patterns = [line.replace("\n", "").strip() for line in pattern_file]
    return patterns

def evaluateFile(paffile_path, ideal_pattern_number):
    planted_patterns = getPlantedPatterns()
    scores = []
    ideal_score = ideal_pattern_number # ideal sum of jaccard indices
    with open(paffile_path, "r") as paf_file:
        counter = 0
        for pattern in paf_file:
            counter += 1
            jaccard_index = findHigherJaccard(pattern, planted_patterns)
            if(counter > ideal_pattern_number): # penalize the final score
                scores.append((1-jaccard_index)*-1) # higher similarities penalize less
            else: # increases the final score
                scores.append(jaccard_index)
    return 100*(sum(scores) / ideal_score) 

def evaluateFiles(configs):
    paf_files = os.listdir("../paf/")
    file_scores = dict()
    ideal_pattern_number = configs["n_planted_patterns"]
    for paf_file in paf_files:
        file_scores[paf_file] = evaluateFile(f"../paf/{paf_file}", ideal_pattern_number)
        
    file_scores = dict(sorted(file_scores.items(), key=lambda item: item[1], reverse=True))
    for key, value in file_scores.items():
        print(f"{value: .2f}% => {key}")
    
configs = None
with open("configs.json", "r") as file:
    configs = json.load(file)

# noise(configs)
# multidupehack(configs)
# paf()
evaluateFiles(configs)
