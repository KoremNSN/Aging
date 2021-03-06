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
<<<<<<< HEAD
from nipype.interfaces.utility import Function
=======
>>>>>>> 4932b0509efbd46be276f973b031941ba801bfd2

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
<<<<<<< HEAD
    np.savetxt(out_motion, regress_data[motion_columns].values[removeTR:,], '%g')
=======
    np.savetxt(out_motion, regress_data[motion_columns].values, '%g')
>>>>>>> 4932b0509efbd46be276f973b031941ba801bfd2
    
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

<<<<<<< HEAD
    return runinfo, str(out_motion)

#%%
infosource = pe.Node(util.IdentityInterface(fields=['subject_id']),
=======
    return [runinfo], str(out_motion)

#%%
infosource = pe.Node(util.IdentityInterface(fields=['subject_id'],),
>>>>>>> 4932b0509efbd46be276f973b031941ba801bfd2
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
<<<<<<< HEAD
    
=======
                                  
>>>>>>> 4932b0509efbd46be276f973b031941ba801bfd2
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

<<<<<<< HEAD


level1estimate = pe.Node(interface=spm.EstimateModel(), name="level1estimate")
level1estimate.inputs.estimation_method = {'Classical': 1}

#%% contrasts
import itertools

event_types = [['pleasant_picture1', 'pleasant_picture2', 'pleasant_picture3', 'pleasant_picture4'],
               ['negative_picture1', 'negative_picture2', 'negative_picture3', 'negative_picture4'],
               ['mon_reward1', 'mon_reward2', 'mon_reward3', 'mon_reward4'],
               ['mon_loss1', 'mon_loss2', 'mon_loss3', 'mon_loss4'],
               ['act_pleasant_picture', 'act_negative_picture', 'act_mon_reward', 'act_mon_loss'], 
               ['act_no']]

cont1_events = event_types[0]+event_types[1]+event_types[2]+event_types[3]
cont2_events = event_types[0]+event_types[2]+event_types[1]+event_types[3]
cont3_events = event_types[2]+event_types[3]
cont4_events = event_types[0]+event_types[1]
cont5_events = list(itertools.chain(*event_types))
cont6_events = event_types[4][:2]
cont7_events = event_types[4][2:]

cont1 = ['money>pictures', 'T',cont1_events, 
                        [1/8,  1/8,  1/8,  1/8,  1/8,  1/8,  1/8,  1/8, 
                        -1/8, -1/8, -1/8, -1/8, -1/8, -1/8, -1/8, -1/8]]
cont2  = ['Positive>Negative', 'T', cont2_events,
                        [1/8,  1/8,  1/8,  1/8,  1/8,  1/8,  1/8,  1/8, 
                        -1/8, -1/8, -1/8, -1/8, -1/8, -1/8, -1/8, -1/8]]

cont3  = ['M_Positive>Negative', 'T', cont3_events, [1/4, 1/4, 1/4, 1/4, -1/4, -1/4, -1/4, -1/4]]
cont4  = ['M_Positive>Negative', 'T', cont3_events, [1/4, 1/4, 1/4, 1/4, -1/4, -1/4, -1/4, -1/4]]
cont5  = ['stim', 'T', cont5_events, [1/21, 1/21, 1/21, 1/21, 1/21, 1/21, 1/21, 1/21, 1/21, 1/21, 1/21, 1/21, 1/21, 1/21, 1/21, 1/21, 1/21, 1/21, 1/21, 1/21, 1/21]]

cont6  = ['act_images', 'T', cont6_events,[1,-1]]
cont7  = ['act_money', 'T', cont7_events,[1,-1]]

cont8  = ['money_gain_l', 'T', event_types[2], [-1.5, -0.5, 0.5, 1.5]]
cont9  = ['money_loss_l', 'T', event_types[3], [-1.5, -0.5, 0.5, 1.5]]

cont10 = ['mg1','T',['mon_reward1'],[1]]
cont11 = ['mg2','T',['mon_reward2'],[1]]
cont12 = ['mg3','T',['mon_reward3'],[1]]
cont13 = ['mg4','T',['mon_reward4'],[1]]

cont14 = ['MG', 'F', [cont10, cont11, cont12, cont13]]



contrasts = [cont1, cont2, cont3, cont4, cont5, cont6, cont7, cont8, cont9, cont10, cont11, cont12, cont13, cont14]


contrastestimate = pe.Node(
    interface=spm.EstimateContrast(), name="contrastestimate")
contrastestimate.overwrite = True
contrastestimate.config = {'execution': {'remove_unnecessary_outputs': False}}
contrastestimate.inputs.contrasts = contrasts               
#%% Connect workflow
wfSPM = Workflow(name="l1spm_resp", base_dir=output_dir)
wfSPM.connect([
        (infosource, selectfiles, [('subject_id', 'subject_id')]),
        (selectfiles, runinfo, [('events','events_file'),
                                ('regressors','regressors_file')]),
=======
#%% Connect workflow
wfSPM = Workflow(name="l1spm_resp", base_dir=work_dir)
wfSPM.connect([
        (infosource, selectfiles, [('subject_id', 'subject_id')]),
        (selectfiles, runinfo, [('events','events_file'),('regressors','regressors_file')]),
>>>>>>> 4932b0509efbd46be276f973b031941ba801bfd2
        (selectfiles, extract, [('func','in_file')]),
        (extract, smooth, [('roi_file','in_files')]),
        (smooth, runinfo, [('smoothed_files','in_file')]),
        (smooth, modelspec, [('smoothed_files', 'functional_runs')]),   
<<<<<<< HEAD
        (runinfo, modelspec, [('info', 'subject_info'), 
                              ('realign_file', 'realignment_parameters')]),
        (modelspec, level1design, [("session_info", "session_info")]),
        (level1design, level1estimate, [('spm_mat_file','spm_mat_file')]),
        (level1estimate, contrastestimate, [('spm_mat_file', 'spm_mat_file'), 
                                            ('beta_images', 'beta_images'),
                                            ('residual_image', 'residual_image')]),
        ])

#%% Run workflow
wfSPM.run('MultiProc', plugin_args={'n_procs': 2})                                
=======
        (runinfo, modelspec, [('info', 'subject_info'), ('realign_file', 'realignment_parameters')]),
        (modelspec, level1design, [("session_info", "session_info")])
        ])

#%% Run workflow
wfSPM.run('MultiProc', plugin_args={'n_procs': 4})                                
>>>>>>> 4932b0509efbd46be276f973b031941ba801bfd2
