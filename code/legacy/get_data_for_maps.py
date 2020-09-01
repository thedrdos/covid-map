#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 2020

@author: TheDrDOS
"""

import generate_maps as gm
import get_data2 as gd2
import pickle


# %% Get map data
print("*** Loading Map Data...")
map_data_state  = gm.get_map_data(entity='state',resolution='low')
map_data_county = gm.get_map_data(entity='county',resolution='low')

state_to_id = dict(zip(map_data_state['name'].values.tolist(),map_data_state['state_id'].values.tolist()))
id_to_state = dict(zip(map_data_state['state_id'].values.tolist(),map_data_state['name'].values.tolist()))

# %% Generate list of all counties in all states
full_county_list = []
full_state_list = []
for state in map_data_state['name']:
    state_id = state_to_id[state]
    full_state_list.append(state)
    for county in map_data_county.loc[map_data_county['state_id']==state_id,'name']:
        full_county_list.append(county+', '+state+', US')

# %% Get all the COVID data
print("*** Refresh Database From GitHub...")
gd2.update()
print("*** Loading COVID Data For All States...")
data_states = gd2.load(full_state_list)
print("*** Loading COVID Data For All Counties..")
data_counties = gd2.load(full_county_list)

# %% Save the data
print("*** Saving Data Files...")
data_path = './tmp_data/'

pickle.dump( state_to_id, open(data_path+"state_to_id.p","wb"))
pickle.dump( id_to_state, open(data_path+"id_to_state.p","wb"))

pickle.dump( map_data_state, open(data_path+"map_data_state.p","wb"))
pickle.dump( map_data_county, open(data_path+"map_data_county.p","wb"))

pickle.dump( data_states, open( data_path+"data_states.p", "wb" ) )
pickle.dump( data_counties, open( data_path+"data_counties.p", "wb" ) )

print("*** Data Saved To Folder: "+data_path)

# %%
print("*** Done.")
