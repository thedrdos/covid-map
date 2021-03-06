#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 21 2020

@author: TheDrDOS

Interface with COVID, population, and location data from various sources

Format the data with columns like the CTP data which has the following columns

 'date',
 'state',
 'positive',                - also in country data
 'negative',
 'pending',
 'hospitalizedCurrently',
 'hospitalizedCumulative',
 'inIcuCurrently',
 'inIcuCumulative',
 'onVentilatorCurrently',
 'onVentilatorCumulative',
 'recovered',               - also in country data
 'hash',
 'dateChecked',
 'death',                   - also in country data
 'hospitalized',
 'total',
 'totalTestResults',
 'posNeg',
 'fips',
 'deathIncrease',
 'hospitalizedIncrease',
 'negativeIncrease',
 'positiveIncrease',
 'totalTestResultsIncrease'

 Additional columns:
     'state' - equivalent to country when reading global
     'country'
     'place'
     'name'

"""
# For updating git
import os

# For data processing
import pandas as pd
import numpy as np

import re

# %% Make redirection possible after a change in the JH dataset
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

def dict_US():
    """
    List all available states for the US ( obtained using load_state() )
    """
    df = load_US()
    ret = {
        'data' : df.columns.tolist(),
        'states': df["state"].unique().tolist(),
        }
    ret['names']=get_state_name(ret['states'])

    return ret

def print_US():
    """
    Print all available data for the US ( obtained using load_state() )
    """
    df = load_US()
    # List the available data
    print(" List of available data columns: ".center(40,"*"))
    for c in df.columns.tolist():
        print("\t'"+c+"'")
    print("")
    print(" List of available states: ".center(40,"*"))
    for n,s in enumerate(df["state"].unique()):
        if n%5==4:
            print("\t'"+s+"'")
        else:
            print("\t'"+s+"'",end="")
    return

def load_state(state):
    """
    Given a country name (str), return a dataframe with the data for that country
    """

    if isinstance(state,list):
        pass
    else:
        state = [state]

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

        out[s]={
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
        if df['state'].str.contains(st).any():
            ret.append(df[df['state']==st]['name'].iloc[0])
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
        if df['name'].str.contains(st).any() & (st not in ['US','UK']):
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
    if isinstance(state,list):
        pass
    else:
        state = [state]
    ret = []
    for st in state:
        if df['Province_State'].str.contains(st).any() & (st not in ['US','UK']):
            ret.append(df[df['Province_State']==st]['Population'].iloc[0])
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
    Use load_country() instead of this function
    """
    # Get data
    # Load data using Pandas
    dfd = {
        'positive': reread_csv(csv_data_file_Global['confirmed_globa']),
        'recovered': reread_csv(csv_data_file_Global['recovered_global']),
        'death':    reread_csv(csv_data_file_Global['deaths_globa']),
    }

    return dfd

def load_country(country):
    """
    Given a country name/s (str/list), return a dictionary with the data for that country
    """

    if isinstance(country,list):
        pass
    else:
        country = [country]

    dfd = load_Counties()

    out = {}

    dfd = load_Global()

    pop     = get_country_population(country)
    lonlat  = get_country_location(country)

    for key in dfd:
            df = dfd[key].drop(columns=['Province/State','Lat','Long']).groupby('Country/Region').sum()

    for n,c in enumerate(country):
        ds = pd.DataFrame()
        for key in dfd:
            df = dfd[key]
            df = df.T
            df.index =  pd.to_datetime(df.index,format='%m/%d/%y')
            df.index.name = 'date'
            df.sort_index(inplace=True)
            df= df[c]
            df= df.to_frame(name=key)
            ds = df.join(ds)

        out[c]={
            'name': c,
            'dataframe': ds,
            'lat' : lonlat[n][1],
            'lon' : lonlat[n][0],
            'lonlat': lonlat[n],
            'population' : pop[n],
            'type': 'country',
            }

    return out

def get_countries():
    """
    Return a list of all available countries
    """
    dfd = load_Global()
    return dfd['positive']['Country/Region'].unique().tolist()

