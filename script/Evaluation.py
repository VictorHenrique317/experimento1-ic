# -*- coding: utf-8 -*-
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
            
        intersection = len(intersection[0])*len(intersection[1])*len(intersection[2])
        union = len(union[0])*len(union[1])*len(union[2])
        
        return intersection / union # 0 <= return <= 1
    
    @staticmethod
    def findMostSimilarFoundPattern(planted_pattern, found_patterns): 
        # returns in conventional notation the most similar found pattern to a given planted one
        similarities = []
        for found_pattern in found_patterns:
            similarities.append(Evaluation.jaccardIndex(found_pattern, planted_pattern))
            
        most_similar_index = similarities.index(max(similarities))
        return found_patterns[most_similar_index]
    
    @staticmethod
    def findHigherJaccard(planted_pattern, found_patterns):
        # given a planted pattern, this returns the jaccard index
        # of the most similar pattern found by paf
        most_similar_found = Evaluation.findMostSimilarFoundPattern(planted_pattern, found_patterns)
        return Evaluation.jaccardIndex(most_similar_found, planted_pattern)
    
    @staticmethod
    def getPlantedPatterns():
        # ['pattern','pattern']
        patterns = None
        with open("../experiment/tensor/dataset.tensor", "r") as pattern_file:
            patterns = [line.replace("\n", "").strip() for line in pattern_file]
        return patterns
    
    @staticmethod
    def evaluateFile(paffile_path):
        # WIP
        # prints the jaccard index of the most similar pattern found by
        # paf for each planted pattern
        planted_patterns = Evaluation.getPlantedPatterns()
        with open(paffile_path, "r") as paf_file:
            found_patterns = [pattern for pattern in paf_file]
            for planted_pattern in planted_patterns:
                print(Evaluation.findHigherJaccard(planted_pattern, found_patterns))
    
    @staticmethod
    def evaluateFiles(configs):
        pass