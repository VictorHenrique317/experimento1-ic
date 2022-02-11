# -*- coding: utf-8 -*-
import collections
import os
import re
import time
from statistics import mean
class Evaluation:
    __dimension = None

    def __init__(self):
        pass
    
    @staticmethod
    def getDimension():
        planted_patterns = Evaluation.getPlantedPatterns(1)
        dimension = planted_patterns[0].split(" ")
        return len(dimension)
        
    @staticmethod
    def formatPattern(pattern):
        if type(pattern) == list: # already formated
            return pattern 
        
        pattern =  pattern.split(" ")
        if len(pattern) > Evaluation.__dimension:
            del pattern[-1] # deletes the density of the pattern found by paf
            
        return [set(numbers.split(",")) for numbers in pattern]
    
    @staticmethod
    def formatMultiplePatterns(patterns):
        formated = []
        for pattern in patterns:
            formated.append(Evaluation.formatPattern(pattern))
        return formated
    
    @staticmethod
    def patternIntersection(found_pattern, planted_pattern): # 1,2 0,1 10,11 # too slow
        # found_pattern = Evaluation.formatPattern(found_pattern)
        # planted_pattern = Evaluation.formatPattern(planted_pattern)
        intersection = []
        for i in range(Evaluation.__dimension):
            ith_tuple1 = found_pattern[i] # {'1', '2'}
            ith_tuple2 = planted_pattern[i] # {'1', '3'}
            intersection.append(ith_tuple1.intersection(ith_tuple2))
        return intersection
    
    @staticmethod
    def patternUnion(found_pattern, planted_pattern): # 1,2 0,1 10,11 # too slow
        union = []
        # found_pattern = Evaluation.formatPattern(found_pattern)
        # planted_pattern = Evaluation.formatPattern(planted_pattern)
        
        for i in range(Evaluation.__dimension):
            ith_tuple1 = found_pattern[i] # {'1', '2'}
            ith_tuple2 = planted_pattern[i] # {'1', '3'}
            union.append(ith_tuple1.union(ith_tuple2))
        return union
        
    @staticmethod
    def calculatePatternArea(pattern):
        pattern_area = 1
        for ith_tuple in pattern:
            pattern_area *= len(ith_tuple)
        return pattern_area
    
    @staticmethod
    def patternIntersectionArea(found_pattern, planted_pattern):# 1,2 0,1 10,11
        intersection = Evaluation.patternIntersection(found_pattern, planted_pattern)
        return Evaluation.calculatePatternArea(intersection)
    
    @staticmethod
    def patternUnionArea(found_pattern, planted_pattern): # 1,2 0,1 10,11
        union = Evaluation.patternUnion(found_pattern, planted_pattern)
        return Evaluation.calculatePatternArea(union)
    
    @staticmethod
    def jaccardIndex(found_pattern, planted_pattern): # 1,2 0,1 10,11 | 1,2 1,1 10,11 (union=12->8+8-4)
        intersection = Evaluation.patternIntersectionArea(found_pattern, planted_pattern)
        union = Evaluation.patternUnionArea(found_pattern, planted_pattern)
        return intersection / union # 0 <= return <= 1
    
    @staticmethod
    def findMostSimilarFoundPattern(planted_pattern, found_patterns): 
        # returns the most similar found pattern to a given planted one
        similarities = []
        index = 0
        planted_pattern = Evaluation.formatPattern(planted_pattern)
        for found_pattern in found_patterns:
            index += 1
            found_pattern = Evaluation.formatPattern(found_pattern)
            jaccard_index = Evaluation.jaccardIndex(found_pattern, planted_pattern)  # too slow
            similarities.append(jaccard_index)
        most_similar_index = similarities.index(max(similarities))
        most_similar_pattern = found_patterns[most_similar_index]
        return most_similar_pattern
    
    @staticmethod
    def getPlantedPatterns(iteration):
        # ['pattern','pattern']
        patterns = None
        with open(f"../experiment/iterations/{iteration}/tensor/dataset.tensor", "r") as pattern_file:
            patterns = [line.replace("\n", "").strip() for line in pattern_file]
        return patterns
    
    @staticmethod
    def truncatePatterns(paf_file, number):
        if number == -1:
            return [pattern.replace("\n", "") for pattern in paf_file]
        
        counter = 0
        truncated_patterns = []
        for pattern in paf_file:
            counter += 1
            if counter > number:
                break
            truncated_patterns.append(pattern.replace("\n",""))
        return truncated_patterns
    
    @staticmethod
    def multiplePatternUnion(patterns):
        union = [set() for i in range(Evaluation.__dimension)]
        for pattern in patterns:
            for i in range(Evaluation.__dimension):
                ith_union_component = union[i]
                ith_pattern_component = pattern[i]
                union[i] = ith_union_component.union(ith_pattern_component)
        return union
    
    @staticmethod
    def multiplePatternUnionArea(patterns):
        union = Evaluation.multiplePatternUnion(patterns)
        union_area = 1
        for ith_tuple in union:
            union_area *= len(ith_tuple)
        return union_area
        
    @staticmethod
    def calculateQualityMeasure(configs, path, truncate):
        iteration_pattern = "\.\.\/experiment\/iterations\/(\d*)\/"
        iteration = re.search(iteration_pattern, path)[1]
        planted_patterns = Evaluation.getPlantedPatterns(iteration)
        found_patterns = []
        all_p_intersection_argmax = []
        
        with open(path, "r") as file:
            if truncate is True:
                found_patterns = Evaluation.\
                    truncatePatterns(file, configs["nb_of_truncated_patterns"])
            else:
                found_patterns = Evaluation.\
                    truncatePatterns(file, -1)
                
        if len(found_patterns) == 0: # no patterns found by the algorithm
            return 0 # zero quality
        
        counter = 0
        for planted_pattern in planted_patterns:
            planted_pattern = Evaluation.formatPattern(planted_pattern)

            counter += 1
            print(f"{100*counter/len(planted_patterns): .2f}%...")
            most_similar_found = Evaluation.\
                    findMostSimilarFoundPattern(planted_pattern, found_patterns)
            most_similar_found = Evaluation.formatPattern(most_similar_found)

            p_intersection_argmax = Evaluation.\
                    patternIntersection(most_similar_found, planted_pattern)
            all_p_intersection_argmax.append(p_intersection_argmax)
        
        numerator = Evaluation.multiplePatternUnionArea(all_p_intersection_argmax)
        
        planted_patterns = Evaluation.formatMultiplePatterns(planted_patterns)
        found_patterns = Evaluation.formatMultiplePatterns(found_patterns)
        
        planted_patterns_union = Evaluation.multiplePatternUnion(planted_patterns)
        found_patterns_union = Evaluation.multiplePatternUnion(found_patterns)

        denominator = Evaluation.\
            patternUnion(planted_patterns_union, found_patterns_union)
        denominator = Evaluation.calculatePatternArea(denominator)
        return numerator / denominator
            
    @staticmethod
    def getIterationNumber():
        return [iteration for iteration in os.listdir("../experiment/iterations")]
    
    @staticmethod
    def averageScores(experiments):
        averaged_experiments = dict() # {i_experiment: average_value}       
        
        for experiment, values in experiments.items():
            averaged_experiments[experiment] = mean(values)
            
        return averaged_experiments
    
    @staticmethod
    def evaluateFiles(configs, multidupehack=False, paf=False, truncate=False): 
        Evaluation.__dimension = Evaluation.getDimension()
        if multidupehack is False and paf is False:
            raise ValueError("multidupehack or paf should be True")
            
        file_type = None
        if multidupehack:
            file_type = "multidupehack"
        elif paf:
            file_type = "paf"
            
        base_folder = None
        experiments = dict() # {i_experiment: [value1, value2, ...]
        experiments_pattern = "co\d*"
        for iteration in Evaluation.getIterationNumber():
            base_folder = f"../experiment/iterations/{iteration}"
            
            for experiment in os.listdir(base_folder):
                if re.search(experiments_pattern, experiment) is None: # picked wrong folder
                    continue
                path = f"{base_folder}/{experiment}/{file_type}/{experiment}.{file_type}"
                print(f"Evaluating {path}")
                value = Evaluation.calculateQualityMeasure(configs, path, truncate)
                experiments.setdefault(experiment, [])
                experiments[experiment].append(value)
        
        return Evaluation.averageScores(experiments)
    
    @staticmethod
    def evaluateMultidupehackFiles(configs):
        return Evaluation.evaluateFiles(configs, multidupehack=True)
    
    @staticmethod
    def evaluatePafFiles(configs, truncate=False):
        return Evaluation.evaluateFiles(configs, paf=True, truncate=truncate)