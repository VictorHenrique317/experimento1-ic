# -*- coding: utf-8 -*-
import re
import os
import shutil
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
            raise ValueError("Parameters all None")
        
    @staticmethod
    def createFolder(path):
        try:
            os.makedirs(path)
        except FileExistsError:
            pass
    @staticmethod
    def deleteFolder(path):
        try:
            shutil.rmtree(path)
        except OSError as e:
            print("Error: %s - %s." % (e.filename, e.strerror))
        
    @staticmethod
    def sumListElements(list1, list2):
        summed_list = []
        for i, value1 in enumerate(list1):
            value2 = list2[i]
            summed_list.append(value1 + value2)
        return summed_list
