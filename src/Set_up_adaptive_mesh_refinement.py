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

import numpy as np
import json

def assign_section_to_part(part_name,section_name):
        mdb.models['main'].parts[part_name].SectionAssignment(offset=0.0,
        offsetField='', offsetType=MIDDLE_SURFACE, region=
        mdb.models['main'].parts[part_name].sets['Set-1'], sectionName=
        section_name, thicknessAssignment=FROM_SECTION)

def change_part_to_thermal_elements(part_name):
        mdb.models['main'].parts[part_name].setElementType(elemTypes=(
            ElemType(elemCode=DC3D8, elemLibrary=STANDARD), ElemType(elemCode=DC3D6,
            elemLibrary=STANDARD), ElemType(elemCode=DC3D4, elemLibrary=STANDARD)),
            regions=(
            mdb.models['main'].parts[part_name].cells, ))
        

def closest_layer_height(given_height):
    height_c_top=given_height

    #  The code below chooses a multiple of the layer thickness above and below the selected height and produces cuts in these planes
    while(round(height_c_top%Octree_mesh_generation.layer_thickness,2)!=0):
        height_c_top=height_c_top+0.001

    height_c_top=round(height_c_top,2)

    return height_c_top

class Octree_mesh_generation: #this class performs octree mesh generation of a geometry at a given height

    material_names_list = ['NO_TRANS_TI6AL4V','ABQ_PHASE_TRANS_TI6AL4V']

    file = open('..\input\input_file.json', 'r')
    dict_var_of_json = json.load(file)
    file.close()

    layer_thickness=dict_var_of_json['layer_thickness']
    number_of_refinements=dict_var_of_json['number_of_refinements']
    heights_of_interest=dict_var_of_json['heights_of_interest']
    component_geometry_path=dict_var_of_json['component_geometry_path']
    substrate_dimensions = dict_var_of_json['substrate_dimensions']

        # Calculate component dimensions
    mdb.Model(modelType=STANDARD_EXPLICIT, name='main') #Creates a model named main, overwritting if needed
    # Import geometry file of component as a part named comp:
    mdb.openAcis(
        str(component_geometry_path)
        , scaleFromFile=OFF)
    mdb.models['main'].PartFromGeometryFile(combine=False, dimensionality=THREE_D, geometryFile=mdb.acis, name='Comp', type=DEFORMABLE_BODY)

    # calculate component dimensions 
    component_dimensions=mdb.models['main'].parts['Comp'].queryGeometry(printResults=FALSE)['boundingBox'][1]
    component_height=component_dimensions[2]

    offset_datum_of_plane = component_dimensions[1]+0.1

    assert abs(component_dimensions[2]%layer_thickness-0.0) < 0.0000001 , "Component height needs to be divisible by the layer thickness"


    #add new data to json file for matlab
    newData = {"component_dimensions": component_dimensions}
    dict_var_of_json.update(newData)

    file = open('.\jsonData.json', 'w')
    json.dump(dict_var_of_json, file, indent=4, sort_keys=True)
    file.close()



    def __init__(self):
        self.current_height=self.layer_thickness
        


    def import_initial_geometry(self):
        # Import geometry file of component as a part named comp:
        mdb.openAcis(
            str(self.component_geometry_path)
            , scaleFromFile=OFF)
        mdb.models['main'].PartFromGeometryFile(combine=False, dimensionality=THREE_D, geometryFile=mdb.acis, name='Comp', type=DEFORMABLE_BODY)

    def calculate_slices_heights(self): #Calculates the heights of the different slices according to the number of refinements specified

        self.slices_array = []
        flag=0

        for n in range (0,self.number_of_refinements):
            self.slices_array.append(Slice())

            if n == 0:  #top layer (current scanning), we want one voxel with layer height
                self.slices_array[n].height_top=self.current_height
                self.slices_array[n].height_bot=self.slices_array[n].height_top-self.layer_thickness
                self.slices_array[n].mesh_refinement = self.layer_thickness

            elif n == 1: # next two layers, we still want high resolution
                # check if current layer build height has been reached
                max_possible_slice_thickness = self.layer_thickness * 2
                current_possible_slice_thickness = max_possible_slice_thickness
                while ((current_possible_slice_thickness + (self.current_height - self.slices_array[n-1].height_bot)) > (self.current_height + 0.000001)):
                    current_possible_slice_thickness = current_possible_slice_thickness - self.layer_thickness

                if abs(current_possible_slice_thickness) - 0.0 <= 0.000001: break

                self.slices_array[n].height_top = self.slices_array[n-1].height_bot
                self.slices_array[n].height_bot = self.slices_array[n].height_top-current_possible_slice_thickness
                self.slices_array[n].mesh_refinement = self.layer_thickness #We keep the same mesh refinement as top layers

            elif n < self.number_of_refinements-1: #the resolution keeps increasing accordingly
                # check if current layer build height has been reached
                max_possible_slice_thickness = self.layer_thickness * 2**(n-1)
                current_possible_slice_thickness = max_possible_slice_thickness
                while ((current_possible_slice_thickness + self.current_height - self.slices_array[n-1].height_bot) > (self.current_height + 0.000001)):
                    current_possible_slice_thickness=current_possible_slice_thickness-self.layer_thickness

                if abs(current_possible_slice_thickness) - 0.0 <= 0.000001: break

                self.slices_array[n].height_top = self.slices_array[n-1].height_bot
                self.slices_array[n].height_bot = self.slices_array[n].height_top-current_possible_slice_thickness
                self.slices_array[n].mesh_refinement = self.layer_thickness * 2**(n-1)

            elif n == self.number_of_refinements-1: #if we have reached max resolution, we will use this until the bottom of the current height
                current_possible_slice_thickness = self.current_height - (self.current_height - self.slices_array[n-1].height_bot) #since we have reached the last refinement, now the maximum thickness is the rest of the current height left

                self.slices_array[n].height_top = self.slices_array[n-1].height_bot
                self.slices_array[n].height_bot = self.slices_array[n].height_top-current_possible_slice_thickness
                self.slices_array[n].mesh_refinement = self.layer_thickness * 2**(n-1)

            if n==0 or n==1:
                c=0
                for height in self.heights_of_interest:    #decreases resolution if layer not of interest

                    height_top=closest_layer_height(height)
                    if abs(self.current_height-height_top)>0.000001:
                        c+=1
                
                if c == len(self.heights_of_interest):
                    self.slices_array[n].mesh_refinement*=2





    def generate_slices_instances(self): #Creates the instances of the different slices using Slices array
        #Create Materials and sections:
        for material_name in self.material_names_list:
            mdb.models['main'].Material(name=material_name)
            mdb.models['main'].HomogeneousSolidSection(material=material_name, name=
                'Section-'+material_name, thickness=None)


        i=0
        for slice in self.slices_array:
            self.import_initial_geometry() #Imports geometry from CAD file
            i=i+1
            
            if slice.height_top>=0.0002: #this if is to delete slides created by bugs
                slice.ID = str(i)
                slice.Create_Slice_Instance() #Cuts the given slice out from the CAD file

                if slice == self.slices_array[0]: #if this is the top slice
                    assign_section_to_part('Slice-'+slice.ID,'Section-NO_TRANS_TI6AL4V')
                else:
                    assign_section_to_part('Slice-'+slice.ID,'Section-NO_TRANS_TI6AL4V')
            else:
                del(self.slices_array[i-1])

    def generate_susbtrate(self):
        gap=self.layer_thickness*16

        # Create substrate out
        mdb.models['main'].ConstrainedSketch(name='__profile__', sheetSize=100.0)
        mdb.models['main'].sketches['__profile__'].rectangle(point1=(self.substrate_dimensions[0]/2+self.component_dimensions[0]/2, self.substrate_dimensions[1]/2+self.component_dimensions[1]/2), 
            point2=(-self.substrate_dimensions[0]/2+self.component_dimensions[0]/2, -self.substrate_dimensions[1]/2+self.component_dimensions[1]/2))
        mdb.models['main'].Part(dimensionality=THREE_D, name='Substrate_out', type=
            DEFORMABLE_BODY)
        mdb.models['main'].parts['Substrate_out'].BaseSolidExtrude(depth=9.0, 
            sketch=mdb.models['main'].sketches['__profile__'])
        
        #cur region for substrate in
        DatumP_XY = mdb.models['main'].parts['Substrate_out'].DatumPlaneByPrincipalPlane(offset=9-0.96, principalPlane=XYPLANE)
        DatumAxisX = mdb.models['main'].parts['Substrate_out'].DatumAxisByPrincipalAxis(principalAxis=YAXIS)
        mdb.models['main'].ConstrainedSketch(gridSpacing=0.05, name='__profile__',
            sheetSize=20.0, transform=
        mdb.models['main'].parts['Substrate_out'].MakeSketchTransform(
        sketchPlane=mdb.models['main'].parts['Substrate_out'].datums[2],
        sketchPlaneSide=SIDE1,
        sketchUpEdge=mdb.models['main'].parts['Substrate_out'].datums[3],
        sketchOrientation=RIGHT, origin=(0.0, 0.0, 0.0)))
        mdb.models['main'].parts['Substrate_out'].projectReferencesOntoSketch(filter=
            COPLANAR_EDGES, sketch=mdb.models['main'].sketches['__profile__'])

        mdb.models['main'].sketches['__profile__'].rectangle(point1=(self.component_dimensions[0]+gap, self.component_dimensions[1]+gap), 
            point2=(-gap, -gap))

        mdb.models['main'].parts['Substrate_out'].CutExtrude(flipExtrudeDirection=ON, sketch=
            mdb.models['main'].sketches['__profile__'], sketchOrientation=RIGHT,
            sketchPlane=mdb.models['main'].parts['Substrate_out'].datums[2], sketchPlaneSide=
            SIDE1, sketchUpEdge=mdb.models['main'].parts['Substrate_out'].datums[3])
        del mdb.models['main'].sketches['__profile__']

        mdb.models['main'].parts['Substrate_out'].PartitionCellByExtrudeEdge(cells=
            mdb.models['main'].parts['Substrate_out'].cells,
            edges=(mdb.models['main'].parts['Substrate_out'].edges[0], 
            mdb.models['main'].parts['Substrate_out'].edges[4], 
            mdb.models['main'].parts['Substrate_out'].edges[7], 
            mdb.models['main'].parts['Substrate_out'].edges[10]), line=
            mdb.models['main'].parts['Substrate_out'].edges[17], sense=REVERSE)


        # Create substrate in
        mdb.models['main'].ConstrainedSketch(name='__profile__', sheetSize=100.0)
        mdb.models['main'].sketches['__profile__'].rectangle(point1=(self.component_dimensions[0]+gap, self.component_dimensions[1]+gap), 
            point2=(-gap, -gap))
        mdb.models['main'].Part(dimensionality=THREE_D, name='Substrate_in', type=
            DEFORMABLE_BODY)
        mdb.models['main'].parts['Substrate_in'].BaseSolidExtrude(depth=0.96, 
            sketch=mdb.models['main'].sketches['__profile__'])
        
        #Add to assembly
        mdb.models['main'].rootAssembly.Instance(dependent=ON, name='Substrate_in-1'
            , part=mdb.models['main'].parts['Substrate_in'])
        mdb.models['main'].rootAssembly.Instance(dependent=ON, name=
            'Substrate_out-1', part=mdb.models['main'].parts['Substrate_out'])
        
        #Translate substrates to bottom
        mdb.models['main'].rootAssembly.translate(instanceList=('Substrate_out-1',), vector=(0.0, 0.0, -9.0))
        mdb.models['main'].rootAssembly.translate(instanceList=( 'Substrate_in-1',), vector=(0.0, 0.0, -0.96))

        #Mesh
        mdb.models['main'].parts['Substrate_out'].seedPart(deviationFactor=0.1,
        minSizeFactor=0.1, size=gap*2)
        mdb.models['main'].parts['Substrate_out'].generateMesh()
        
        mdb.models['main'].parts['Substrate_in'].seedPart(deviationFactor=0.1,
        minSizeFactor=0.1, size=self.slices_array[-1].mesh_refinement*2)
        mdb.models['main'].parts['Substrate_in'].generateMesh()

        #Change mesh to thermal elements
        change_part_to_thermal_elements('Substrate_in')
        change_part_to_thermal_elements('Substrate_out')

        #create sets-1 and assign section
        mdb.models['main'].parts['Substrate_in'].Set(elements=mdb.models['main'].parts['Substrate_in'].elements, name='Set-1')
        mdb.models['main'].parts['Substrate_out'].Set(elements=mdb.models['main'].parts['Substrate_out'].elements, name='Set-1')
        assign_section_to_part('Substrate_in','Section-NO_TRANS_TI6AL4V')
        assign_section_to_part('Substrate_out','Section-NO_TRANS_TI6AL4V')

    #tie substrate_in to last slice
        
        #Create Surfaces
        mdb.models['main'].rootAssembly.Surface(name='subst_in_top_surface', side1Faces=
            mdb.models['main'].rootAssembly.instances['Substrate_in-1'].faces.getByBoundingBox(-10000000,-1000000,-0.00001,10000000,1000000,0.00001))        
        
        self.slices_array[-1].create_bot_surface()  #creates bottom surface of last slice

        #Creates tie
        mdb.models['main'].Tie(adjust=ON, main=
            mdb.models['main'].rootAssembly.surfaces['subst_in_top_surface'], name=
            'Component_to_substrate', positionToleranceMethod=COMPUTED, secondary=
            mdb.models['main'].rootAssembly.surfaces[self.slices_array[-1].bot_surface_name], thickness=
            ON, tieRotations=ON)

    #tie both substrates
        #Create Surfaces
        mdb.models['main'].rootAssembly.Surface(name='subst_in_out_surface', side1Faces=
            mdb.models['main'].rootAssembly.instances['Substrate_in-1'].faces.getByBoundingBox(-gap,-gap,-self.substrate_dimensions[2]-1,gap+self.component_dimensions[0],gap+self.component_dimensions[1],1))
        
        mdb.models['main'].rootAssembly.Surface(name='subst_out_in_surface', side1Faces=
            mdb.models['main'].rootAssembly.instances['Substrate_out-1'].faces.getByBoundingBox(-gap,-gap,-1,gap+self.component_dimensions[0],gap+self.component_dimensions[1],1))        

        #Creates tie
        mdb.models['main'].Tie(adjust=ON, main=
            mdb.models['main'].rootAssembly.surfaces['subst_out_in_surface'], name=
            'subst_to_subst', positionToleranceMethod=COMPUTED, secondary=
            mdb.models['main'].rootAssembly.surfaces['subst_in_out_surface'], thickness=
            ON, tieRotations=ON)


    def tie_slices(self,top_slice,bot_slice):
        mdb.models['main'].Tie(adjust=ON, main=
            mdb.models['main'].rootAssembly.surfaces[bot_slice.top_surface_name], name=
            'Constraint_'+'Slice-'+top_slice.ID+'_and_'+'Slice-'+bot_slice.ID, positionToleranceMethod=COMPUTED, secondary=
            mdb.models['main'].rootAssembly.surfaces[top_slice.bot_surface_name], thickness=
            ON, tieRotations=ON)

    def generate_tie_constraits(self):

        j=0
        for slice in self.slices_array:
            if slice != self.slices_array[-1]: #if we are not in the bottom slice
                slice.create_bot_surface()

                if j < len(self.slices_array)-1:
                    self.slices_array[j+1].create_top_surface()
                    self.tie_slices(slice,self.slices_array[j+1])
                    
            j=j+1
    
    def create_assembly_set_1(self):
        cells_list=[]
        for i in mdb.models['main'].rootAssembly.instances.keys():
            cells_list.append(mdb.models['main'].rootAssembly.instances[i].cells)       # mdb.models['main'].rootAssembly.Set(name='Set-1')

        mdb.models['main'].rootAssembly.Set(cells=cells_list, name='Set-1')

    def create_job_and_write_inp(self):
        current_layer_number = str(int(self.current_height/self.layer_thickness))

        mdb.Job(activateLoadBalancing=False, atTime=None, contactPrint=OFF, 
            description='', echoPrint=OFF, explicitPrecision=SINGLE, 
            getMemoryFromAnalysis=True, historyPrint=OFF, memory=90, memoryUnits=
            PERCENTAGE, model='main', modelPrint=OFF, multiprocessingMode=DEFAULT, 
            name='layer-'+current_layer_number, nodalOutputPrecision=SINGLE, numCpus=1, numDomains=1, 
            numGPUs=0, numThreadsPerMpiProcess=1, parallelizationMethodExplicit=DOMAIN, 
            queue=None, resultsFormat=ODB, scratch='', type=ANALYSIS, userSubroutine=''
            , waitHours=0, waitMinutes=0)
        
        mdb.jobs['layer-'+current_layer_number].writeInput()

    def  create_element_HO_set_at(self,height,slice,n):
    #Create element set for history outputs containing the middle element of each layer

        height_c_top=height

        #  The code below chooses a multiple of the layer thickness above and below the selected height and produces cuts in these planes
        while(round(height_c_top%self.layer_thickness,2)!=0):
            height_c_top=height_c_top+0.001

        height_c_top=round(height_c_top,2)

        position=np.array([self.component_dimensions[0]/2,self.component_dimensions[1]/2,height_c_top])

        #set bounding box positions of x and y
        positionMax=position+slice.mesh_refinement+0.001
        positionMin=position-slice.mesh_refinement+0.001

        #set bounding box positions of z
        positionMax[2]=height_c_top+slice.mesh_refinement+0.001
        positionMin[2]=height_c_top-slice.mesh_refinement-0.001

        # print(height_c_top)
        # print(positionMax)
        # print(positionMin)


        # mdb.models['main'].rootAssembly.Set(elements=
        #     mdb.models['main'].rootAssembly.instances['Slice-'+slice.ID+'-1'].elements.getByBoundingBox(0,0,0,2.55,2.55,1.04), name='Set-HO-layer-prevent-error')
        #     # mdb.models['main'].rootAssembly.instances['COMP-1'].elements.getByBoundingBox(positionMin[0],positionMin[1],positionMin[2],positionMax[0],positionMax[1],positionMax[2]), name='Set-HO-layer-'+str(int(lay_number)))


        lay_number=height_c_top/self.layer_thickness
        mdb.models['main'].rootAssembly.Set(elements=
            # mdb.models['main'].rootAssembly.instances['COMP-1'].elements.getByBoundingBox(2.45,2.45,0.94,2.55,2.55,1.04), name='Set-HO-layer-'+str(int(lay_number)))
            mdb.models['main'].rootAssembly.instances['Slice-'+slice.ID+'-1'].elements.getByBoundingBox(positionMin[0],positionMin[1],positionMin[2],positionMax[0],positionMax[1],positionMax[2]), name='Set-HO-layer-'+str(int(lay_number)))

    def  create_node_HO_set_at(self,height,slice,n):
    #Create nodes set for history outputs containing the middle element of each layer
    # !!NEEDS CORRECTION!!

        height_c_top=height

        #  The code below chooses a multiple of the layer thickness above and below the selected height and produces cuts in these planes
        while(round(height_c_top%self.layer_thickness,2)!=0):
            height_c_top=height_c_top+0.001

        height_c_top=round(height_c_top,2)

        position=np.array([self.component_dimensions[0]/2,self.component_dimensions[1]/2,height_c_top])

        #set bounding box positions of x and y
        positionMax=position+slice.mesh_refinement-0.000001
        positionMin=position-slice.mesh_refinement+0.000001

        #set bounding box positions of z
        positionMax[2]=height_c_top+slice.mesh_refinement-0.000001
        positionMin[2]=height_c_top-slice.mesh_refinement+0.000001

        # print(height_c_top)
        # print(positionMax)
        # print(positionMin)


        # mdb.models['main'].rootAssembly.Set(elements=
        #     mdb.models['main'].rootAssembly.instances['Slice-'+slice.ID+'-1'].elements.getByBoundingBox(0,0,0,2.55,2.55,1.04), name='Set-HO-layer-prevent-error')
        #     # mdb.models['main'].rootAssembly.instances['COMP-1'].elements.getByBoundingBox(positionMin[0],positionMin[1],positionMin[2],positionMax[0],positionMax[1],positionMax[2]), name='Set-HO-layer-'+str(int(lay_number)))


        lay_number=height_c_top/self.layer_thickness
        mdb.models['main'].rootAssembly.Set(nodes=
            # mdb.models['main'].rootAssembly.instances['COMP-1'].elements.getByBoundingBox(2.45,2.45,0.94,2.55,2.55,1.04), name='Set-HO-layer-'+str(int(lay_number)))
            mdb.models['main'].rootAssembly.instances['Slice-'+slice.ID+'-1'].nodes.getByBoundingBox(positionMin[0],positionMin[1],positionMin[2],positionMax[0],positionMax[1],positionMax[2]), name='Set-HO-layer-'+str(int(lay_number)))



    def generate_sets_for_history_outputs(self):
        
        for des_height in self.heights_of_interest:

            if self.current_height+0.0001>des_height:

                k=1
                for slice in self.slices_array:
                    if slice.height_top+0.0001>des_height-0.001 and slice.height_bot-0.0001< des_height-0.001:
                        self.create_element_HO_set_at(des_height,slice,k)
                        # self.create_node_HO_set_at(des_height,slice,k)
                        k=k+1






    
    def run(self):
        mdb.Model(modelType=STANDARD_EXPLICIT, name='main') #Creates a model named main, overwritting if needed
        self.calculate_slices_heights()
        self.generate_slices_instances()
        self.generate_susbtrate()
        self.generate_tie_constraits()
        self.create_assembly_set_1()
        self.generate_sets_for_history_outputs()
        self.create_job_and_write_inp()



