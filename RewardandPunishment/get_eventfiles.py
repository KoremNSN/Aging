#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 13 16:38:16 2021

@author: nachshon
"""

from glob import glob
import pandas as pd   
import os
#import shutil


types = ['no','pleasnt_picture', 'negative_picture', 'mon_reward', 'mon_loss']
output = '/media/Data/Lab_Projects/Aging/neuroimaging/event_files'

try:
    os.mkdir(output)
except:
    print('folders ready')
    
duration = 6

glober = '/media/Data/Lab_Projects/Aging/behavioral/Reward_and_Punishment/AG_*_RP/ETRP_*.csv'
block, offset, = 0, 0

for subject in glob(glober):
    try:
        df = pd.read_csv(subject)

        sub = df.subjID[1]
        sub_dir = output + "/sub-" + str(sub) + '/ses-1' + '/func/'
        
        try: 
            os.makedirs(sub_dir)
        except:
            print('subject folder exist {}'.format(sub_dir))
        
        # df['trial_type'] = [types[i] for i in df['Type']]
        # df['act'] = [act[i] for i in df['Actualization']]
        
        for i in range(df.shape[0]):

            if df.Block.loc[i] != block:
                run = pd.DataFrame(columns=['onset', 'duration', 'trial_type'])
                onset = 7
                block = df.Block.loc[i]

           
            act = 'act_' + types[df['Type'][i]*df['Actualization'][i]]
            
            run = run.append({'onset': onset, 'duration': duration, 'trial_type': types[df['Type'][i]]}, ignore_index=True)
            run = run.append({'onset': onset+8, 'duration': duration, 'trial_type': act[df['Actualization'][i]]}, ignore_index=True)
            
            onset += round(df.TrialDur.loc[i])
            
            if df['TrialNum'][i] == 24:
                path = sub_dir + '/sub-' + str(sub) + '_ses-1_task-task' + str(block) + '_events.csv'
                run.to_csv(path, sep=',', index=False)
                

    except:
        print('error in file {}'.format(subject))
        