def print_countries():
    """
    Print all available countries
    """
    cs = sorted(get_countries())
    # List the available data
    print(" List of available countries: ".center(40,"*"))
    for n,s in enumerate(cs):
        if n%1==0:
            print("'"+s+"'")
        else:
            print("'"+s+"'\t".expandtabs(32),end="")
    return cs


def get_country_population(state):
    """
    Get population of state (str or list)
    """
    df = reread_csv(csv_data_file_US["pop_info"])
    if isinstance(state,list):
        pass
    else:
        state = [state]
    ret = []
    for st in state:
        if df['Country_Region'].str.contains(st).any():
            df = df[df['Province_State'].fillna('')==''] # remove proviences/states, they do not need to be summed to get the total pop
            ret.append(df[df['Country_Region']==st]['Population'].sum())
        else:
            ret.append(np .nan)
    return ret

def get_country_location(state):
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
        lat = df.loc[df['Combined_Key']==st,'Lat'].values[0]
        lon = df.loc[df['Combined_Key']==st,'Long_'].values[0]
        ret.append((lon,lat))
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

def load_county(county_state_country):
    """
    Given a country name (str)/list, return a dictionary with time history data in a dataframe and rest in other fields
    """
    if isinstance(county_state_country,list):
        pass
    else:
        county_state_country = [county_state_country]

    county_state_country_org = county_state_country.copy()

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
    for n,csc in enumerate(county_state_country):
        ds  = pd.DataFrame()

        if csc in Combined_Keys:
            # Get the loaded timehistory data
            for key in dfd:
                df = dfd[key]
                df = df.T # Transpose
                df.index =  pd.to_datetime(df.index,format='%m/%d/%y')
                df.index.name = 'date'
                df.sort_index(inplace=True)
                df= df[csc]
                df= df.to_frame(name=key)
                ds = df.join(ds)
            ds['recovered'] = 0 # no data on recovery in counties


            # Assign the data to the output dictionary
            out[county_state_country_org[n]]={
                'name': county_state_country_org[n],
                'dataframe': ds,
                'lat' : aux[county_state_country[n]]['lat'],
                'lon' : aux[county_state_country[n]]['lon'],
                'lonlat': (aux[county_state_country[n]]['lon'],aux[county_state_country[n]]['lat']),
                'population' : aux[county_state_country[n]]['pop'],
                'type': 'county',
                }
        else:
            # fill empty dataframe
            for k in dfd.keys():
                ds[k] = [float('NaN')]
            ds['recovered'] = [float('NaN')] # no data on recovery in counties

            # Assign the data to the output dictionary
            out[county_state_country_org[n]]={
                'name': county_state_country_org[n],
                'dataframe': ds,
                'lat' : float('NaN'),
                'lon' : float('NaN'),
                'lonlat': (float('NaN'),float('NaN')),
                'population' : float('NaN'),
                'type': 'county',
                }
    return out

def get_counties(state=''):
    """
    Return a list of all available counties (optionally give state name)
    """
    dfd = load_Counties()

    ret = dfd['positive']['Combined_Key'].unique().tolist()

    if state is '':
        ret = dfd['positive']['Combined_Key'].unique().tolist()
    else:
        ds = pd.DataFrame(dfd['positive'])
        ds = ds[ds['Province_State']==state]
        ret = ds['Combined_Key'].tolist()

    return ret

def print_counties():
    """
    Print all available countries
    """
    cs = sorted(get_counties())
    # List the available data
    print(" List of available countries: ".center(40,"*"))
    for n,s in enumerate(cs):
        if n%1==0:
            print("'"+s+"'")
        else:
            print("'"+s+"'\t".expandtabs(32),end="")
    return cs

def get_county_population(county_state_country):
    """
    Get population of state (str or list)
    """
    county_state_country_org = county_state_country;
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
def load(csc):
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
    for st in csc:
        ab = get_state_abbreviation(st)
        if (',' in st)&('Korea' not in st):
            counties.append(st)
        elif ((len(st)==2)& (st not in ['US','UK'])) | (ab!=st):
            states.append(st)
        else:
            countries.append(st)

    # Load all the countries/states/counties
    out={}
    if countries:
        out.update(load_country(countries))

    if states:
        out.update(load_state(states))

    if counties:
        out.update(load_county(counties))
    return out
