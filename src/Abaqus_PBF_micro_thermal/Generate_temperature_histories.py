import os
from pathlib import Path
import shutil

import matplotlib.pyplot as plt
import numpy as np

def Generate_temperature_histories(self, temp_history_output_path = ""):

    os.chdir(self.Output_Path)

    os.system(f'abaqus cae noGUI={ str(self.module_path/"read_history_output.py") }')


    points_of_interest = np.array(self.input_file_dict["points_of_interest"])

    
    for point in points_of_interest:
        plt.figure()
        plt.title(f"Temperature history at point {point}")
        plt.xlabel("Time [s]")
        plt.ylabel("Temperature [K]")
        plt.ylim(26.0, 1650.0) 
        plt.grid()

        path = Path(f"Temperature_Element_at_heigt_{point[2]}.csv")

        if path.exists():
            data = np.loadtxt(path, delimiter=",")
            if len(data) > 1:
                plt.plot( data[:,0],data[:,1],label = "element 1" )
                plt.legend()
                plt.savefig(self.Output_Path / f"Temperature_history_point_{point[0]}_{point[1]}_{point[2]}.png")
                plt.close()

    plt.figure()
    for point in points_of_interest:

        plt.title(f"Temperature histories all points")
        plt.xlabel("Time [s]")
        plt.ylabel("Temperature [K]") 
        plt.ylim(26.0, 1650.0) 
        
        plt.grid()

        path = Path(f"Temperature_Element_at_heigt_{point[2]}.csv")

        if path.exists():
            if len(data) > 1:
                data = np.loadtxt(path, delimiter=",")
                plt.plot( data[:,0],data[:,1],label = f"Temperature_history_point_{point[0]}_{point[1]}_{point[2]}.png" )

                plt.legend()
                plt.savefig(self.Output_Path / f"Temperature_histories_all_points.png")
                plt.close()

    #Make copy of csv files into output folder specified by the user
    if temp_history_output_path != "":
        for point in points_of_interest:
            path = self.Output_Path / f"Temperature_Element_at_heigt_{point[2]}.csv"
            shutil.copy(path, temp_history_output_path / f"Temperature_Element_at_heigt_{point[2]}.csv")

    
    if self.input_file_dict["add_thermocouple"] == "yes":
        plt.figure()
        plt.title(f"Thermocouple temperature history")
        plt.xlabel("layer [-]")
        plt.ylabel("Temperature [$^\circ$C]") 
        plt.ylim(-10.0, 100.0) 
        plt.yticks(np.arange(0, 90.1, 10))
        plt.yticks(np.arange(0, 90.1, 5), minor=True)
        plt.xlim(-30.0, 280.0) 
        plt.xticks(np.arange(0, 250.1, 50))
        plt.xticks(np.arange(0, 250.1, 25), minor=True)
        plt.grid(True)
        # plt.axes().set_aspect('equal')
        # plt.gca().set_aspect('equal')

        path = Path(f"Temperature_Thermocouple.csv")
    

        if path.exists():
            data = np.loadtxt(path, delimiter=",")

            #substract ambient temperature:
            data[:,1]=data[:,1]-self.input_file_dict["Chamber_Temperature"]

            #transform time to layer
            printing_time = data[-1,0] - (self.input_file_dict["final_cooling_time"] - self.input_file_dict["inter_layer_time"]) 

            layer =  data[:,0] * 250 / printing_time

            plt.plot(layer,data[:,1])

            # plt.legend()
            plt.savefig(self.Output_Path / f"Thermocouple_temperature_history.png")
            plt.close()

        #Make copy of csv files into output folder specified by the user
        # if temp_history_output_path != "":
        #     path = self.Output_Path / f"Thermocouple.csv"
        #     shutil.copy(path, temp_history_output_path / f"Thermocouple.csv")
            
        os.chdir(self.user_path)