class Slice:  #class to store attributes and methods for each slice


    def __init__(self):
        self.height_top = 0.0001
        self.height_bot = 0
        self.mesh_refinement = 0.06
        self.offset_datum_of_plane=Octree_mesh_generation.offset_datum_of_plane
        self.material_name = Octree_mesh_generation.material_names_list[0]
        self.ID = 'x'

        assert self.height_top > self.height_bot, "height_top should be higher than height_bot'"


    def Create_Slice_Instance(self): #Creates a slice on part named component using the top and bottom heights of the slice object and assigns name "name"

        DatumP_XZ = mdb.models['main'].parts['Comp'].DatumPlaneByPrincipalPlane(offset=self.offset_datum_of_plane, principalPlane=XZPLANE)
        DatumAxisZ = mdb.models['main'].parts['Comp'].DatumAxisByPrincipalAxis(principalAxis=ZAXIS)

        mdb.models['main'].ConstrainedSketch(gridSpacing=0.05, name='__profile__',
            sheetSize=2.16, transform=
        mdb.models['main'].parts['Comp'].MakeSketchTransform(
        sketchPlane=mdb.models['main'].parts['Comp'].datums[2],
        sketchPlaneSide=SIDE1,
        sketchUpEdge=mdb.models['main'].parts['Comp'].datums[3],
        sketchOrientation=RIGHT, origin=(0.0, self.offset_datum_of_plane, 0.0)))
        mdb.models['main'].parts['Comp'].projectReferencesOntoSketch(filter=
            COPLANAR_EDGES, sketch=mdb.models['main'].sketches['__profile__'])

        mdb.models['main'].sketches['__profile__'].rectangle(point1=(-1000000.0, -1000000.0),  #bottom rectangle
            point2=(1000000.0, self.height_bot))
        mdb.models['main'].sketches['__profile__'].rectangle(point1=(-100.0, self.height_top),   #top rectangle
            point2=(1000000.0,1000000.0))

        mdb.models['main'].parts['Comp'].CutExtrude(flipExtrudeDirection=OFF, sketch=
            mdb.models['main'].sketches['__profile__'], sketchOrientation=RIGHT,
            sketchPlane=mdb.models['main'].parts['Comp'].datums[2], sketchPlaneSide=
            SIDE1, sketchUpEdge=mdb.models['main'].parts['Comp'].datums[3])
        del mdb.models['main'].sketches['__profile__']
        mdb.models['main'].parts.changeKey(fromName='Comp', toName='Slice-'+self.ID)

        #Mesh part
        mdb.models['main'].parts['Slice-'+self.ID].seedPart(deviationFactor=0.1,
        minSizeFactor=0.1, size=self.mesh_refinement)
        mdb.models['main'].parts['Slice-'+self.ID].generateMesh()


        #Change mesh to thermal elements
        mdb.models['main'].parts['Slice-'+self.ID].setElementType(elemTypes=(
            ElemType(elemCode=DC3D8, elemLibrary=STANDARD), ElemType(elemCode=DC3D6,
            elemLibrary=STANDARD), ElemType(elemCode=DC3D4, elemLibrary=STANDARD)),
            regions=(
            mdb.models['main'].parts['Slice-'+self.ID].cells, ))

        #Create part element set-1 with the all elements of the part
        mdb.models['main'].parts['Slice-'+self.ID].Set(elements=mdb.models['main'].parts['Slice-'+self.ID].elements, name='Set-1')


        #Add part to Assembly
        mdb.models['main'].rootAssembly.Instance(dependent=ON, name='Slice-'+self.ID+'-1', part=
            mdb.models['main'].parts['Slice-'+self.ID])

        # print("slice "+ self.ID +  " created with top_height=" + str(self.height_top) + " and bot_height=" + str(self.height_bot) + ". Mesh refinement = " + str(self.mesh_refinement))

    def get_slice_thickness(self):
        return (self.height_top-self.height_bot)

    def assign_section(self):
        mdb.models['main'].parts['Slice-'+self.ID].SectionAssignment(offset=0.0,
        offsetField='', offsetType=MIDDLE_SURFACE, region=
        mdb.models['main'].parts['Slice-'+self.ID].sets['Set-1'], sectionName=
        'Section-NO_TRANS_TI6AL4V', thicknessAssignment=FROM_SECTION)

    def create_bot_surface(self):
        self.bot_surface_name= 'Slice-'+self.ID+'-bot-surf'
        mdb.models['main'].rootAssembly.Surface(name=self.bot_surface_name, side1Faces=
            mdb.models['main'].rootAssembly.instances['Slice-'+self.ID+'-1'].faces.getByBoundingBox(-10000000,-1000000,self.height_bot-0.00001,10000000,1000000,self.height_bot+0.00001))
        
    def create_top_surface(self):
        self.top_surface_name= 'Slice-'+self.ID+'-top-surf'
        mdb.models['main'].rootAssembly.Surface(name=self.top_surface_name, side1Faces=
            mdb.models['main'].rootAssembly.instances['Slice-'+self.ID+'-1'].faces.getByBoundingBox(-10000000,-1000000,self.height_top-0.00001,10000000,1000000,self.height_top+0.00001))



###################################################################################################################################
##################################################### MAIN ########################################################################
###################################################################################################################################



Process = Octree_mesh_generation() #Performs an octree mesh with tie surfaces for the given geometry at a given layer height

Process.current_height=83*0.06

# for i in range(42,43):
while abs(Process.component_height + Process.layer_thickness - Process.current_height)>0.000001: # Performs Octree mesh generation until it has been done for all layer heights
    print(Process.current_height)
    Process.run()
    Process.current_height=round(Process.current_height+Process.layer_thickness,2)
