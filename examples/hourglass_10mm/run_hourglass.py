from Refined_Thermal_FEA_Additive import Refined_Thermal_FEA_Additive_class

# import Simulation class
from Refined_Thermal_FEA_Additive import Refined_Thermal_FEA_Additive_class

#Create simulation object
Simulation = Refined_Thermal_FEA_Additive_class("./inputs/hourglass_thermocouple.json")

##Generate scanpath from mtt file (only if libSLM with translators installed)
Simulation.Generate_scanpath_from_mtt()

##Run Simulation
Simulation.run(Generate_meshes= True, from_layer=1, until_layer="end")

###Post Process
#Generate video
Simulation.Generate_Output_Video(from_layer=120, until_layer=130)

#Generate temperature histories
Simulation.Generate_temperature_histories()
