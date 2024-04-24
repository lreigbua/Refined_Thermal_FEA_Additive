#This file is used to create the main class of this module and import methods from different files in this module

from .utils import *
from pathlib import Path #library to handle paths

class Abaqus_PBF_micro_thermal_class:
#Class for running a single Abaqus thermal PBF simulation

    def __init__(self,input_file_path): #Path of input file

        #Set Correct Paths:
        self.input_file_path = Path(input_file_path) #path to input file 
        self.module_path =  Path(__file__).parent #path to directory of this script, which is the module path
        self.input_file_dict = utils.read_json_file(self.input_file_path) #Read json input file and save as dictionary
        self.user_path = Path.cwd() #path to user directory (where the user is running script from)
        self.input_file_parent_folder = self.input_file_path.parent #parent folder of input file

        self.Output_Path = self.input_file_parent_folder / self.input_file_dict["output_path"] #output folder path, specified by user
        self.Output_Path = self.Output_Path.resolve() #convert to absolute path
        self.component_geometry_path = self.input_file_parent_folder / self.input_file_dict["component_geometry_path"] #component geometry path, specified by user
        self.component_geometry_path = self.component_geometry_path.resolve() #convert to absolute path
        self.AM_build_file = self.input_file_parent_folder / self.input_file_dict["AM_build_file"] #AM build file path, specified by user if wants to translate it
        self.AM_build_file = self.AM_build_file.resolve() #convert to absolute path
        self.scanpath_folder = self.input_file_parent_folder / self.input_file_dict["scanpath_folder"] #scanpath folder path, specified by user if use own scanpath
        self.scanpath_folder = self.scanpath_folder.resolve() #convert to absolute path

        self.eps = 1e-9 #very small number for rounding errors

#import methods from other files:

    #methods for pre-processing
    from .Generate_scanpath_from_mtt import Generate_scanpath_from_mtt

    #methods for processing
    from .run import run
    from .Generate_Step_files_for_layer import Generate_Step_files_for_layer #private method
    
    #methods for post-processing
    from .Generate_Output_Video import Generate_Output_Video
    from .Generate_temperature_histories import Generate_temperature_histories

