from .layer_class import my_layer

def Generate_scanpath(self):
        
        import pyslm
        import pyslm.analysis
        import pyslm.visualise
        import pyslm.hatching

        import numpy as np
        from pyslm import geometry as slm
        from libSLM import mtt

        def Calculate_distance(coords0,coords1): #Calculate distance between two points
            return np.sqrt((coords1[0]-coords0[0])**2 + (coords1[1]-coords0[1])**2)

        #Read input_file.json
        scanspeed = self.input_file_dict["Laser_Speed"] #mm/s
        jump_speed = self.input_file_dict["jump_speed"] #mm/s
        dosing_time = self.input_file_dict["dosing_time"] #s
        Power = self.input_file_dict["Laser_Power"] #W
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
        for layer in layers:

            this_layer = my_layer(layer_thickness * n_layer, layer_thickness)

            Geoms = layer.getGeometry()
        # for x in range (0,2):
        #     Geoms = layers[x].getGeometry()

            layer_path = np.empty((0,2), int)

            #Extract laser path:
            count = 0
            length_geoms_array=[]
            for geom in Geoms:
                layer_path = np.append(layer_path,geom.coords, axis=0)
                length_geoms_array.append(len(geom.coords))
            
                
            number_of_hatch_coords = len(Geoms[0].coords)

            #Relocate to origin:
            min_coords = layer_path[np.argmin(np.sum(layer_path, axis=1))]

            layer_path = layer_path - min_coords + np.array([offset,offset])

            # np.savetxt("../data/coords.csv", layer_path, delimiter=",")

            #Calculate time:
            n=0
            time = []
            for coords in layer_path:
                if n == 0:
                    time.append(dosing_time)
                else:
                    if n % 2 != 0: #during hatching, odd n means laser is on and the speed is equal to the scan speed
                        speed = scanspeed
                    else:
                        speed = jump_speed

                    previous_length = length_geoms_array[0] #during contouring, jump speed is used only at the end of the contour
                    for i in range(1,len(length_geoms_array)): 
                        if previous_length + 1 < n+1 <= previous_length + length_geoms_array[i]:
                            speed = scanspeed
                        elif previous_length == n:
                            speed = jump_speed
                        previous_length+=length_geoms_array[i]
                        

                    time.append( time[n-1] + (Calculate_distance(layer_path[n-1],layer_path[n])/speed) ) 
                n += 1

            # Calculate time of scanning
            this_layer.scan_time = time[-1] - dosing_time

            time = np.array(time)

            #Add z position
            z =np.ones((len(layer_path),1)) * layer_thickness * n_layer
            Power_column =np.ones((len(layer_path),1)) * Power

            #Add Power column

                #During hatching, power is zero every other coordinate
            Power_column[1:len(Power_column):2] = 0 
            
                #During contour, it is only zero at the end of the contour
            count = 0
            previous_length = 0
            for length in length_geoms_array:
                if count != 0:
                    Power_column[previous_length:previous_length+length-1] = Power 
                    Power_column[previous_length+length-1] = 0
                previous_length += length
                count += 1
            

            layer_path = np.append(layer_path, z, axis=1)
            layer_path = np.append(layer_path, Power_column, axis=1)

            heat_event = np.append(time.reshape(-1,1),layer_path, axis=1)


            #Add cooling time
            cooling_event = np.array([time[-1]+inter_layer_time-dosing_time,0,0,0,0])
            heat_event = np.vstack([heat_event, cooling_event])


            np.savetxt(self.input_file_dict["output_path"] + "/Heat_Series_ly%i.csv" %(n_layer), heat_event, delimiter=",")
            #Need to create roller_event_series

            roller_event = np.array([0,0,0,layer_thickness*n_layer,1])
            roller_event = np.vstack((roller_event, np.array([dosing_time,0,substrate_dimensions[1],layer_thickness*n_layer,1])))

            np.savetxt(self.input_file_dict["output_path"] + "/Roller_Series_ly%i.csv" %(n_layer), roller_event, delimiter=",")

            
            #Add layer to layer_objects_arrays
            self.layer_objects_array.append(this_layer)

            n_layer+=1
