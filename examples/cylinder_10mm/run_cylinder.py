import sys
# adding folder to system path to use from import
sys.path.insert(0, '../../')
# import Simulation class
from Refined_Thermal_FEA_Additive import Abaqus_PBF_micro_thermal_class

#Create simulation object, which reads the input json file
Simulation = Abaqus_PBF_micro_thermal_class("./inputs/Cylinder_d10_thermocouple.json")

##Generate scanpath from mtt file (only if libSLM with translators installed)
Simulation.Generate_scanpath_from_mtt()

##Run Simulation
Simulation.run(Generate_meshes= True, from_layer=1, until_layer="end")

###Post Process

#Generate video
Simulation.Generate_Output_Video(from_layer=45, until_layer=55)

#Generate temperature histories
Simulation.Generate_temperature_histories()
