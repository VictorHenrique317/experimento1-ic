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


   
configs = None
with open("configs.json", "r") as file:
    configs = json.load(file)

Utils.deleteFolder("../experiment")
for i in range(1, configs["nb_iterations"]+1):
    Tensor.create(configs)
    Noise.run(configs)
    
    base_folder = f"../experiment/iterations/{i}"
    Utils.createFolder(base_folder)
    
    Multidupehack.run(configs, i)
    Paf.run(i)

Analysis.plotMultipleGraphs(configs, save=True)

# Evaluation.evaluateFile("../paf/t0-co1-e2.7-s3.paf")
# Evaluation.evaluateFiles(configs)
