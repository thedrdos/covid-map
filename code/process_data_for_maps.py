#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 12:17:17 2020

@author: TheDrDOS

Generates the following files:
    DF_Counties_COVID.p     dictionary of dataframes with county COVID data
    DF_States_COVID.p       dictionary of dataframes with state COVID data
    DI_Counties_map.p       dictionary of dictionaries with county map data
    DI_States_map.p         dictionary of dictionaries with state map data

"""

# Clear the Spyder console and variables
try:
    from IPython import get_ipython
    get_ipython().magic('clear')
    get_ipython().magic('reset -f')
except:
    pass

import generate_maps as gm
import pickle

import numpy as np
import pandas as pd

import progress_bar as pbar

from bokeh.models import ColumnDataSource # for interfacing with Pandas

# %% Load the data
data_path = './tmp_data/'
print("*** Loading Data Files From: "+data_path)

state_to_id     = pickle.load(open(data_path+"state_to_id.p","rb"))
id_to_state     = pickle.load(open(data_path+"id_to_state.p","rb"))

map_data_state  = pickle.load(open(data_path+"map_data_state.p","rb"))
map_data_county = pickle.load(open(data_path+"map_data_county.p","rb"))

data_states     = pickle.load(open(data_path+"data_states.p", "rb"))
data_counties   = pickle.load(open(data_path+"data_counties.p", "rb"))



# %% Process the COVID data - compute extra fields
print("*** Processing The COVID Data...")

def diff(x):
    return np.diff(x)

def pdiff(x):
    return np.clip(np.diff(x),0,None)
# Process the individual states/countries
ed = []
prog_label = ['Processing States:', 'Processing Counties:']
datas = [data_states, data_counties]
pops = []

cd_datas = []

for n,data in enumerate(datas):
    cd_data = {}
    pop     = {}
    print('Processing Part '+str(n+1)+' of '+str(len(datas)))
    print(prog_label[n])
    N = len(data)
    prog = 0
    for nn,k in enumerate(data):
        if (prog+0.002)<nn/N:
            prog = nn/N
            pbar.progress_bar(nn,N)

        df = data[k]['dataframe'].copy()

        # Remove dates with no reported cases and calculate active positive cases
        df = df[df['positive']!=0]
        df["positiveActive"] = df["positive"].fillna(0)-df["recovered"].fillna(0)-df["death"].fillna(0)

        # Fill in x day old cases as recovered if no recovery data is available
        rdays = 15 # assumed number of days it takes to recovere
        if df['recovered'].count()<7: # if less than one week of recovered reporting, then ignore it
            df['recovered'] = 0
        df['recovered_recorded'] = df['recovered']
        if df['recovered'].fillna(0).sum()==0:
            stmp = df['positive']
            df['recovered']=stmp.shift(rdays).fillna(0)-df['death']
        df['recovered'] = df['recovered'].replace(0, float('NaN'))


        # Normalize to people per million (func of population)
        columns_to_normalize = ['death','positiveActive','recovered','positive']
        for c in columns_to_normalize:
            if c not in ['date','population']:
                if np.issubdtype(df[c].dtype,np.number):
                    df['Absolute_'+c] = df[c]
                    df[c] = df[c]/data[k]['population']*1000000

        # Calculate actual and averaged increase
        df['positive_increase'] = df['positive'].rolling(2).apply(pdiff)
        df['positive_increase_mav'] = df['positive_increase'].rolling(7).mean()

        df['positiveActive_increase'] = df['positiveActive'].rolling(2).apply(diff)

        # Remove active calculations from when recovered data was not available, and one more entry to avoid the resultant cliff
        if len(df['positive'].values)>1:
            df.loc[df['recovered'].isnull(),'positiveActive_increase'] = float('NaN')
            try:
                df.loc[df['positiveActive_increase'].first_valid_index(),'positiveActive_increase']=float('NaN')
            except:
                pass
        df['positiveActive_increase_mav'] = df['positiveActive_increase'].rolling(7).mean()

        if len(df['positive'].values)>1:
            df.loc[df['recovered'].isnull(),'positiveActive_increase_mav'] = float('NaN')


        df['death_increase'] = df['death'].rolling(2).apply(diff)
        df['death_increase10_mav'] = df['death_increase'].rolling(7).mean()*10

        # cd_data[datas[n][k]['name']] = ColumnDataSource(df)
        cd_data[datas[n][k]['name']] = df
        pop[datas[n][k]['name']]  = data[k]['population']

    pbar.progress_bar(nn+1,N)
    cd_datas.append(cd_data)
    pops.append(pop)

pop_States = pops[0]
pop_Counties = pops[1]

DF_States_COVID     = cd_datas[0]
DF_Counties_COVID   = cd_datas[1]

# %% Save Processed COVID data
print("*** Save Processed COVID Data to "+data_path)
pickle.dump( pop_States, open( data_path+"pop_States.p", "wb" ) )
pickle.dump( pop_Counties, open( data_path+"pop_Counties.p", "wb" ) )

pickle.dump( DF_States_COVID, open( data_path+"DF_States_COVID.p", "wb" ) )
pickle.dump( DF_Counties_COVID, open( data_path+"DF_Counties_COVID.p", "wb" ) )
print("Save complete.")


DF_States_COVID     = pickle.load(open(data_path+"DF_States_COVID.p","rb"))
DF_Counties_COVID   = pickle.load(open(data_path+"DF_Counties_COVID.p","rb"))
pop_States     = pickle.load(open(data_path+"pop_States.p","rb"))
pop_Counties   = pickle.load(open(data_path+"pop_Counties.p","rb"))

# %% Process map data
print("*** Processing Map Data...")
# Process all counties in all states
DI_States_map = {}
DI_Counties_map = {}

# List fields to capture the last value of and add to the data (to e.g. use for color)
capture_current = ['Absolute_positive','Absolute_death','Absolute_recovered','Absolute_positiveActive','positive','death','recovered','positiveActive','positiveActive_increase_mav','positive_increase_mav']

N_counties = []
for state_name in map_data_state['name']:
    state_id = state_to_id[state_name]

    map_data = map_data_county[map_data_county['state_id']==state_id].copy()
    map_data = gm.lonlat_to_xy(map_data)

    xs = [np.asarray(x) for x in map_data['x']]
    ys = [np.asarray(y) for y in map_data['y']]
    N_counties.append(len(map_data['name'].values.tolist()))

    covid_data_labels = [ county_name+', '+state_name+', US' for county_name in map_data['name'].values.tolist()]

    pops = []
    current = {c: [] for c in capture_current}
    for dl in covid_data_labels:
        pops.append(pop_Counties[dl])
        try:
            for c in capture_current:
                if np.isfinite(DF_Counties_COVID[dl][c].iloc[-1]):
                    current[c].append(DF_Counties_COVID[dl][c].iloc[-1])
                else:
                    current[c].append(-1)
        except:
            for c in capture_current:
                #current[c].append(float('NaN'))
                current[c].append(-1)

    data = {
            'x':    xs,
            'y':    ys,
            'xc':   [np.nanmean(x) for x in xs], # the nans in the data denote
            'yc':   [np.nanmean(y) for y in ys], # distinct polygons, like islands
            'name': map_data['name'].values.tolist(),
            'state_id':  map_data['state_id'].values.tolist(),
            'state_name': [state_name for i in map_data['state_id']],
            #'number_of_counties': [N_counties[-1] for i in map_data['state_id']],
            'color' : [np.divide(cnt,len(map_data['name'])) for cnt,d in enumerate(map_data['name'])],
            'population': pops,
            'covid_data_labels': covid_data_labels,
            }
    for c in capture_current:
        pass
        data['current_'+c] = current[c]

    DI_Counties_map[state_name] = data


# Process states data
map_data = map_data_state.copy();
map_data = gm.lonlat_to_xy(map_data)

xs = [np.asarray(x) for x in map_data['x']]
ys = [np.asarray(y) for y in map_data['y']]

covid_data_labels = map_data['name'].values.tolist();
pops = []
current = {c: [] for c in capture_current}

for dl in covid_data_labels:
    pops.append(pop_States[dl])
    try:
        for c in capture_current:
            if np.isfinite(DF_States_COVID[dl][c].iloc[-1]):
                current[c].append(DF_States_COVID[dl][c].iloc[-1])
            else:
                current[c].append(-1)
    except:
        for c in capture_current:
            #current[c].append(float('NaN'))
            current[c].append(-1)

sdata = {
        'x':    xs,
        'y':    ys,
        'xc':   [np.nanmedian(x) for x in xs], # the nans in the data denote
        'yc':   [np.nanmedian(y) for y in ys], # distinct polygons, like islands
        'name':  map_data['name'].values.tolist(),
        'state_id':  map_data['state_id'].values.tolist(),
        'state_name': map_data['name'].values.tolist(),
        'number_of_counties': N_counties,
        'color' : [np.divide(cnt,len(map_data['name'])) for cnt,d in enumerate(map_data['name'])],
        'covid_data_labels':  map_data['name'].values.tolist(),
        'population': pops,
        }
for c in capture_current:
    pass
    sdata['current_'+c] = current[c]
DI_States_map = sdata

# %% Save the map data
print("*** Save Map Data to "+data_path)
pickle.dump( DI_Counties_map, open( data_path+"DI_Counties_map.p", "wb" ) )
pickle.dump( DI_States_map, open( data_path+"DI_States_map.p", "wb" ) )
print("Save complete.")

# # %% Test conversion into ColumnDataSource
# print('*** Test conversion into ColumnDataSource')
# DS_States_COVID     = {}
# DS_Counties_COVID   = {}
# DS_Counties_map     = {}
# DS_States_map       = {}

# print('Converting States COVID Data...')
# N = len(DF_States_COVID)-1
# for n,d in enumerate(DF_States_COVID):
#     pbar.progress_bar(n, N)
#     DS_States_COVID[d] = ColumnDataSource(DF_States_COVID[d])
# del DF_States_COVID

# print('Converting Counties COVID Data...')
# N = len(DF_Counties_COVID)-1
# for n,d in enumerate(DF_Counties_COVID):
#     pbar.progress_bar(n, N)
#     DS_Counties_COVID[d] = ColumnDataSource(DF_Counties_COVID[d])
# del DF_Counties_COVID

# print('Converting Counties map Data...')
# N = len(DI_Counties_map)-1
# for n,d in enumerate(DI_Counties_map):
#     pbar.progress_bar(n, N)
#     DS_Counties_map[d] = ColumnDataSource(DI_Counties_map[d])
# del DI_Counties_map

# print('Converting States COVID Data...')
# DS_States_map = ColumnDataSource(DI_States_map)
# pbar.progress_bar(1, 1)
# del DI_States_map

# print('Conversions Completed.')

# %%
print("*** Done.")
