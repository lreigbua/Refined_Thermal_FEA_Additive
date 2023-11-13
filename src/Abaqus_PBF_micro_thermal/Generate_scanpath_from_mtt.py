def Generate_scanpath_from_mtt(self):
    try:
        import pyslm
        import pyslm.analysis
        import pyslm.visualise
        import pyslm.hatching

        from pyslm import geometry as slm
        from libSLM import mtt
    except:
        raise Exception("PySLM is not installed. Please install PySLM with libSLM and translators or input your own scanpath as event series files.")

    import numpy as np
    import os


    def Calculate_distance(coords0,coords1): #Calculate distance between two points
        return np.sqrt((coords1[0]-coords0[0])**2 + (coords1[1]-coords0[1])**2)

    print("Generating scanpaths from mtt file: "+str(self.AM_build_file)+" ...")

    # Create output data folder if it does not exist:
    if not self.Output_Path.exists(): # if output folder does not exit
        os.mkdir(self.Output_Path)

    #Create scanpath folder
    path = self.Output_Path / "scanpath"
    if not os.path.exists(path):
        os.mkdir(path)

    #Read input_file.json
    scanspeed = self.input_file_dict["Laser_Speed"] #mm/s
    jump_speed = self.input_file_dict["jump_speed"] #mm/s
    dosing_time = self.input_file_dict["dosing_time"] #s
    Power_value = self.input_file_dict["Laser_Power"] #W
    layer_thickness = self.input_file_dict["layer_thickness"] #mm
    offset = self.input_file_dict["offset"]
    substrate_dimensions = self.input_file_dict["substrate_dimensions"] #mm
    AM_build_file = self.AM_build_file

    #Read mtt file
    mttReader = mtt.Reader()
    mttReader.setFilePath(str(AM_build_file.resolve()))
    mttReader.parse()

    layers = mttReader.layers

    #initialize some variables
    n_layer=1
    self.layer_objects_array=[]

    for layer in layers: #iterate through layers

        layer_height = layer_thickness * n_layer

        Geoms = layer.getGeometry()

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
                            speed = scanspeed
                        else:
                            p = Power_value
                            speed = jump_speed

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
                
                Power_column.append(p)

        #Relocate layer_path to origin (sample in mtt is not at origin):
        min_coords = layer_path[np.argmin(np.sum(layer_path, axis=1))]
        layer_path = layer_path - min_coords + np.array([offset,offset])

        #Create event series array
        heat_event = np.hstack((np.array(time).reshape(-1, 1), layer_path, np.ones((len(layer_path),1)) * layer_height, np.array(Power_column).reshape(-1, 1)))

        time = np.array(time)

        # #Add cooling time
        # cooling_event = np.array([time[-1]+inter_layer_time-dosing_time,0,0,0,0])
        # heat_event = np.vstack([heat_event, cooling_event])


        #Save heat_event_series
        np.savetxt(self.Output_Path / "scanpath" / f"Heat_Series_ly{n_layer}.csv" , heat_event, delimiter=",")
        
        #Need to create roller_event_series
        roller_event = np.array([0,0,0,layer_thickness*n_layer,1])
        roller_event = np.vstack((roller_event, np.array([dosing_time,0,substrate_dimensions[1],layer_thickness*n_layer,1])))

        np.savetxt(self.Output_Path / "scanpath" / f"Roller_Series_ly{n_layer}.csv", roller_event, delimiter=",")

        n_layer+=1

    print("Scanpaths generated!")
