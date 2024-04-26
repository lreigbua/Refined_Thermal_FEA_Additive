import numpy as np
import os

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
        sphere = Sphere(point_of_interest, self.input_file_dict["radius_sphere_of_interest"])
        line = Line.from_points(coords0, coords1)

        try:
            point_a, point_b = sphere.intersect_line(line)
            return point_a, point_b
        except:
            return False
        
    def change_event_series_for_build_pre_heat():
        #This method changes the event series file for the build plate pre-heat step
        
        #read event series from files:
        path = self.scanpath_folder / f"Heat_Series_ly1.csv"
        scanpath_comp_series = np.loadtxt(path, delimiter=",")

        path = self.module_path / f"Heat_Series_pre_heat_meander.csv"
        scanpath_pre_heat_series = np.loadtxt(path, delimiter=",")
    
        path = self.scanpath_folder / f"Roller_Series_ly1.csv"
        roller_series = np.loadtxt(path, delimiter=",")

        ## 1.remove extra scans from scanpath_pre_heat_series
        # Get the first column of the array
        first_column = scanpath_pre_heat_series[:, 0]
        # Create a boolean mask where the first column values are less than or equal to the pre-heat time requested by the user
        mask = first_column <= self.input_file_dict["bp_pre_heat_time"]
        # Apply the mask to the array to get the filtered array
        final_h_event_series = scanpath_pre_heat_series[mask]
        # remove heat from last row to ensure it laser is off at the end
        final_h_event_series[-1, -1] = 0
        
        ## 2. add component scanpath to event series
        #add pre_heating time to component scanpath:
        scanpath_comp_series[:,0] += self.input_file_dict["bp_pre_heat_time"]
        # concatenate to final event series
        final_h_event_series = np.concatenate((final_h_event_series, scanpath_comp_series), axis=0)

        ## 3. modify roller series
        #add heating time to roller series:
        roller_series[:,0] += self.input_file_dict["bp_pre_heat_time"]

        ##4. Save files to output folder to be read by Abaqus
        np.savetxt(self.Output_Path / "Event_series_Heat_mm.inp", final_h_event_series, delimiter=",")
        np.savetxt(self.Output_Path / "Event_series_Roller_mm.inp", roller_series, delimiter=",")

    def change_event_series_for_layer_post_heat(layer_number):
        #This method changes the event series file to add layer post-heating
        
        #read event series from files:
        path = self.scanpath_folder / f"Heat_Series_ly{layer_number}.csv"
        scanpath_comp_series = np.loadtxt(path, delimiter=",")

        # make a copy of the scanpath for the rescan
        scanpath_rescan = scanpath_comp_series.copy()
        # remove the dosing time
        scanpath_rescan[:,0] -= self.input_file_dict["dosing_time"]
        #change power to rescan power specified by user
        power_column = scanpath_rescan[:, -1]
        power_column[power_column > self.eps] = self.input_file_dict["post_heat_power"]
        scanpath_rescan[:, -1] = power_column

        scanpath_rescan_cur = scanpath_rescan.copy()

        for i in range(0, self.input_file_dict["post_heat_n_rescans"]):
            scanpath_rescan_cur[:,0] = scanpath_rescan[:,0] + scanpath_comp_series[-1,0] + Calculate_distance(scanpath_comp_series[-1,1:3],scanpath_comp_series[0,1:3])/self.input_file_dict["jump_speed"]
            scanpath_comp_series = np.concatenate((scanpath_comp_series, scanpath_rescan_cur), axis=0)

        ##4. Save files to output folder to be read by Abaqus
        np.savetxt(self.Output_Path / "Event_series_Heat_mm.inp", scanpath_comp_series, delimiter=",")




    layer_height = layer * self.input_file_dict["layer_thickness"]
    scan_speed = self.input_file_dict["Laser_Speed"] #mm/s
    jump_speed = self.input_file_dict["jump_speed"] #mm/s


    #Delete previous step files:
    if os.path.isfile('Steps.inp'):
        os.remove('Steps.inp')

    # add bottom BC if requested
    if self.input_file_dict["bottom_BC"] == "yes":
        bottom_BC = ""
    else:
        bottom_BC = "**"

    # add thermocouple history output if requested:
    if self.input_file_dict["add_thermocouple"] == "yes":
        thermocouple_text = """** Thermocouple History Output
*Output, history
*Node Output, nset=Set-thermocouple-HO
NT
**"""
    else:
        thermocouple_text = "**"

    step_text=f"""**
** ----------------------------------------------------------------
** 
** STEP: S-{{0}}
** 
*Step, name=S-{{1}},EXTRAPOLATION=NO, INC=100000000, UNSYMM=YES
*Heat Transfer, end=PERIOD, deltmx=1000000.
{{2}}, {{3}}, 0.000001, {{4}},
**
** BOUNDARY CONDITIONS
** 
** Name: Temp-BC-1 Type: Temperature
{bottom_BC}*Boundary
{bottom_BC}Set-subst_bot_surface, 11, 11, {self.input_file_dict["Chamber_Temperature"]}
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
Set-1, FFS, {self.input_file_dict["Chamber_Temperature"]}, 0.018
** Interaction: Int-2
*Radiate
Set-1, RFS, {self.input_file_dict["Chamber_Temperature"]}, 0.25
** 
** OUTPUT REQUESTS
** 
*Restart, write, frequency=0
**
** FIELD OUTPUT: F-Output-2
**
*Output, field{{5}}
*Element Output, directions=YES
***SDV,
**
** FIELD OUTPUT: F-Output-1
** 
*Node Output
NT
{{6}}**
{thermocouple_text} 
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
    points_of_interest_np = np.array(self.input_file_dict["points_of_interest"])
    h_o_i = points_of_interest_np[:,2]

    HO_all=''
    for height in h_o_i:
        if layer_height+self.eps-height >= 0.0: # this if is to request only history outputs of layers than have been printed
            layer_number = round(height/self.input_file_dict["layer_thickness"])
            HO_all+=HO_text.format(layer_number,layer_number)

    if self.input_file_dict["post_heat_n_rescans"] - 0 >= self.eps:
        change_event_series_for_layer_post_heat(layer)

    #read scanpath from event series file:
    if self.input_file_dict["post_heat_n_rescans"] - 0 >= self.eps:
        # this if is here to prevent error in case post heat and bp pre heat at the same time
        path = self.Output_Path / "Event_series_Heat_mm.inp"
    elif self.input_file_dict["scanpath_folder"] == "":
        path = self.Output_Path / "scanpath" / f"Heat_Series_ly{layer}.csv"
    else:
        path = self.scanpath_folder / f"Heat_Series_ly{layer}.csv"
        
    heat_event_series = np.loadtxt(path, delimiter=",", usecols=(0,1,2,3))

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
        if (layer_height >= point[2]-self.eps) and abs(layer_height - point[2] + self.eps) <= self.input_file_dict["radius_sphere_of_interest"]:
            point_of_interest = point
            layer_is_of_interest = True
            break
    
    if layer_is_of_interest:
        layer_path = heat_event_series[:,1:3]

        for c in range(1,len(layer_path)): #we start at 1 to skip dosing time coordinates
            #Calculate time of intersection with sphere of interest:

            Coord_ini = np.append(layer_path[c-1], layer_height).transpose()
            Coord_final = np.append(layer_path[c], layer_height).transpose()

            intersection = Calculate_sphere_intersection(Coord_ini,Coord_final, point_of_interest)
                
            if intersection is not False and layer_height >= (point_of_interest[2]-self.eps): #If there is an intersection in the top half of the sphere

                point_a, point_b = intersection
                
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


    increment = self.input_file_dict["large_time_increment"]

    short_increment = self.input_file_dict["small_time_increment"]

# Write Steps.inp file:
    if layer_is_of_interest:

        freq_scan = ", TIME POINTS=LASERON, TIME MARKS=YES"


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

        #print Build Plate pre_heat step if it is 1st layer and requested by user
        if layer == 1 and self.input_file_dict["bp_pre_heat_time"] != 0:
            #Change event-series
            change_event_series_for_build_pre_heat()

            #write step
            f.write(step_text.format("Pre-Heat", "Pre_heat", 10, self.input_file_dict["bp_pre_heat_time"], 10, freq, HO_all))

        #print rolling step
        f.write(step_text.format(1, 1 ,dosing_time/4 , dosing_time, dosing_time/4, freq, HO_all))
        #print scanning step
        f.write(step_text.format(2, 2 , increment, scan_time, increment, freq_scan, HO_all))
        #prints short increment cooling step
        f.write(step_text.format(3, 3 , 0.2, 0.2, 0.2,freq, HO_all))
        #print long increment cooling step
        f.write(step_text.format(4, 4 , 1.0, inter_layer_time, 1.0,freq, HO_all))

        #add long cooling if last layer:
        if layer == self.number_of_layers:
            f.write(step_text.format(30, 30, 1.0, inter_layer_time, 1.0,freq, HO_all))


    else:

        f = open('Steps.inp', 'w')
        #print rolling step
        f.write(step_text.format(1, 1 ,dosing_time/4 , dosing_time, dosing_time/4,freq, HO_all))
        #print scanning step
        f.write(step_text.format(2, 2 , increment, scan_time, increment,freq, HO_all))
        #prints short increment cooling step
        f.write(step_text.format(3, 3 , 0.2, 0.2, 0.2,freq, HO_all))
        #print long increment cooling step
        f.write(step_text.format(4, 4 , 1.0, inter_layer_time, 1.0,freq, HO_all))

        #add long cooling if last layer:
        if layer == self.number_of_layers:
            f.write(step_text.format(5, 5, 1.0, self.input_file_dict["final_cooling_time"], 5.0,freq, HO_all))
        
    
