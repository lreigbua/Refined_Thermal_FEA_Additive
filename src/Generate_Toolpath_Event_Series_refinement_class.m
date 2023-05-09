

classdef Generate_Toolpath_Event_Series_refinement_class < handle

properties
    %Use International Units
    %Laser speed (assumed constant)
    % Vel=600;
    Vel=1029;
    %Scan Spacing/ hatch spacing (distance between laser paths in same layer)
    % spa=0.10;
    spa=0.060;
    %length in x of rectangle in mm
    lx=0.96;
    %length in y of rectangle in mm
    ly=0.96;
    %Thickness of each layer
    %tlay=60e-6;
    tlay=0.060;
    %Power
    %Power=120000; %Watts
    Power=375000; %Watts
    %Roller time
    troll=0.2;
    %Time to rest for recoating
    %trest=30.2; 
    trest=1-0.2; %substract troll
    %initial laye
    nlayers;
    layini;

    %layers of interest:
    heights_of_interest=[0.3]

    
    %arrays to measure how long and scanning takes to define appropiate time step lengths      
    time_of_scanning;
    indexes_of_scanning;
end

methods
    function obj = generate_event_series_files(obj)    

        %initial layer
        obj.layini=obj.nlayers;        
    
        timemat(1)=0;
        xmat(1)=0;
        ymat(1)=obj.ly/2;
        zmat(1)=obj.tlay*obj.layini;
        mat(1)=1;
        
        time(1)=obj.troll;
        x(1)=obj.spa;
        y(1)=obj.spa;
        z(1)=obj.tlay*obj.layini;
        p(1)=0;
             
        %%
        % Calculate x and y for each layer
         
        
        n=2;
        k=2;    
        for layer=obj.layini:1:obj.nlayers
            
        
            if layer ~= obj.layini
                timemat(k)=time(n-1)-obj.trest;
            else
                timemat(k)=obj.troll;
            end
            xmat(k)=obj.lx;
            ymat(k)=obj.ly/2;
            zmat(k)=(layer)*obj.tlay;
            mat(k)=0;
            
            t_before_scan=time(n-1);
            index_before_scan=n-1;
        
        
        
        if is_even(layer)
                for i=1:1:(obj.ly/(2*obj.spa)+1)%npasseslayer
                    sc=obj.spa;
          
            %Start Square Contour
            
            %Increase x
                    x(n)=obj.lx-obj.spa;
                    y(n)=y(n-1);    
                    %Calculate z
                    z(n)=(layer)*obj.tlay;
                    %Calculate time during layer
                    time(n)=(norm([x(n) y(n) z(n)]-[x(n-1) y(n-1) z(n-1)]))/obj.Vel+time(n-1);
                    %Appobj.ly obj.Power
                    p(n)=0;
                    n=n+1;
            
                %Increase y
                    x(n)=obj.lx-obj.spa;
                    y(n)=y(n-1)+sc;    
                    %Calculate z
                    z(n)=(layer)*obj.tlay;
                    %Calculate time during layer
                    time(n)=(norm([x(n) y(n) z(n)]-[x(n-1) y(n-1) z(n-1)]))/obj.Vel+time(n-1);
                    %Appobj.ly obj.Power
                    p(n)=obj.Power;
                    n=n+1;
            
                %Decrease x
                    x(n)=obj.spa;
                    y(n)=y(n-1);    
                    %Calculate z
                    z(n)=(layer)*obj.tlay;
                    %Calculate time during layer
                    time(n)=(norm([x(n) y(n) z(n)]-[x(n-1) y(n-1) z(n-1)]))/obj.Vel+time(n-1);
                    %Appobj.ly obj.Power
                    p(n)=0;
                    n=n+1;
                    if (i <= ((obj.ly-obj.spa)/(2*obj.spa))) %if it's not the last scan
                    %Increase y again
                            x(n)=obj.spa;
                            y(n)=y(n-1)+sc;    
                            %Calculate z
                            z(n)=(layer)*obj.tlay;
                            %Calculate time during layer
                            time(n)=(norm([x(n) y(n) z(n)]-[x(n-1) y(n-1) z(n-1)]))/obj.Vel+time(n-1);
                            %Appobj.ly obj.Power
                            p(n)=obj.Power;
                            n=n+1;
                    end
            
            
                end
        else
            for i=1:1:(obj.lx/(2*obj.spa)+1)%npasseslayer
                sc=obj.spa;
        
            %Start Square Contour
            
            %Increase x
                x(n)=x(n-1);
                y(n)=obj.ly-obj.spa;    
                %Calculate z
                z(n)=(layer)*obj.tlay;
                %Calculate time during layer
                time(n)=(norm([x(n) y(n) z(n)]-[x(n-1) y(n-1) z(n-1)]))/obj.Vel+time(n-1);
                %Appobj.ly obj.Power
                p(n)=0;
                n=n+1;
        
            %Increase y
                x(n)=x(n-1)+sc;
                y(n)=obj.ly-obj.spa;    
                %Calculate z
                z(n)=(layer)*obj.tlay;
                %Calculate time during layer
                time(n)=(norm([x(n) y(n) z(n)]-[x(n-1) y(n-1) z(n-1)]))/obj.Vel+time(n-1);
                %Appobj.ly obj.Power
                p(n)=obj.Power;
                n=n+1;
        
            %Decrease x
                x(n)=x(n-1);
                y(n)=obj.spa;    
                %Calculate z
                z(n)=(layer)*obj.tlay;
                %Calculate time during layer
                time(n)=(norm([x(n) y(n) z(n)]-[x(n-1) y(n-1) z(n-1)]))/obj.Vel+time(n-1);
                %Appobj.ly obj.Power
                p(n)=0;
                n=n+1;
        
                if (i <= ((obj.lx-obj.spa)/(2*obj.spa))) %if it's not the last scan
                %Increase y again
                        x(n)=x(n-1)+sc;
                        y(n)=obj.spa;    
                        %Calculate z
                        z(n)=(layer)*obj.tlay;
                        %Calculate time during layer
                        time(n)=(norm([x(n) y(n) z(n)]-[x(n-1) y(n-1) z(n-1)]))/obj.Vel+time(n-1);
                        %Appobj.ly obj.Power
                        p(n)=obj.Power;
                        n=n+1;
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
            p(n)=obj.Power;
            z(n)=z(n-1)+obj.tlay;
            x(n)=obj.spa;
            y(n)=obj.spa;
            time(n)=time(n-1)+obj.trest+obj.troll;
        
            %Move roller to beggining
            xmat(k+1)=0;
            ymat(k+1)=obj.ly/2;
            zmat(k+1)=(layer)*obj.tlay;
            mat(k+1)=0;
            timemat(k+1)=timemat(k)+0.00001;
        
        
            %Move roller up
            xmat(k+2)=0;
            ymat(k+2)=obj.ly/2;
            zmat(k+2)=(layer)*obj.tlay+obj.tlay;
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
        '*Restart, write, frequency=1\n'...
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
        freq=', number interval=2';  % number of times field is output in this step
        freq_scan=', number interval=50';
        %%
