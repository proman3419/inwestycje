#!/bin/bash
#SBATCH --job-name=inwestycje_sigma10000
#SBATCH --time=02:00:00
#SBATCH --account=plgwtdydoptym-cpu
#SBATCH --partition=plgrid
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=12
#SBATCH --output="joblog_sigma10000.txt"
#SBATCH --error="joberr_sigma10000.txt"

module load python/3.9.6
module load poetry/1.5.1-gcccore-12.3.0
srun poetry install
srun poetry run python run_cmaes.py --SIGMA=10000 --STORAGE_DIRNAME_BASE='sigma10000'
