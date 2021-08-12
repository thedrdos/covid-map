"""
Created on Tue Jul 21 2020

@author: TheDrDOS

Interface with COVID, population, and location data from various sources

"""
# For updating git
import os

# For data processing
import pandas as pd
import numpy as np

import progress_bar as pbar

import hashlib
import json
import multiprocessing as mp

from time import time as now
from time import perf_counter as pnow

import gzip

T0 = now()

# %% Update and denote datafiles
def update():
    """
    Updates the Database

    Returns
    -------
    None.

    """
    os.system("git submodule update --recursive --remote")
    return None

'''
------------------------------------------------------------------------------
Load Data
------------------------------------------------------------------------------
'''
print('Update data')
update()
print("Load Data:")
t0 = pnow()

# src = "../DataSet/NYT/rolling-averages/us-counties-recent.csv"
src = "../DataSet/NYT/rolling-averages/us-counties.csv"
df = pd.read_csv(src)
df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
df.set_index('date',inplace=True)
df.sort_index(inplace=True)

df['location'] = df['county']+', '+df['state']+', US'
df.drop(columns=['county','state','geoid'],inplace=True)



# dates = df['date'].unique().tolist()
dates = df.index.unique().tolist()

dfmt  = '%Y%m%d'; 

nan_code = -987654321
df.fillna(value=nan_code,inplace=True)

# dates_str = dates.strftime()

# data = {}

# for d in dates:
#     dstr = d.strftime(dfmt)
#     data[dstr] = {}
#     data[dstr]['date'] = dstr
#     for k in df.keys().tolist():
#         data[dstr][k] = df[k].tolist()

# This spits out the dictionary I want
# df[df.index==pd.to_datetime('2021-08-03')].set_index('location').to_dict('index')

print("    Completed in :{} sec".format(pnow()-t0))

# %% 
'''
------------------------------------------------------------------------------
Support Functions
------------------------------------------------------------------------------
'''
def short_hash(st,digits=8,num_only=False):
    ''' Generate a short hash from a string '''
    if num_only:
        if digits>49:
            digits=49;
        return int(hashlib.sha1(st.encode()).hexdigest(),16)%(10**digits)
    else:
        if digits>40:
            digits=40;
        return hashlib.sha1(st.encode()).hexdigest().upper()[0:digits-1]

def dic_to_jsonreadydata(dic,nan_code):
    data = {}
    for k in dic:
        data[k] = np.nan_to_num(dic[k],nan=nan_code).tolist() # replace NaNs and cast to float using tolist, the first tolist is needed for string arrays with NaNs to be processed (will replace with 'nan')
    return data     

def mp_dump_date_gz(d):
    ''' Dump data for a date to json files'''
    FilesMade = 0
    if d in dates:
        filename = d.strftime(dfmt)

        data = {
            'filename': filename,
            'date': d.value, #/1e6,
            'nan_code': nan_code,
            'data': df[df.index==d].set_index('location').to_dict('index') ,
        }
            
        with  gzip.GzipFile(ext_data_path+filename+'.json'+'.gz', 'w') as outfile:
            outfile.write(json.dumps(data).encode('utf-8'))
        FilesMade +=1    
    return FilesMade    

# %%
'''
------------------------------------------------------------------------------
Make filenames and json datafiles

Use short hash for filenames to generate a short filenames that uniquely 
(one-to-one and onto) correspond to the location strings.
This allows consistent file naming if locations are added or removed.
Of course, the file name will change if the location name is changed. 
------------------------------------------------------------------------------
'''
ext_data_path = "../site/plots/data/" 
# ext_data_path = "./tmpdata/" 


N = len(dates)
n = 0
Ncpu = min([mp.cpu_count(),N]) # use maximal number of local CPUs
chunksize = 1
pool = mp.Pool(processes=Ncpu)
print("Dump Data To json Files For All Dates:")
t0 = pnow()

for n,d in enumerate(pool.imap_unordered(mp_dump_date_gz,dates,chunksize=chunksize)):
    if n%15==0:
        pbar.progress_bar(n,N-1)
    pass
    if d==0:
        print("No output file made for (Date not found): "+d)
pbar.progress_bar(n,N-1)
pool.terminate()

print("    Completed in :{} sec".format(pnow()-t0))

filename = 'date_to_filename'
data = {d.value: d.strftime(dfmt) for d in dates};
data['date_to_filename_format'] = dfmt
data['dates'] = sorted([d.value for d in dates])
with  gzip.GzipFile(ext_data_path+filename+'.json'+'.gz', 'w') as outfile:
    outfile.write(json.dumps(data).encode('utf-8'))
filename = 'filename_to_date'
data = {d.strftime(dfmt):d.value for d in dates};
with  gzip.GzipFile(ext_data_path+filename+'.json'+'.gz', 'w') as outfile:
    outfile.write(json.dumps(data).encode('utf-8'))



print("Script Completed in :{} sec".format(now()-T0))