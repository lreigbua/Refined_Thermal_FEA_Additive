from Abaqus_PBF_micro_thermal import Abaqus_PBF_micro_thermal_class

#Create simulation object
Simulation = Abaqus_PBF_micro_thermal_class("../input/Rectangle_build_1_meander_default.json")

##Generate scanpath from mtt file (only if pySLM with libSLM and translators installed)
# Simulation.Generate_scanpath_from_mtt()

###Run Simulation
Simulation.run(Generate_meshes= False, from_layer = 96)

###Post Process

##Generate video
Simulation.Generate_Output_Video()
#Generate temperature histories
Simulation.Generate_temperature_histories()
