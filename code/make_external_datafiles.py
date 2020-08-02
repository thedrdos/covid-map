#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created Jul 2020

@author: TheDrDOS
"""
# Clear the Spyder console and variables
try:
    from IPython import get_ipython
    get_ipython().magic('clear')
    get_ipython().magic('reset -f')
except:
    pass

from bokeh.models import ColumnDataSource
import os

import numpy as np
import datetime
from datetime import date, timedelta

import pandas as pd

import pickle
import progress_bar as pbar

import json_extra as je

# %% Get data
data_path = './tmp_data/'
print('*** Load Processed Data From: ' + data_path)
pbar.progress_bar(0, 4)
DF_States_COVID = pickle.load(open(data_path + "DF_States_COVID.p", "rb"))
pbar.progress_bar(1, 4)
DF_Counties_COVID = pickle.load(open(data_path + "DF_Counties_COVID.p", "rb"))
pbar.progress_bar(2, 4)
DI_States_map = pickle.load(open(data_path + "DI_States_map.p", "rb"))
pbar.progress_bar(3, 4)
DI_Counties_map = pickle.load(open(data_path + "DI_Counties_map.p", "rb"))
pbar.progress_bar(4, 4)

# %% Convert into ColumnDataSource
print('*** Convert Data into ColumnDataSource')
DS_States_COVID = {}
DS_Counties_COVID = {}
DS_Counties_map = {}
DS_States_map = {}

keep_covid_data = {
    'keys': ['death', 'positive', 'recovered', 'positiveActive', 'Absolute_death', 'Absolute_positiveActive', 'Absolute_recovered', 'Absolute_positive', 'positive_increase', 'positive_increase_mav', 'positiveActive_increase', 'positiveActive_increase_mav', 'death_increase', 'death_increase10_mav', 'hospitalizedCurrently', 'inIcuCurrently', 'Absolute_hospitalizedCurrently', 'Absolute_inIcuCurrently'],
    'first_date':   pd.Timestamp.now() - pd.DateOffset(months=4),
    'last_date':    pd.Timestamp.now(),
}


print('Converting States COVID Data...')
N = len(DF_States_COVID) - 1
# track whats the maximum positive number per million (increment to find the nearest whole digit percentage)
max_pos = 10000
for n, d in enumerate(DF_States_COVID):
    pbar.progress_bar(n, N)
    if len(DF_States_COVID[d]['positive']) > 0:
        if max(DF_States_COVID[d]['positive'].values) > max_pos:
            max_pos = max_pos + 10000
    keys = set(keep_covid_data['keys']).intersection(list(DF_States_COVID[d].keys()))
    DF_States_COVID[d] = DF_States_COVID[d][keys].truncate(
        keep_covid_data['first_date'], keep_covid_data['last_date'])
    DS_States_COVID[d] = ColumnDataSource(DF_States_COVID[d])
del DF_States_COVID

print('Converting Counties COVID Data...')
N = len(DF_Counties_COVID) - 1
for n, d in enumerate(DF_Counties_COVID):
    pbar.progress_bar(n, N)
    keys = set(keep_covid_data['keys']).intersection(list(DF_Counties_COVID[d].keys()))
    DF_Counties_COVID[d] = DF_Counties_COVID[d][keys].dropna(
    ).truncate(keep_covid_data['first_date'], keep_covid_data['last_date'])
    DS_Counties_COVID[d] = ColumnDataSource(DF_Counties_COVID[d])
del DF_Counties_COVID

print('Conversions Completed.')

# %%
"""
Make the external datafiles
"""
ext_data_path = "../site/plots/ext_data/"
filename_key2datafilename = "key_to_filename.json"
key2datafilename = {'0Info': """Keys map to the respective datafile with the COVID data
The datafiles have 3 keys: {}
'key': [string, the key the file is associated with],
'filename': [string, the filename],
'data': [dictionary, the data from the respective ColumnDataSource]
}"""}
N = len(DS_Counties_COVID) - 1 + len(DS_States_COVID) - 1
n = 0
for d in DS_States_COVID:
    pbar.progress_bar(n, N)
    datafilename = 'data_' + '{:05.0f}'.format(n) + '.json'
    key2datafilename[d] = datafilename
    je.dump({'key': d, 'filename': datafilename,
             'data': DS_States_COVID[d].data}, ext_data_path + datafilename, human_readable=False)
    n = n + 1
for d in DS_Counties_COVID:
    pbar.progress_bar(n, N)
    datafilename = 'data_' + '{:05.0f}'.format(n) + '.json'
    key2datafilename[d] = datafilename
    je.dump({'key': d, 'filename': datafilename,
             'data': DS_Counties_COVID[d].data}, ext_data_path + datafilename, human_readable=False)
    n = n + 1
je.dump(key2datafilename, ext_data_path + filename_key2datafilename)
