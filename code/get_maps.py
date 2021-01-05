#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 23 2020

@author: TheDrDOS

Get map data


Country maps source:
    https://www.naturalearthdata.com/downloads/

State and county maps source:
    http://www2.census.gov/geo/tiger/

"""

import datetime
import pandas as pd
import os
import requests
import shapefile
import itertools

import geopandas as gpd
from shapely.geometry.polygon import Polygon
from shapely.geometry.multipolygon import MultiPolygon


def get_maps(entity='county',resolution='high', local_file_path='./map_data/', year = (datetime.datetime.now().year-1)):
    year = 2019 # hardcode the year in early 2020 because census website not yet updated
    map_coordsys = 3857 #4326;#3395 # epsg

    entities = {
    'county': 'county',
    'state' : 'state',
    'country': 'country',
    }
    if entity not in ['country']:
        resolutions = {
            'high'  : '500k',
            'medium': '5m',
            'low'   : '20m'
        }
        shape_data_file = 'cb_'+str(year)+'_us_'+entities[entity]+'_'+resolutions[resolution]
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

        map_gpd = gpd.read_file(sfile)
        map_gpd = map_gpd.to_crs(epsg=map_coordsys)

    else:
        resolutions = {
            'high'  : 'ne_10m_admin_0_countries',
            'medium': 'ne_50m_admin_0_countries',
            'low'   : 'ne_110m_admin_0_countries'
        }
        sfile = local_file_path+resolutions[resolution]+'/'+resolutions[resolution]+'.shp'
        map_gpd = gpd.read_file(sfile)
        map_gpd = map_gpd.to_crs(epsg=map_coordsys)

    out = map_gpd

    return out

def get_MultiPolyLists(mpoly,coord_type='x'):
    """Returns the coordinates ('x' or 'y') for the exterior and interior of MultiPolygon digestible by multi_polygons in Bokeh"""
    if coord_type == 'x':
        i=0
    elif coord_type == 'y':
        i=1

    # Get the x or y coordinates
    c = []
    if isinstance(mpoly,Polygon):
        mpoly = [mpoly]
    for poly in mpoly: # the polygon objects return arrays, it's important they be lists or Bokeh fails
        exterior_coords = poly.exterior.coords.xy[i].tolist();
        interior_coords = []
        for interior in poly.interiors:
            if isinstance(interior.coords.xy[i],list):
                interior_coords += [interior.coords.xy[i]];
            else:
                interior_coords += [interior.coords.xy[i].tolist()];
        c.append([exterior_coords, *interior_coords])
    return c

def get_MultiPolyLists_xy(mpoly):
    """Returns the coordinates ('x','y') for the exterior and interior of MultiPolygon digestible by multi_polygons in Bokeh"""
    # Get the x or y coordinates
    x = []
    y = []
    if isinstance(mpoly,Polygon):
        mpoly = [mpoly]
    for poly in mpoly: # the polygon objects return arrays, it's important they be lists or Bokeh fails
        exterior_coords_x = poly.exterior.coords.xy[0].tolist();
        interior_coords_x = []
        exterior_coords_y = poly.exterior.coords.xy[1].tolist();
        interior_coords_y = []

        for interior in poly.interiors:
            if isinstance(interior.coords.xy[0],list):
                interior_coords_x += [interior.coords.xy[0]];
                interior_coords_y += [interior.coords.xy[1]];
            else:
                interior_coords_x += [interior.coords.xy[0].tolist()];
                interior_coords_y += [interior.coords.xy[1].tolist()];
        x.append([exterior_coords_x, *interior_coords_x])
        y.append([exterior_coords_y, *interior_coords_y])
    return (x,y)
