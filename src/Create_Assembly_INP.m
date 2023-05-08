function Create_Assembly_INP(initial_INP)
    
    str = fileread(initial_INP); 
    pos = strfind(str, "*End Assembly");
    str( pos-2 : end) = [];
    fid = fopen( 'current-layer-Assembly.inp', 'w' );     %This code deletes everything after *End Assembly
    fprintf( fid, '%s', str );
    fclose( fid );

end

