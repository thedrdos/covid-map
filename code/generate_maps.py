#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 23 10:41:38 2020

@author: david_sigthorsson
"""

import datetime
import pandas as pd
import os
import requests
import shapefile
import itertools




def demo():
    pass
    # from bokeh.io import show
    # from bokeh.models import ColorMapper, LogColorMapper
    # from bokeh.palettes import Viridis6 as palette
    # from bokeh.plotting import figure 
    # from bokeh.models import ColumnDataSource # for interfacing with Pandas
    # import numpy as np
    
    # map_data_state  = get_map_data(entity='state')
    # map_data_county = get_map_data(entity='county')
    
    # state_to_id = dict(zip(map_data_state['name'].values.tolist(),map_data_state['state_id'].values.tolist()))
    # id_to_state = dict(zip(map_data_state['state_id'].values.tolist(),map_data_state['name'].values.tolist()))
        
    # state_name = 'Ohio'
    # state_id = state_to_id[state_name]
    
    # map_data = map_data_county[map_data_county['state_id']==state_id].copy()
    
    # map_data['xc'] = [np.nanmean(d,) for d in map_data['x']]
    # map_data['yc'] = [np.nanmean(d,) for d in map_data['y']]
    
    # map_data['cnt'] = [cnt+1 for cnt,d in enumerate(map_data['name'])]
    
    # data = {
    #     'x' : [  for d in map_data]
    #     ,
    #     }
        
    # color_mapper = ColorMapper(palette=palette) 
        
    # TOOLS = "pan,wheel_zoom,reset,hover,save"

    # # p = figure(
    # #     title=state_name, tools=TOOLS,
    # #     x_axis_location=None, y_axis_location=None,
    # #     tooltips=[
    # #         ("Name", "@name"),("(Long, Lat)", "($x, $y)")
    # #     ])
    
    # # p.grid.grid_line_color = None
    # # p.hover.point_policy = "follow_mouse"
    # p = figure(
    #     title=state_name, tools=TOOLS,
    #     x_axis_location=None, y_axis_location=None,
    #     )    
    
    # p.patches('x', 'y', source=data)
    
    # # p.patches('x', 'y', source=data,
    # #           fill_color={'field': 'cnt', 'transform': color_mapper},
    # #           fill_alpha=0.7, line_color="white", line_width=0.5)
    
    # show(p)   
    
    
# palette = tuple(reversed(palette))

# state_ids = {
#     code : 
#     }

# counties = {
#     code: county for code, county in counties.items() if county["state"] == "tx"
# }

# county_xs = [county["lons"] for county in counties.values()]
# county_ys = [county["lats"] for county in counties.values()]

# county_names = [county['name'] for county in counties.values()]
# county_rates = [unemployment[county_id] for county_id in counties]
# color_mapper = LogColorMapper(palette=palette)

# data=dict(
#     x=county_xs,
#     y=county_ys,
#     name=county_names,
#     rate=county_rates,
# )

# TOOLS = "pan,wheel_zoom,reset,hover,save"

# p = figure(
#     title="Texas Unemployment, 2009", tools=TOOLS,
#     x_axis_location=None, y_axis_location=None,
#     tooltips=[
#         ("Name", "@name"), ("Unemployment rate", "@rate%"), ("(Long, Lat)", "($x, $y)")
#     ])
# p.grid.grid_line_color = None
# p.hover.point_policy = "follow_mouse"

# p.patches('x', 'y', source=data,
#           fill_color={'field': 'rate', 'transform': color_mapper},
#           fill_alpha=0.7, line_color="white", line_width=0.5)

# show(p)    

def get_map_data(entity='county',resolution='high', local_file_path='./map_data/', year = (datetime.datetime.now().year-1)):
    """
    Get data to e.g. generate colored maps of US states or counties    

    Parameters
    ----------
    entity : string, 'county', 'state', and 'nation' are valid
        DESCRIPTION. 
        The default is 'county'.
    resolution : string, 'high', 'medium', and 'low' are valid
        DESCRIPTION. 
        The default is 'high'.
    local_file_path : string, path to the map data 
        This is where data will be downloaded to from www2.census.gov/geo/tiger/ d
        if the data files are not available already. 
        The default is './map_data/'.
    year : integer, year from which to download the data 
        Data isn't necessarily available from the current year, 
        so previous year is used by default. (Tested with 2019) 
        The default is (datetime.datetime.now().year-1).

    Returns
    -------
    map_data : Pandas DataFrame
        Contains the location data (latitude and longitude) for each entity
        ('x', and 'lats' are the latitudes, 'y' and 'lons' are the longitudes)
        Also has the state id (see entity='state' to see the id of each state)
        Also 'name' has the name of the entities (states or counties). 

    """
    entities = {
        'county': 'county',
        'state' : 'state',
        'nation': 'nation',
        }
    
    resolutions = {
        'high'  : '500k',
        'medium': '5m',
        'low'   : '20m'
        }
    
    shape_data_file = 'cb_'+str(year)+'_us_'+entities[entity]+'_'+resolutions[resolution]
    
    #url = "http://www2.census.gov/geo/tiger/GENZ2015/shp/" + shape_data_file + ".zip"
    url = "http://www2.census.gov/geo/tiger/GENZ" + str(year) + "/shp/" + shape_data_file + ".zip"
    zfile = local_file_path + shape_data_file + ".zip"
    sfile = local_file_path + shape_data_file + ".shp"
    dfile = local_file_path + shape_data_file + ".dbf"
    if not os.path.exists(zfile):
        print("Getting file: ", url)
        response = requests.get(url)
        with open(zfile, "wb") as code:
            code.write(response.content)

    if not os.path.exists(sfile):
        uz_cmd = 'unzip ' + zfile + " -d " + local_file_path
        print("Executing command: " + uz_cmd)
        os.system(uz_cmd)

    shp = open(sfile, "rb")
    dbf = open(dfile, "rb")
    sf = shapefile.Reader(shp=shp, dbf=dbf)

    lats = []
    lons = []
    name = []
    st_id = []
    for shprec in sf.shapeRecords():
    # for n,shprec in enumerate(sf.shapeRecords()):
    #     if n<3:
    #         print('*** Entry:' +str(n)+ '***')
    #         for k in range(0,len(shprec.record)):
    #             print(k)
    #             print(shprec.record[k])
        st_id.append(int(shprec.record[0]))
        name.append(shprec.record[5])
        lat, lon = map(list, zip(*shprec.shape.points))
        indices = shprec.shape.parts.tolist()
        lat = [lat[i:j] + [float('NaN')] for i, j in zip(indices, indices[1:]+[None])]
        lon = [lon[i:j] + [float('NaN')] for i, j in zip(indices, indices[1:]+[None])]
        lat = list(itertools.chain.from_iterable(lat))
        lon = list(itertools.chain.from_iterable(lon))
        lats.append(lat)
        lons.append(lon)

    map_data = pd.DataFrame({'x': lats, 'y': lons,'lats': lons, 'lons':lats, 'state_id': st_id, 'name': name})
    return map_data

def lonlat_to_xy(map_data):
    import math
    allxs = []
    allys = []
    
    for (lons,lats) in zip(map_data['lons'],map_data['lats']) :
        xs = []
        ys = []
        xys = []
    
        for (lon,lat) in zip(lons,lats):
            if math.isnan(lon)|math.isnan(lat):
                x = math.nan
                y = math.nan
            else:
                r_major = 6378137.000
                x = r_major * math.radians(lon)
                scale = x/lon
                y = 180.0/math.pi * math.log(math.tan(math.pi/4.0 + (lat * (math.pi/180.0)/2.0))) * scale
                    
            xs.append(x)
            ys.append(y)
            xys.append((x,y))
            
        allxs.append(xs)
        allys.append(ys)
    map_data['x'] = allxs
    map_data['y'] = allys
    return map_data