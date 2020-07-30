#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 23 2020

@author: TheDrDOS
"""

import datetime
import pandas as pd
import os
import requests
import shapefile
import itertools

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
