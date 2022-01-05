# -*- coding: utf-8 -*-
from Utils import Utils
class Noise:
    def __init__(self):
        pass
    
    @staticmethod
    def genFuzzyName(correct_observations):
        return f"dataset-co{correct_observations}.fuzzy_tensor"
    
    @staticmethod
    def noise(configs):
        correct_obs = configs["correct_obs"]
        dataset_size = configs["dataset_size"]
        tensor_name = configs["tensor_name"]
        for observations in correct_obs: 
            fuzzy_name = Noise.genFuzzyName(observations)
            command = f"cat ../tensor/{tensor_name} "
            command += f"| num-noise '{dataset_size[0]} "
            command += f"{dataset_size[1]} "
            command += f"{dataset_size[2]}' "
            command += f"{observations} 0 > ../fuzzy_tensors/{fuzzy_name}"
            print(command)
            Utils.execute(command)
