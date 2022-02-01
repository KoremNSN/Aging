#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 15 15:02:13 2019
@author: Or Duek
A short script that will convert to NIFTI.GZ (from raw DICOM data) and then create a BIDS compatible structure
"""

# convert to NIFTI
import os   
from nipype.interfaces.dcm2nii import Dcm2niix
import shutil


#%% Convert functions Converts DICOM to NIFTI.GZ
def convert (source_dir, output_dir, subName, session): # this is a function that takes input directory, output directory and subject name and then converts everything accordingly
    try:
        os.makedirs(os.path.join(output_dir, subName, session))
    except:
        print ("folder already there")
#    try:
#       os.makedirs(os.path.join(output_dir, subName, ))
#    except:
#       print("Folder Exist")    
    converter = Dcm2niix()
    converter.inputs.source_dir = source_dir
    converter.inputs.compression = 7
    converter.inputs.output_dir = os.path.join(output_dir, subName, session)
    converter.inputs.out_filename = subName + '_' + '%2s' + "_" +'%p'
    print('start convertation')
    converter.run()
    print('convertation complete')

#%% Check functions
def checkGz (extension):
     # check if nifti gz or something else
    if extension[1] =='.gz':
        return '.nii.gz'
    else:
        return extension[1]

def checkTask(funcdir, subName, ses):
    
    files = next(os.walk(funcdir))[2]
    files.sort()
    task  = {'rest' : {},
             'task' : {}}
    
    for f in files:
        if f.find('rest')!=-1:
            task['rest'][f.split('_')[1]] = 'rest'+str(len(task['rest']))
        else:
            run = f.split('bold')[1].split('.')[0].replace('(MB4iPAT2)','').replace('task','').replace('_','').replace('-','')
            if  run == '':
                task['task'][f.split('_')[1]] = 'task'+str(len(task['task']))
            else:
                task['task'][f.split('_')[1]] = run
                            
    
    for f in files:
        ext = checkGz(os.path.splitext(f))
        src = (os.path.join(funcdir, f))
        kind = 'task'
        if f.find('rest')!=-1:
             kind = 'rest'
        dest = funcdir + subName + '_' + ses + '_task-' + task[kind][f.split('_')[1]] + "_bold" + ext
        
        os.rename(src, dest)

def checkdwi(dwidir, subName, ses):
    files = next(os.walk(dwidir))[2]
    files.sort()
    runs = []
    for f in files:
        runs.append(int(f.split('_')[1]))
    minrun = min(runs)
    for f in files:
        ext = checkGz(os.path.splitext(f))
        run = 1+int(f.split('_')[1])-minrun
        src = (os.path.join(dwidir, f))
        dest = dwidir + subName + '_' + ses + '_run-' + str(run) + '_dwi' + ext
        os.rename(src, dest)
    
#%%
def organizeFiles(output_dir, subName, session):
    
    fullPath = os.path.join(output_dir, subName, session)
    os.makedirs(fullPath + '/dwi')
    os.makedirs(fullPath + '/anat')    
    os.makedirs(fullPath + '/func')
    os.makedirs(fullPath + '/misc')    
    
    a = next(os.walk(fullPath)) # list the subfolders under subject name
    dwi = False
    # run through the possibilities and match directory with scan number (day)
    for n in a[2]:
        print (n)
        b = os.path.splitext(n)
        # add method to find (MB**) in filename and scrape it
        if n.find('diff')!=-1:
            print ('This file is DWI')
            dwi = True
            shutil.move((fullPath +'/' + n), fullPath + '/dwi/' + n)
        elif n.find('MPRAGE')!=-1:
            print (n + ' Is Anat')
            shutil.move((fullPath + '/' + n), (fullPath + '/anat/' + n))
            os.rename(os.path.join(fullPath,'anat' , n), (fullPath + '/anat/' + subName+ '_' + session + '_acq-mprage_T1w' + checkGz(b)))
        elif n.find('t1_flash')!=-1:
            print (n + ' Is Anat')
            shutil.move((fullPath + '/' + n), (fullPath + '/anat/' + n))
            os.rename(os.path.join(fullPath,'anat' , n), (fullPath + '/anat/' + subName+ '_' + session + '_acq-flash_T1w' + checkGz(b)))
        elif n.find('t1_fl2d')!=-1:
            print (n + ' Is Anat')
            shutil.move((fullPath + '/' + n), (fullPath + '/anat/' + n))
            os.rename(os.path.join(fullPath,'anat' , n), (fullPath + '/anat/' + subName+ '_' + session + '_acq-fl2d1_T1w' + checkGz(b))) 
        elif n.find('GRE_3D_Sag_Spoiled')!=-1:
            print (n + ' Is Anat')
            shutil.move((fullPath + '/' + n), (fullPath + '/anat/' + n))
            os.rename(os.path.join(fullPath,'anat' , n), (fullPath + '/anat/' + subName+ '_' + session + '_acq-gre_spoiled_T1w' + checkGz(b)))            
        elif n.find('bold')!=-1:
            print(n  + ' Is functional')
            shutil.move((fullPath + '/' + n), (fullPath + '/func/' + n))
        else:
            print (n + 'Is MISC')
            shutil.move((fullPath + '/' + n), (fullPath + '/misc/' + n))
           
    checkTask((fullPath + '/func/'), subName, session)
    if dwi:
        checkdwi((fullPath + '/dwi/'), subName, session)
    
# need to run thorugh misc folder and extract t1's when there is no MPRAGE - Need to solve issue with t1 - as adding the names is not validated with BIDS
#%%
# sessionDict = {'ses-1': '/media/Data/Lab_Projects/Aging/neuroimaging/raw_dicom/pb9984_levy'}
# subNumber = '10'
def fullBids(subNumber, sessionDict):
    output_dir = '/home/nachshon/Documents/Aging/BIDS/'
    subName = 'sub-' + subNumber
    
    for i in sessionDict:
        session = i
        source_dir = sessionDict[i]
        print (session, source_dir)
        fullPath = os.path.join(output_dir, subName, session)
        print(fullPath)
        convert(source_dir,  output_dir, subName, session)
        organizeFiles(output_dir, subName, session)        
        
    
    #print (v)
#%%
sublist = [
           # {'subNumber': '10',
           #  'sessionDict': {'ses-1': '/media/Data/Lab_Projects/Aging/neuroimaging/raw_dicom/pb9984_levy/'}},
           # {'subNumber': '11',
           #  'sessionDict': {'ses-1': '/media/Data/Lab_Projects/Aging/neuroimaging/raw_dicom/pb10007_levy/'}},
           # {'subNumber': '13',
           #  'sessionDict': {'ses-1': '/media/Data/Lab_Projects/Aging/neuroimaging/raw_dicom/pb10072_levy/'}},
           # {'subNumber': '14',
           #  'sessionDict': {'ses-1': '/media/Data/Lab_Projects/Aging/neuroimaging/raw_dicom/pb10114_levy/'}},
           # {'subNumber': '15',
           #  'sessionDict': {'ses-1': '/media/Data/Lab_Projects/Aging/neuroimaging/raw_dicom/pb10255_levy/'}},
           # {'subNumber': '16',
           #  'sessionDict': {'ses-1': '/media/Data/Lab_Projects/Aging/neuroimaging/raw_dicom/pb10297_levy/'}},
           # {'subNumber': '17',
           #  'sessionDict': {'ses-1': '/media/Data/Lab_Projects/Aging/neuroimaging/raw_dicom/pb10342_levy/'}},
           # {'subNumber': '18',
           #  'sessionDict': {'ses-1': '/media/Data/Lab_Projects/Aging/neuroimaging/raw_dicom/pb10383_levy/'}},
           # {'subNumber': '19',
           #  'sessionDict': {'ses-1': '/media/Data/Lab_Projects/Aging/neuroimaging/raw_dicom/pb10475_levy/'}},
           # {'subNumber': '20',
           #  'sessionDict': {'ses-1': '/media/Data/Lab_Projects/Aging/neuroimaging/raw_dicom/pb10520_levy/'}},
           # {'subNumber': '23',
           #  'sessionDict': {'ses-1': '/media/Data/Lab_Projects/Aging/neuroimaging/raw_dicom/pb11288_levy/'}},
           # {'subNumber': '24',
           #  'sessionDict': {'ses-1': '/media/Data/Lab_Projects/Aging/neuroimaging/raw_dicom/pb11123_levy/'}},
           # {'subNumber': '25',
           #  'sessionDict': {'ses-1': '/media/Data/Lab_Projects/Aging/neuroimaging/raw_dicom/pb11019_levy/'}},
           # {'subNumber': '26',
           #  'sessionDict': {'ses-1': '/media/Data/Lab_Projects/Aging/neuroimaging/raw_dicom/pb11228_levy/'}},
           # {'subNumber': '27',
           #  'sessionDict': {'ses-1': '/media/Data/Lab_Projects/Aging/neuroimaging/raw_dicom/pb11316_levy/'}},
           # {'subNumber': '30',
           #  'sessionDict': {'ses-1': '/media/Data/Lab_Projects/Aging/neuroimaging/raw_dicom/pb11386_levy/'}},
           # {'subNumber': '32',
           #  'sessionDict': {'ses-1': '/media/Data/Lab_Projects/Aging/neuroimaging/raw_dicom/pb11495_levy/'}},
           # {'subNumber': '36',
           #  'sessionDict': {'ses-1': '/media/Data/Lab_Projects/Aging/neuroimaging/raw_dicom/pb11656_levy/'}},
           # {'subNumber': '37',
           #  'sessionDict': {'ses-1': '/media/Data/Lab_Projects/Aging/neuroimaging/raw_dicom/pb11539_levy/'}},
           # {'subNumber': '38',
           #  'sessionDict': {'ses-1': '/media/Data/Lab_Projects/Aging/neuroimaging/raw_dicom/pb11678_levy/'}},
           # {'subNumber': '39',
           #  'sessionDict': {'ses-1': '/media/Data/Lab_Projects/Aging/neuroimaging/raw_dicom/pb11638_levy/'}},
           # {'subNumber': '40',
           #  'sessionDict': {'ses-1': '/media/Data/Lab_Projects/Aging/neuroimaging/raw_dicom/pb11617_levy/'}},
           # {'subNumber': '41',
           #  'sessionDict': {'ses-1': '/media/Data/Lab_Projects/Aging/neuroimaging/raw_dicom/pb11698_levy/'}},
           # {'subNumber': '42',
           #  'sessionDict': {'ses-1': '/media/Data/Lab_Projects/Aging/neuroimaging/raw_dicom/pb11711_levy/'}}
           # {'subNumber': '43',
           #  'sessionDict': {'ses-1': '/media/Data/Lab_Projects/Aging/neuroimaging/raw_dicom/pb11734_levy/'}},
           # {'subNumber': '44',
           #  'sessionDict': {'ses-1': '/media/Data/Lab_Projects/Aging/neuroimaging/raw_dicom/pb11743_levy/'}},
           # {'subNumber': '46',
           #  'sessionDict': {'ses-1': '/media/Data/Lab_Projects/Aging/neuroimaging/raw_dicom/pb11769_levy/'}},
           # {'subNumber': '50',
           #  'sessionDict': {'ses-1': '/media/Data/Lab_Projects/Aging/neuroimaging/raw_dicom/pb11800_levy/'}},
           # {'subNumber': '51',
           #  'sessionDict': {'ses-1': '/media/Data/Lab_Projects/Aging/neuroimaging/raw_dicom/pb11837_levy/'}},
           {'subNumber': '55',
             'sessionDict': {'ses-1': '/media/Data/Lab_Projects/Aging/neuroimaging/raw_dicom/PB11875_levy/'}},
           {'subNumber': '56',
             'sessionDict': {'ses-1': '/media/Data/Lab_Projects/Aging/neuroimaging/raw_dicom/PB11903_levy/'}},
           {'subNumber': '58',
             'sessionDict': {'ses-1': '/media/Data/Lab_Projects/Aging/neuroimaging/raw_dicom/PB11912_levy/'}},
           {'subNumber': '60',
             'sessionDict': {'ses-1': '/media/Data/Lab_Projects/Aging/neuroimaging/raw_dicom/pb11952_levy/'}},
           {'subNumber': '57',
             'sessionDict': {'ses-1': '/media/Data/Lab_Projects/Aging/neuroimaging/raw_dicom/pb11961_levy/'}},
           {'subNumber': '61',
             'sessionDict': {'ses-1': '/media/Data/Lab_Projects/Aging/neuroimaging/raw_dicom/pb11978_levy/'}},
           {'subNumber': '62',
             'sessionDict': {'ses-1': '/media/Data/Lab_Projects/Aging/neuroimaging/raw_dicom/pb11986_levy/'}},
           {'subNumber': '64',
             'sessionDict': {'ses-1': '/media/Data/Lab_Projects/Aging/neuroimaging/raw_dicom/pb12013_levy/'}},
           {'subNumber': '66',
             'sessionDict': {'ses-1': '/media/Data/Lab_Projects/Aging/neuroimaging/raw_dicom/pb12030_levy/'}},
           
           ]


for sub in sublist: 
    fullBids(sub['subNumber'], sub['sessionDict'])
