# -*- coding: utf-8 -*-
from time import time
import re
from Noise import Noise
from Utils import Utils
class Multidupehack:
    def __init__(self):
        pass

    @staticmethod
    def genMultidupehackName(correct_observations, epsilon, size):
        return f"co{correct_observations}-e{epsilon}-s{size}.multidupehack"
    
    @staticmethod
    def getTensorPath(multidupehack_name):
        pattern = "(co\d*)"
        correct_observations = re.search(pattern, multidupehack_name).group()
        return f"../fuzzy_tensors/dataset-{correct_observations}.fuzzy_tensor"
    
    @staticmethod
    def multidupehack(configs, iteration):
        correct_obs = configs["correct_obs"]
        u_values = configs["u_values"]
        s = configs["s"]
        counter = 0
        total_count = len(correct_obs) * len(u_values)
        for observations in correct_obs:
            for u in u_values:
                counter += 1
                e = float(f"{3**2*(1-u): .1f}")
                
                multidupehack_name = Multidupehack.genMultidupehackName(observations, e, s)
                experiment_folder_name = Utils.getExperimentFolderName(multidupehack_name=multidupehack_name)
                
                output_folder = f"../iterations/{iteration}/{experiment_folder_name}/multidupehack"
                Utils.createFolder(output_folder)
                
                #skips existing files
                pattern = f"(co{observations}-e{e}-s{s}.multidupehack)"
                if Utils.fileExists(pattern, output_folder):
                    continue
                
                fuzzy_name = Noise.genFuzzyName(observations)
                command = f"multidupehack -s'{s} {s} {s}' "
                command += f"-e '{e} {e} {e}' ../fuzzy_tensors/{fuzzy_name} "
                command += f"-o {output_folder}/{multidupehack_name} "
                command += f"> {output_folder}/log.txt"
                print("="*120)
                print(command)
                Utils.execute(command)                
                
                #prints the progression
                print(f"({counter} of {total_count} done)")
                print("="*120)
