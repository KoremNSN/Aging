#!/bin/bash
#
#SBATCH --j Aging_fp_21_3
#SBATCH --array=1 # Replace indices with the right number of subjects
#SBATCH --time=48:00:00
#SBATCH -n 1
#SBATCH --cpus-per-task=4
#SBATCH --mem-per-cpu=8G
# Outputs ----------------------------------
#SBATCH -o %x-%A-%a.out
#SBATCH -e %x-%A-%a.err
#SBATCH --mail-user=nachshon.korem@yale.edu # replace with your email
#SBATCH --mail-type=ALL
# ------------------------------------------



#SUBJ=(sub-13 sub-18 sub-25 sub-36 sub-41 sub-50 sub-58 sub-66 sub-14 sub-19 
#      sub-26 sub-37 sub-42 sub-51 sub-60 sub-15 sub-20 sub-27 sub-38 sub-43 
#      sub-55 sub-61 sub-10 sub-16 sub-23 sub-30 sub-39 sub-44 sub-56 sub-62 
#      sub-11 sub-17 sub-24 sub-32 sub-40 sub-46 sub-57 sub-64 sub-55 sub-56 
#      sub-58 sub-60 sub-57 sub-61 sub-62 sub-64 sub-66)

SUBJ=(sub-64)

BASE_DIR="/gpfs/gibbs/pi/levy_ifat/Nachshon/Aging"
BIDS_DIR="/gpfs/gibbs/pi/levy_ifat/Nachshon/Aging/Aging_Bids" # change directory
DERIVS_DIR="derivatives" # the end point folder for fmriprep (should be in derivatives so don't touch unless you're know what yoou're doing)
WORK_DIR="/home/nk549/scratch60/work" # enter working directory here

mkdir -p $HOME/.cache/templateflow
mkdir -p ${BIDS_DIR}/${DERIVS_DIR}
mkdir -p ${BIDS_DIR}/${DERIVS_DIR}/freesurfer-6.0.1
ln -s    ${BIDS_DIR}/${DERIVS_DIR}/freesurfer-6.0.1 ${BIDS_DIR}/${DERIVS_DIR}/freesurfer

export SINGULARITYENV_FS_LICENSE=$HOME/pipeline/licenseFreeSurfer.txt # freesurfer license file
export SINGULARITYENV_TEMPLATEFLOW_HOME="/templateflow"

SINGULARITY_CMD="singularity run --cleanenv -B $HOME/.cache/templateflow:/templateflow -B ${WORK_DIR}:/work /gpfs/gibbs/pi/levy_ifat/shared/fmriPrep/fmriprep-21.0.1.simg"


echo Starting ${SUBJ[$SLURM_ARRAY_TASK_ID-1]}

cmd="${SINGULARITY_CMD} ${BIDS_DIR} ${BIDS_DIR}/${DERIVS_DIR} participant --participant-label ${SUBJ[$SLURM_ARRAY_TASK_ID-1]} -w /work/ -vv --omp-nthreads 8 --nthreads 12 --mem_mb 30000 --output-spaces MNI152NLin2009cAsym:res-2 anat fsnative fsaverage5 --cifti-output"
      # --use-aroma"

# Setup done, run the command
echo Running task ${SLURM_ARRAY_TASK_ID}
echo Commandline: $cmd
eval $cmd
exitcode=$?

# Output results to a table
echo "sub-$subject   ${SLURM_ARRAY_TASK_ID}    $exitcode" \
      >> ${SLURM_JOB_NAME}.${SLURM_ARRAY_JOB_ID}.tsv
echo Finished tasks ${SLURM_ARRAY_TASK_ID} with exit code $exitcode
exit $exitcode
