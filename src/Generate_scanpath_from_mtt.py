import json

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

f = open("../input/input_file.json", "r")
input_file = json.load(f)

scanspeed = input_file["Laser_Speed"] #mm/s
jump_speed = input_file["jump_speed"] #mm/s
dosing_time = input_file["dosing_time"] #s
Power = input_file["Laser_Power"] #W
layer_thickness = input_file["layer_thickness"] #mm
inter_layer_time = input_file["inter_layer_time"] #s
offset = input_file["offset"]
substrate_dimensions = input_file["substrate_dimensions"] #mm
AM_build_file = input_file["AM_build_file"] 

#Read mtt file

mttReader = mtt.Reader()
mttReader.setFilePath(AM_build_file)
mttReader.parse()

layers = mttReader.layers

n_layer=1
# for layer in layers:
    # Geoms = layer.getGeometry()
for x in range (0,2):
    Geoms = layers[x].getGeometry()

    layer_path = np.empty((0,2), int)

    #Extract laser path:
    for geom in Geoms[0:3]:
        
        layer_path = np.append(layer_path,geom.coords, axis=0)
        
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
            if n % 2 != 0: #not even
                speed = scanspeed
            else:
                speed = jump_speed
            time.append( time[n-1] + (Calculate_distance(layer_path[n-1],layer_path[n])/speed) ) 
        n += 1



    time = np.array(time)

    #Add z position and power
    z =np.ones((len(layer_path),1)) * layer_thickness * n_layer
    Power_column =np.ones((len(layer_path),1)) * Power

    Power_column[1:len(Power_column):2] = 0

    layer_path = np.append(layer_path, z, axis=1)
    layer_path = np.append(layer_path, Power_column, axis=1)

    heat_event = np.append(time.reshape(-1,1),layer_path, axis=1)


    #Add cooling time
    cooling_event = np.array([time[-1]+inter_layer_time-dosing_time,0,0,0,0])
    heat_event = np.vstack([heat_event, cooling_event])


    np.savetxt("./Heat_Series_ly%i.csv" %(n_layer), heat_event, delimiter=",")
    #Need to create roller_event_series

    roller_event = np.array([0,0,0,layer_thickness*n_layer,1])
    roller_event = np.vstack((roller_event, np.array([dosing_time,0,substrate_dimensions[1],layer_thickness*n_layer,1])))

    np.savetxt("./Roller_Series_ly%i.csv" %(n_layer), roller_event, delimiter=",")

    n_layer+=1
