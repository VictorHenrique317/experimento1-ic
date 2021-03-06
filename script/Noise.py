# -*- coding: utf-8 -*-
from Utils import Utils
class Noise:
    def __init__(self):
        pass
    
    @staticmethod
    def genFuzzyName(correct_observations):
        return f"dataset-co{correct_observations}.fuzzy_tensor"
    
    @staticmethod
    def run(configs, iteration):
        correct_obs = configs["correct_obs"]
        dataset_size = configs["dataset_size"]
        tensor_name = configs["tensor_name"]
        base_folder = f"../experiment/iterations/{iteration}/fuzzy_tensors"
        Utils.createFolder(base_folder)
        for observations in correct_obs: 
            fuzzy_name = Noise.genFuzzyName(observations)
            
            command = f"cat ../experiment/iterations/{iteration}/tensor/{tensor_name} "
            command += f"| num-noise '{dataset_size[0]} "
            command += f"{dataset_size[1]} "
            command += f"{dataset_size[2]}' "
            command += f"{observations} 0 > {base_folder}/{fuzzy_name}"
            print(command)
            print("="*120)
            Utils.execute(command)
           