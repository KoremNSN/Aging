#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 11 09:52:15 2022

Level 1 analysis for multi run experiment with uneven diusterbution of trials between the runs.

@author: nachshon
"""

#%%
# General python libraries

import os
import pandas as pd
import numpy as np

# nipype libraries


import nipype.interfaces.io as nio  # Data i/o
import nipype.interfaces.utility as util  # utility
import nipype.pipeline.engine as pe  # pypeline engine
import nipype.algorithms.modelgen as model  # model specification
from nipype import Node, Workflow, MapNode

from nipype.interfaces import fsl
from nipype.interfaces import spm
from nipype.interfaces.matlab import MatlabCommand

# SPM and FSL initiation

MatlabCommand.set_default_paths('/home/nk549/Documents/MATLAB/spm12') # set default SPM12 path in my computer. 
fsl.FSLCommand.set_default_output_type('NIFTI_GZ')

#%%
# Adjust locations

data_root = '/gpfs/gibbs/pi/levy_ifat/Nachshon/Aging/Aging_Bids/derivatives'
output_dir = '/gpfs/gibbs/pi/levy_ifat/Nachshon/Aging/spm'
work_dir = '/home/nk549/scratch60/work'

# subject list

subject_list = [10, 11]

# basic experiment properties

fwhm = 6
tr = 1
removeTR = 4

#%% regressors for design matrix

def _bids2nipypeinfo(in_file, events_file, regressors_file,
                     regressors_names=None,
                     motion_columns=None, removeTR = 4,
                     decimals=3, amplitude=1.0):
    
    from pathlib import Path
    from nipype.interfaces.base.support import Bunch
    import pandas as pd
    import numpy as np

    # Process the events file
    events = pd.read_csv(events_file, sep = ',')
    bunch_fields = ['onsets', 'durations', 'amplitudes']

    if not motion_columns:
        from itertools import product
        motion_columns = ['_'.join(v) for v in product(('trans', 'rot'), 'xyz')]

    out_motion = Path('motion.par').resolve()
    regress_data = pd.read_csv(regressors_file, sep=r'\s+')
    np.savetxt(out_motion, regress_data[motion_columns].values, '%g')
    
    if regressors_names is None:
        regressors_names = sorted(set(regress_data.columns) - set(motion_columns))

    if regressors_names:
        bunch_fields += ['regressor_names']
        bunch_fields += ['regressors']

    runinfo = Bunch(
        scans=in_file,
        conditions=list(set(events.trial_type.values)),
        **{k: [] for k in bunch_fields})

    for condition in runinfo.conditions:
        event = events[events.trial_type.str.match(condition)]

        runinfo.onsets.append(np.round(event.onset.values-removeTR, 3).tolist()) # added -removeTR to align to the onsets after removing X number of TRs from the scan
        runinfo.durations.append(np.round(event.duration.values, 3).tolist())
        if 'amplitudes' in events.columns:
            runinfo.amplitudes.append(np.round(event.amplitudes.values, 3).tolist())
        else:
            runinfo.amplitudes.append([amplitude] * len(event))

    if 'regressor_names' in bunch_fields:
        runinfo.regressor_names = regressors_names
        runinfo.regressors = regress_data[regressors_names].fillna(0.0).values[removeTR:,].T.tolist() # adding removeTR to cut the first rows

    return [runinfo], str(out_motion)

#%%
infosource = pe.Node(util.IdentityInterface(fields=['subject_id'],),
                  name="infosource")

infosource.iterables = [('subject_id', subject_list)]

templates = {'func': data_root + '/sub-{subject_id}/ses-1/func/sub-{subject_id}_ses-1_task-task{task_id}_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold.nii.gz',
             'mask': data_root + '/sub-{subject_id}/ses-1/func/sub-{subject_id}_ses-1_task-task{task_id}_space-MNI152NLin2009cAsym_res-2_desc-brain_mask.nii.gz',
             'regressors': data_root + '/sub-{subject_id}/ses-1/func/sub-{subject_id}_ses-1_task-task{task_id}_desc-confounds_timeseries.tsv',
             'events': '/gpfs/gibbs/pi/levy_ifat/Nachshon/Aging/event_files_lvl/sub-{subject_id}/ses-1/func/sub-{subject_id}_ses-1_task-task{task_id}_events.csv'}

# Flexibly collect data from disk to feed into flows.
selectfiles = pe.Node(nio.SelectFiles(templates,
                      base_directory=data_root),
                      name="selectfiles")

selectfiles.inputs.task_id = [1,2,3,4]   
        
runinfo = MapNode(util.Function(
    input_names=['in_file', 'events_file', 'regressors_file', 'regressors_names', 'removeTR', 'motion_columns'],
    function=_bids2nipypeinfo, output_names=['info', 'realign_file']),
    name='runinfo',
    iterfield = ['in_file', 'events_file', 'regressors_file'])

        
runinfo.inputs.regressors_names = ['std_dvars', 'framewise_displacement'] + \
                                  ['a_comp_cor_%02d' % i for i in range(6)]
runinfo.inputs.removeTR = removeTR                                  
 
runinfo.inputs.motion_columns   = ['trans_x', 'trans_x_derivative1', 'trans_x_derivative1_power2', 'trans_x_power2'] + \
                                  ['trans_y', 'trans_y_derivative1', 'trans_y_derivative1_power2', 'trans_y_power2'] + \
                                  ['trans_z', 'trans_z_derivative1', 'trans_z_derivative1_power2', 'trans_z_power2'] + \
                                  ['rot_x', 'rot_x_derivative1', 'rot_x_derivative1_power2', 'rot_x_power2'] + \
                                  ['rot_y', 'rot_y_derivative1', 'rot_y_derivative1_power2', 'rot_y_power2'] + \
                                  ['rot_z', 'rot_z_derivative1', 'rot_z_derivative1_power2', 'rot_z_power2']
                                  
extract = pe.MapNode(fsl.ExtractROI(), name="extract", iterfield = ['in_file'])
extract.inputs.t_min = removeTR
extract.inputs.t_size = -1
extract.inputs.output_type='NIFTI' 

smooth = Node(spm.Smooth(), name="smooth", fwhm = fwhm)


modelspec = Node(interface=model.SpecifySPMModel(), name="modelspec") 
modelspec.inputs.concatenate_runs = False
modelspec.inputs.input_units = 'scans' # supposedly it means tr
modelspec.inputs.output_units = 'scans'
modelspec.inputs.time_repetition = 1.  # make sure its with a dot 
modelspec.inputs.high_pass_filter_cutoff = 128.

level1design = pe.Node(interface=spm.Level1Design(), name="level1design") #, base_dir = '/media/Data/work')
level1design.inputs.timing_units = modelspec.inputs.output_units
level1design.inputs.interscan_interval = 1.
level1design.inputs.bases = {'hrf': {'derivs': [0, 0]}}
level1design.inputs.model_serial_correlations = 'AR(1)'

#%% Connect workflow
wfSPM = Workflow(name="l1spm_resp", base_dir=work_dir)
wfSPM.connect([
        (infosource, selectfiles, [('subject_id', 'subject_id')]),
        (selectfiles, runinfo, [('events','events_file'),('regressors','regressors_file')]),
        (selectfiles, extract, [('func','in_file')]),
        (extract, smooth, [('roi_file','in_files')]),
        (smooth, runinfo, [('smoothed_files','in_file')]),
        (smooth, modelspec, [('smoothed_files', 'functional_runs')]),   
        (runinfo, modelspec, [('info', 'subject_info'), ('realign_file', 'realignment_parameters')]),
        (modelspec, level1design, [("session_info", "session_info")])
        ])

#%% Run workflow
wfSPM.run('MultiProc', plugin_args={'n_procs': 4})                                