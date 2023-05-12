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

file = open('.\jsonData.json', 'r')
dict_var_of_json = json.load(file)
file.close()

component_dimensions=dict_var_of_json['component_dimensions']
layer_thickness=dict_var_of_json['layer_thickness']

component_height=component_dimensions[2]

n_layers=component_height/layer_thickness

for layer_number in range(10,int(n_layers+1)):
    Job_name="Job-layer-{}".format(layer_number)

    odbname=Job_name
    path='./'                    # set odb path here (if in working dir no need to change!)
    myodbpath=path+odbname+'.odb'    
    odb=openOdb(path=myodbpath)

    for step in odb.steps.keys():
        if odb.steps[step].historyRegions.keys()!=[]:
            history_region_name=odb.steps[step].historyRegions.keys()[0]

            data=np.array(odb.steps[step].historyRegions[history_region_name].historyOutputs['TEMP'].data)

            if(type(data)=='numpy.ndarray'):
                np.savetxt("./history_out_{}_step_{}.csv".format(Job_name,step),data)

    odb.close()