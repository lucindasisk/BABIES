
# coding: utf-8

# In[1]:


from nibabel import load
from numpy import shape
import os
import glob
import pandas as pd
from shutil import copyfile
import nipype.pipeline.engine as pe
from nipype.interfaces import fsl


# In[2]:


#Set filepaths and variables
fp = '/Volumes/iang/active/BABIES/BABIES_Longitudinal/BABIES_Longitudinal-T2'
home = '/Volumes/iang/active/BABIES/BABIES_diffusion/subjsDir/'
destfp = '/Volumes/iang/active/BABIES/BABIES_diffusion/subjsDir/Newborn'
params = home + 'acq_params.txt'
index = home + 'index.txt'
index104 = home + 'index104.txt'
index105 = home + 'index105.txt'
index1 = pd.read_csv(home + 'index105.txt', sep = " ", header = None)
print(len(index1))
workflow_dir = '/Volumes/iang/active/BABIES/BABIES_diffusion/workflows'


# In[3]:


sub = input('Please enter IDs for subs you wish to run:  ')

dest = destfp + '/' + sub + '/'
pe1_nii = destfp + '/' + sub + '/raw/DTI_pe1.nii.gz'
pe1_bvec = destfp + '/' + sub + '/raw/DTI_pe1.bvec'
pe1_bval = destfp + '/' + sub + '/raw/DTI_pe1.bval'
pe0_nii = destfp + '/' + sub + '/raw/DTI_pe0_ms103.nii.gz'
pe0_bvec = destfp + '/' + sub + '/raw/DTI_pe0_ms103.bvec'
pe0_bval = destfp + '/' + sub + '/raw/DTI_pe0_ms103.bval'


# In[4]:


def check_bvecs(file):
    bvec_pe0 = pd.read_csv(dest + 'raw/DTI_pe0_ms103.bvec', sep = ' ', header = None)
    nifti_pe0 = load(file)
    index1 = pd.read_csv(home + 'index105.txt', sep = ' ', header = None)
    bv1 = len(bvec_pe0.columns)
    in1 = len(index1)
    ni1 = nifti_pe0.shape
    return 'SUBID {}: Number of entries in bvec: {}, length of index: {}, nifti dimensions: {}'.format(sub, bv1, in1, ni1)

output = check_bvecs(dest +'raw/DTI_pe0_ms103.nii.gz')
print(output)
file = open(dest + "info.txt","w")
file.write(output)
file.close()


# In[ ]:


print('Extracting ROIs for {}'.format(sub))
fslroi = fsl.ExtractROI(in_file = pe0_nii, t_min = 0, t_size = 1, roi_file = dest + 'bu_pe0.nii.gz').run()
fslroi2 = fsl.ExtractROI(in_file = pe1_nii, t_min = 0, t_size = 1, roi_file = dest + 'bd_pe1.nii.gz').run()


# In[ ]:


print('Working on merging files for {}'.format(sub))
dest = destfp + '/' + sub + '/'
fslmerge = fsl.Merge(in_files = [dest + 'bu_pe0.nii.gz', dest + 'bd_pe1.nii.gz'], dimension = 't', merged_file = dest + 'bud_nwf.nii.gz').run()


# In[ ]:


print('Working on topup for {}'.format(sub))
dest = destfp + '/' + sub + '/'
topup = fsl.TOPUP(in_file = dest + 'bud_nwf.nii.gz', encoding_file = params, config = 'b02b0.cnf', out_base = dest + 'DTI_topup_nwf').run()


# In[ ]:


print('Working on applying topup for {} pe1'.format(sub))
dest = destfp + '/' + sub + '/'
applytopup2 = fsl.ApplyTOPUP(encoding_file = params, in_files = [dest + 'raw/DTI_pe1.nii.gz'],
                                                method = 'jac',
                                                in_topup_fieldcoef = dest + 'DTI_topup_nwf_fieldcoef.nii.gz',
                                                in_topup_movpar = dest + 'DTI_topup_nwf_movpar.txt',
                                                in_index = [2],
                                                out_corrected = dest + 'DTI_pe0_unwarped_nwf.nii.gz',
                                                output_type = "NIFTI_GZ").run()


