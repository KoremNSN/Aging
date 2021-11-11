#!/bin/bash
#SBATCH --partition=general
#SBATCH -J Aging_run4
#SBATCH --output=Aging_ses-1.txt
#SBATCH --error=Aging_ses-1.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=12
#SBATCH --mem-per-cpu=8G
#SBATCH -t 16:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=nachshon.korem@yale.edu


echo "Running script"

module load miniconda
module load FSL

source activate aging

. /gpfs/ysm/apps/software/FSL/6.0.4-centos7_64/etc/fslconf/fsl.sh

python /home/nk549/Documents/Aging/fsl_first_level.py >> log8.txt
