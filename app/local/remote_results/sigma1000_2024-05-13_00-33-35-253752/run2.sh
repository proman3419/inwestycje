#!/bin/bash
#SBATCH --job-name=inwestycje_sigma1000
#SBATCH --time=02:00:00
#SBATCH --account=plgwtdydoptym-cpu
#SBATCH --partition=plgrid
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=12
#SBATCH --error="joberr_sigma1000.txt"

module load python/3.9.6
module load poetry/1.5.1-gcccore-12.3.0
srun poetry install
srun poetry run python run_cmaes.py --SIGMA=1000 --STORAGE_DIRNAME_BASE='sigma1000'
