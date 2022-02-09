# -*- coding: utf-8 -*-
import os
from LogModel import LogModel
from Utils import Utils
from Multidupehack import Multidupehack
from Evaluation import Evaluation
from statistics import mean
import re
import matplotlib.pyplot as plt
import matplotlib.ticker
import collections

class Analysis:
    base_folder = "../experiment/iterations"
    def __init__(self):
        pass

    @staticmethod                
    def calculateAttributeAverage(logs, attribute):
        values = []
        for log in logs:
            value = "0s"
            try:
                value = log.attributes[attribute]
            except KeyError:
                print(f"No attribute {attribute}")
                
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
            
        experiments_pattern = "co\d*"
        data = dict() # {i_experiment: [log1, log2, ..., logn]}
        for iteration in os.listdir(Analysis.base_folder):
            path = f"{Analysis.base_folder}/{iteration}"
            for experiment in os.listdir(path):
                if re.search(experiments_pattern, experiment) is None: # picked wrong folder
                    continue
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
    def customYLimits(ylabel):
        if ylabel == "Nb of patterns":
            return[10**0, 10**5]
        elif ylabel == "Run time":
            return [10**-2, 10**3]
        elif ylabel == "Quality":
            return [0, 1.1]
        elif ylabel == "Memory (kb)":
            return [10**3, 10**6]
        else:
            raise ValueError(f"Y limits not defined for {ylabel}")
            
    @staticmethod
    def defYLimits(u_values, multidupehack_experiments, paf_experiments):
        max_values = []
        min_values = []
        for u in u_values:
            max_multidupehack_key = max(multidupehack_experiments, \
                                        key=multidupehack_experiments.get)
            min_multidupehack_key = min(multidupehack_experiments, \
                                        key=multidupehack_experiments.get)
            max_multidupehack_value = multidupehack_experiments[max_multidupehack_key]
            
            min_multidupehack_value = multidupehack_experiments[min_multidupehack_key]
            
            
            max_paf_key = max(paf_experiments, \
                                        key=paf_experiments.get)
            min_paf_key = min(paf_experiments, \
                                        key=paf_experiments.get)
            max_paf_value = paf_experiments[max_paf_key]
           
            min_paf_value = paf_experiments[min_paf_key]
            
            max_values.append(max([max_multidupehack_value, max_paf_value]))
            min_values.append(min([min_multidupehack_value, min_paf_value]))
            
        max_value = int(max(max_values))
        min_value = int(min(min_values))
        
        upper_limit = len(str(max_value))
        upper_limit = 10**upper_limit
        
        lower_limit = len(str(min_value)) - 1
        lower_limit = 10**lower_limit
        
        return(lower_limit, upper_limit)
    
    @staticmethod
    def plotGraph(x, y, u, color, xlabel, ylabel, algorithm, y_limits):
        plt.scatter(x,y,color=color)
        plt.plot(x,y, color=color, label=algorithm)
        plt.legend()
        plt.grid()
        plt.title(f"{ylabel} for u={u}")
        
        plt.xlabel(xlabel)
        plt.xlim(max(x), min(x))
        
        plt.ylabel(ylabel)
        axis = plt.gca()
        
        if y_limits is None: # them use custom ylimits
            y_limits= Analysis.customYLimits(ylabel)

        axis.set_ylim([y_limits[0],y_limits[1]])
        if ylabel.lower() != "quality":
            plt.yscale("log")
        plt.xscale("log", base=2)
        axis.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
        axis.get_xaxis().set_minor_formatter(matplotlib.ticker.NullFormatter())
        
        axis.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
        axis.get_yaxis().set_minor_formatter(matplotlib.ticker.NullFormatter())
    @staticmethod
    def getXYFromExperiments(experiments):
        data = dict()
        for experiment, average in experiments.items():
            key = re.findall("co(\d*)", experiment)[0]
            key = float(key)
            data[key] = average
        data = collections.OrderedDict(sorted(data.items()))
        xy = (data.keys(), data.values())
        return xy
        
    @staticmethod
    def plotExperimentsByUValue(configs, multidupehack_experiments, \
                                paf_experiments, ylabel, save, custom_ylimits):
        u_values = configs["u_values"]
        correct_obs = configs["correct_obs"]
        
        y_limits = None
        if custom_ylimits is False: # automatic generated ylimits
            y_limits = Analysis.defYLimits(u_values, multidupehack_experiments, paf_experiments)
        
        for u in u_values:
            fig, ax = plt.subplots()
            xlabel = f"nb. of correct observations"
            
            filtered_multidupehack_experiments = Analysis.\
                filterExperimentsByEpsilon(multidupehack_experiments, u)
                
            filtered_paf_experiments = Analysis.\
                filterExperimentsByEpsilon(paf_experiments, u)
                
            x1,y1 = Analysis.getXYFromExperiments(filtered_multidupehack_experiments)
            x2,y2 = Analysis.getXYFromExperiments(filtered_paf_experiments)
            
            Analysis.plotGraph(x1,y1,u,"blue",xlabel,ylabel, "multidupehack", y_limits)
            Analysis.plotGraph(x2,y2,u,"red",xlabel,ylabel, "paf", y_limits)
            
            if ylabel == "Run time": 
                # time graph, show time of multidupehack + paf
                x3 = x1
                y3 = Utils.sumListElements(list(y1), list(y2))
                Analysis.plotGraph(x3, y3, u,"green",xlabel,ylabel, "multidupehack + paf", y_limits)
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
                              ylabel, save=False, custom_ylimits=True):
        multidupehack_experiment_averages = Analysis.\
            averageExperiments(multidupehack_attribute, multidupehack=True)
            
        paf_experiment_averages = Analysis.\
            averageExperiments(paf_attribute, paf=True)
            
        Analysis.plotExperimentsByUValue(configs, \
                multidupehack_experiment_averages, paf_experiment_averages, \
                ylabel, save, custom_ylimits)
    
    @staticmethod
    def plotScoreGraph(configs, save=False, custom_ylimits=True):
        multidupehack_experiments = Evaluation.evaluateMultidupehackFiles(configs) # {i_experiment: score}
        paf_experiments = Evaluation.evaluatePafFiles(configs) # {i_experiment: score}
        Analysis.plotExperimentsByUValue(configs, \
                multidupehack_experiments, paf_experiments, \
                "Quality", save, custom_ylimits)

    @staticmethod
    def plotMultipleGraphs(configs, save=False, custom_ylimits=True):
        plot_attributes = configs["plot_attributes"] 
        # {"label": ["multidupehack_attribute","paf_attribute"]}
        
        for label, attributes in plot_attributes.items():
            multidupehack_attribute = attributes[0]
            paf_attribute = attributes[1]
            Analysis.plotOverlappingGraphs(configs, multidupehack_attribute, \
                                           paf_attribute, label ,save=save, \
                                           custom_ylimits=custom_ylimits)
        
        Analysis.plotScoreGraph(configs, save=save, custom_ylimits=custom_ylimits)
        