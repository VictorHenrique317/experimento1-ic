# -*- coding: utf-8 -*-
import os
from LogModel import LogModel
from Utils import Utils
from Multidupehack import Multidupehack
from Evaluation import Evaluation
from statistics import mean
import re
import matplotlib.pyplot as plt
import collections

class Analysis:
    base_folder = "../experiment/iterations"
    def __init__(self):
        pass

    @staticmethod                
    def calculateAttributeAverage(logs, attribute):
        values = []
        for log in logs:
            value = log.attributes[attribute]
            value = float(value.replace("s",""))
            values.append(value)
        return mean(values)
    
    @staticmethod
    def getLogsFor(paf=False, multidupehack=False):
        log_type = None
        if paf is True:
            log_type = "paf"
        elif multidupehack is True:
            log_type = "multidupehack"
        else:
            raise ValueError("Especify paf or multidupehack log type") 
        
        data = dict() # {i_experiment: [log1, log2, ..., logn]}
        for iteration in os.listdir(Analysis.base_folder):
            path = f"{Analysis.base_folder}/{iteration}"
            for experiment in os.listdir(path):
                log_path = f"{path}/{experiment}/{log_type}/log.txt"
                log = LogModel(log_path)
                
                data.setdefault(experiment, [])
                log_list = data[experiment]
                log_list.append(log)
                data[experiment] = log_list
        return data
        
    @staticmethod
    def averageExperiments(attribute, paf=False, multidupehack=False):
        # {i_experiment: [log1, log2, ..., logn]}
        experiments = Analysis.getLogsFor(paf=paf, multidupehack=multidupehack)
        experiment_averages = dict()
        
        for experiment in experiments:
            logs = experiments[experiment]
            experiment_averages[experiment] = Analysis\
                .calculateAttributeAverage(logs, attribute)
        return experiment_averages
    
    @staticmethod
    def filterExperimentsByEpsilon(experiments, u):
        epsilon = Multidupehack.calculateEpsilon(u)
        filtered_experiments = dict()
        
        for experiment, average in experiments.items():
            if re.search(f"e{epsilon}", experiment) != None: # found
                filtered_experiments[experiment] = average
                
        return filtered_experiments
    
    @staticmethod
    def defYLimits(ylabel):
        if ylabel == "Nb of patterns":
            return[10**0, 10**4]
        elif ylabel == "Run time":
            return [10**-2, 10**2]
        elif ylabel == "Quality":
            return [10**-1, 10**0.05]
        else:
            raise ValueError(f"Y limits not defined for {ylabel}")
    
    @staticmethod
    def plotGraph(x, y, u, color, xlabel, ylabel, algorithm):
        plt.scatter(x,y,color=color)
        plt.plot(x,y, color=color, label=algorithm)
        
        plt.legend()
        plt.grid()
        plt.title(f"{ylabel} for u={u}")
        
        plt.xlabel(xlabel)
        plt.xlim(max(x), min(x))
        
        plt.ylabel(ylabel)
        axis = plt.gca()
        y_limits= Analysis.defYLimits(ylabel)
        axis.set_ylim([y_limits[0],y_limits[1]])
        plt.yscale("log")
        
    @staticmethod
    def getXYFromExperiments(experiments):
        data = dict()
        for experiment, average in experiments.items():
            key = re.findall("co(\d*)", experiment)[0]
            key = float(key)
            data[key] = average
        data = collections.OrderedDict(sorted(data.items()))
        return (data.keys(), data.values())
        
    @staticmethod
    def plotExperimentsByUValue(configs, multidupehack_experiments, \
                                paf_experiments, ylabel, save):
        u_values = configs["u_values"]
        correct_obs = configs["correct_obs"]
        
        
        for u in u_values:
            fig, ax = plt.subplots()
            xlabel = f"nb. of correct observations"
            
            filtered_multidupehack_experiments = Analysis.\
                filterExperimentsByEpsilon(multidupehack_experiments, u)
                
            filtered_paf_experiments = Analysis.\
                filterExperimentsByEpsilon(paf_experiments, u)
                
            x1,y1 = Analysis.getXYFromExperiments(filtered_multidupehack_experiments)
            x2,y2 = Analysis.getXYFromExperiments(filtered_paf_experiments)
            
            Analysis.plotGraph(x1,y1,u,"blue",xlabel,ylabel, "multidupehack")
            Analysis.plotGraph(x2,y2,u,"red",xlabel,ylabel, "paf")
            
            if ylabel == "Run time": 
                # time graph, show time of multidupehack + paf
                x3 = x1
                y3 = Utils.sumListElements(list(y1), list(y2))
                Analysis.plotGraph(x3, y3, u,"green",xlabel,ylabel, "multidupehack + paf")
                            
            if save is True:
                graph_folder ="../experiment/analysis/graphs"
                Utils.createFolder(graph_folder)
                filename = ylabel.lower().replace(" ","-")
                filename = f"{filename}-for-u-{u}.png"
                plt.savefig(f"{graph_folder}/{filename}")
                plt.close(fig)
            else:
                plt.show()
    
    @staticmethod
    def plotOverlappingGraphs(configs, multidupehack_attribute, paf_attribute,\
                              ylabel, save=False):
        multidupehack_experiment_averages = Analysis.\
            averageExperiments(multidupehack_attribute, multidupehack=True)
            
        paf_experiment_averages = Analysis.\
            averageExperiments(paf_attribute, paf=True)
            
        Analysis.plotExperimentsByUValue(configs, \
                multidupehack_experiment_averages, paf_experiment_averages, \
                ylabel, save)
    
    @staticmethod
    def plotScoreGraph(configs, save=False):
        multidupehack_experiments = Evaluation.evaluateMultidupehackFiles(configs) # {i_experiment: score}
        paf_experiments = Evaluation.evaluatePafFiles(configs) # {i_experiment: score}
        Analysis.plotExperimentsByUValue(configs, \
                multidupehack_experiments, paf_experiments, \
                "Quality", save)

    @staticmethod
    def plotMultipleGraphs(configs, save=False):
        plot_attributes = configs["plot_attributes"] 
        # {"label": ["multidupehack_attribute","paf_attribute"]}
        
        for label, attributes in plot_attributes.items():
            # print("===============")
            # print(label)
            # print(attributes)
            # print("Plotting graph...")
            multidupehack_attribute = attributes[0]
            paf_attribute = attributes[1]
            Analysis.plotOverlappingGraphs(configs, multidupehack_attribute, \
                                           paf_attribute, label ,save=save)
        
        Analysis.plotScoreGraph(configs, save=save)
        