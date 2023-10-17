#This file is used to create the main class of this module and import methods from different files in this module

import os
from .utils import *

from .layer_class import my_layer

class Abaqus_PBF_micro_thermal_class:
#Class for running a single Abaqus PBF simulation

    def __init__(self,input_file_path): #Path of input file
        self.input_file_path = os.getcwd() + "/" + input_file_path 
        self.module_path =  os.path.dirname(os.path.realpath(__file__)) #path to directory of this script
        self.input_file_dict = utils.read_json_file(self.input_file_path) #Read json input file and save as dict
        self.eps = 1e-9 #very small number for rounding errors

    #import methods from other files:

    #methods for processing
    from .run import run
    from .Generate_scanpath_from_mtt import Generate_scanpath
    from .Generate_Step_files_for_layer import Generate_Step_files_for_layer
    
    #methods for post-processing
    from .Generate_Output_Video import Generate_Output_Video

