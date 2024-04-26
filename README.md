# Adaptive thermal FEA model of LPBF

## Introduction

This library allows to solve thermal models of powder bed fusion processes in Abaqus. It uses layer-wise adaptive mesh refinement to speed up the simulation. Since it is still a computationally expensive simulation,
it uses a high time resolution only in the layers specified, where temperature will be recorded as history outputs.

<img src="https://github.com/lreigbua/Process_Structure_FEA_SLM_w_refinement/assets/93150422/c12be3a9-2974-4319-aa18-f156adb31724" width="300" align="center">
<img src="https://github.com/lreigbua/Process_Structure_FEA_SLM_w_refinement/assets/93150422/fc1ceabc-31f1-445b-ba11-ef01afd27e2b" width="500" align="center">
<img src="https://github.com/lreigbua/Process_Structure_FEA_SLM_w_refinement/assets/93150422/e1dc1768-931a-45fd-93ef-78fa8d7ffe4f" width="750" align="center">

## Layer-wise Adaptive Meshing

The mesh is modified every time a layer is printed to keep a high resolution only near the layer being scanned. A steep change in element size is achieved through tie constraints.

![Adaptive_Mesh](https://github.com/lreigbua/Process_Structure_FEA_SLM_w_refinement/assets/93150422/401ebba0-85db-4618-8f64-6ca9010424e8)

## Adaptive time incrementations

High resolution thermal histories are only calculated at points specified by the user. An imaginary sphere of interest is created around these points, and when the laser is scanning inside it the time incrementation is reduced. This speeds up the simulation significantly.

![Adaptive_time](https://github.com/lreigbua/Process_Structure_FEA_SLM_w_refinement/assets/93150422/0d3b199f-417d-4e58-a81b-7d8556d441a7)

## Dependencies

- Abaqus (tested on 2020 only)
- Numpy
- scikit-spatial

Optional:
- Pyslm with mtt translator for translating Rensishaw's mtt laser scanpath file (https://github.com/drlukeparry/libSLM)
- moviepy to generate videos of simulation

## How to run examples

```bash
# Download repository
git clone https://github.com/lreigbua/Refined_Thermal_FEA_Additive.git

#Go to example folder
cd Refined_Thermal_FEA_Additive/examples/cube_1mm

#Run python script
python run_1mm_cube.py
```

The output files are generated in an output folder in this directory. This will contain the Abaqus simulation files and post-processing outputs.

## Configuration
You need a cad file of your geometry that can be read by Abaqus CAE, which must be added to the input folder.
Options are set in a json input file:

- number_of_refinements -> How many times the mesh is refined from a characteristic length equal to the layer thickness upwards.
- heights_of_interst -> At what height are the temperatures measured.
- high_resolution_only_one_bead -> specify "yes" or "no" if only a single bead is used with high resolution or the whole layer of interest.
- component_geometry_path -> path to cad file which will be read by Abaqus.
- output_folder_name -> name of folder where the simulation data will be saved.

## Post-Processing

Post processing can take time, at the moment, videos of the simulation field outputs and temperature histories at the point of interest can be automatically generated. See examples.

## Disclaimer:

- Not guaranteed to be free of bugs.
