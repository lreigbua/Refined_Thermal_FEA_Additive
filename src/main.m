clc
close all
clear variables

%change directory to output folder
current_script_Path = matlab.desktop.editor.getActiveFilename;
folder_of_current_script_Path = current_script_Path(1:end-6);
cd(folder_of_current_script_Path);
addpath(folder_of_current_script_Path);
cd ../input/

input_file_struct = read_input_file();
mkdir("../"+input_file_struct.output_folder_name)
cd("../"+input_file_struct.output_folder_name)

%% Run Python Script to generate refined meshes for all layers:
system('abaqus cae noGUI=../src/Set_up_adaptive_mesh_refinement.py')


%% Run Abaqus Jobs
copyfile ../src/INP_default.inp ./INP.txt

data_file_struct = read_data_file();
total_number_of_layers=data_file_struct.total_number_of_layers;
Process_Generate_toolpath_and_steps = Generate_Toolpath_Event_Series_refinement_class();
Process_Generate_toolpath_and_steps.read_input_file()

% for current_layer=1:1:2
for current_layer=1:1:total_number_of_layers
    delete *.lck
    Process_Generate_toolpath_and_steps.current_layer=current_layer;
    Process_Generate_toolpath_and_steps.run();
    Create_Assembly_INP("layer-"+Process_Generate_toolpath_and_steps.nlayers+".inp")
    

    current_layer_job_name="Job-layer-"+current_layer;

    if current_layer==1
        copyfile ('./INP.txt',current_layer_job_name+".inp")
    else
        add_mapping(current_layer)
        copyfile ('INP_w_mapping.inp',current_layer_job_name+".inp")
    end
    
    command = "abaqus job="+ current_layer_job_name + " cpus=16 user=../src/HETVAL-alpha-thick.f ask_delete=OFF interactive";
    status = system(command)  %Run Abaqus Job in cmd

end

function data_file_struct = read_data_file()
%Calculates total number of layers using data from updated json file
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
        
        component_dimensions = cellfun(@double,cell(struct_output.component_dimensions));
        data_file_struct.total_number_of_layers = component_dimensions(3)/struct_output.layer_thickness;

end

function input_file_struct = read_input_file()
%Calculates total number of layers using data from updated json file
    code=[
            "import json"
            "with open('.\input_file.json', 'r') as myfile:"
            "    data=myfile.read()"
            "obj = json.loads(data)"
            "out=obj"
        ];

        %transform python dict to matlab struct
        dict_output = pyrun(code,'out');
        struct_output = struct(dict_output);
        
        input_file_struct.output_folder_name = string(struct_output.output_folder_name);

end