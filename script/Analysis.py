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
    def plotGraph(x, y, u, color, xlabel, ylabel,save):
        fig, ax = plt.subplots()
        plt.scatter(x,y,color=color)
        plt.plot(x,y, color=color)
        
        plt.grid()
        plt.title(f"{ylabel} for u={u}")
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        
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
    def getXYFromExperiments(experiments):
        data = dict()
        for experiment, average in experiments.items():
            key = re.findall("co(\d*)", experiment)[0]
            key = float(key)
            data[key] = average
        data = collections.OrderedDict(sorted(data.items()))
        return (data.keys(), data.values())
    
    @staticmethod
    def plotExperimentsByUValue(configs, experiments, attribute,color, save):
        u_values = configs["u_values"]
        correct_obs = configs["correct_obs"]
        
        for u in u_values:
            xlabel = f"nb. of correct observations"
            ylabel = f"{attribute}"
            
            filtered_experiments = Analysis.\
                filterExperimentsByEpsilon(experiments, u)
                
            x,y = Analysis.getXYFromExperiments(filtered_experiments)
            Analysis.plotGraph(x,y,u,color,xlabel,ylabel,save)
        
    @staticmethod
    def plotMultidupehackAttributeGraph(configs, attribute, color="blue", save=False):
        experiment_averages = Analysis\
            .averageExperiments(attribute, multidupehack=True)
        
        Analysis.plotExperimentsByUValue(configs, experiment_averages, attribute, color, save)
        
    @staticmethod
    def plotScoreGraph(configs, color, save):
        experiments = Evaluation.evaluateFiles(configs) # {i_experiment: score}
        Analysis.plotExperimentsByUValue(configs, experiments, "Score", color, save)
       
    @staticmethod
    def plotPafAttributeGraph(configs, attribute, color="blue", save=False):
        experiment_averages = Analysis\
            .averageExperiments(attribute, paf=True)
        
        Analysis.plotExperimentsByUValue(configs, experiment_averages, attribute, color, save)

    @staticmethod
    def plotMultipleGraphs(configs, color="blue", save=False):
        multidupehack_plot_attributes = configs["multidupehack_plot_attributes"]
        paf_plot_attributes = configs["paf_plot_attributes"]
        u_values = configs["u_values"]
        counter = 0
        max_counter = len(multidupehack_plot_attributes) + len(paf_plot_attributes)
        max_counter *= len(u_values)
        for multidupehack_attribute in multidupehack_plot_attributes:
            counter += len(u_values)
            print("="*120)
            print("Plotting graph...")
            
            Analysis.plotMultidupehackAttributeGraph(configs, \
                                                      multidupehack_attribute,\
                                                          color=color, save=save)
            print(f"{counter} of {max_counter} done")
        
        for paf_attribute in paf_plot_attributes:
            counter += len(u_values)
            print("="*120)
            print("Plotting graph...")
            
            Analysis.plotPafAttributeGraph(configs, paf_attribute, \
                                           color=color, save=save)
            print(f"{counter} of {max_counter} done")
        
        Analysis.plotScoreGraph(configs, color, save)
        