from .layer_class import my_layer

import pyslm
import pyslm.analysis
import pyslm.visualise
import pyslm.hatching

import numpy as np
from skspatial.objects import Line, Sphere

from pyslm import geometry as slm
from libSLM import mtt

def Generate_scanpath(self):
        
        def Calculate_distance(coords0,coords1): #Calculate distance between two points
            return np.sqrt((coords1[0]-coords0[0])**2 + (coords1[1]-coords0[1])**2)
        
        # def Calculate_intersection(coords0,coords1,point_of_interest):
        #     sphere = Sphere(point_of_interest, 0.018)
        #     line = Line([0, 0, 0], [1, 1, 1])

        #     #Calculates the two points of intersection between a scan line and a sphere around a given point of interest



        #Read input_file.json
        scanspeed = self.input_file_dict["Laser_Speed"] #mm/s
        jump_speed = self.input_file_dict["jump_speed"] #mm/s
        dosing_time = self.input_file_dict["dosing_time"] #s
        Power_value = self.input_file_dict["Laser_Power"] #W
        layer_thickness = self.input_file_dict["layer_thickness"] #mm
        inter_layer_time = self.input_file_dict["inter_layer_time"] #s
        offset = self.input_file_dict["offset"]
        substrate_dimensions = self.input_file_dict["substrate_dimensions"] #mm
        AM_build_file = self.input_file_dict["AM_build_file"] 

        #Read mtt file
        mttReader = mtt.Reader()
        mttReader.setFilePath(AM_build_file)
        mttReader.parse()

        layers = mttReader.layers

        n_layer=1
        self.layer_objects_array=[]

        for layer in layers: #iterate through layers

            this_layer = my_layer(layer_thickness * n_layer, layer_thickness)

            Geoms = layer.getGeometry()
            number_of_hatch_coords = len(Geoms[0].coords)

            

            #Extract layer path:
            layer_path = np.empty((0,2), int)
            time = []
            Power_column = []

            c = 0
            for geom in Geoms: #iterate through geoms (hatches and contours) of each layer
                layer_path = np.append(layer_path,geom.coords, axis=0)

                if geom.type.value == 1: #type of geom, if it is a contour or a hatch
                    type_of_geom= "Contour"
                elif geom.type.value == 2:
                    type_of_geom= "Hatch"

                for n in range(0,len(geom.coords)): #iterate through coordinates of each geom
                    if c==0: #Recoating event
                        time.append(dosing_time)
                        p = 0

                    else:
                        if type_of_geom == "Hatch":
                            if n % 2 != 0:
                                p = 0
                                speed = jump_speed
                            else:
                                p = Power_value
                                speed = scanspeed

                        elif type_of_geom == "Contour":
                            if n == 0:
                                p = Power_value
                                speed = scanspeed
                            elif n == len(geom.coords)-1:
                                p = 0
                                speed = jump_speed
                            else:
                                p = Power_value
                                speed = scanspeed

                        time.append( time[c-1] + (Calculate_distance(layer_path[c-1],layer_path[c])/speed) )

                        #Calculate time of intersection with sphere of interest:

                    
                    c += 1

                    #Save times of middle bead:
                    if n == number_of_hatch_coords/2 + 1:
                        this_layer.scan_time_before_middle_bead = time[-3] - dosing_time
                        this_layer.scan_time_after_middle_bead = time[-1] - dosing_time

                    
                    Power_column.append(p)

            #Relocate layer_path to origin (sample in mtt is not at origin):
            min_coords = layer_path[np.argmin(np.sum(layer_path, axis=1))]

            layer_path = layer_path - min_coords + np.array([offset,offset])

            #Create event series array
            heat_event = np.hstack((np.array(time).reshape(-1, 1), layer_path, np.ones((len(layer_path),1)) * layer_thickness * n_layer, np.array(Power_column).reshape(-1, 1)))
            np.savetxt("heat_event_trial.csv", heat_event, delimiter=",")
            
                
            



            # Calculate time of scanning:
            this_layer.scan_time = time[-1] - dosing_time

            time = np.array(time)

            # #Calculate time:
            # n=0
            # time = []
            # for _ in layer_path:
            #     if n == 0:
            #         time.append(dosing_time)
            #     else:
            #         if n % 2 != 0: #during hatching, odd n means laser is on and the speed is equal to the scan speed
            #             speed = scanspeed
            #         else:
            #             speed = jump_speed

            #         previous_length = length_geoms_array[0] #during contouring, jump speed is used only at the end of the contour
            #         for i in range(1,len(length_geoms_array)): 
            #             if previous_length + 1 < n+1 <= previous_length + length_geoms_array[i]:
            #                 speed = scanspeed
            #             elif previous_length == n:
            #                 speed = jump_speed
            #             previous_length+=length_geoms_array[i]

            #         time.append( time[n-1] + (Calculate_distance(layer_path[n-1],layer_path[n])/speed) ) 
            

            #     n += 1

            # # Calculate time of scanning
            # this_layer.scan_time = time[-1] - dosing_time

            # time = np.array(time)

            # #Add z position
            # z =np.ones((len(layer_path),1)) * layer_thickness * n_layer
            # Power_value_column =np.ones((len(layer_path),1)) * Power_value

            #Add Power_value column

                #During hatching, power is zero every other coordinate
            # Power_value_column[1:len(Power_value_column):2] = 0 
            
            #     #During contour, it is only zero at the end of the contour
            # count = 0
            # previous_length = 0
            # for length in length_geoms_array:
            #     if count != 0:
            #         Power_value_column[previous_length:previous_length+length-1] = Power_value 
            #         Power_value_column[previous_length+length-1] = 0
            #     previous_length += length
            #     count += 1
            

            # layer_path = np.append(layer_path, z, axis=1)
            # layer_path = np.append(layer_path, Power_value_column, axis=1)

            # heat_event = np.append(time.reshape(-1,1),layer_path, axis=1)


            #Add cooling time
            cooling_event = np.array([time[-1]+inter_layer_time-dosing_time,0,0,0,0])
            heat_event = np.vstack([heat_event, cooling_event])


            #Save heat_event_series
            np.savetxt(self.input_file_dict["output_path"] + "/Heat_Series_ly%i.csv" %(n_layer), heat_event, delimiter=",")
            
            
            #Need to create roller_event_series
            roller_event = np.array([0,0,0,layer_thickness*n_layer,1])
            roller_event = np.vstack((roller_event, np.array([dosing_time,0,substrate_dimensions[1],layer_thickness*n_layer,1])))

            np.savetxt(self.input_file_dict["output_path"] + "/Roller_Series_ly%i.csv" %(n_layer), roller_event, delimiter=",")

            
            #Add layer to layer_objects_arrays
            self.layer_objects_array.append(this_layer)

            n_layer+=1
