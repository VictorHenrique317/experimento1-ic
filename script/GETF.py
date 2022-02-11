from fnmatch import translate
from Utils import Utils
from Multidupehack import Multidupehack
from Noise import Noise
import numpy as np
import re

class GETF():
    def __init__(self) -> None:
        pass

    @staticmethod
    def calculateNoiseEndurance(u):
        return u

    @staticmethod
    def genGETFName(observations, noise_endurance, max_pattern_number):
        return f"co{observations}-ne{noise_endurance}-pn{max_pattern_number}.getf"

    @staticmethod
    def genNumpyName(observations, noise_endurance, max_pattern_number):
        return f"co{observations}-ne{noise_endurance}-pn{max_pattern_number}"

    @staticmethod
    def translateFuzzyTensor(configs, fuzzy_path, iteration):
        dataset_size = configs["dataset_size"]
        # dataset_size = [4,4]
        translated_tensor =  np.zeros(dataset_size)
        # depth, row, column
        
        with open(fuzzy_path) as file:
            for line in file:
                line = [float(character) for character in line.split(" ")]
                value = line[-1] 
                value = 1 if value > 0.5 else 0
                dims = [int(dim) for dim in line[:-1]]

                replacer_string = f"translated_tensor{dims} = {value}"
                exec(replacer_string)

        output_folder = f"../experiment/iterations/{iteration}/numpy_tensors"
        filename = fuzzy_path.split("/")[-1]
        filename = re.sub(".fuzzy_tensor", "", filename)
        Utils.createFolder(output_folder)

        translated_tensor_path = f"{output_folder}/{filename}"
        np.save(translated_tensor_path, translated_tensor)
        return translated_tensor_path + ".npy"
    
    @staticmethod
    def translateNumpyPatterns(configs, pattern_file_path, getf_name, iteration):
        print("================================")
        numpy_tensor = np.load(pattern_file_path)
        patterns = [pattern for pattern in numpy_tensor]
        # reconstructed_tensor = 
        for index, value in np.ndenumerate(numpy_tensor):
            # print(f"{index} = {value}")
            pass

    @staticmethod   
    def run(configs, iteration):
        correct_obs = configs["correct_obs"]
        u_values = configs["u_values"]
        max_pattern_number = configs["getf_max_pattern_number"]
        size = configs["s"]

        getf_folder = "../libs/GETF"
        script_name = "run.R"

        total_count = len(correct_obs) * len(u_values)
        counter = 0
        for observations in correct_obs:
            fuzzy_name = Noise.genFuzzyName(observations)
            fuzzy_path = f"../experiment/iterations/{iteration}/fuzzy_tensors/{fuzzy_name}"
            translated_tensor_path = GETF.translateFuzzyTensor(configs, fuzzy_path, iteration)

            for u in u_values:
                counter += 1
                noise_endurance = GETF.calculateNoiseEndurance(u)
                
                #  ===== only for getting experiment folder name
                epsilon = Multidupehack.calculateEpsilon(u)
                multidupehack_name = Multidupehack.genMultidupehackName(observations, epsilon, size)
                experiment_folder_name = Utils.getExperimentFolderName(multidupehack_name=multidupehack_name)
                #  ===== 
                
                getf_name = GETF.genGETFName(observations, noise_endurance, max_pattern_number)
                numpy_name = GETF.genNumpyName(observations, noise_endurance, max_pattern_number)
                
                
                output_folder = f"../experiment/iterations/{iteration}/{experiment_folder_name}/getf"
                Utils.createFolder(output_folder)

                # getf_name = GETF.genGETFName(observations, noise_endurance, max_pattern_number)
                # getf_name = "co16"
                #numpy_tensor_path, noise_endurance, max_pattern_number
                command = f"Rscript {getf_folder}/{script_name} {translated_tensor_path} "
                command += f"{noise_endurance} "
                command += f"{max_pattern_number} "
                command += f"{iteration} "
                command += f"{experiment_folder_name} "
                command += f"{numpy_name}"

                print("="*120)
                print(command)
                Utils.execute(command)                
                
                #prints the progression
                print(f"({counter} of {total_count} done)")
                print("="*120)
                # pattern_file_path = f"../experiment/iterations/{iteration}/{experiment_folder_name}/getf/{numpy_name}"
                # GETF.translateNumpyPatterns(configs, pattern_file_path, getf_name, iteration)
                
        # getf_folder = "../libs/GETF"
        # script_name = "run.R"
        # Utils.execute(f"Rscript {getf_folder}/{script_name}")