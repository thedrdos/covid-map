#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 21 2020

@author: TheDrDOS

Interface with COVID, population, and location data from various sources

Use:
    # Format of input list elements:
    # Countries - name_of_country
    # US state  - name_of_state+", US"
    # US county - name_of_state+", "+name_of_county+", US"
import get_data as gd
places  = ['Italy','US','Idaho, US','Orange, New York, US']
data    = gd.load(places)
    # data is a dictionary of dictionaries,
    # keys are the elements of places
    # values are dictionaries with the following stucture
    # 'name': name of place, from places
    # 'dataframe': the Covid data in Pandas dataframe format (minimally providing: 'date' 'death' 'recovered' 'positive', states have more data as indicated in CTP documentation)
    # 'lat': latitude
    # 'lon': longitude
    # 'lonlat': (lon, lat)
    # 'population': population of place
    # 'type': type of place ('country','state', or 'county')
"""
# For updating git
import os

# For data processing
import pandas as pd
import numpy as np

# For multi processing
import multiprocessing as mp
mp_dic = {} # will use this for multi processing as a simple passing of input data

# For showing a progress bar
import progress_bar as pb

import re

# %% Make redirection possible after a change in the CTP dataset
def reread_csv(src):
    df = pd.read_csv(src)
    if len(df.columns.tolist())==1:
        df = pd.read_csv(re.search('https.*',df.columns.tolist()[0]).group())
    return df


# %% Data sources
# Covid Tracking Project for US data
csv_data_file_US  = {
    'timeseries':   '../DataSet/CTP/data/states_daily_4pm_et.csv',
    'info':         '../DataSet/CTP/data/states_info.csv',
    'pop_info':     '../DataSet/JH/csse_covid_19_data/UID_ISO_FIPS_LookUp_Table.csv',
    }
# John Hopkins data timeseries for global/country data
csv_data_file_Global = {
    'confirmed_globa':  '../DataSet/JH/csse_covid_19_data/csse_covid_19_time_series//time_series_covid19_confirmed_global.csv',
    'confirmed_US':     '../DataSet/JH/csse_covid_19_data/csse_covid_19_time_series//time_series_covid19_confirmed_US.csv',
    'recovered_global': '../DataSet/JH/csse_covid_19_data/csse_covid_19_time_series//time_series_covid19_recovered_global.csv',
    'deaths_globa':     '../DataSet/JH/csse_covid_19_data/csse_covid_19_time_series//time_series_covid19_deaths_global.csv',
    'deaths_US':        '../DataSet/JH/csse_covid_19_data/csse_covid_19_time_series//time_series_covid19_deaths_US.csv',
    'pop_info':         '../DataSet/JH/csse_covid_19_data/UID_ISO_FIPS_LookUp_Table.csv',
    }


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

    # %% Load USA data
def load_US():
    """
    Use load_state() instead of this function
    """
    # Get data
    # Load data using Pandas
    df = reread_csv(csv_data_file_US["timeseries"])
    # Make sure date data is formatted correctly/consitently and typecast
    df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
    df = df.set_index('date')
    df.sort_index(inplace=True)
    return df

def get_states():
    """
    List all available states for the US ( obtained using load_state() )
    """
    df = load_US()
    abr = df["state"].unique().tolist()

    return get_state_name(abr)

def load_state(state):
    """
    Given a country name (str), return a dataframe with the data for that country
    """

    if isinstance(state,list):
        pass
    else:
        state = [state]
    state_org = state
    state = get_state_abbreviation(state)

    # Load the US data
    dso = load_US()

    names = get_state_name(state)
    lonlat = get_state_location(names)
    pop   = get_state_population(names)

    out ={}
    for n, s in enumerate(state):
        ds = dso[dso['state']==s] # Select the state
        ds = ds[ds['positive'].notna()] # Remove rows with no total positive cases reported
        ds = ds[ds['positive']!=0]      # Remove rows with zero total positive cases reported

        out[state_org[n]]={
            'name': names[n],
            'dataframe': ds,
            'lat' : lonlat[n][1],
            'lon' : lonlat[n][0],
            'lonlat': lonlat[n],
            'population' : pop[n],
            'type': 'state',
            }
    return out

def get_state_name(state):
    """
    Convert a state abbreviation (str or list) into the state name/s
    """
    df = reread_csv(csv_data_file_US["info"])
    if isinstance(state,list):
        pass
    else:
        state = [state]
    ret = []
    for st in state:
        if df['state'].str.contains(st,regex=False).any():
            ret.append(df[df['state']==st]['name'].iloc[0]+', US')
        else:
            ret.append(st)
    return ret

def get_state_abbreviation(state):
    """
    Convert a state name (str or list) into the state abbreviation/s
    """
    df = reread_csv(csv_data_file_US["info"])
    if isinstance(state,list):
        pass
    else:
        state = [state]

    ret = []
    for st in state:
        if st.endswith(', US'):
            st = st[0:-4]

        if df['name'].str.contains(st,regex=False).any() & (st not in ['US','UK']):
            ret.append(df[df['name']==st]['state'].iloc[0])
        else:
            ret.append(st)
    return ret

def get_state_population(state):
    """
    Get population of state (str or list)
    """
    state = get_state_name(state)
    df = reread_csv(csv_data_file_US["pop_info"])
    df.index = df['Combined_Key'];
    if isinstance(state,list):
        pass
    else:
        state = [state]
    ret = []
    for st in state:
        if df['Combined_Key'].str.contains(st,regex=False).any() & (st not in ['US','UK']):
            ret.append(df[df['Combined_Key']==st]['Population'].iloc[0])
        else:
            ret.append(float('NaN'))

    return ret

def get_state_location(state):
    """
    Get location (longitude and lattitude) of state (str or list)
    """
    df = reread_csv(csv_data_file_US["pop_info"])
    df.index = df['Combined_Key'];
    if isinstance(state,list):
        pass
    else:
        state = [state]
    ret = []
    for st in state:
        if df.loc[df['Combined_Key']==st,'Lat'].any():
            lat = df.loc[df['Combined_Key']==st,'Lat'].values[0]
        else:
            lat = float('NaN')
        if df.loc[df['Combined_Key']==st,'Long_'].any():
            lon = df.loc[df['Combined_Key']==st,'Long_'].values[0]
        else:
            lon = float('NaN')
        ret.append((lon,lat))
    return ret


# %% Load Global data
def load_Global():
    """
    Load Global data
    """
    # Get data
    # Load data using Pandas
    dfd = {
        'positive': reread_csv(csv_data_file_Global['confirmed_globa']),
        'recovered': reread_csv(csv_data_file_Global['recovered_global']),
        'death':    reread_csv(csv_data_file_Global['deaths_globa']),
    }

    return dfd

def load_country(country,progress_bar=False, chunksize=1):
    """
    Given a country name/s (str/list), return a dictionary with the data for that country
    """

    if isinstance(country,list):
        pass
    else:
        country = [country]

    out = {}

    dfd = load_Global()

    pop     = get_country_population(country)
    lonlat  = get_country_location(country)
    Combined_Keys = dfd['positive']['Country/Region'].tolist()

    for key in dfd:
            dfd[key] = dfd[key].drop(columns=['Province/State','Lat','Long']).groupby('Country/Region').sum()

    global mp_dic
    mp_dic = {
        'dfd': dfd,
        'pop': pop,
        'lonlat':lonlat,
        'Combined_Keys':Combined_Keys,
        }
    Nitems = len(country)
    Ncpu = min([mp.cpu_count(),Nitems]) # use maximal number of local CPUs
    chunksize = 1
    pool = mp.Pool(processes=Ncpu)

    #for n,d in enumerate(pool.imap_unordered(mp_load_country,country,chunksize=chunksize)):
    for n,do in enumerate(country):
        d = mp_load_country(do)

        if progress_bar:
            pb.progress_bar(n,-(-Nitems/chunksize)-1)
        out[d['key']]=d['data'];
    pool.terminate()
    return out

def mp_load_country(country):
    ds = pd.DataFrame()
    if country in mp_dic['Combined_Keys']:
        for key in  mp_dic['dfd']:
            df = mp_dic['dfd'][key]
            df = df.T
            df.index =  pd.to_datetime(df.index,format='%m/%d/%y')
            df.index.name = 'date'
            df.sort_index(inplace=True)
            df= df[country]
            df= df.to_frame(name=key)
            ds = df.join(ds)

        out={
            'name': country,
            'dataframe': ds,
            'lat' : mp_dic['lonlat'][country][1],
            'lon' : mp_dic['lonlat'][country][0],
            'lonlat': mp_dic['lonlat'][country],
            'population' : mp_dic['pop'][country],
            'type': 'country',
            }
    else:
        # fill empty dataframe
        for k in mp_dic['dfd'].keys():
            ds[k] = [float('NaN')]
        ds['recovered'] = [float('NaN')] # no data on recovery in counties
        ds['date'] = [float('NaN')]

        # Assign the data to the output dictionary
        out={
            'name': country,
            'dataframe': ds,
            'lat' : float('NaN'),
            'lon' : float('NaN'),
            'lonlat': (float('NaN'),float('NaN')),
            'population' : float('NaN'),
            'type': 'county',
            }

    return {'key':country,'data':out}

def get_countries():
    """
    Return a list of all available countries
    """
    dfd = load_Global()
    return dfd['positive']['Country/Region'].unique().tolist()


def get_country_population(country):
    """
    Get population of country (str or list)
    """
    df = reread_csv(csv_data_file_US["pop_info"])
    if not isinstance(country,list):
        country = [country]
    ret = {}
    for st in country:
        if df['Country_Region'].str.contains(st,regex=False).any():
            df = df[df['Province_State'].fillna('')==''] # remove proviences/states, they do not need to be summed to get the total pop
            ret[st] = df[df['Country_Region']==st]['Population'].sum()
        else:
            ret[st]= np .nan
    return ret

def get_country_location(country):
    """
    Get location (longitude and lattitude) of state (str or list)
    """
    df = reread_csv(csv_data_file_US["pop_info"])
    df.index = df['Combined_Key'];
    if not isinstance(country,list):
        country = [country]
    ret = {}
    for st in country:
        if st in df['Combined_Key']:
            lat = df.loc[df['Combined_Key']==st,'Lat'].values[0]
            lon = df.loc[df['Combined_Key']==st,'Long_'].values[0]
        else:
            lat = np.nan
            lon = np.nan
        ret[st] = (lon,lat)
    return ret

# %% Load County data
def load_Counties():
    """
    Use load_country() instead of this function
    """
    # Get data
    # Load data using Pandas
    dfd = {
        'positive': reread_csv(csv_data_file_Global['confirmed_US']),
        'death':    reread_csv(csv_data_file_Global['deaths_US']),
    }

    return dfd

def load_county(county_state_country,progress_bar=False):
    """
    Given a country name (str)/list, return a dictionary with time history data in a dataframe and rest in other fields
    """
    if isinstance(county_state_country,list):
        pass
    else:
        county_state_country = [county_state_country]

    for n, csc in enumerate(county_state_country):
        if not csc.endswith(', US'):
            county_state_country[n] = csc+', US'

    dfd = load_Counties()

    Combined_Keys = dfd['positive']['Combined_Key'].tolist()

     # Find location and population data
    aux = dfd['death'].T.loc[['Lat','Long_','Population','Combined_Key']]
    aux = aux.rename({'Lat':'lat','Long_':'lon','Population':'pop'},axis='index')
    aux.columns = aux.loc['Combined_Key'] # assign the combined key row as the columns
    aux = aux.drop('Combined_Key')        # now the combined key row is redundant since its embedded in defining the column names

    # Drop unused columns
    for key in dfd:
        if key is 'positive':
            dfd[key] = dfd[key].drop(columns=['UID','iso2','iso3','code3','FIPS','Province_State','Country_Region','Lat','Long_']).groupby('Combined_Key').sum()
        else:
            dfd[key] = dfd[key].drop(columns=['UID','iso2','iso3','code3','FIPS','Province_State','Country_Region','Lat','Long_','Population']).groupby('Combined_Key').sum()

    out = {}

    global mp_dic
    mp_dic = {
        'dfd': dfd,
        'aux': aux,
        'Combined_Keys':Combined_Keys
        }
    Nitems = len(county_state_country)
    Ncpu = min([mp.cpu_count(),Nitems]) # use maximal number of local CPUs
    chunksize = 1
    pool = mp.Pool(processes=Ncpu)
    
    for n,d in enumerate(pool.imap_unordered(mp_load_county,county_state_country,chunksize=chunksize)):
    # for n,c in enumerate(county_state_country):
    #     d = mp_load_county(c)
        if progress_bar:
            pb.progress_bar(n,-(-Nitems/chunksize)-1)
        out[d['key']]=d['data'];
    pool.terminate()
    return out

def mp_load_county(csc):
    ds  = pd.DataFrame()
    if csc in mp_dic['Combined_Keys']:
        # Get the loaded timehistory data
        for key in mp_dic['dfd']:
            df = mp_dic['dfd'][key]
            df = df.T # Transpose
            df.index =  pd.to_datetime(df.index,format='%m/%d/%y')
            df.index.name = 'date'
            df.sort_index(inplace=True)
            if csc in df:
                df= df[csc]
                df= df.to_frame(name=key)
                ds = df.join(ds)
            else:
                ds[key] = float('NaN')
        ds['recovered'] = 0 # no data on recovery in counties
        
       
        # Assign the data to the output dictionary
        if csc in mp_dic['aux']:
            lat = mp_dic['aux'][csc]['lat']
            lon = mp_dic['aux'][csc]['lon']
            pop = mp_dic['aux'][csc]['pop']
        else:
            lat = float('NaN')
            lon = float('NaN')
            pop = float('NaN')
                
        out={
            'name': csc,
            'dataframe': ds,
            'lat' : lat,
            'lon' : lon,
            'lonlat': (lon,lat),
            'population' : pop,
            'type': 'county',
            }
    else:
        # fill empty dataframe
        for k in mp_dic['dfd'].keys():
            ds[k] = [float('NaN')]
        ds['recovered'] = [float('NaN')] # no data on recovery in counties
        ds['date'] = [float('NaN')]

        # Assign the data to the output dictionary
        out={
            'name': csc,
            'dataframe': ds,
            'lat' : float('NaN'),
            'lon' : float('NaN'),
            'lonlat': (float('NaN'),float('NaN')),
            'population' : float('NaN'),
            'type': 'county',
            }
    return {'key':csc, 'data': out}

def get_counties(state=''):
    """
    Return a list of all available counties (optionally give state name)
    """
    dfd = load_Counties()

    ret = dfd['positive']['Combined_Key'].unique().tolist()

    exceptions =['American Samoa, US',
                 'Diamond Princess, US',
                 'Grand Princess, US',
                 'Guam, US',
                 'Northern Mariana Islands, US',
                 'Virgin Islands, US']

    if state is '':
        ret = [r for r in ret if r not in exceptions]
    elif state not in exceptions:
        prov = state
        if prov.endswith(', US'):
            prov = prov[0:-4]
        ds = pd.DataFrame(dfd['positive'])
        ds = ds[ds['Province_State']==prov]
        ret = ds['Combined_Key'].tolist()
    else:
        ret = []

    return ret

def get_county_population(county_state_country):
    """
    Get population of state (str or list)
    """
    if not county_state_country.endswith(', US'):
        county_state_country = county_state_country+', US'

    ds = pd.DataFrame(load_Counties()['death'])

    ret = ds[ds['Combined_Key']==county_state_country]['Population'].iat[0]

    if ret>0:
        pass
    else:
        ret = 100
    return ret


# %% Load command, detect country, state, county
def load(csc,progress_bar=False):
    """
    Given a country/state name/abreviation (str or list), return a dictionary of dataframes with the data for that country/state as the key/s
    """
    if isinstance(csc,list):
        pass
    else:
        csc = [csc]

    countries   = []
    states      = []
    counties    = []

    # Detect country/state/counties (to speed up batch loading of each category)
    # Format:
    # Countries - name_of_country
    # US state  - name_of_state+", US"
    # US county - name_of_state+", "+name_of_county+", US"

    for st in csc:
        if (st.count(',')==2):
            counties.append(st)
        elif st.endswith(', US'):
            states.append(st)
        else:
            countries.append(st)

    # Load all the countries/states/counties
    out={}
    if countries:
        if progress_bar:
            print('Loading Countries:')
        out.update(load_country(countries,progress_bar=progress_bar))

    if states:
        if progress_bar:
            print('Loading States...')
        out.update(load_state(states))

    if counties:
        if progress_bar:
            print('Loading Counties:')
        out.update(load_county(counties,progress_bar=progress_bar))
    return out
