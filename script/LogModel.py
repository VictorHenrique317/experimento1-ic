# -*- coding: utf-8 -*-
import re
class LogModel:
    def __init__(self, path):
        self.path = path
        self._initialize()
        
    def _initialize(self):
        data = dict() # {property: value}
        with open(self.path) as log:
            for line in log:
                match = re.findall("(.*):(.*)", line)
                key = match[0][0]
                value = match[0][1]
                data[key] = value
        self.attributes = data
