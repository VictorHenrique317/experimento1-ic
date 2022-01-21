# -*- coding: utf-8 -*-
from time import time
import re
import os
from Utils import Utils
from Multidupehack import Multidupehack
class Paf:
    def __init__(self):
        pass
    
    @staticmethod
    def getMultidupehackName(multidupehack_file_path):
        pattern = "(co\d*-e\d*\.*\d*-s\d*\.*\d*\.multidupehack)"
        return re.findall(pattern, multidupehack_file_path)[0]

    @staticmethod
    def genPafName(multidupehack_file_path):
        multidupehack_name = Paf.getMultidupehackName(multidupehack_file_path)
        return f"{multidupehack_name.replace('.multidupehack', '')}.paf"
      
        
    @staticmethod
    def getMultidupackFilePaths(iteration):
        multidupack_file_paths = []
        for folder in os.listdir(f"../experiment/iterations/{iteration}"):
            path = f"../experiment/iterations/{iteration}/{folder}/multidupehack/{folder}.multidupehack"
            multidupack_file_paths.append(path)
            
        return multidupack_file_paths

    @staticmethod
    def run(iteration, a=1000000):
        #co16-e1-s3.6.paf
        # cat ../fuzzy_tensors/dataset-co32.fuzzy_tensor |
        # paf -vf - -a150000 t1-co32-e1-s4.5.multidupehack  
    
        counter = 0
        multidupack_file_paths = Paf.getMultidupackFilePaths(iteration)
        for multidupehack_file_path in multidupack_file_paths:
            # pattern = "-(co\d*-e\d*\.\d*-s\d*\.\d*)"
           
            multidupehack_name = Paf.getMultidupehackName(multidupehack_file_path)
            paf_name = Paf.genPafName(multidupehack_file_path)
            experiment_folder_name = Utils.getExperimentFolderName(paf_name=paf_name)
            
            output_folder = f"../experiment/iterations/{iteration}/{experiment_folder_name}/paf"
            Utils.createFolder(output_folder)
            
            counter += 1
            
            tensor_path = Multidupehack.getTensorPath(multidupehack_name) 
            command = f"/usr/bin/time -o {output_folder}/log.txt -f 'Memory: %M' "
            command += f"cat {tensor_path} | "
            command += f"paf -o {output_folder}/{paf_name} -f "
            command += f"- -a{a} ../experiment/iterations/{iteration}/{experiment_folder_name}/multidupehack/{multidupehack_name} "
            command += f">> {output_folder}/log.txt"
            print("="*120)
            print(command)
            
            Utils.execute(command)
            print(f"({counter} of {len(multidupack_file_paths)} done)")
            print("="*120)

