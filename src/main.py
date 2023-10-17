from Abaqus_PBF_micro_thermal import Abaqus_PBF_micro_thermal_class

#Create simulation object
Simulation = Abaqus_PBF_micro_thermal_class("../input/cube_with_holes.json")

#Run Simulation
Simulation.run()

#Post Process
# Simulation.Generate_Output_Video()