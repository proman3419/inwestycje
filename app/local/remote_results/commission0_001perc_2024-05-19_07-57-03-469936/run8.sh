#!/bin/bash
#SBATCH --job-name=inwestycje_commission0_001perc
#SBATCH --time=12:00:00
#SBATCH --account=plgwtdydoptym-cpu
#SBATCH --partition=plgrid
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=12
#SBATCH --output="joblog_commission0_001perc.txt"
#SBATCH --error="joberr_commission0_001perc.txt"

module load python/3.9.6
module load poetry/1.5.1-gcccore-12.3.0
srun poetry install
srun poetry run python run_cmaes.py --LAMBDA=50 --SIGMA=1000 --N_RESTARTS=10000 --MAX_N_GENERATIONS=20000 --COMMISSION=0.001 --STORAGE_DIRNAME_BASE='commission0_001perc' --DATASET='data/pkn_d.csv'
