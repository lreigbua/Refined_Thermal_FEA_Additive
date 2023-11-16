from part import *
from material import *
from section import *
from assembly import *
from step import *
from interaction import *
from load import *
from mesh import *
from optimization import *
from job import *
from sketch import *
from visualization import *
from connectorBehavior import *
import odbAccess

import numpy as np
import json
import os

import sys


#This is an Abaqus python script to read temperature histories from Abaqus odb files.
#Extracts the temperature history from each odb file at the points of interest. It is assumed that the points of interest are in the same order as the points in the json file.
#It puts together the temperature history for each point of interest in a csv file.
#The temperature history is saved in a csv file for each point of interest. The csv file has two columns: time and temperature.


#It would be possible to use historyPoints and improve this script, but it would require nodeSets. Currently the rest of the code uses elementSets:
        # instance_name=odb.rootAssembly.elementSets[hist_point['HO_set_name']].elements[0][0].instanceName
        # first_element_in_HO = odb.rootAssembly.instances[instance_name].elementSets[hist_point['HO_set_name']].elements[0][0]
        # histPoint = odbAccess.HistoryPoint(first_element_in_HO)
        # tipHistories = odb.steps[step].getHistoryRegion(histPoint)
        # data = np.array(otipHistories.historyOutputs['TEMP'].data)



#Calculate number of layers by reading json file
file = open('./jsonData.json', 'r')
dict_var_of_json = json.load(file)
file.close()
component_dimensions=dict_var_of_json['component_dimensions']
layer_thickness=dict_var_of_json['layer_thickness']
component_height=component_dimensions[2]
n_layers=component_height/layer_thickness

points_of_interest=np.array(dict_var_of_json['points_of_interest'])
heights_of_interest=list(points_of_interest[:,2])

layers_of_interest=[]
for height in heights_of_interest:
    layers_of_interest.append(int(height/layer_thickness))

        
Temp_history_points_dict = {}
for layer_number in layers_of_interest:
    Temp_history_points_dict[layer_number] = {}
    Temp_history_points_dict[layer_number]['HO_set_name'] = 'SET-HO-LAYER-{}'.format(layer_number)
    Temp_history_points_dict[layer_number]['height'] = layer_number*layer_thickness
    Temp_history_points_dict[layer_number]['data'] = np.empty((0,2))



nparray=np.array([0,1])

for layer_number in range(1,int(n_layers)):
# for layer_number in range(73,76):
    Job_name="Job-layer-{}".format(layer_number)

    odbname=Job_name
    path='./'                    # set odb path here (if in working dir no need to change!)
    myodbpath=path+odbname+'.odb'    
    odb=openOdb(path=myodbpath)

    results=np.array([])


    for step in odb.steps.keys():

        if odb.steps[step].historyRegions.keys()!=[]: #if there are history outputs in this step
            
            for layer_of_int, hist_point in Temp_history_points_dict.items():  #for each history point

                if layer_number >= layer_of_int:  #if the current layer is higher than the layer number of interest, meaning the element set is in the output
                    
                    # print >> sys.__stdout__, layer_of_int, layer_number
                    # print >> sys.__stdout__, hist_point['HO_set_name']

                    HO_set=odb.rootAssembly.elementSets[hist_point['HO_set_name']]
                    first_element_in_HO_set=HO_set.elements[0][0].label
                    instance_name=HO_set.elements[0][0].instanceName

                    for Hist_Reg_Name in odb.steps[step].historyRegions.keys():
                        if str(first_element_in_HO_set) in Hist_Reg_Name and instance_name in Hist_Reg_Name:
                            history_region_name = Hist_Reg_Name
                            break

                    data=np.array(odb.steps[step].historyRegions[history_region_name].historyOutputs['TEMP'].data)

                    if(type(data)==type(nparray)):
                        
                        # if len(hist_point['data']) == 0:  #add previous time of the simulation to the first time_step of this history output
                        #     index_of_previous_hist_point = layers_of_interest.index(layer_of_int)-1
                        #     if index_of_previous_hist_point >= 0:
                        #         hist_point['data']=Temp_history_points_dict[layers_of_interest[index_of_previous_hist_point]]['data'][:,0]

                        # print >> sys.__stdout__, hist_point['data']

                        if len(hist_point['data']) > 1: 
                            data[:,0]=data[:,0]+hist_point['data'][-1,0] #add previos time

                        else: #add previous time of the simulation to the first time_step of this history output
                            index_of_previous_hist_point = layers_of_interest.index(layer_of_int)-1
                            if index_of_previous_hist_point >= 0:
                                data[:,0]=Temp_history_points_dict[layers_of_interest[index_of_previous_hist_point]]['data'][-1,0]

                        hist_point['data']=np.vstack((hist_point['data'],data))

    odb.close()

for hist_point in Temp_history_points_dict.values():
    np.savetxt("./Temperature_Element_at_heigt_{}.csv".format(hist_point['height']),hist_point['data'],delimiter=",")