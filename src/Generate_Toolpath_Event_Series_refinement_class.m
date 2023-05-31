

classdef Generate_Toolpath_Event_Series_refinement_class < handle

properties
    %Use International Units
    %Laser speed (assumed constant)
    % Laser_Speed=600;
    Laser_Speed;
    %Scan Spacing/ hatch hatch_spacingcing (distance between laser paths in same layer)
    % hatch_spacing=0.10;
    hatch_spacing=0.12;
    %length in x of rectangle in mm
    lx=0.96;
    %length in y of rectangle in mm
    ly=0.96;
    lz;
    %Thickness of each layer
    %layer_thickness=60e-6;
    layer_thickness=0.060;
    %Power
    %Laser_Power=120000; %Watts
    Laser_Power=375000; %Watts
    %Roller time
    dosing_time=0.2;
    %Time to rest for recoating
    %inter_layer_time=30.2; 
    inter_layer_time=1-0.2; %substract dosing_time
    %initial laye
    nlayers;
    current_layer;

    %layers of interest:
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
    function generate_event_series_files(obj)    

        %initial layer
        obj.nlayers=obj.current_layer;
    
        timemat(1)=0;
        xmat(1)=0;
        ymat(1)=obj.ly/2;
        zmat(1)=obj.layer_thickness*obj.current_layer;
        mat(1)=1;
        
        time(1)=obj.dosing_time;
        x(1)=obj.hatch_spacing;
        y(1)=obj.hatch_spacing;
        z(1)=obj.layer_thickness*obj.current_layer;
        p(1)=obj.Laser_Power;
             
        %%
        % Calculate x and y for each layer
         
        
        n=2;
        k=2;
        flg=0;
        for layer=obj.current_layer:1:obj.nlayers
            
        
            if layer ~= obj.current_layer
                timemat(k)=time(n-1)-obj.inter_layer_time;
            else
                timemat(k)=obj.dosing_time;
            end
            xmat(k)=obj.lx;
            ymat(k)=obj.ly/2;
            zmat(k)=(layer)*obj.layer_thickness;
            mat(k)=0;
            
            t_before_scan=time(n-1);
            index_before_scan=n-1;
        
        
        
        if is_even(layer)
                for i=1:1:(obj.ly/(2*obj.hatch_spacing)+1)%npasseslayer
                    sc=obj.hatch_spacing;
          
            %Start Square Contour
            
            %Increase x
                    x(n)=obj.lx-obj.hatch_spacing;
                    y(n)=y(n-1);    
                    %Calculate z
                    z(n)=(layer)*obj.layer_thickness;
                    %Calculate time during layer
                    time(n)=(norm([x(n) y(n) z(n)]-[x(n-1) y(n-1) z(n-1)]))/obj.Laser_Speed+time(n-1);
                    %Appobj.ly obj.Laser_Power
                    p(n)=0;
                    n=n+1;
            
                %Increase y
                    x(n)=obj.lx-obj.hatch_spacing;
                    y(n)=y(n-1)+sc;    
                    %Calculate z
                    z(n)=(layer)*obj.layer_thickness;
                    %Calculate time during layer
                    time(n)=(norm([x(n) y(n) z(n)]-[x(n-1) y(n-1) z(n-1)]))/obj.Laser_Speed+time(n-1);
                    %Appobj.ly obj.Laser_Power
                    p(n)=obj.Laser_Power;
                    n=n+1;
            
                %Decrease x
                    x(n)=obj.hatch_spacing;
                    y(n)=y(n-1);    
                    %Calculate z
                    z(n)=(layer)*obj.layer_thickness;
                    %Calculate time during layer
                    time(n)=(norm([x(n) y(n) z(n)]-[x(n-1) y(n-1) z(n-1)]))/obj.Laser_Speed+time(n-1);
                    %Appobj.ly obj.Laser_Power
                    p(n)=0;
                    n=n+1;
                    if (i <= ((obj.ly-obj.hatch_spacing)/(2*obj.hatch_spacing))) %if it's not the last scan
                    %Increase y again
                            x(n)=obj.hatch_spacing;
                            y(n)=y(n-1)+sc;    
                            %Calculate z
                            z(n)=(layer)*obj.layer_thickness;
                            %Calculate time during layer
                            time(n)=(norm([x(n) y(n) z(n)]-[x(n-1) y(n-1) z(n-1)]))/obj.Laser_Speed+time(n-1);
                            %Appobj.ly obj.Laser_Power
                            p(n)=obj.Laser_Power;
                            n=n+1;
                    end
                

                    if y(n-1)>obj.ly/2 && flg==0
                        flg=1;

                        obj.time_per_bead = time(n-1)-time(n-3);
                        obj.time_before_mid_bead = time(n-3);

                    end
            
            
                end
                
                
                
        else
            for i=1:1:(obj.lx/(2*obj.hatch_spacing)+1)%npasseslayer
                sc=obj.hatch_spacing;
        
            %Start Square Contour
            
            %Increase x
                x(n)=x(n-1);
                y(n)=obj.ly-obj.hatch_spacing;    
                %Calculate z
                z(n)=(layer)*obj.layer_thickness;
                %Calculate time during layer
                time(n)=(norm([x(n) y(n) z(n)]-[x(n-1) y(n-1) z(n-1)]))/obj.Laser_Speed+time(n-1);
                %Appobj.ly obj.Laser_Power
                p(n)=0;
                n=n+1;
        
            %Increase y
                x(n)=x(n-1)+sc;
                y(n)=obj.ly-obj.hatch_spacing;    
                %Calculate z
                z(n)=(layer)*obj.layer_thickness;
                %Calculate time during layer
                time(n)=(norm([x(n) y(n) z(n)]-[x(n-1) y(n-1) z(n-1)]))/obj.Laser_Speed+time(n-1);
                %Appobj.ly obj.Laser_Power
                p(n)=obj.Laser_Power;
                n=n+1;
        
            %Decrease x
                x(n)=x(n-1);
                y(n)=obj.hatch_spacing;    
                %Calculate z
                z(n)=(layer)*obj.layer_thickness;
                %Calculate time during layer
                time(n)=(norm([x(n) y(n) z(n)]-[x(n-1) y(n-1) z(n-1)]))/obj.Laser_Speed+time(n-1);
                %Appobj.ly obj.Laser_Power
                p(n)=0;
                n=n+1;
        
                if (i <= ((obj.lx-obj.hatch_spacing)/(2*obj.hatch_spacing))) %if it's not the last scan
                %Increase y again
                        x(n)=x(n-1)+sc;
                        y(n)=obj.hatch_spacing;    
                        %Calculate z
                        z(n)=(layer)*obj.layer_thickness;
                        %Calculate time during layer
                        time(n)=(norm([x(n) y(n) z(n)]-[x(n-1) y(n-1) z(n-1)]))/obj.Laser_Speed+time(n-1);
                        %Appobj.ly obj.Laser_Power
                        p(n)=obj.Laser_Power;
                        n=n+1;
                end


                if x(n-1)>obj.lx/2 && flg==0
                    flg=1;

                    obj.time_per_bead = time(n-1)-time(n-3);
                    obj.time_before_mid_bead = time(n-3);

                end
    
            end
        
        end
            %Calculate scan time:
            t_after_scan=time(n-1);
            index_after_scan=n-1;
        
            obj.time_of_scanning(layer)=t_after_scan-t_before_scan;
            obj.indexes_of_scanning(layer)=index_after_scan-index_before_scan;
        
            p(n-1)=0;
            %Appobj.ly rest time after layer, increase z and do first pass of
            %sequent layer
            p(n)=obj.Laser_Power;
            z(n)=z(n-1)+obj.layer_thickness;
            x(n)=obj.hatch_spacing;
            y(n)=obj.hatch_spacing;
            time(n)=time(n-1)+obj.inter_layer_time+obj.dosing_time;
        
            %Move roller to beggining
            xmat(k+1)=0;
            ymat(k+1)=obj.ly/2;
            zmat(k+1)=(layer)*obj.layer_thickness;
            mat(k+1)=0;
            timemat(k+1)=timemat(k)+0.00001;
        
        
            %Move roller up
            xmat(k+2)=0;
            ymat(k+2)=obj.ly/2;
            zmat(k+2)=(layer)*obj.layer_thickness+obj.layer_thickness;
            mat(k+2)=1;
            timemat(k+2)=time(n-1);
            k=k+3;
            
            n=n+1;
        
        end
        
        %plot
        plot3(x,y,z)
        hold on
        plot3(xmat,ymat,zmat)
        % axis equal
        set(gca,'DataAspectRatio',[4 4 1])
        
        xlabel('x')
        ylabel('y')
        zlabel('z')
        
        writematrix( [time(:) x(:) y(:) z(:) p(:)],'Event_series_Heat_mm.csv','Delimiter','comma');
        
        %GENERATE MATERIAL FILE FOR SLM
        
        writematrix( [timemat(:) xmat(:) ymat(:) zmat(:) mat(:)],'Event_series_Roller_mm.csv','Delimiter','comma');
        
        %Change to inps:
        copyfile 'Event_series_Heat_mm.csv' 'Event_series_Heat_mm.inp'
        copyfile 'Event_series_Roller_mm.csv' 'Event_series_Roller_mm.inp'
        
        delete 'Event_series_Heat_mm.csv'
        delete 'Event_series_Roller_mm.csv'
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

        %% Generate scan path for 3D thesis
        % Mode=zeros(1,length(x));
        % Pmod=p./obj.Laser_Power;
        % 
        % 
        % 
        % Mode=Mode(1:indexes_of_scanning(obj.current_layer)).';
        % x=x(1:indexes_of_scanning(obj.current_layer)).';
        % y=y(1:indexes_of_scanning(obj.current_layer)).';
        % z=z(1:indexes_of_scanning(obj.current_layer)).';
        % z=zeros(length(z),1);
        % Pmod=1-Pmod(1:indexes_of_scanning(obj.current_layer)).'; %I changed 0s to 1s for 3Dtehsis convention
        % time=time(1:indexes_of_scanning(obj.current_layer)).';
        % time(:)=obj.Laser_Speed/1000;
        % 
        % time(1)=0.000001;
        % Mode(1)=1;
        % 
        % Thesis3D_output = table(Mode,x,y,z,Pmod,time);
        % Thesis3D_output.Properties.VariableNames([2 3 4 6]) = {'X(mm)' 'Y(mm)' 'Z(mm)' 'Time(s)/obj.Laser_Speed(m/s)'};
        % writetable(Thesis3D_output,'Path.txt','Delimiter','tab')

    end
end