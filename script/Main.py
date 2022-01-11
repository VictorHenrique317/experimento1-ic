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
iterations = 3
with open("configs.json", "r") as file:
    configs = json.load(file)

Tensor.create(configs)
Noise.run(configs)
for i in range(1, iterations+1):
    folder_path = f"../experiment/iterations/{i}"
    Utils.createFolder(folder_path)
    
    Multidupehack.run(configs, i)
    Paf.run(i)

Analysis.plotMultipleGraphs(configs, color="red", save=True)

# Evaluation.evaluateFile("../paf/t0-co1-e2.7-s3.paf")
# Evaluation.evaluateFiles(configs)
