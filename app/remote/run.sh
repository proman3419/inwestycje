#!/bin/bash
#SBATCH --job-name=inwestycje
#SBATCH --time=00:02:00
#SBATCH --account=plgwtdydoptym-cpu
#SBATCH --partition=plgrid
#SBATCH --ntasks=48
#SBATCH --cpus-per-task=1
#SBATCH --output="joblog.txt"
#SBATCH --error="joberr.txt"

module load python/3.9.6
module load poetry/1.5.1-gcccore-12.3.0
srun poetry install
srun poetry run python run_cmaes.py
