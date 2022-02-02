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

# for the current 1st level analysis I chose only this categories. 
# by adding more cattegories like level you can do other contrasts
types = ['no','pleasant_picture', 'negative_picture', 'mon_reward', 'mon_loss']

# where to save to the event files (this is not bids compatibale)
output = '/media/Data/Lab_Projects/Aging/neuroimaging/event_files'

# try to create the folder. If you want to create s folder and a sub folder use makedirs
try:
    os.mkdir(output)
except:
    print('folders already exist')
    
# duration of each stimuli presentation
duration = 6

# where are the csv files located
glober = '/media/Data/Lab_Projects/Aging/behavioral/Reward_and_Punishment/AG_*_RP/ETRP_*.csv'

# those are counters
block, offset, = 0, 0

for subject in glob(glober):
    try:
        # read csv
        df = pd.read_csv(subject)

        # get sub number
        sub = df.subjID[1]
        # create path for new folders
        sub_dir = output + "/sub-" + str(sub) + '/ses-1' + '/func/'
        
        try: 
            os.makedirs(sub_dir)
        except:
            print('subject folder exist {}'.format(sub_dir))
        
        # run line by line on csv
        for i in range(df.shape[0]):
            
            # generates headers
            if df.Block.loc[i] != block:
                run = pd.DataFrame(columns=['onset', 'duration', 'trial_type'])
                onset = 7
                block = df.Block.loc[i]

            # add act_ to the name of the condition if actualize. if not avctualize will be named act_no
            act = 'act_' + types[df['Type'][i]*df['Actualization'][i]]
            
            # add lines to the run.csv
            run = run.append({'onset': onset, 'duration': duration, 'trial_type': types[df['Type'][i]]}, ignore_index=True)
            run = run.append({'onset': onset+8, 'duration': duration, 'trial_type': act}, ignore_index=True)
            
            onset += round(df.TrialDur.loc[i])
            
            # each block has 24 trials if trials is 24 creates a csv file.
            if df['TrialNum'][i] == 24:
                path = sub_dir + '/sub-' + str(sub) + '_ses-1_task-task' + str(block) + '_events.csv'
                run.to_csv(path, sep=',', index=False)
                

    except:
        print('error in file {}'.format(subject))
        