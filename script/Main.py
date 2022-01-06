# -*- coding: utf-8 -*-
import json
import os
from Noise import Noise
from Paf import Paf
from Multidupehack import Multidupehack
from Evaluation import Evaluation
from Utils import Utils 


   
configs = None
iterations = 3
with open("configs.json", "r") as file:
    configs = json.load(file)

for i in range(1, iterations+1):
    folder_path = f"../iterations/{i}"
    Utils.createFolder(folder_path)
    
    Multidupehack.multidupehack(configs, i)
    Paf.paf(i)
    
# Noise.noise(configs)

# Evaluation.evaluateFile("../paf/t0-co1-e2.7-s3.paf")
# Evaluation.evaluateFiles(configs)
