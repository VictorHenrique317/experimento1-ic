# -*- coding: utf-8 -*-
import re
import os
class Utils:
    def __init__(self):
        pass

    @staticmethod
    def execute(command):
        os.system(command)
    
    @staticmethod
    def fileExists(pattern, folder):
        for filename in os.listdir(folder):
            if re.search(pattern, filename) != None:
                print(f"=> skipped {filename}")
                return True
            
    @staticmethod
    def getExperimentFolderName(multidupehack_name=None, paf_name=None):
        if multidupehack_name is not None:
            return re.sub(".multidupehack", "", multidupehack_name)
        elif paf_name is not None:
            return re.sub(".paf", "", paf_name)
        else:
            raise ValueError("Two None parameters")
        
    @staticmethod
    def createFolder(path):
        try:
            os.makedirs(path)
        except FileExistsError:
            pass