%         calculate what layers are of interest based on heights of interest
        for i=1:1:length(obj.heights_of_interest)
            top_height=obj.heights_of_interest(i);
            while (round(rem(top_height,obj.tlay),2)~=round(0,2))
                top_height=top_height+0.001;
            end
            layers_of_interest(i)=round(top_height,2)/obj.tlay;
        end
        
        HO_text=[
        '** HISTORY OUTPUT: H-Output-%i\n'...
        '**\n' ...
        '*Output, history\n'...
        '*Element Output, elset=SET-HO-layer-%i\n'...
        'TEMP, SDV\n' ...
        ];
        
        HO_all='';
        for i=1:1:length(layers_of_interest)
            if round(obj.layini)>=layers_of_interest(i) %this if is to request only history outputs of layers than have been printed
                HO_all=append(HO_all,sprintf(HO_text,layers_of_interest(i),layers_of_interest(i)));
            end
        end
        %
        
        stepN=1;
        for i=obj.layini:1:obj.nlayers
            
            if ismember(i,layers_of_interest)
        %     tscan=timemat(4)-timemat(2);
            tscan=obj.time_of_scanning(i);
            
            %prints rolling step
            fprintf(fileID,text,stepN,stepN,obj.troll/4, obj.troll, obj.troll/4, freq,HO_all);
            %prints scanning step
            fprintf(fileID,text,stepN+1,stepN+1,0.001, tscan, 0.001,freq_scan,HO_all);
            %prints short increment cooling step
            fprintf(fileID,text,stepN+2,stepN+2,0.001, 0.2, 0.001,freq_scan,HO_all);
            %prints resting step
            fprintf(fileID,text,stepN+3,stepN+3,1.0, obj.trest, 1.0, freq,HO_all);
            stepN=stepN+3;
            
            else
            tscan=obj.time_of_scanning(i);
            
            %prints rolling step
            fprintf(fileID,text,stepN,stepN,obj.troll/4, obj.troll, obj.troll/4, freq, HO_all);
            %prints scanning step
            fprintf(fileID,text,stepN+1,stepN+1,tscan/4, tscan, tscan/4, freq, HO_all);
            %prints short increment cooling step
            fprintf(fileID,text,stepN+2,stepN+2, 0.2, 0.2, 0.2, freq, HO_all);
            %prints resting step
            fprintf(fileID,text,stepN+3,stepN+3,1.0, obj.trest, 1.0, freq, HO_all);
            stepN=stepN+3;
            
            end
        
        end
        
