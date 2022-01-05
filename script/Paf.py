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
    def genPafName(multidupehack_name, a, time):
        filename = None
        if a == 1000000: # dont show a
            filename = f"{multidupehack_name.replace('.multidupehack', '')}.paf"
        else: # show a
            filename = f"{multidupehack_name.replace('.multidupehack', '')}-a{a}.paf"
            
        return re.sub("(t\d*)", f"t{time}", filename)
    
    @staticmethod
    def paf(iteration, a=1000000):
        #t1-co16-e1-s3.6.paf
        # cat ../fuzzy_tensors/dataset-co32.fuzzy_tensor |
        # paf -vf - -a150000 t1-co32-e1-s4.5.multidupehack  
        
        counter = 0
        multidupack_files = os.listdir(f"../iterations/{iteration}/multidupehack/")
        for multidupehack_name in multidupack_files:
            # pattern = "-(co\d*-e\d*\.\d*-s\d*\.\d*)"
            pattern = re.sub("t\d*-", "", multidupehack_name)
            pattern = re.sub("multidupehack", "paf", pattern)
            counter += 1
            if Utils.fileExists(pattern, f"../iterations/{iteration}/paf/"):
                continue
            
            tensor_path = Multidupehack.getTensorPath(multidupehack_name) 
            command = f"cat {tensor_path} | "
            command += f"paf -o ../iterations/{iteration}/paf/temp.txt -vf "
            command += f"- -a{a} ../iterations/{iteration}/multidupehack/{multidupehack_name} "
            
            print("="*120)
            print(command)
            #runs paf and calculate time
            t0 = time()
            Utils.execute(command)
            delta = round(time() - t0)
            
            #creates the FINAL file
            paf_filename = Paf.genPafName(multidupehack_name, a, delta)
            command = f"mv ../iterations/{iteration}/paf/temp.txt ../iterations/{iteration}/paf/{paf_filename}"
            # print(command)
            Utils.execute(command)
            print(f"({counter} of {len(multidupack_files)} done)")
            print("="*120)

