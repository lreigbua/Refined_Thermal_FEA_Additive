from Abaqus_PBF_micro_thermal import Abaqus_PBF_micro_thermal_class

#Create simulation object
Simulation = Abaqus_PBF_micro_thermal_class("../input/10mm_cube_meander.json")

#Run Simulation
Simulation.run()

#Post Process
# Simulation.Generate_Output_Video()