# In[ ]:


print('Working on applying topup for {} pe0'.format(sub))
dest = destfp + '/' + sub + '/'
applytopup1 = fsl.ApplyTOPUP(encoding_file = params, in_files = [dest + 'raw/DTI_pe0_ms103.nii.gz'],
                                                method = 'jac',
                                                in_topup_fieldcoef = dest + 'DTI_topup_nwf_fieldcoef.nii.gz',
                                                in_topup_movpar = dest + 'DTI_topup_nwf_movpar.txt',
                                                in_index = [1],
                                                out_corrected = dest + 'DTI_pe0_unwarped_nwf.nii.gz',
                                                output_type = "NIFTI_GZ").run()


# In[ ]:


print('Working on skullstripping {} pe0'.format(sub))
dest = destfp + '/' + sub + '/'
bet = fsl.BET(in_file = dest + 'DTI_pe0_unwarped_nwf.nii.gz', mask = True, out_file = dest + 'DTI_pe0_unwarped_stripped.nii.gz').run()



# In[ ]:


print('Performing eddy correction for {} pe0'.format(sub))
dest = destfp + '/' + sub + '/'
eddy = fsl.Eddy(in_file = dest + 'DTI_pe0_unwarped_stripped.nii.gz', in_acqp = params, in_bval = dest + 'raw/DTI_pe0_ms103.bval', in_bvec = dest + 'raw/DTI_pe0_ms103.bvec',
                                        in_index = index105, in_mask = dest + 'DTI_pe0_unwarped_stripped_mask.nii.gz',
                                        out_base = dest + 'DTI_unwarped_eddy').run()


# In[26]:


check_bvecs(dest+'DTI_unwarped_eddy.nii.gz')
print('Completed {}!'.format(sub))
#### WORKFLOW ATTEMPTED BELOW


# In[17]:


# for sub in ready_to_run:
#     dest = destfp + '/' + sub + '/'
#     pe1_nii = destfp + '/' + sub + '/raw/DTI_pe1.nii.gz'
#     pe1_bvec = destfp + '/' + sub + '/raw/DTI_pe1.bvec'
#     pe1_bval = destfp + '/' + sub + '/raw/DTI_pe1.bval'
#     pe0_nii = destfp + '/' + sub + '/raw/DTI_pe0_ms103.nii.gz'
#     pe0_bvec = destfp + '/' + sub + '/raw/DTI_pe0_ms103.bvec'
#     pe0_bval = destfp + '/' + sub + '/raw/DTI_pe0_ms103.bval'
#     fslroi = pe.MapNode(interface = fsl.ExtractROI(t_min = 0, t_size = 1),
#                        name = 'fslroi',
#                        iterfield = ["in_file"])
#     fslroi.inputs.in_file = [pe1_nii, pe0_nii]
#     fslroi.outputs.roi_file = [dest + 'bd_pe1.nii.gz', dest + 'bu_pe0.nii.gz']
#     fslmerge = pe.Node(interface = fsl.Merge(dimension = 't', merged_file = dest + 'bud.nii.gz'), name = 'fslmerge')
#     topup = pe.Node(interface = fsl.TOPUP(encoding_file = params, config = 'b02b0.cnf', out_base = dest + 'DTI_topup'),
#                     name = 'topup')
#     dest = destfp + '/' + sub + '/'
#     anatflow_c = pe.Workflow(name = "anatflow_c")
#     anatflow_c.connect([(fslroi, fslmerge, [('roi_file', 'in_files')]),
#                         (fslmerge, topup, [('merged_file', 'in_file')])
#                        ])
#     anatflow_c.base_dir = workflow_dir
#     anatflow_c.write_graph(graph2use = 'flat')
#     anatflow_c.run('MultiProc', plugin_args={'n_procs': 1})
# ready_to_run   


# In[ ]:


