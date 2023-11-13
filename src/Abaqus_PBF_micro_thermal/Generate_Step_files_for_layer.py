import numpy as np

from skspatial.objects import Line, Sphere

def Generate_Step_files_for_layer(self,layer):
    #This method creates the step files of a given layer object

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
        sphere = Sphere(point_of_interest, 0.18)
        line = Line.from_points(coords0, coords1)

        try:
            point_a, point_b = sphere.intersect_line(line)
            return point_a, point_b
        except:
            return False


    layer_height = layer * self.input_file_dict["layer_thickness"]
    scan_speed = self.input_file_dict["Laser_Speed"] #mm/s
    jump_speed = self.input_file_dict["jump_speed"] #mm/s

    step_text="""**
** ----------------------------------------------------------------
** 
** STEP: S-{}
** 
*Step, name=S-{},EXTRAPOLATION=NO, INC=100000000, UNSYMM=YES
*Heat Transfer, end=PERIOD, deltmx=1000000.
{}, {}, 0.000001, {},
**
** BOUNDARY CONDITIONS
** 
** Name: Temp-BC-1 Type: Temperature
***Boundary
**SET-4, 11, 11, 26.
** 
** LOADS
** 
** Name: Load-1   Type: Body heat flux
*Dflux
Set-1, MBFNU, ,"ABQ_AM.Moving Heat Source"
** 
** INTERACTIONS
** 
** Interaction: Int-1
*Film
Set-1, FFS, 26., 0.018
** Interaction: Int-2
*Radiate
Set-1, RFS, 26., 0.25
** 
** OUTPUT REQUESTS
** 
*Restart, write, frequency=0
**
** FIELD OUTPUT: F-Output-2
**
*Output, field{}
*Element Output, directions=YES
***SDV,
**
** FIELD OUTPUT: F-Output-1
** 
*Node Output
NT
{} 
*Activate elements, activation=ElementProgressiveActivation1, expansion time constant=2.
"ABQ_AM.Material Input"
*End Step
    **"""

    freq = ''
    freq_scan = "" # Used to set the time increments and number of outputs

    dosing_time = self.input_file_dict["dosing_time"]
    inter_layer_time = self.input_file_dict["inter_layer_time"]

    #Specify history outputs requested:
    HO_text="""**
** HISTORY OUTPUT: H-Output-{}
**
*Output, history
*Element Output, elset=SET-HO-layer-{}
TEMP
    **"""
        
    HO_all=''
    for height in self.input_file_dict["heights_of_interest"]:
        if layer_height+self.eps-height >= 0.0: # this if is to request only history outputs of layers than have been printed
            layer_number = round(height/self.input_file_dict["layer_thickness"])
            HO_all+=HO_text.format(layer_number,layer_number)



    #read scanpath from event series file:
    if self.input_file_dict["scanpath_path"] == "":
        path = self.Output_Path / "scanpath" / f"Heat_Series_ly{layer}.csv"
    else:
        path = self.scanpath_path / f"Heat_Series_ly{layer}.csv"
        
    heat_event_series = np.loadtxt(path, delimiter=",", usecols=(0,1,2,3))

    layer_path = heat_event_series[:,1:3]
    time = heat_event_series[:,0]

    #add cooling time
    # time = np.append(time,time[-1]+inter_layer_time-dosing_time)

    #Calculate scan time
    scan_time = time[-1] - dosing_time


#Calculate intersection times with sphere around points of interest

    intersection_times = []
    points_of_interest = self.input_file_dict["points_of_interest"]

    #Calculate point of interest for this layer:
    layer_is_of_interest = False
    for point in points_of_interest:
        if layer_height >= point[2]-self.eps and abs(layer_height - point[2] + self.eps) <= 0.18:
            point_of_interest = point
            layer_is_of_interest = True
            break
    
    if layer_is_of_interest:

        for c in range(1,len(layer_path)): #we start at 1 to skip dosing time coordinates
            #Calculate time of intersection with sphere of interest:
            Coord_ini = np.append(layer_path[c-1], layer_height).transpose()
            Coord_final = np.append(layer_path[c], layer_height).transpose()

            intersection = Calculate_sphere_intersection(Coord_ini,Coord_final, point_of_interest)
                
            if intersection is not False and layer_height >= point_of_interest[2]-self.eps: #If there is an intersection in the top half of the sphere
                point_a, point_b = intersection
                # print((point_a, point_b))
                #time of entering sphere:
                start_time_of_intersection = time[c-1] + (Calculate_distance(layer_path[c-1],point_a)/scan_speed)
                end_time_of_intersection = time[c-1] + (Calculate_distance(layer_path[c-1],point_b)/scan_speed)

                # #The next two ifs are used to address if the start of a layerpath is inside the sphere of interest
                # if start_time_of_intersection_inside_sphere == False:
                #     if inSphere(Coord_ini, point_of_interest, 0.018): #if beggining of hatch is inside sphere
                #         start_time_of_intersection = time[c-1] + (Calculate_distance(layer_path[c-1],point_a)/speed)
                #         start_time_of_intersection_inside_sphere = True

                # if inSphere(Coord_final, point_of_interest, 0.018) and start_time_of_intersection_inside_sphere: #if end of hatch is inside sphere                            
                #     continue
                # else:

                # print((start_time_of_intersection, end_time_of_intersection))
                intersection_times.append((start_time_of_intersection, end_time_of_intersection))


    
# Write Steps.inp file:
    if layer_is_of_interest:

        freq_scan = ", TIME POINTS=LASERON, TIME MARKS=YES"
        increment = scan_time/8

        short_increment = 0.001

        time_mark_text=f"""**
*TIME POINTS, NAME=LASERON, GENERATE
"""

        for i in range(len(intersection_times)):
            t1 = intersection_times[i][0] - dosing_time
            t2 = intersection_times[i][1] - dosing_time
            if i < len(intersection_times)-1:
                t3 = intersection_times[i+1][0] - dosing_time
            else:
                t3 = scan_time

            if t2 < t1: continue #this is to avoid errors for the moment

            if i == 0: #first line
                time_mark_text += f"0.0, {t1}, {increment}\n"

            time_mark_text += f"{t1}, {t2}, {short_increment}\n"
            time_mark_text += f"{t2}, {t3}, {increment}\n"



        #add time points to Steps.inp     
        f=open("Steps.inp",'w')
        f.write(time_mark_text)

        #print rolling step
        f.write(step_text.format(1, 1 ,dosing_time/4 , dosing_time, dosing_time/4, freq, HO_all))
        #print scanning step
        f.write(step_text.format(2, 2 , increment, scan_time, increment, freq_scan, HO_all))
        #prints short increment cooling step
        f.write(step_text.format(3, 3 , 0.2, 0.2, 0.2,freq, HO_all))
        #print long increment cooling step
        f.write(step_text.format(4, 4 , 1.0, inter_layer_time, 1.0,freq, HO_all))

    else:

        f = open('Steps.inp', 'w')
        #print rolling step
        f.write(step_text.format(1, 1 ,dosing_time/4 , dosing_time, dosing_time/4,freq, HO_all))
        #print scanning step
        f.write(step_text.format(2, 2 , scan_time/4 , scan_time, scan_time/4,freq, HO_all))
        #prints short increment cooling step
        f.write(step_text.format(3, 3 , 0.2, 0.2, 0.2,freq, HO_all))
        #print long increment cooling step
        f.write(step_text.format(4, 4 , 1.0, inter_layer_time, 1.0,freq, HO_all))
    
