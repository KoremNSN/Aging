import nipype.interfaces.io as nio  # Data i/o
import nipype.interfaces.fsl as fsl  # fsl
import nipype.interfaces.utility as util  # utility
import nipype.pipeline.engine as pe  # pypeline engine
import nipype.algorithms.modelgen as model  # model generation
from nipype.interfaces.fsl import Merge
from nltools.data import Brain_Data
import os

from glob import glob

#%%
def collect_data(sub, contrast, base_dir):
    '''
    get subject number and contrast number
    return list of cope, vcopes and average mask for the flameo
    '''

    cope = '/gpfs/gibbs/pi/levy_ifat/Nachshon/Aging/results/run-*/modelfit/_subject_id_'+sub+'/modelestimate/results/cope'+contrast+'.nii.gz'
    vcope = '/gpfs/gibbs/pi/levy_ifat/Nachshon/Aging/results/run-*/modelfit/_subject_id_'+sub+'/modelestimate/results/varcope'+contrast+'.nii.gz'

    copes = glob(cope)
    vcopes = glob(vcope)

    mask_name = '/gpfs/gibbs/pi/levy_ifat/Nachshon/Aging/Aging_Bids/derivatives/sub-'+sub+'/ses-1/func/sub-'+sub+'_ses-1_task-task2_space-MNI152NLin2009cAsym_res-2_desc-brain_mask.nii.gz'
    ''' 
    # create average mask - was found to produce bad results.
    mask_name = base_dir + '/mask.nii.gz' 

    if os.path.exists(mask_name):
        print(sub + 'mask exists')
    else:
        mask = '/gpfs/gibbs/pi/levy_ifat/Nachshon/Aging/Aging_Bids/derivatives/fmriprep/sub-'+sub+'/ses-1/func/sub-'+sub+'_ses-1_task-task2_space-MNI152NLin2009cAsym_res-2_desc-brain_mask.nii.gz'
        #masks = glob(mask)
        #print('averageing mask...'+ mask_name)
        #Brain_Data(masks).mean().write(mask_name)
        print('mask complete')
    '''
    return(copes, vcopes, mask_name)
#%%
subject_list = ['10', '11', '13', '14', '15', '16','17', '18', '19',
                '20', '23', '24', '25', '26', '27', 
                '30', '32', '36', '37', '38', '39', 
                '40', '41', '42', '43', '46', # '44',
                '50', '51', '55', '56', '58', '57',
                '60', '61', '62', '64', '66']

contrasts = ['1', '2', '3', '4', '5', '6', '7']
home_dir = '/gpfs/gibbs/pi/levy_ifat/Nachshon/Aging/results/fixedef/'

for sub in subject_list:
    for contrast in contrasts:
        base_dir = os.path.join(home_dir, sub, contrast)
        try:
            os.makedirs(base_dir)
        except:
            print('folder {base_dir} exists!')
        copes, vcopes, avg_mask = collect_data(sub, contrast, base_dir)

        copemerge = pe.MapNode(
            interface=fsl.Merge(dimension='t'),
            iterfield=['in_files'],
            name="copemerge")
        copemerge.inputs.in_files = copes

        varcopemerge = pe.MapNode(
            interface=fsl.Merge(dimension='t'),
            iterfield=['in_files'],
            name="varcopemerge")
        varcopemerge.inputs.in_files = vcopes

        level2model = pe.Node(interface=fsl.L2Model(num_copes=4), 
                            name='l2model')

        flameo = pe.MapNode(
            interface=fsl.FLAMEO(run_mode='fe'),
            name="flameo",
            iterfield=['cope_file', 'var_cope_file'])
        flameo.inputs.mask_file = avg_mask

        # %%
        fixed_fx = pe.Workflow(name='fixedfx', base_dir=base_dir)

        fixed_fx.connect([
            (copemerge, flameo, [('merged_file', 'cope_file')]),
            (varcopemerge, flameo, [('merged_file', 'var_cope_file')]),
            (level2model, flameo, [('design_mat', 'design_file'),
                                ('design_con', 't_con_file'), ('design_grp',
                                                                'cov_split_file')]),
        ])

        #%%

        fixed_fx.run()