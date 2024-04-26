# Adaptive thermal FEA model of LPBF

## Introduction

This code solves a thermal model of a powder bed fusion process in Abaqus. It uses layer-wise adaptive mesh refinement to speed up the simulation. Since it is still a computationally expensive simulation,
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

## How to run

```bash
git clone
```

## Configuration
You need a cad file of your geometry that can be read by Abaqus CAE, which must be added to the input folder.
Options are set in input_file.json:

- number_of_refinements -> How many times the mesh is refined from a characteristic length equal to the layer thickness upwards.
- heights_of_interst -> At what height are the temperatures measured.
- high_resolution_only_one_bead -> specify "yes" or "no" if only a single bead is used with high resolution or the whole layer of interest.
- component_geometry_path -> path to cad file which will be read by Abaqus.
- output_folder_name -> name of folder where the simulation data will be saved.

## Post-Processing

Post processing can take time

- Generate_animation_files_for_each_job.py creates a video of each layer. In order to correct the zoom you may need to modify this.
- Generate_Video_of_Simulation.py puts the video of each layer together.
- read_history_output.py reads the temperature history recorded in each layer of interest and saves them to text files.
- plot_history_output.mlx can be used to plot the history outputs

## Known Issues:

- Component height needs to be a multiple of layer height.
- Meshing works better if the domain can be a multiple of the highest element length.

## Disclaimer:

- Not guaranteed to be free of bugs.
