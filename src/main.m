clc
close all
clear variables

cd D:\mkb21147\Abaqus\Macro_Models\Process_Structure_FEA_SLM_w_refinement\Process_Structure_FEA_SLM_w_refinement\data


%Run Python Script to generate refined meshes for all layers:
system('abaqus cae noGUI=../src/Set_up_adaptive_mesh_refinement.py')
total_number_of_layers=2;

% for current_layer=1:1:total_number_of_layers
for current_layer=1:1:2
    delete *.lck
    Process_Generate_toolpath_and_steps = Generate_Toolpath_Event_Series_refinement_class();
    Process_Generate_toolpath_and_steps.read_input_file()
    Process_Generate_toolpath_and_steps.current_layer=current_layer;
    Process_Generate_toolpath_and_steps.run();
    Create_Assembly_INP("layer-"+Process_Generate_toolpath_and_steps.nlayers+".inp")
    

    current_layer_job_name="Job-layer-"+current_layer;
    previous_layer_job_name="Job-layer-"+(current_layer-1);
    if current_layer==1
        copyfile ('INP_default_first_layer.inp',current_layer_job_name+".inp")
        command = "abaqus job="+ current_layer_job_name + " ask_delete=OFF interactive";
        status = system(command)
    % else if (last_layer)
    %     status = system('abaqus job=INP_default_last_layer ask_delete=OFF interactive')
    else
        copyfile ('INP_default_second_layer.inp',current_layer_job_name+".inp")
        command = "abaqus job=" + current_layer_job_name + " oldjob=" + previous_layer_job_name + " ask_delete=OFF interactive";
        status = system(command)
    end

end