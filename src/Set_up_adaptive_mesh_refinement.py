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

class Mesh_Refinement_Pre_Processing:

    component_height=10
    layer_thickness=0.06
    number_of_refinements=6
    component_geometry_name = 'Comp_geometry_my_rectangle_true_height.sat'

    def __init__(self):
        self.current_height = 5

    def import_initial_geometry(self):
        # Import geometry file of component as a part named comp:
        mdb.openAcis(
            './'+ self.component_geometry_name
            , scaleFromFile=OFF)
        mdb.models['main'].PartFromGeometryFile(combine=False, dimensionality=THREE_D, geometryFile=mdb.acis, name='Comp', type=DEFORMABLE_BODY)

    def calculate_slices_heights(self): #Calculates the heights of the different slices according to the number of refinements specified
        
        self.slices_array = []
        
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

                print(n)




        

    def generate_slices_instances(self): #Creates the instances of the different slices using Slices array
        i=0
        for slice in self.slices_array:

            self.import_initial_geometry() #Imports geometry from CAD file
            i=i+1
            if slice.height_top  > self.layer_thickness/2:  #This if is to avoid cutting empty slice objects
                slice.Create_Slice_Instance(str(i)) #Cuts the given slice out from the CAD file


class Slice:
    offset_datum_of_plane=15

    def __init__(self):
        self.height_top = 0.01
        self.height_bot = 0
        self.mesh_refinement = 0.06

        assert self.height_top > self.height_bot, "height_top should be higher than height_bot'"


    def Create_Slice_Instance(self,name): #Creates a slice on part named component using the top and bottom heights of the slice object and assigns name "name"
        
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
        mdb.models['main'].parts.changeKey(fromName='Comp', toName='Slice-'+name)


        #Mesh part
        mdb.models['main'].parts['Slice-'+name].seedPart(deviationFactor=0.1, 
        minSizeFactor=0.1, size=self.mesh_refinement)
        mdb.models['main'].parts['Slice-'+name].generateMesh()

        #Add part to Assembly
        mdb.models['main'].rootAssembly.Instance(dependent=ON, name='Slice-'+name+'-1', part=
            mdb.models['main'].parts['Slice-'+name])

        print("slice "+ name +  " created with top_height=" + str(self.height_top) + " and bot_height=" + str(self.height_bot) + ". Mesh refinement = " + str(self.mesh_refinement))

    def get_slice_thickness(self):
        return (self.height_top-self.height_bot)


###################################################################################################################################
##################################################### MAIN ########################################################################
###################################################################################################################################

# Creates Model called main, where the actions will be performed
mdb.Model(modelType=STANDARD_EXPLICIT, name='main')

Process = Mesh_Refinement_Pre_Processing()


Process.calculate_slices_heights()
Process.generate_slices_instances()