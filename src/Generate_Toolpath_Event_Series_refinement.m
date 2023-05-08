
%Use International Units

%Laser speed (assumed constant)
% Vel=600;
Vel=1029;
%Scan Spacing/ hatch spacing (distance between laser paths in same layer)
% spa=0.10;
spa=0.030;
%length in x of rectangle in mm
lx=0.6;
%length in y of rectangle in mm
ly=0.12;
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
trest=1-troll; %substract troll
%initial layer
layini=7;

%Number of Layers
% nlayers=5.04/0.06;
nlayers=8;
% nlayers_high_res=layini+1;
% nlayers_low_res=nlayers_high_res+64;

%layers of interest:
% heights_of_interest=readmatrix("layers_of_interest.csv");


%tpass=lx/Vel;
%npasseslayer=lx/2/spa;

timemat(1)=0;
xmat(1)=0;
ymat(1)=ly/2;
zmat(1)=tlay*layini;
mat(1)=1;

time(1)=troll;
x(1)=spa;
y(1)=spa;
z(1)=tlay;
p(1)=Power;


%%
% Calculate x and y for each layer
 

n=2;
k=2;    
for layer=layini:1:nlayers
    

    if layer ~= layini
        timemat(k)=time(n-1)-trest;
    else
        timemat(k)=troll;
    end
    xmat(k)=lx;
    ymat(k)=ly/2;
    zmat(k)=(layer)*tlay;
    mat(k)=0;
    
    t_before_scan=time(n-1);
    index_before_scan=n-1;



if is_even(layer)
        for i=1:1:(ly/(2*spa)+1)%npasseslayer
            sc=spa;
  
    %Start Square Contour
    
    %Increase x
            x(n)=lx-spa;
            y(n)=y(n-1);    
            %Calculate z
            z(n)=(layer)*tlay;
            %Calculate time during layer
            time(n)=(norm([x(n) y(n) z(n)]-[x(n-1) y(n-1) z(n-1)]))/Vel+time(n-1);
            %Apply Power
            p(n)=0;
            n=n+1;
    
        %Increase y
            x(n)=lx-spa;
            y(n)=y(n-1)+sc;    
            %Calculate z
            z(n)=(layer)*tlay;
            %Calculate time during layer
            time(n)=(norm([x(n) y(n) z(n)]-[x(n-1) y(n-1) z(n-1)]))/Vel+time(n-1);
            %Apply Power
            p(n)=Power;
            n=n+1;
    
        %Decrease x
            x(n)=spa;
            y(n)=y(n-1);    
            %Calculate z
            z(n)=(layer)*tlay;
            %Calculate time during layer
            time(n)=(norm([x(n) y(n) z(n)]-[x(n-1) y(n-1) z(n-1)]))/Vel+time(n-1);
            %Apply Power
            p(n)=0;
            n=n+1;
            if (i <= ((ly-spa)/(2*spa))) %if it's not the last scan
            %Increase y again
                    x(n)=spa;
                    y(n)=y(n-1)+sc;    
                    %Calculate z
                    z(n)=(layer)*tlay;
                    %Calculate time during layer
                    time(n)=(norm([x(n) y(n) z(n)]-[x(n-1) y(n-1) z(n-1)]))/Vel+time(n-1);
                    %Apply Power
                    p(n)=Power;
                    n=n+1;
            end
    
    
        end
else
    for i=1:1:(lx/(2*spa)+1)%npasseslayer
        sc=spa;

    %Start Square Contour
    
    %Increase x
        x(n)=x(n-1);
        y(n)=ly-spa;    
        %Calculate z
        z(n)=(layer)*tlay;
        %Calculate time during layer
        time(n)=(norm([x(n) y(n) z(n)]-[x(n-1) y(n-1) z(n-1)]))/Vel+time(n-1);
        %Apply Power
        p(n)=0;
        n=n+1;

    %Increase y
        x(n)=x(n-1)+sc;
        y(n)=ly-spa;    
        %Calculate z
        z(n)=(layer)*tlay;
        %Calculate time during layer
        time(n)=(norm([x(n) y(n) z(n)]-[x(n-1) y(n-1) z(n-1)]))/Vel+time(n-1);
        %Apply Power
        p(n)=Power;
        n=n+1;

    %Decrease x
        x(n)=x(n-1);
        y(n)=spa;    
        %Calculate z
        z(n)=(layer)*tlay;
        %Calculate time during layer
        time(n)=(norm([x(n) y(n) z(n)]-[x(n-1) y(n-1) z(n-1)]))/Vel+time(n-1);
        %Apply Power
        p(n)=0;
        n=n+1;

        if (i <= ((lx-spa)/(2*spa))) %if it's not the last scan
        %Increase y again
                x(n)=x(n-1)+sc;
                y(n)=spa;    
                %Calculate z
                z(n)=(layer)*tlay;
                %Calculate time during layer
                time(n)=(norm([x(n) y(n) z(n)]-[x(n-1) y(n-1) z(n-1)]))/Vel+time(n-1);
                %Apply Power
                p(n)=Power;
                n=n+1;
        end


    end

