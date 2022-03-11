#!/bin/bash
#SBATCH --partition=general
#SBATCH -J spm
#SBATCH --output=spm_test.txt
#SBATCH --error=spm_test.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=4G
#SBATCH -t 2:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=nachshon.korem@yale.edu


echo "Running script"

module load miniconda
module load FSL
module load MATLAB/2021b

source activate aging

. /gpfs/ysm/apps/software/FSL/6.0.4-centos7_64/etc/fslconf/fsl.sh

python /home/nk549/Documents/Aging/RewardandPunishment/SPM_first_level.py > spmlog.log