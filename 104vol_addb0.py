
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


fp = '/Volumes/iang/active/BABIES/BABIES_Longitudinal/BABIES_Longitudinal-T2'
home = '/Volumes/iang/active/BABIES/BABIES_diffusion/subjsDir/'
destfp = '/Volumes/iang/active/BABIES/BABIES_diffusion/subjsDir/Newborn'
params = home + 'acq_params.txt'
index = home + 'index.txt'
index104 = home + 'index104.txt'
index105 = home + 'index105.txt'
index1 = pd.read_csv(home + 'index105.txt', sep = " ", header = None)


# In[32]:


sub = input('Please enter IDs for subs you wish to run:  ')

dest = destfp + '/' + sub + '/'
pe1_nii = destfp + '/' + sub + '/raw/DTI_pe1.nii.gz'
pe1_bvec = destfp + '/' + sub + '/raw/DTI_pe1.bvec'
pe1_bval = destfp + '/' + sub + '/raw/DTI_pe1.bval'
pe0_nii = destfp + '/' + sub + '/raw/DTI_pe0_ms103.nii.gz'
pe0_bvec = destfp + '/' + sub + '/raw/DTI_pe0_ms103.bvec'
pe0_bval = destfp + '/' + sub + '/raw/DTI_pe0_ms103.bval'


# In[33]:


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

#file = open(dest + "info.txt","w")
# file.write(output)
# file.close()


# In[40]:


def add_b0_bvec():
    bvec = pd.read_csv(dest + 'raw/DTI_pe0_ms103.bvec', sep = ' ', header = None)
    idx = 0
    new_col = [0.0, 0.0, 0.0]  # can be a list, a Series, an array or a scalar   
    bvec.insert(loc=idx, column='0.0', value=new_col)
    #os.rename(dest + 'raw/DTI_pe0_ms103.bvec', dest + 'raw/DTI_pe0_ms103_RAW.bvec')
    bvec.to_csv(dest + 'raw/DTI_pe0_ms103.bvec', header = None, index = False, sep = ' ', index_label=False)


# In[41]:


def fix_b0_nifti():
    fslroi = fsl.ExtractROI(in_file = pe0_nii, t_min = 0, t_size = 1, roi_file = dest + 'b0vol.nii.gz')
    fslroi.run()
    fslmerge = fsl.Merge(in_files = [dest + 'b0vol.nii.gz', pe0_nii], dimension = 't', merged_file = dest + '/raw/DTI_pe0_ms103_105.nii.gz')
    fslmerge.run()
    


# In[44]:


bvec_len = input('Do the nifti and bvec file contain 104 volumes instead of 105? Enter Yes or No:  ')
if bvec_len == 'Yes':
    print('Adding an additional column to .bvec file ....   ')
    add_b0_bvec()
#     print('Adding an additional b0 vol to pe0 nifti ....   ')
#     fix_b0_nifti()
    print('Performing final check ....   ')
    finalout = check_bvecs(dest +'raw/DTI_pe0_ms103_105.nii.gz')
    print('   ')
    print(finalout)
    print('   ')
elif bvec_len == 'No':
    print('If they have 105 vols, you should be good to go!  ')
else:
    print('Sorry, please try again and enter Yes or No.  ')
   


# In[43]:


finalout = check_bvecs(dest +'raw/DTI_pe0_ms103_105.nii.gz')
print(finalout)


# In[46]:


finalq = input('Are bvec, index, and nifti all now 105? Enter Yes or No:  ')
if finalq == 'Yes':
    print('Great! Renaming files ....   ')
    os.rename(pe0_nii, dest +'raw/DTI_pe0_ms103_RAW.nii.gz')
    os.rename(dest +'raw/DTI_pe0_ms103_105.nii.gz', dest +'raw/DTI_pe0_ms103.nii.gz')
    print('Check completed! ')
elif bvec_len == 'No':
    print('Hmm. Something went wrong. Please check your files and try again.')
else:
    print('Sorry, please try again and enter Yes or No.  ')

