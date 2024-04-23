#!/bin/bash

#======================================================
#
# Job script for running ABAQUS on multiple cores (shared)
#
#======================================================

#======================================================
# Propogate environment variables to the compute node
#SBATCH --export=ALL
#
# Run in the standard partition (queue)
#SBATCH --partition=standard
#
# Specify project account
#SBATCH --account=rahimi-omp
#
# No. of tasks required (max of 40), all cores on the same node
#SBATCH --ntasks=$$number_of_tasks --nodes=1
#
# Specify (hard) runtime (HH:MM:SS)
#SBATCH --time=03:00:00
#
# Job name
#SBATCH --job-name=abaqus_test
#
# Output file
#SBATCH --output=slurm-%j.out
#======================================================

module purge
module load abaqus/2020
unset SLURM_GTIDS

#======================================================
# Prologue script to record job details
# Do not change the line below
#======================================================
/opt/software/scripts/job_prologue.sh 
#------------------------------------------------------


abaqus job=INP cpus=$SLURM_NTASKS mp_mode=threads interactive

#======================================================
# Epilogue script to record job endtime and runtime
# Do not change the line below
#======================================================
/opt/software/scripts/job_epilogue.sh
#------------------------------------------------------
