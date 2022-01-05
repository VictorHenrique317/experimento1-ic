# -*- coding: utf-8 -*-
from time import time
import re
from Noise import Noise
from Utils import Utils
class Multidupehack:
    def __init__(self):
        pass

    @staticmethod
    def genMultidupehackName(correct_observations, epsilon, size, time):
        return f"t{time}-co{correct_observations}-e{epsilon}-s{size}.multidupehack"
    
    @staticmethod
    def getTensorPath(multidupehack_name):
        pattern = "-(co\d*)"
        correct_observations = re.search(pattern, multidupehack_name).group()
        return f"../fuzzy_tensors/dataset{correct_observations}.fuzzy_tensor"
    
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
                
                #skips existing files
                pattern = f"(t.+-co{observations}-e{e}-s{s}.multidupehack)"
                if Utils.fileExists(pattern, f"../iterations/{iteration}/multidupehack/"):
                    continue
                
                fuzzy_name = Noise.genFuzzyName(observations)
                command = f"multidupehack -s'{s} {s} {s}' "
                command += f"-e '{e} {e} {e}' ../fuzzy_tensors/{fuzzy_name} "
                command += f"> ../iterations/{iteration}/multidupehack/temp.txt"
                print("="*120)
                print(command)
                
                #runs multidupehack and calculate time
                t0 = time()
                Utils.execute(command)
                delta = round(time() - t0)
                
                #creates the FINAL file
                multidupehackName = Multidupehack.genMultidupehackName(observations, e, s, delta)
                command = f"mv ../iterations/{iteration}/multidupehack/temp.txt ../iterations/{iteration}/multidupehack/{multidupehackName}"
                Utils.execute(command)
                
                #prints the progression
                print(f"({counter} of {total_count} done)")
                print("="*120)
