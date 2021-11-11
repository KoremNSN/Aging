#!/usr/bin/env python
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
"""
Created 10.14.21
@author: Nachshon Korem based on: Or Duek
1st level analysis using FSL output
In this one we smooth using SUSAN, which takes longer. 
"""
#%%
from __future__ import print_function
from __future__ import division
from builtins import str
from builtins import range

import os  # system functions

import nipype.interfaces.io as nio  # Data i/o
import nipype.interfaces.fsl as fsl  # fsl
import nipype.interfaces.utility as util  # utility
import nipype.pipeline.engine as pe  # pypeline engine
import nipype.algorithms.modelgen as model  # model generation
#import nipype.algorithms.rapidart as ra  # artifact detection
from niflow.nipype1.workflows.fmri.fsl.preprocess import create_susan_smooth
from nipype.interfaces.utility import Function
"""
The output file format for FSL routines is being set to compressed NIFTI.
"""

fsl.FSLCommand.set_default_output_type('NIFTI_GZ')

#%%
fwhm = 6
tr = 1
run = '4'
removeTR = 4 #Number of TR's to remove before initiating the analysis

data_dir = os.path.abspath('/gpfs/gibbs/pi/levy_ifat/Nachshon/Aging/Aging_Bids/derivatives/fmriprep/')
output_dir = '/gpfs/gibbs/pi/levy_ifat/Nachshon/Aging/results/run-%s' %run
#%% Methods 
def _bids2nipypeinfo(in_file, events_file, regressors_file,
                     regressors_names=None,
                     motion_columns=None, removeTR = 4,
                     decimals=3, amplitude=1.0):
    from pathlib import Path
    import numpy as np
    import pandas as pd
    from nipype.interfaces.base.support import Bunch

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
subject_list = ['13', '11', '14', '15', '16', '17', '18', '19', 
                '20', '23', '24', '25', '26', '27', '30', '32', '36', 
                '37', '38', '39', '40', '41', '42']


infosource = pe.Node(util.IdentityInterface(fields=['subject_id']),
                                            name = "infosource")
infosource.iterables = [('subject_id', subject_list)]

# SelectFiles - to grab the data (alternativ to DataGrabber)
templates = {'func': data_dir + '/sub-{subject_id}/ses-1/func/sub-{subject_id}_ses-1_task-task' + run + '_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold.nii.gz',
             'mask': data_dir + '/sub-{subject_id}/ses-1/func/sub-{subject_id}_ses-1_task-task' + run + '_space-MNI152NLin2009cAsym_res-2_desc-brain_mask.nii.gz',
             'regressors': data_dir + '/sub-{subject_id}/ses-1/func/sub-{subject_id}_ses-1_task-task' + run + '_desc-confounds_timeseries.tsv',
             'events': '/gpfs/gibbs/pi/levy_ifat/Nachshon/Aging/event_files/aging_{subject_id}/events_' + run + '.csv'}

selectfiles = pe.Node(nio.SelectFiles(templates,
                                      base_directory=data_dir),
                      name = "selectfiles")

#%%
# Extract motion parameters from regressors file
runinfo = pe.Node(util.Function(
    input_names=['in_file', 'events_file', 'regressors_file', 'regressors_names', 'removeTR'],
    function=_bids2nipypeinfo, output_names=['info', 'realign_file']),
    name='runinfo')
runinfo.inputs.removeTR = removeTR

# Set the column names to be used from the confounds file
runinfo.inputs.regressors_names = ['dvars', 'framewise_displacement'] + \
    ['a_comp_cor_%02d' % i for i in range(6)] + ['cosine%02d' % i for i in range(4)]
#%%
skip = pe.Node(interface=fsl.ExtractROI(), name = 'skip') 
skip.inputs.t_min = removeTR
skip.inputs.t_size = -1

#%%

susan = pe.Node(interface=fsl.SUSAN(), name = 'susan') #create_susan_smooth()
susan.inputs.fwhm = fwhm
susan.inputs.brightness_threshold = 1000.0

#%%
modelfit = pe.Workflow(name='modelfit', base_dir= output_dir)

modelspec = pe.Node(interface=model.SpecifyModel(),                  
                    name="modelspec")

modelspec.inputs.input_units = 'secs'
modelspec.inputs.time_repetition = tr
modelspec.inputs.high_pass_filter_cutoff= 120
#%%

## Building contrasts
level1design = pe.Node(interface=fsl.Level1Design(), name="level1design")
cont1 = ['Money>picture', 'T', ['mon_reward', 'mon_loss', 'pleasnt_picture', 'negative_picture'], [0.5, 0.5, -0.5, -0.5]]
cont2 = ['Positive>Negative', 'T', ['mon_reward', 'mon_loss', 'pleasnt_picture', 'negative_picture'], [0.5, -0.5, 0.5, -0.5]]
cont3 = ['M_Positive>Negative', 'T', ['mon_reward', 'mon_loss', 'pleasnt_picture', 'negative_picture'], [1, -1, 0, 0]]
cont4 = ['P_Positive>Negative', 'T', ['mon_reward', 'mon_loss', 'pleasnt_picture', 'negative_picture'], [0, 0, 1, -1]]
cont5 = ['stim', 'T', ['mon_reward', 'mon_loss', 'pleasnt_picture', 'negative_picture'], [0.25, 0.25, 0.25, 0.25]]

#%%
contrasts = [cont1, cont2, cont3, cont4, cont5]

level1design.inputs.interscan_interval = tr
level1design.inputs.bases = {'dgamma': {'derivs': False}}
level1design.inputs.contrasts = contrasts
level1design.inputs.model_serial_correlations = True    

#%%

modelgen = pe.Node(
    interface=fsl.FEATModel(),
    name='modelgen',
    )
mask =  pe.Node(interface= fsl.maths.ApplyMask(), name = 'mask')


modelestimate = pe.Node(
    interface=fsl.FILMGLS(smooth_autocorr=True, mask_size=5, threshold=1000),
    name='modelestimate',
    )
    
#%%
modelfit.connect([
    (infosource, selectfiles, [('subject_id', 'subject_id')]),
    (selectfiles, runinfo, [('events','events_file'),('regressors','regressors_file')]),
    (selectfiles, skip,[('func','in_file')]),
    (skip,susan,[('roi_file','in_file')]),

    (susan, runinfo, [('smoothed_file', 'in_file')]),
    (susan, modelspec, [('smoothed_file', 'functional_runs')]),
    (runinfo, modelspec, [('info', 'subject_info'), ('realign_file', 'realignment_parameters')]),
    (modelspec, level1design, [('session_info', 'session_info')]),
    (level1design, modelgen, [('fsf_files', 'fsf_file'), ('ev_files', 'ev_files')]),

    (susan, mask, [('smoothed_file', 'in_file')]),
    (selectfiles, mask, [('mask', 'mask_file')]),
    (mask, modelestimate, [('out_file','in_file')]),
    (modelgen, modelestimate, [('design_file', 'design_file'),('con_file', 'tcon_file'),('fcon_file','fcon_file')]),
    ])

#%%
modelfit.run('MultiProc', plugin_args={'n_procs': 12})

