import numpy as np
import os
import math as m

from skspatial.objects import Line, Sphere


def Generate_Step_files_for_layer(self,layer):
    #This method creates the step files of a given layer object

    #import helper functions for this method
    from .Generate_Step_helper_functions import Calculate_distance, Calculate_sphere_intersection, sphere_segment_intersection, change_event_series_for_build_pre_heat, change_event_series_for_layer_post_heat, Calculate_intersection_times


    #copy some variables to local variables to write less
    layer_height = layer * self.input_file_dict["layer_thickness"]
    scan_speed = self.input_file_dict["Laser_Speed"] #mm/s
    jump_speed = self.input_file_dict["jump_speed"] #mm/s

    #Delete previous step files:
    if os.path.isfile('Steps.inp'):
        os.remove('Steps.inp')

    # Read the step file template from the file, which we will populate with the required values along this method
    with open(self.module_path / 'step_template.txt', 'r') as file:
        step_template = file.read()

    # add bottom BC if requested
    if self.input_file_dict["bottom_BC"] == "yes":
        bottom_BC = ""
    else:
        bottom_BC = "**"

    # add thermocouple history output if requested:
    if self.input_file_dict["add_thermocouple"] == "yes":
        thermocouple_text = (
            "** Thermocouple History Output\n"
            "*Output, history\n"
            "*Node Output, nset=Set-thermocouple-HO\n"
            "NT\n"
            "**"
        )
    else:
        thermocouple_text = "**"

    # Specify history outputs requested:

    #text to define each history output
    HO_text = (
        "**\n"
        "** HISTORY OUTPUT: H-Output-{}\n"
        "**\n"
        "*Output, history\n"
        "*Element Output, elset=SET-HO-layer-{}\n"
        "TEMP\n"
        "**"
    )

    points_of_interest_np = np.array(self.input_file_dict["points_of_interest"])
    h_o_i = points_of_interest_np[:,2]

    HO_all=''
    for height in h_o_i:
        if layer_height+self.eps-height >= 0.0: # this if is to request only history outputs of layers than have been printed
            layer_number = round(height/self.input_file_dict["layer_thickness"])
            HO_all+=HO_text.format(layer_number,layer_number)

    # modify event series for rescans if requested
    if self.input_file_dict["post_heat_n_rescans"] - 0 >= self.eps:
        change_event_series_for_layer_post_heat(self,layer)

    #read scanpath from event series file:
    if self.input_file_dict["post_heat_n_rescans"] - 0 >= self.eps:
        # this if is here to prevent error in case post heat and bp pre heat at the same time
        path = self.Output_Path / "Event_series_Heat_mm.inp"
    elif self.input_file_dict["scanpath_folder"] == "":
        path = self.Output_Path / "scanpath" / f"Heat_Series_ly{layer}.csv"
    else:
        path = self.scanpath_folder / f"Heat_Series_ly{layer}.csv"
        
    heat_event_series = np.loadtxt(path, delimiter=",", usecols=(0,1,2,3))

    time_before_cooling = heat_event_series[:,0]

    #add cooling time
    # time = np.append(time,time[-1]+inter_layer_time-dosing_time)




    #Calculate intersection times with sphere around points of interest
    intersection_times = []
    points_of_interest = self.input_file_dict["points_of_interest"]

    # Check if layer is of interest
    layer_is_of_interest = False
    for point in points_of_interest:
        if (layer_height >= point[2]-self.eps) and abs(layer_height - point[2] + self.eps) <= self.input_file_dict["radius_sphere_of_interest"]:
            point_of_interest = point
            layer_is_of_interest = True
            break

    increment = self.input_file_dict["large_time_increment"]

    short_increment = self.input_file_dict["small_time_increment"]

    cooling_short_increment = 0.05

    # Finally Write Steps.inp file:

    # Define the text template for each step, which we will populate with the required values through formatting
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
    scan_time = time_before_cooling[-1] - dosing_time

    #If we are in a layer in contact with a sphere of interest, we need to add time marks
    if layer_is_of_interest:

        #Activate time marks and write them for the adaptive time increments
        freq_scan = ", TIME POINTS=LASERON, TIME MARKS=YES"

        time_mark_text = (
            "**\n"
            "*TIME POINTS, NAME=LASERON, GENERATE\n"
        )

        # Calculate intersection times with sphere of interest
        if layer_is_of_interest:
            layer_path = heat_event_series[:,1:3]
            intersection_times = Calculate_intersection_times(self, layer_path, time_before_cooling, layer_height, point_of_interest)



        # Write time marks to string for adaptive time increments
        for i in range(len(intersection_times)):
            t1 = intersection_times[i][0] - dosing_time
            t2 = intersection_times[i][1] - dosing_time
            if i < len(intersection_times)-1:
                t3 = intersection_times[i+1][0] - dosing_time
            else:
                t3 = scan_time            

            if i == 0: #first
                if t1 < 0.00005: # in case the first time mark is too close to the begining, we skip it to avoid error
                    t1 = 0
                else:
                    time_mark_text += f"0.0, {t1}, {increment}\n"

            time_mark_text += f"{t1}, {t2}, {short_increment}\n"

            if t3 - t2 > 0.00005: # in case the time mark is too close to the next one, we skip it to avoid error
                time_mark_text += f"{t2}, {t3}, {increment}\n"

        #add time points at beggining of Steps.inp     
        f=open("Steps.inp",'w')
        f.write(time_mark_text)

        #print Build Plate pre_heat step if it is 1st layer and requested by user
        if layer == 1 and self.input_file_dict["bp_pre_heat_time"] != 0:
            #Change event-series
            change_event_series_for_build_pre_heat(self)

            #write step
            f.write(step_text.format("Pre-Heat", "Pre_heat", 10, self.input_file_dict["bp_pre_heat_time"], 10, freq, HO_all))

        #print rolling step
        f.write(step_text.format(1, 1 ,dosing_time/4 , dosing_time, dosing_time/4, freq, HO_all))
        #print scanning step
        f.write(step_text.format(2, 2 , increment, scan_time, increment, freq_scan, HO_all))
        #prints short increment cooling step
        f.write(step_text.format(3, 3 , cooling_short_increment, 0.2, cooling_short_increment,freq, HO_all))
        #print long increment cooling step
        f.write(step_text.format(4, 4 , 1.0, inter_layer_time, 1.0,freq, HO_all))

        #add long cooling if last layer:
        if layer == self.number_of_layers:
            f.write(step_text.format(30, 30, 1.0, inter_layer_time, 1.0,freq, HO_all))


    else: #If we are not in a layer in contact with a sphere of interest, we can use slowe time increments all along

        f = open('Steps.inp', 'w')
        #print rolling step
        f.write(step_text.format(1, 1 ,dosing_time/4 , dosing_time, dosing_time/4,freq, HO_all))
        #print scanning step
        f.write(step_text.format(2, 2 , increment, scan_time, increment,freq, HO_all))
        #prints short increment cooling step
        f.write(step_text.format(3, 3 , cooling_short_increment, 0.2, cooling_short_increment,freq, HO_all))
        #print long increment cooling step
        f.write(step_text.format(4, 4 , 1.0, inter_layer_time, 1.0,freq, HO_all))

        #add long cooling if last layer:
        if layer == self.number_of_layers:
            f.write(step_text.format(5, 5, 1.0, self.input_file_dict["final_cooling_time"], 5.0,freq, HO_all))
        
    


