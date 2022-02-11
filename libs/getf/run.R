args = commandArgs()
translated_tensor_path = args[6]
noise_endurance = as.double(args[7])
max_pattern_number = as.integer(args[8])
iteration = as.integer(args[9])
experiment_folder_name = args[10]
numpy_name = args[11]

source("../libs/GETF/GETF_CP.R")
library("reticulate")

np <- import("numpy")
tensor <- np$load(translated_tensor_path)
Factors <- NULL

try_counter = 0
while(TRUE){
    try_counter <- try_counter + 1
    if(try_counter > 5){ # out of tentatives
        break
    }
    Factors<-GETF_CP(TENS = tensor, Thres = noise_endurance, B_num = max_pattern_number, COVER = 0.9, Exhausive = F)
    if(is.na(Factors[[1]][1])){ # nothing found
        print("No pattern found by GETF trying again")
    }else{
        break
    }
}

Patterns <- Get_Patterns(tensor, Factors)

for(i in 1:length(Patterns)){
    Pattern <- Patterns[[i]]
    pattern_file_path = paste("../experiment/iterations/", iteration, "/", experiment_folder_name, "/getf/p", i, "-",numpy_name)
    pattern_file_path = gsub(" ", "", pattern_file_path)
    np$save(pattern_file_path, Pattern)
}