%         %Add final, long cooling step
%         text_cooling_step=['** ----------------------------------------------------------------\n'...
%         '*STEP, name=Cooling, INC=10000\n'...
%         '*HEAT TRANSFER\n'...
%         '1.,60., ,\n'...
%         '**\n'...
%         '** OUTPUT REQUESTS\n'...
%         '**\n'...
%         '*Restart, write, frequency=0\n'...
%         '**\n'...
%         '** FIELD OUTPUT: F-Output-2\n'...
%         '**\n'...
%         '*OUTPUT,FIELD, number interval=10\n'...
%         '*Element Output, directions=YES\n'...
%         'SDV\n'...
%         '**\n'...
%         '** FIELD OUTPUT: F-Output-1\n'...
%         '**\n'...
%         '*Node Output\n'...
%         'NT\n'...
%         '%s'...
%         '*Activate elements, activation=ElementProgressiveActivation1, expansion time constant=2.\n'...
%         '"ABQ_AM.Material Input"\n'...
%         '*END STEP\n'];
%         
%         fprintf(fileID, text_cooling_step, HO_all);
        
        
        
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
        % Pmod=p./obj.Power;
        % 
        % 
        % 
        % Mode=Mode(1:indexes_of_scanning(obj.layini)).';
        % x=x(1:indexes_of_scanning(obj.layini)).';
        % y=y(1:indexes_of_scanning(obj.layini)).';
        % z=z(1:indexes_of_scanning(obj.layini)).';
        % z=zeros(length(z),1);
        % Pmod=1-Pmod(1:indexes_of_scanning(obj.layini)).'; %I changed 0s to 1s for 3Dtehsis convention
        % time=time(1:indexes_of_scanning(obj.layini)).';
        % time(:)=obj.Vel/1000;
        % 
        % time(1)=0.000001;
        % Mode(1)=1;
        % 
        % Thesis3D_output = table(Mode,x,y,z,Pmod,time);
        % Thesis3D_output.Properties.VariableNames([2 3 4 6]) = {'X(mm)' 'Y(mm)' 'Z(mm)' 'Time(s)/obj.Vel(m/s)'};
        % writetable(Thesis3D_output,'Path.txt','Delimiter','tab')

    end
end