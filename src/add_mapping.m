function add_mapping(layer)

%This function activates an initial condition reading the previous layer's
%odb
    previous_layer=layer-1;
    fid  = fopen('INP.txt','r');
    f=fread(fid);
    fclose(fid);
    f = strrep(f,"***Initial Conditions, type=TEMPERATURE, file=.\Job-layer-2.odb, INTERPOLATE","*Initial Conditions, type=TEMPERATURE, file=.\Job-layer-"+previous_layer+".odb, INTERPOLATE");
    fid  = fopen('INP_w_mapping.inp','w');
    fprintf(fid,'%s',f);
    fclose(fid);

end

