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

#Calculate number of layers by reading json file
file = open('./jsonData.json', 'r')
dict_var_of_json = json.load(file)
file.close()
component_dimensions=dict_var_of_json['component_dimensions']
layer_thickness=dict_var_of_json['layer_thickness']
component_height=component_dimensions[2]
n_layers=component_height/layer_thickness

heights_of_interest=dict_var_of_json['heights_of_interest']

class element():

    def __init__(self, height):

        self.height=height
        self.data=np.empty((0,2))
        self.flag = 0


element_array = []
for height in heights_of_interest:
    element_array.append(element(height))
        

nparray=np.array([0,1])

for layer_number in range(1,int(n_layers+1)):
# for layer_number in range(73,76):
    Job_name="Job-layer-{}".format(layer_number)

    odbname=Job_name
    path='./'                    # set odb path here (if in working dir no need to change!)
    myodbpath=path+odbname+'.odb'    
    odb=openOdb(path=myodbpath)

    results=np.array([])


    for step in odb.steps.keys():
        if odb.steps[step].historyRegions.keys()!=[]:     

            Hist_Region_ID=len(odb.steps[step].historyRegions.keys())-1-7
            i=0

            print(len(odb.steps[step].historyRegions.keys()))
            for element in range(0,len(odb.steps[step].historyRegions.keys())/8):
                


                history_region_name=odb.steps[step].historyRegions.keys()[Hist_Region_ID]
                
                

                data=np.array(odb.steps[step].historyRegions[history_region_name].historyOutputs['TEMP'].data)

                if(type(data)==type(nparray)):
                    if len(element_array[i].data) > 1: 
                        data[:,0]=data[:,0]+element_array[i].data[-1,0] #add previos time

                    element_array[i].data=np.vstack((element_array[i].data,data))

                Hist_Region_ID = Hist_Region_ID-8
                i = i+1

    odb.close()

for el in element_array:
    np.savetxt("./Temperature_Element_at_heigt_{}.csv".format(el.height),el.data)