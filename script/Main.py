# -*- coding: utf-8 -*-
import json
import os
from Noise import Noise
from Paf import Paf
from Multidupehack import Multidupehack
from Analysis import Analysis
from Evaluation import Evaluation
from Utils import Utils 
from Tensor import Tensor
from GETF import GETF

configs = None
with open("configs.json", "r") as file:
    configs = json.load(file)

# Utils.deleteFolder("../experiment")
# for i in range(1, configs["nb_iterations"]+1):
#     Tensor.create(configs, i)
#     Noise.run(configs, i)
    
#     base_folder = f"../experiment/iterations/{i}"
#     Utils.createFolder(base_folder)
    
#     Multidupehack.run(configs, i)
#     Paf.run(i)
#     # Paf.run(i,a=10) # resultados estranhos

# Analysis.plotMultipleGraphs(configs, save=True, custom_ylimits=True)
# Analysis.plotScoreGraph(configs, save=True)
# translation = GETF.translateFuzzyTensor(configs, "../experiment/iterations/1/fuzzy_tensors/2d_test_fuzzy.fuzzy_tensor", 1)
# translation = GETF.translateFuzzyTensor(configs, "../experiment/iterations/1/fuzzy_tensors/dataset-co16.fuzzy_tensor", 1)
# print(translation)
getf_folder = "../libs/GETF"
script_name = "run.R"

path = "../experiment/iterations/1/numpy_tensors/2d_test_fuzzy.npy"
# Utils.execute(f"Rscript {getf_folder}/{script_name} {path} 0.9 20 1 co16-e3.6-s3 2d_test_fuzzy")
pattern_file_path = f"../experiment/iterations/1/co16-e3.6-s3/getf/2d_test_fuzzy.npy"
# GETF.translateNumpyPatterns(configs, pattern_file_path, "co16.getf", 1)
GETF.run(configs, 1)

