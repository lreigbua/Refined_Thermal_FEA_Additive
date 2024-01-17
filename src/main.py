from Abaqus_PBF_micro_thermal import Abaqus_PBF_micro_thermal_class

#Create simulation object
Simulation = Abaqus_PBF_micro_thermal_class("../input/10mm_Cube_change_parameters_for_rescanning.json")

##Generate scanpath from mtt file (only if pySLM with libSLM and translators installed)
# Simulation.Generate_scanpath_from_mtt()

###Run Simulation
Simulation.run(Generate_meshes= False, from_layer = 1, until_layer = 2)

###Post Process

##Generate video
Simulation.Generate_Output_Video()
#Generate temperature histories
Simulation.Generate_temperature_histories()
