from .layer_class import my_layer

def Generate_Step_files_for_layer(self,layer):
    #This method prints the step files of a given layer object
    
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

    it_is_layer_of_interest = False
    for height in self.input_file_dict["heights_of_interest"]:
        if abs(layer_height-height) < self.eps:
            it_is_layer_of_interest = True

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

        if self.input_file_dict["high_resolution_only_one_bead"] == "yes":

            freq_scan = ", TIME POINTS=LASERON, TIME MARKS=YES"
            increment = scan_time/6

            #Calculate time points
            t1 = layer.scan_time_before_middle_bead
            t2 = layer.scan_time_after_middle_bead
            t3 = scan_time

            time_mark_text=f"""**
*TIME POINTS, NAME=LASERON, GENERATE
0.0, {t1}, {increment} 
{t1}, {t2}, 0.0001 
{t2}, {t3}, {increment} 
            **"""
            #add time points to Steps.inp     
            f=open("Steps.inp",'w')
            f.write(time_mark_text)

            #print rolling step
            f.write(step_text.format(1, 1 ,dosing_time/4 , dosing_time, dosing_time/4, freq, HO_all))
            #print scanning step
            f.write(step_text.format(2, 2 , scan_time/20 , scan_time, scan_time/20, freq_scan, HO_all))
            #prints short increment cooling step
            f.write(step_text.format(3, 3 , 0.2, 0.2, 0.2,freq, HO_all))
            #print long increment cooling step
            f.write(step_text.format(4, 4 , 1.0, inter_layer_time, 1.0,freq, HO_all))

        else:
            
            f = open('Steps.inp', 'w')
            increment = 0.001
            #print rolling step
            f.write(step_text.format(1, 1 ,dosing_time/4 , dosing_time, dosing_time/4,freq, HO_all))
            #print scanning step
            f.write(step_text.format(2, 2 , increment , scan_time, increment, freq, HO_all))
            #prints short increment cooling step
            f.write(step_text.format(3, 3 , increment, 0.2, increment,freq, HO_all))
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
    
