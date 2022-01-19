# -*- coding: utf-8 -*-
import collections
import os
class Evaluation:
    def __init__(self):
        pass
    
    @staticmethod
    def jaccardIndex(found_pattern, planted_pattern): # 1,2 0,1 10,11 | 1,2 1,1 10,11
        found_pattern = [set(numbers.split(",")) for numbers in found_pattern.split(" ")]
        planted_pattern = [set(numbers.split(",")) for numbers in planted_pattern.split(" ")]
        
        intersection = []
        union = []    
        for i in range(3):
            intersection.append(found_pattern[i].intersection(planted_pattern[i]))
            union.append(found_pattern[i].union(planted_pattern[i]))
        
        intersection = len(intersection[0])+len(intersection[1])+len(intersection[2])
        union = len(union[0])+len(union[1])+len(union[2])
        return intersection / union # 0 <= return <= 1
    
    @staticmethod
    def findMostSimilarFoundPattern(planted_pattern, found_patterns): 
        # returns in conventional notation the most similar found pattern to a given planted one
        # found_patterns =[(0, "1,2 0,1 10,11"), (1, "1,2 1,1 10,11"), ...]
        similarities = []
        
        for found_pattern in found_patterns:
            jaccard_index = Evaluation.jaccardIndex(found_pattern[1], planted_pattern)
            similarities.append(jaccard_index)
            
        most_similar_index = similarities.index(max(similarities))
        line_nb = found_patterns[most_similar_index][0]
        most_similar_pattern = found_patterns[most_similar_index][1]
        # returns the line  number of the most similar pattern and the most similar pattern
        return (line_nb, most_similar_pattern)
    
    @staticmethod
    def findHigherJaccard(planted_pattern, found_patterns):
        # given a planted pattern, this returns the jaccard index
        # of the most similar pattern found by paf
        line_number, most_similar_found = Evaluation.\
            findMostSimilarFoundPattern(planted_pattern, found_patterns)
        jaccard_index = Evaluation.jaccardIndex(most_similar_found, planted_pattern)
        
        return (line_number, jaccard_index)
    
    @staticmethod
    def getPlantedPatterns():
        # ['pattern','pattern']
        patterns = None
        with open("../experiment/tensor/dataset.tensor", "r") as pattern_file:
            patterns = [line.replace("\n", "").strip() for line in pattern_file]
        return patterns
    
    @staticmethod
    def deletePatternInLine(line, patterns):
        remove_index = None
        for index, pattern in enumerate(patterns):
            line_nb = pattern[0]
            if line_nb == line:
                remove_index = index
                break
        del patterns[remove_index] 
        
    @staticmethod
    def truncatePatterns(paf_file, number):
        counter = 0
        truncated_patterns = []
        for line_nb, pattern in enumerate(paf_file):
            counter += 1
            if counter > number:
                break
            truncated_patterns.append((line_nb, pattern.replace("\n","")))
        return truncated_patterns
    
    @staticmethod
    def calculateScore(configs, evaluation_data):
        evaluation_data = collections.OrderedDict(sorted(evaluation_data.items()))
        
        numerator = 0
        denominator = 0
        for line_nb, jaccard_index in evaluation_data.items():
            numerator += jaccard_index
            denominator += 1
            
        return numerator/denominator
        
    
    @staticmethod
    def evaluateFile(configs, path):
        planted_patterns = Evaluation.getPlantedPatterns()
        evaluation_data = dict()
        with open(path, "r") as file:
            found_patterns = Evaluation.\
                truncatePatterns(file, configs["nb_of_truncated_patterns"])
            
            for planted_pattern in planted_patterns:
                if len(found_patterns) == 0: 
                    break
                line_nb, jaccard_index = Evaluation.findHigherJaccard(planted_pattern, found_patterns)
                Evaluation.deletePatternInLine(line_nb, found_patterns)
                evaluation_data[line_nb] = jaccard_index
                
        file_score = Evaluation.calculateScore(configs, evaluation_data)                
        return file_score
    
    @staticmethod
    def evaluateFiles(configs, multidupehack=False, paf=False): # IMPLEMENTAR MÉDIA
        if multidupehack is False and paf is False:
            raise ValueError("multidupehack or paf should be True")
            
        file_type = None
        if multidupehack:
            file_type = "multidupehack"
        elif paf:
            file_type = "paf"
        base_folder = "../experiment/iterations/1"
        experiments = dict()
        
        for experiment in os.listdir(base_folder):
            path = f"{base_folder}/{experiment}/{file_type}/{experiment}.{file_type}"
            value = Evaluation.evaluateFile(configs, path)
            experiments[experiment] = value
        return experiments
    
    @staticmethod
    def evaluateMultidupehackFiles(configs):
        return Evaluation.evaluateFiles(configs, multidupehack=True)
    
    @staticmethod
    def evaluatePafFiles(configs):
        return Evaluation.evaluateFiles(configs, paf=True)