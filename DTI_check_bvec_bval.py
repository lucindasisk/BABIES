
# coding: utf-8

# In[44]:


from nibabel import load
from pandas import Series, DataFrame, read_csv
from os import path
from glob import glob
from datetime import date


# In[61]:


timepoint = input('Which timepoint are you checking? Enter "Newborn" or "6month":  ')
fp = '/Volumes/iang/active/BABIES/BABIES_diffusion/subjsDir/'+ timepoint
sublist = Series(glob(fp + '/*-*-T*')).str.replace(fp+'/', '')
subs = sublist.sort_values()


# In[62]:


final = DataFrame(columns = ['ID', '#bvals', '#bvecs', 'NIFTI length'])
for sub in subs:
    if path.exists(fp + '/'+sub+'/raw/DTI_pe0_ms103.bval'):
        bval = read_csv(fp + '/' + sub +'/raw/DTI_pe0_ms103.bval', sep = ' ', header = None)
        bval1 = len(bval.columns)
    else:
        print('Bval not found for {}'.format(sub))
    if path.exists(fp + '/'+sub+'/raw/DTI_pe0_ms103.bvec'):
        bvec = read_csv(fp + '/' + sub +'/raw/DTI_pe0_ms103.bvec', sep = ' ', header = None)
        bvec1 = len(bvec.columns)
    else:
        print('Bvec not found for {}'.format(sub))
    if path.exists(fp + '/'+sub+'/raw/DTI_pe0_ms103.bvec'):
        nii = load(fp + '/' + sub +'/raw/DTI_pe0_ms103.nii.gz')
        nii1 = nii.shape[3]
    else:
        print('Nifti not found for {}'.format(sub))
    data = Series([sub, bval1, bvec1, nii1], index = ['ID', '#bvals', '#bvecs', 'NIFTI length'])
    final = final.append(data, ignore_index = True)


# In[63]:


final


# In[37]:


today = str(date.today())
final.to_csv(fp+'/'+timepoint+'_File_QC_Report_'+today+'.csv')

