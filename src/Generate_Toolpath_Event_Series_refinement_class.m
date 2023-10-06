

classdef Generate_Toolpath_Event_Series_refinement_class < handle

properties
    Laser_Speed;
    hatch_spacing=0.12;
    lx=0.96;
    ly=0.96;
    lz;
    layer_thickness=0.060;
    %Power
    Laser_Power=375000; %Watts
    %Roller time
    dosing_time=0.2;
    inter_layer_time=1-0.2; %substract dosing_time
    nlayers;
    current_layer;

    heights_of_interest;

    component_dimensions;

    last_layer;

    
    %arrays to measure how long and scanning takes to define appropiate time step lengths      
    time_of_scanning;
    indexes_of_scanning;

    number_of_refinements
    component_geometry_path

    time_per_bead;
    time_before_mid_bead;
    high_resolution_only_one_bead;
    
end

methods
    function read_input_file(obj)
        %Python code to read json file
        code=[
                "import json"
                "with open('.\jsonData.json', 'r') as myfile:"
                "    data=myfile.read()"
                "obj = json.loads(data)"
                "out=obj"
        ];
        %transform python dict to matlab struct
        dict_output = pyrun(code,'out');
        struct_output = struct(dict_output);
        
        %specify object attributes
        obj.layer_thickness=struct_output.layer_thickness;
        obj.hatch_spacing=struct_output.hatch_spacing;
        obj.number_of_refinements=struct_output.number_of_refinements;
        obj.heights_of_interest=struct_output.heights_of_interest;
        obj.component_geometry_path=struct_output.component_geometry_path;
        obj.Laser_Power=struct_output.Laser_Power;
        obj.Laser_Speed=struct_output.Laser_Speed;
        obj.dosing_time=struct_output.dosing_time;
        obj.inter_layer_time=struct_output.inter_layer_time;
        obj.high_resolution_only_one_bead=struct_output.high_resolution_only_one_bead;
        obj.component_dimensions=struct_output.component_dimensions;
        obj.heights_of_interest = cellfun(@double,cell(obj.heights_of_interest));
        obj.component_dimensions = cellfun(@double,cell(obj.component_dimensions));
        

        

        obj.lx=obj.component_dimensions(1);
        obj.ly=obj.component_dimensions(2);
        obj.lz=obj.component_dimensions(3);

        obj.last_layer=round(obj.lz/obj.layer_thickness);
        
        assert( rem(obj.component_dimensions(3),obj.layer_thickness) - 0.0 < 0.000001 , "Component height needs to be divisible by the layer thickness specified.")
        
    end

    function generate_steps_file(obj)
        %Generate STEPs INP
        
        text=['** ----------------------------------------------------------------\n'...
        '**\n'... 
        '** STEP: S-%i\n'...
        '**\n'... 
        '*Step, name=S-%i,EXTRAPOLATION=NO, INC=100000000, UNSYMM=YES\n'...
        '*Heat Transfer, end=PERIOD, deltmx=1000000.\n'...
        '%f, %f, 0.000001, %f,\n'...
        '**\n'...
        '** BOUNDARY CONDITIONS\n'...
        '** \n'...
        '** Name: Temp-BC-1 Type: Temperature\n'...
        '***Boundary\n'...
        '**SET-4, 11, 11, 26.\n'...
        '** \n'...
        '** LOADS\n'...
        '** \n'...
        '** Name: Load-1   Type: Body heat flux\n'...
        '*Dflux\n'...
        'Set-1, MBFNU, ,"ABQ_AM.Moving Heat Source"\n'...
        '** \n'...
        '** INTERACTIONS\n'...
        '** \n'...
        '** Interaction: Int-1\n'...
        '*Film\n'...
        'Set-1, FFS, 26., 0.018\n'...
        '** Interaction: Int-2\n'...
        '*Radiate\n'...
        'Set-1, RFS, 26., 0.25\n'...
        '** \n'...
        '** OUTPUT REQUESTS\n'...
        '**\n'... 
        '*Restart, write, frequency=0\n'...
        '**\n'...
        '** FIELD OUTPUT: F-Output-2\n'...
        '**\n'...
        '*Output, field%s\n'...
        '*Element Output, directions=YES\n'...
        'SDV,\n'...
        '**\n'...
        '** FIELD OUTPUT: F-Output-1\n'...
        '**\n'... 
        '*Node Output\n'...
        'NT\n'...
        '%s' ...
        '*Activate elements, activation=ElementProgressiveActivation1, expansion time constant=2.\n'...
        '"ABQ_AM.Material Input"\n'...
        '*End Step\n'];
        
        fileID = fopen('Steps.txt','w');
        %specify frequency of outputs
        freq='';  % number of times field is output in this step
%         freq_scan=', number interval=50';
        freq_scan='';
        %%
