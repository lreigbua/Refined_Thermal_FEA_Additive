from Abaqus_PBF_micro_thermal import Abaqus_PBF_micro_thermal_class

#Create simulation object
Simulation = Abaqus_PBF_micro_thermal_class("../input/1mm_cube.json")

#Generate scanpath from mtt file (only if pySLM with libSLM and translators installed)
Simulation.Generate_scanpath_from_mtt()

#Run Simulation
Simulation.run()

#Post Process
# Simulation.Generate_Output_Video()