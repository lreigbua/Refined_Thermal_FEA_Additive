# Adaptive thermal FEA model of LPBF

## Introduction

This library allows to calculate high resolution thermal histories during powder bed fusion processes with Abaqus. It uses layer-wise adaptive mesh refinement to speed up the simulation. Since it is still a computationally expensive simulation, it uses a high time resolution only around the points specified, where temperature will be recorded as history outputs.

<img src="https://github.com/lreigbua/Process_Structure_FEA_SLM_w_refinement/assets/93150422/c12be3a9-2974-4319-aa18-f156adb31724" width="300" align="center">
<img src="https://github.com/lreigbua/Process_Structure_FEA_SLM_w_refinement/assets/93150422/fc1ceabc-31f1-445b-ba11-ef01afd27e2b" width="500" align="center">

Scanpath can be read from Renishaw AM CAM file for exact representation:
<img src="https://github.com/lreigbua/Process_Structure_FEA_SLM_w_refinement/assets/93150422/e1dc1768-931a-45fd-93ef-78fa8d7ffe4f" width="750" align="center">

## Layer-wise Adaptive Meshing

The mesh is modified every time a layer is printed to keep a high resolution only near the layer being scanned. A steep change in element size is achieved through tie constraints.

![image](https://github.com/user-attachments/assets/3b2c25e8-f470-4b45-b770-720e716ce1cb)
![Adaptive_Mesh](https://github.com/lreigbua/Process_Structure_FEA_SLM_w_refinement/assets/93150422/401ebba0-85db-4618-8f64-6ca9010424e8)

## Adaptive time incrementations

High resolution thermal histories are only calculated at points specified by the user. An imaginary sphere of interest is created around these points, and when the laser is scanning inside it the time incrementation is reduced. This speeds up the simulation significantly.

![image](https://github.com/user-attachments/assets/c265f90a-cf37-43fa-97ee-8aaef692109f)
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
# Download repository and build the library
git clone https://github.com/lreigbua/Refined_Thermal_FEA_Additive.git
cd Refined_Thermal_FEA_Additive
pip install -e .

#Go to example folder
cd examples/cube_1mm

#Run python script
python run_1mm_cube.py
```

The output files are generated in an output folder in this directory. This will contain the Abaqus simulation files and post-processing outputs.

## Inputs
The library is used by importing the module and creating an object with Refined_Thermal_FEA_Additive_class that reads an input json file.

```python
# import Simulation class
from Refined_Thermal_FEA_Additive import Refined_Thermal_FEA_Additive_class

#Create simulation object, which reads the input json file
Simulation = Refined_Thermal_FEA_Additive_class("./inputs/1mm_cube.json")
```

The json file includes the configuration parameters of the simulation.
Besides the json input file, a CAD model of the component to be simulated and a rensishaw's mtt file with the scanpath are needed, which must be specified in the json input file.

Options in input json file:

- number_of_refinements -> How many times the mesh is refined from a characteristic length equal to the layer thickness upwards.
- heights_of_interst -> At what height are the temperatures measured.
- high_resolution_only_one_bead -> specify "yes" or "no" if only a single bead is used with high resolution or the whole layer of interest.
- component_geometry_path -> path to cad file which will be read by Abaqus.
- output_folder_name -> name of folder where the simulation data will be saved.

## Post-Processing

Videos of the simulation field outputs and temperature history outpyts at the point of interest can be automatically generated. See examples. Post-processing can take time.

## Citation & Documentation

If you use this code in your research, please cite the foundational doctoral thesis. The full text also serves as the primary documentation for this repository, containing comprehensive details on the computational model's theoretical background, architecture, and validation.

**DOI:** [10.48730/pkpm-t966](https://doi.org/10.48730/pkpm-t966)

```bibtex
@phdthesis{reigbuades2026,
  author       = {Reig Buades, Luis Miguel},
  title        = {An integrated process-structure-property-performance modelling framework for additive layer manufacturing of Ti-6Al-4V},
  school       = {University of Strathclyde},
  year         = {2026},
  doi          = {10.48730/pkpm-t966},
  url          = {[https://doi.org/10.48730/pkpm-t966](https://doi.org/10.48730/pkpm-t966)}
}
```