%         calculate what layers are of interest based on heights of interest
        for i=1:1:length(obj.heights_of_interest)
            top_height=obj.heights_of_interest(i);
            while (round(rem(top_height,obj.layer_thickness),2)~=round(0,2))
                top_height=top_height+0.001;
            end
            layers_of_interest(i)=round(top_height,2)/obj.layer_thickness;
            layers_of_interest(i)=round(layers_of_interest(i));
        end
        
        HO_text=[
        '** HISTORY OUTPUT: H-Output-%i\n'...
        '**\n' ...
        '*Output, history\n'...
        '*Element Output, elset=SET-HO-layer-%i\n'...
        'TEMP\n' ...
        ];
        
        HO_all='';
        for i=1:1:length(layers_of_interest)
            if round(obj.current_layer)>=layers_of_interest(i) %this if is to request only history outputs of layers than have been printed
                HO_all=append(HO_all,sprintf(HO_text,layers_of_interest(i),layers_of_interest(i)));
            end
        end
        
        %
        time_mark_text=[
        '*TIME POINTS, NAME=LASERON, GENERATE\n'...
        '0.0, %f, %f \n'...
        '%f, %f, 0.001 \n'...
        '%f, %f, %f \n'...
        ];


        
        stepN=1;
        for i=obj.current_layer:1:obj.nlayers
            tscan=obj.time_of_scanning(i);
           

            if ismember(i,layers_of_interest)
                
            
                if obj.high_resolution_only_one_bead == "yes"

                    freq_scan = ", TIME POINTS=LASERON, TIME MARKS=YES";
                    slow_time = obj.time_per_bead;
                    %prints time marks on top:
                    fprintf(fileID, time_mark_text, obj.time_before_mid_bead-obj.dosing_time, slow_time, obj.time_before_mid_bead-obj.dosing_time, obj.time_before_mid_bead-obj.dosing_time+obj.time_per_bead, obj.time_before_mid_bead-obj.dosing_time+obj.time_per_bead, tscan, slow_time);
                    scan_increment=obj.time_per_bead;

                else
                    scan_increment=0.001;
                end
    
                %prints rolling step
                fprintf(fileID,text,stepN,stepN,obj.dosing_time/4, obj.dosing_time, obj.dosing_time/4, freq,HO_all);
                %prints scanning step
                fprintf(fileID,text,stepN+1,stepN+1, scan_increment, tscan, scan_increment,freq_scan,HO_all);
                %prints short increment cooling step
                fprintf(fileID,text,stepN+2,stepN+2, scan_increment, 0.2, scan_increment,'',HO_all);
                %prints resting step
                fprintf(fileID,text,stepN+3,stepN+3,1.0, obj.inter_layer_time, 1.0, freq,HO_all);
                stepN=stepN+3;
                
            else
            
                %prints rolling step
                fprintf(fileID,text,stepN,stepN,obj.dosing_time/4, obj.dosing_time, obj.dosing_time/4, freq, HO_all);
                %prints scanning step
                fprintf(fileID,text,stepN+1,stepN+1,tscan/4, tscan, tscan/4, freq, HO_all);
                %prints short increment cooling step
                fprintf(fileID,text,stepN+2,stepN+2, 0.2, 0.2, 0.2, freq, HO_all);
                %prints resting step
                fprintf(fileID,text,stepN+3,stepN+3,1.0, obj.inter_layer_time, 1.0, freq, HO_all);
                stepN=stepN+3;
                
            end
        
        end
        
        if obj.current_layer==obj.last_layer
        
            %Add final, long cooling step
            text_cooling_step=['** ----------------------------------------------------------------\n'...
            '*STEP, name=Cooling, INC=10000\n'...
            '*HEAT TRANSFER\n'...
            '1.,60., ,\n'...
            '**\n'...
            '** OUTPUT REQUESTS\n'...
            '**\n'...
            '*Restart, write, frequency=0\n'...
            '**\n'...
            '** FIELD OUTPUT: F-Output-2\n'...
            '**\n'...
            '*OUTPUT,FIELD, number interval=10\n'...
            '*Element Output, directions=YES\n'...
            'SDV\n'...
            '**\n'...
            '** FIELD OUTPUT: F-Output-1\n'...
            '**\n'...
            '*Node Output\n'...
            'NT\n'...
            '%s'...
            '*Activate elements, activation=ElementProgressiveActivation1, expansion time constant=2.\n'...
            '"ABQ_AM.Material Input"\n'...
            '*END STEP\n'];
            
            fprintf(fileID, text_cooling_step, HO_all);
        end
        
        
        
        status = system('copy Steps.txt   Steps.inp')
        
        fclose(fileID);
        delete Steps.txt
        
    end

    function run(obj)
        obj.generate_event_series_files()
        obj.generate_steps_file()
    end

    end
end