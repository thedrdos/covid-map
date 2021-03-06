#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created Aug 2020

@author: TheDrDOS
"""
# Clear the Spyder console and variables
try:
    from IPython import get_ipython
    #get_ipython().magic('clear')
    get_ipython().magic('reset -f')
except:
    pass

import os

import pickle
import progress_bar as pbar

import hashlib
import json
import multiprocessing as mp

from time import time as now
from time import perf_counter as pnow

import gzip

T0 = now()
# %% 
'''
------------------------------------------------------------------------------
Load Data
------------------------------------------------------------------------------
'''
print("Load Data:")
t0=pnow()
data_path = './tmp_data/'
data = pickle.load(open(data_path+'tmp_data_and_maps.p','rb'))
print("    Loading Completed in :{} sec".format(pnow()-t0))
# From: (assign the keys as variables in the workspace)
# data = {
#     'covid_data': covid_data,
#     'GraphData':GraphData,     
#     'MapData':MapData,
#     'Type_to_LocationNames':Type_to_LocationNames,
#     'LocationName_to_Type':LocationName_to_Type,
#         }
for d in data:
    globals()[d] = data[d]
del data

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

def mp_dump_location(l):
    ''' Dump data for a location to json files (from both GraphData and MapData)'''
    FilesMade = 0
    if l in GraphData:
        with open(ext_data_path+GraphData[l]['filename'], 'w', encoding ='utf8') as outfile:
            json.dump(GraphData[l], outfile)
        FilesMade +=1
    if l in MapData:
        with open(ext_data_path+MapData[l]['filename'], 'w', encoding ='utf8') as outfile:
            json.dump(MapData[l], outfile)   
        FilesMade +=1        
    return FilesMade

def mp_dump_location_gz(l):
    ''' Dump data for a location to json files (from both GraphData and MapData)'''
    FilesMade = 0
    if l in GraphData:
        with  gzip.GzipFile(ext_data_path+GraphData[l]['filename']+'.gz', 'w') as outfile:
            outfile.write(json.dumps(GraphData[l]).encode('utf-8'))
        FilesMade +=1
    if l in MapData:
        with  gzip.GzipFile(ext_data_path+MapData[l]['filename']+'.gz', 'w') as outfile:
            outfile.write(json.dumps(MapData[l]).encode('utf-8'))
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

location_to_filename = {}
filename_to_location = {}
location_to_mapfilename = {}
print("Generate Filenames:")
t0 = pnow()
for l in GraphData:
    h = short_hash(l)
    location_to_filename[l] = h
    filename_to_location[h] = l
    
    GraphData[l]['filename'] = h+'.json'
    if l in MapData:
        MapData[l]['filename'] = h+'_map.json'
        location_to_mapfilename[l] = h+'_map'
l = 'Earth'
h = short_hash(l)
location_to_filename[l] = h
location_to_mapfilename[l] = h+'_map'
filename_to_location[h] = l
MapData[l]['filename'] = h+'_map.json'

print("    Completed in :{} sec".format(pnow()-t0))

N = len(GraphData)
n = 0
N = len(GraphData)
Ncpu = min([mp.cpu_count(),N]) # use maximal number of local CPUs
chunksize = 1
pool = mp.Pool(processes=Ncpu)
print("Dump Data To json Files For All Locations:")
t0 = pnow()
locations = [k for k in GraphData]+['Earth']
for n,d in enumerate(pool.imap_unordered(mp_dump_location_gz,locations,chunksize=chunksize)):
    if n%15==0:
        pbar.progress_bar(n,N-1)
    pass
    if d==0:
        print("No output file made for (location not found): "+l)
pbar.progress_bar(n,N-1)
pool.terminate()

# save the translation files            
# with open(ext_data_path+'location_to_filename'+'.json', 'w', encoding ='utf8') as outfile:
#             json.dump(location_to_filename, outfile,indent=4, sort_keys=True)
# with open(ext_data_path+'filename_to_location'+'.json', 'w', encoding ='utf8') as outfile:
#             json.dump(filename_to_location, outfile,indent=4, sort_keys=True)     
with gzip.GzipFile(ext_data_path+'location_to_filename'+'.json'+'.gz', 'w') as outfile:
            outfile.write(json.dumps(location_to_filename,indent=4, sort_keys=True).encode('utf-8'))
with gzip.GzipFile(ext_data_path+'filename_to_location'+'.json'+'.gz', 'w') as outfile:
            outfile.write(json.dumps(filename_to_location,indent=4, sort_keys=True).encode('utf-8'))
with gzip.GzipFile(ext_data_path+'location_to_mapfilename'+'.json'+'.gz', 'w') as outfile:
            outfile.write(json.dumps(location_to_mapfilename,indent=4, sort_keys=True).encode('utf-8'))            
         
if len(location_to_filename)==len(filename_to_location):
    #print('Filenames are unique')
    pass
else:
    print('Filenames are NOT unique')
    
print("    Completed in :{} sec".format(pnow()-t0))
    
print("Script Completed in :{} sec".format(now()-T0))
    