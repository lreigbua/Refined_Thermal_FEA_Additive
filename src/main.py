from Abaqus_PBF_micro_thermal import Abaqus_PBF_micro_thermal_class

#Create simulation object
Simulation = Abaqus_PBF_micro_thermal_class("../input/Cylinder_Corrected_5s.json")

##Generate scanpath from mtt file (only if libSLM with translators installed)
Simulation.Generate_scanpath_from_mtt()

###Run Simulation
Simulation.run(Generate_meshes= False   , from_layer=1, until_layer="end")

###Post Process

# ##Generate video
# Simulation.Generate_Output_Video(from_layer=45, until_layer=55)

# #Generate temperature histories
Simulation.Generate_temperature_histories()
