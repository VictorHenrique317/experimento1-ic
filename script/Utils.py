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