end
    %Calculate scan time:
    t_after_scan=time(n-1);
    index_after_scan=n-1;

    time_of_scanning(layer)=t_after_scan-t_before_scan;
    indexes_of_scanning(layer)=index_after_scan-index_before_scan;

    p(n-1)=0;
    %Apply rest time after layer, increase z and do first pass of
    %sequent layer
    p(n)=Power;
    z(n)=z(n-1)+tlay;
    x(n)=spa;
    y(n)=spa;
    time(n)=time(n-1)+trest+troll;

    %Move roller to beggining
    xmat(k+1)=0;
    ymat(k+1)=ly/2;
    zmat(k+1)=(layer)*tlay;
    mat(k+1)=0;
    timemat(k+1)=timemat(k)+0.00001;


    %Move roller up
    xmat(k+2)=0;
    ymat(k+2)=ly/2;
    zmat(k+2)=(layer)*tlay+tlay;
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


%Generate STEPs INP

text=['** ----------------------------------------------------------------\n'...
'**\n'... 
'** STEP: S-%i\n'...
'**\n'... 
'*Step, name=S-%i,EXTRAPOLATION=NO, INC=100000000, UNSYMM=YES\n'...
'*Heat Transfer, end=PERIOD, deltmx=1000000.\n'...
'%f, %f, 0.0001, %f,\n'...
'**\n'...
'** OUTPUT REQUESTS\n'...
'**\n'... 
'*Restart, write, frequency=0\n'...
'**\n'...
'** FIELD OUTPUT: F-Output-2\n'...
'**\n'...
'*Output, field%s\n'...
'*Element Output, directions=YES\n'...
'SDV, GRADT\n'...
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
% calculate what layers are of interest based on heights of interest
% for i=1:1:length(heights_of_interest)
%     top_height=heights_of_interest(i);
%     while (round(rem(top_height,tlay),2)~=round(0,2))
%         top_height=top_height+0.001;
%     end
%     layers_of_interest(i)=round(top_height,2)/tlay;
% end
% 
% HO_text=[
% '** HISTORY OUTPUT: H-Output-%i\n'...
% '**\n' ...
% '*Output, history\n'...
% '*Element Output, elset=SET-HO-layer-%i\n'...
% 'TEMP, GRADT, SDV\n' ...
% ];
% 
HO_all='';
% for i=1:1:length(layers_of_interest)
%     HO_all=append(HO_all,sprintf(HO_text,layers_of_interest(i),layers_of_interest(i)));
% end
%%

stepN=2;
for i=layini:1:nlayers
    
%     if ismember(i,layers_of_interest)
% %     tscan=timemat(4)-timemat(2);
%     tscan=time_of_scanning(i);
% 
%     %prints scanning step
%     fprintf(fileID,text,stepN,stepN,0.001, tscan, 0.001,freq_scan,HO_all);
%     %prints rolling step
%     fprintf(fileID,text,stepN+1,stepN+1,0.001, troll, 0.001, freq,HO_all);
%     %prints resting step
%     fprintf(fileID,text,stepN+2,stepN+2,1.0, trest, 1.0, freq,HO_all);
%     stepN=stepN+3;
%     
%     else
    
%     tscan=timemat(4)-timemat(2);
    tscan=time_of_scanning(i)

    %prints scanning step
    fprintf(fileID,text,stepN,stepN,tscan/4, tscan, tscan/4, freq, HO_all);
    %prints rolling step
    fprintf(fileID,text,stepN+1,stepN+1,troll/4, troll, troll/4, freq, HO_all);
    %prints resting step
    fprintf(fileID,text,stepN+2,stepN+2,1.0, trest, 1.0, freq, HO_all);
    stepN=stepN+3;
    
%     end

end

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



status = system('copy Steps.txt   Steps.inp')

fclose(fileID);
delete Steps.txt



% %% Generate scan path for 3D thesis
% Mode=zeros(1,length(x));
% Pmod=p./Power;
% 
% 
% 
% Mode=Mode(1:indexes_of_scanning(layini)).';
% x=x(1:indexes_of_scanning(layini)).';
% y=y(1:indexes_of_scanning(layini)).';
% z=z(1:indexes_of_scanning(layini)).';
% z=zeros(length(z),1);
% Pmod=1-Pmod(1:indexes_of_scanning(layini)).'; %I changed 0s to 1s for 3Dtehsis convention
% time=time(1:indexes_of_scanning(layini)).';
% time(:)=Vel/1000;
% 
% time(1)=0.000001;
% Mode(1)=1;
% 
% Thesis3D_output = table(Mode,x,y,z,Pmod,time);
% Thesis3D_output.Properties.VariableNames([2 3 4 6]) = {'X(mm)' 'Y(mm)' 'Z(mm)' 'Time(s)/Vel(m/s)'};
% writetable(Thesis3D_output,'Path.txt','Delimiter','tab')

function [is_even] = is_even(x)
%UNTITLED Summary of this function goes here
%   Detailed explanation goes here
    is_even = 0 == rem(x,2);
end