# for sub in ready_to_run:
#     dest = destfp + '/' + sub + '/'
#     pe1_nii = destfp + '/' + sub + '/raw/DTI_pe1.nii.gz'
#     pe1_bvec = destfp + '/' + sub + '/raw/DTI_pe1.bvec'
#     pe1_bval = destfp + '/' + sub + '/raw/DTI_pe1.bval'
#     pe0_nii = destfp + '/' + sub + '/raw/DTI_pe0_ms103.nii.gz'
#     pe0_bvec = destfp + '/' + sub + '/raw/DTI_pe0_ms103.bvec'
#     pe0_bval = destfp + '/' + sub + '/raw/DTI_pe0_ms103.bval'
#     applytopup = pe.Node(interface = fsl.ApplyTOPUP(encoding_file = params,
#                                                     in_files = [pe0_nii],
#                                                     method = 'jac',
#                                                     in_topup_fieldcoef = dest + 'DTI_topup_fieldcoef.nii.gz',
#                                                     in_topup_movpar = dest + 'DTI_topup_movpar.txt',
#                                                     in_index = [1],
#                                                     out_corrected = dest + 'DTI_pe0_unwarped.nii.gz',
#                                                     output_type = "NIFTI_GZ"),
#                             name = 'applytopup')
#     #applytopup.outputs.out_corrected = dest + 'DTI_pe0_corrected.nii.gz'
#     bet = pe.Node(interface = fsl.BET(mask = True, out_file = dest + 'DTI_pe0_unwarped_stripped.nii.gz'),
#                   name = 'bet')
#     init_proc_c=pe.Workflow(name="init_proc_c")
#     init_proc_c.connect([(applytopup, bet, [('out_corrected', 'in_file')])
#                        ])
#     init_proc_c.base_dir = workflow_dir
#     init_proc_c.write_graph(graph2use = 'flat')
#     init_proc_c.run('MultiProc', plugin_args={'n_procs': 1})


# In[ ]:


# for sub in ready_to_run:
#     dest = destfp + '/' + sub + '/'
#     pe1_nii = destfp + '/' + sub + '/raw/DTI_pe1.nii.gz'
#     pe1_bvec = destfp + '/' + sub + '/raw/DTI_pe1.bvec'
#     pe1_bval = destfp + '/' + sub + '/raw/DTI_pe1.bval'
#     pe0_nii = destfp + '/' + sub + '/raw/DTI_pe0_ms103.nii.gz'
#     pe0_bvec = destfp + '/' + sub + '/raw/DTI_pe0_ms103.bvec'
#     pe0_bval = destfp + '/' + sub + '/raw/DTI_pe0_ms103.bval'
#     applytopup = pe.Node(interface = fsl.ApplyTOPUP(encoding_file = params,
#                                                     in_files = [pe0_nii],
#                                                     method = 'jac',
#                                                     in_topup_fieldcoef = dest + 'DTI_topup_fieldcoef.nii.gz',
#                                                     in_topup_movpar = dest + 'DTI_topup_movpar.txt',
#                                                     in_index = [1],
#                                                     out_corrected = dest + 'DTI_pe0_unwarped.nii.gz',
#                                                     output_type = "NIFTI_GZ"),
#                             name = 'applytopup')
#     eddy = pe.Node(interface = fsl.Eddy(in_acqp = params, in_bval = pe0_bval, in_bvec = dest + '/raw/DTI_pe0_ms103.bvec',
#                                             in_index = index105, in_mask = dest + 'DTI_pe0_unwarped_stripped_mask.nii.gz',
#                                             out_base = dest + 'DTI_unwarped_eddy'),
#                                     name = 'eddy')

#     eddyflow_c = pe.Workflow(name='eddyflow_c')
#     eddyflow_c.connect([(applytopup, eddy, [('out_corrected', 'in_file')])
#                      ])
#     eddyflow_c.base_dir = workflow_dir
#     eddyflow_c.run('MultiProc', plugin_args={'n_procs': 1})
    

