import nipype.interfaces.io as nio  # Data i/o
import nipype.interfaces.fsl as fsl  # fsl
import nipype.interfaces.utility as util  # utility
import nipype.pipeline.engine as pe  # pypeline engine
import nipype.algorithms.modelgen as model  # model generation
from nipype.interfaces.fsl import Merge
from nltools.data import Brain_Data

from glob import glob

#%%

cope = '/gpfs/gibbs/pi/levy_ifat/Nachshon/Aging/results/run-*/modelfit/_subject_id_13/modelestimate/results/cope5.nii.gz'
vcope = '/gpfs/gibbs/pi/levy_ifat/Nachshon/Aging/results/run-*/modelfit/_subject_id_13/modelestimate/results/varcope5.nii.gz'

mask = '/gpfs/gibbs/pi/levy_ifat/Nachshon/Aging/Aging_Bids/derivatives/fmriprep/sub-13/ses-1/func/sub-13_ses-1_task-task*_space-MNI152NLin2009cAsym_res-2_desc-brain_mask.nii.gz'

copes = glob(cope)
vcopes = glob(vcope)

masks = glob(mask)
avg_mask = '/home/nk549/Documents/Aging/fixedfx/mask.nii.gz'
print('averageing mask...')
Brain_Data(masks).mean().write(avg_mask)
#Brain_Data(masks).mean().to_file(avg_mask)

#%%
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
fixed_fx = pe.Workflow(name='fixedfx', base_dir='/home/nk549/Documents/Aging/')

fixed_fx.connect([
    (copemerge, flameo, [('merged_file', 'cope_file')]),
    (varcopemerge, flameo, [('merged_file', 'var_cope_file')]),
    (level2model, flameo, [('design_mat', 'design_file'),
                           ('design_con', 't_con_file'), ('design_grp',
                                                          'cov_split_file')]),
])

#%%

fixed_fx.run()