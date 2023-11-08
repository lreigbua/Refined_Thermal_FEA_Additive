from .layer_class import my_layer

def Generate_Step_files_for_layer(self,layer):
    #This method prints the step files of a given layer object

    print(layer.intersection_times)
    
    layer_height = layer.height

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

    it_is_layer_of_interest = layer.is_of_interest

    dosing_time = self.input_file_dict["dosing_time"]
    scan_time = layer.scan_time
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


    

    if it_is_layer_of_interest:



        freq_scan = ", TIME POINTS=LASERON, TIME MARKS=YES"
        increment = scan_time/12

        #Calculate time points
        t1 = layer.scan_time_before_middle_bead
        t2 = layer.scan_time_after_middle_bead
        t3 = scan_time
        
        short_increment = 0.001

        time_mark_text=f"""**
*TIME POINTS, NAME=LASERON, GENERATE
"""

        for i in range(len(layer.intersection_times)):
            t1 = layer.intersection_times[i][0] - dosing_time
            t2 = layer.intersection_times[i][1] - dosing_time
            if i < len(layer.intersection_times)-1:
                t3 = layer.intersection_times[i+1][0] - dosing_time
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
        f.write(step_text.format(2, 2 , scan_time/20 , scan_time, scan_time/12, freq_scan, HO_all))
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
    
