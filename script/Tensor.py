# -*- coding: utf-8 -*-
from Utils import Utils
import time
class Tensor:
    def __init__(self):
        pass
    
    @staticmethod
    def _createSizesFile(pattern_size, n_patterns, base_folder):
        filename = "sizes.gennsets"
        if Utils.fileExists(filename, base_folder):
            print("Pattern sizes file already exists, skipping creation...")
            return
        else:
            print(f"Creating pattern sizes file...")
            line = f"{pattern_size} {pattern_size} {pattern_size}"
            with open(f"{base_folder}/sizes.gennsets", 'w') as sizes_file:
                for n in range(n_patterns):
                    sizes_file.write(f"{line}\n")
            print(f"Created {n_patterns} patterns with size {line}")
        
    
    @staticmethod
    def create(configs, iteration):
        time.sleep(1)
        dataset_size = configs["dataset_size"]
        tensor_name = configs["tensor_name"]
        pattern_size = configs["pattern_size"]
        n_patterns = configs["n_patterns"]
        
        base_folder = f"../experiment/iterations/{iteration}/tensor"
        Utils.createFolder(base_folder)
        Tensor._createSizesFile(pattern_size, n_patterns, base_folder)
        
        command = f"gennsets '{dataset_size[0]} {dataset_size[1]} {dataset_size[2]}' "
        command += f"{base_folder}/sizes.gennsets {base_folder}/{tensor_name} "
        command += f"> {base_folder}/log.txt"
        Utils.execute(command)
        print(f"Tensor file created")
            

        
