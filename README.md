# Process_Structure_FEA_SLM_w_refinemen

## Introduction

This code solves a thermal model of a powder bed fusion process in Abaqus. It uses layer-wise adaptive mesh refinement to speed up the simulation. It is still a computationally expensive simulation.
It uses a high time resolution only in the layers specified, where temperature will be recorded as history outputs.

## How to run

Run main.m in src folder.

## Configuration
You need a cad file of your geometry that can be read by Abaqus CAE, which must be added to the input folder.
Options are set in input_file.json:

- number_of_refinements -> How many times the mesh is refined from a characteristic length equal to the layer thickness upwards.
- heights_of_interst -> At what height are the temperatures measured.
- high_resolution_only_one_bead -> specify "yes" or "no" if only a single bead is used with high resolution or the whole layer of interest.
- component_geometry_path -> path to cad file which will be read by Abaqus.

## Versions:
- Currently tested on Abaqus 2022

## Known Issues:

- Component height needs to be a multiple of layer height.
- Meshing works better if the domain can be a multiple of the highest element length.

## Disclaimer:

- Not guaranteed to be free of bugs.
