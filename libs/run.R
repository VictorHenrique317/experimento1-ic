args = commandArgs()
translated_tensor_path = args[6]
noise_endurance = as.double(args[7])
max_pattern_number = as.integer(args[8])
iteration = as.integer(args[9])
experiment_folder_name = args[10]
getf_name = args[11]

source("../libs/GETF/GETF_CP.R")
library("reticulate")

np <- import("numpy")
tensor <- np$load(translated_tensor_path)

# TENS<-Tensor_Simulate(Dims = c(6,6,6),pattern = 5,density = 1,Noise = 0)
Patterns<-GETF_CP(TENS = tensor, Thres = noise_endurance, B_num = max_pattern_number, COVER = 0.9, Exhausive = F)

pattern_file_path = paste("../experiment/iterations/", iteration, "/", experiment_folder_name, "/getf/", getf_name)
pattern_file_path = gsub(" ", "", pattern_file_path)
np$save(pattern_file_path, Patterns)

