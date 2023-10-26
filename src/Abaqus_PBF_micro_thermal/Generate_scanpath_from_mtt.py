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
        
        def inSphere(point, centre, radius):
            #Checks if point is inside a sphere with centre and radius

            # Calculate the difference between the reference and measuring point
            diff = np.subtract(point, centre)

            # Calculate square length of vector (distance between ref and point)^2
            dist = np.sum(np.power(diff, 2))

            # If dist is less than radius^2, return True, else return False
            return dist < radius ** 2
        
        def Calculate_sphere_intersection(coords0,coords1,point_of_interest):
            #Calculates the two points of intersection between a scan line and a sphere around a given point of interest
            sphere = Sphere(point_of_interest, 0.3)
            line = Line.from_points(coords0, coords1)

            try:
                point_a, point_b = sphere.intersect_line(line)
                return point_a, point_b
            except:
                return False


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

        #initialize some variables
        n_layer=1
        self.layer_objects_array=[]


        start_time_of_intersection_inside_sphere = False

        for layer in layers: #iterate through layers

            this_layer = my_layer(layer_thickness * n_layer, layer_thickness)

            this_layer.intersection_times = []

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
                            
                    c += 1 #counter for coordinates in this layer

                    #Save times of middle bead:
                    if n == number_of_hatch_coords/2 + 1:
                        this_layer.scan_time_before_middle_bead = time[-3] - dosing_time
                        this_layer.scan_time_after_middle_bead = time[-1] - dosing_time
                    
                    Power_column.append(p)

            #Relocate layer_path to origin (sample in mtt is not at origin):
            min_coords = layer_path[np.argmin(np.sum(layer_path, axis=1))]
            layer_path = layer_path - min_coords + np.array([offset,offset])


            point_of_interest = [0.6, 4.2, 2.34] #mm
            # Iterate again through layer_path coordinates to calculate intersections, looping again is needed because of relocation
            for c in range(1,len(layer_path)): #we start at 1 to skip dosing time coordinates
                #Calculate time of intersection with sphere of interest:
                Coord_ini = np.append(layer_path[c-1], this_layer.height).transpose()
                Coord_final = np.append(layer_path[c], this_layer.height).transpose()

                intersection = Calculate_sphere_intersection(Coord_ini,Coord_final, point_of_interest)
                
                if n_layer == 39 and intersection != False:
                    print(Coord_ini, Coord_final)
                    print(intersection)
                    
                if intersection is not False and this_layer.height >= point_of_interest[2]-self.eps: #If there is an intersection in the top half of the sphere
                    point_a, point_b = intersection
                    #time of entering sphere:
                    start_time_of_intersection = time[c-1] + (Calculate_distance(layer_path[c-1],point_a)/speed)
                    end_time_of_intersection = time[c-1] + (Calculate_distance(layer_path[c-1],point_b)/speed)

                    # #The next two ifs are used to address if the start of a layerpath is inside the sphere of interest
                    # if start_time_of_intersection_inside_sphere == False:
                    #     if inSphere(Coord_ini, point_of_interest, 0.018): #if beggining of hatch is inside sphere
                    #         start_time_of_intersection = time[c-1] + (Calculate_distance(layer_path[c-1],point_a)/speed)
                    #         start_time_of_intersection_inside_sphere = True

                    # if inSphere(Coord_final, point_of_interest, 0.018) and start_time_of_intersection_inside_sphere: #if end of hatch is inside sphere                            
                    #     continue
                    # else:
                    this_layer.intersection_times.append((start_time_of_intersection, end_time_of_intersection))   


            #Create event series array
            heat_event = np.hstack((np.array(time).reshape(-1, 1), layer_path, np.ones((len(layer_path),1)) * this_layer.height, np.array(Power_column).reshape(-1, 1)))
            np.savetxt("heat_event_trial.csv", heat_event, delimiter=",")

            # Calculate time of scanning:
            this_layer.scan_time = time[-1] - dosing_time

            time = np.array(time)

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
