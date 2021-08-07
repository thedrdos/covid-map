#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created Jul 2020

@author: TheDrDOS
"""
# # Clear the Spyder console and variables
# try:
#     from IPython import get_ipython
#     get_ipython().magic('clear')
#     get_ipython().magic('reset -f')
# except:
#     pass


from bokeh.io import show, save, output_file
from bokeh.util.browser import view
from bokeh.models import ColorBar, ColorMapper, LogColorMapper, LogTicker, LinearColorMapper, NumeralTickFormatter
from bokeh.models import BasicTicker as LinearTicker
from bokeh.models import BasicTickFormatter, LogTicker, FixedTicker, FuncTickFormatter
from bokeh.palettes import Magma11 as palette
from bokeh.palettes import Inferno256, Turbo256
from bokeh.plotting import figure
from bokeh.models import Div
from bokeh.models import ColumnDataSource, DateRangeSlider, Select, Spinner
from bokeh.models.tools import HoverTool, BoxZoomTool  # for showing the hover tool

from bokeh_template_external_js import template as template_ext_js

from bokeh import events
from bokeh.models import Label, LabelSet, CustomJS, TapTool, Toggle, Button, Spacer, TextInput, RadioButtonGroup
from bokeh.tile_providers import CARTODBPOSITRON_RETINA, get_provider
import os
import sys

import numpy as np
import datetime
from datetime import date, timedelta

from bokeh.models import NumeralTickFormatter, BasicTickFormatter
# for adding the second axis
from bokeh.models import LogAxis, LinearAxis, Range1d, DataRange1d
# for formatting the dates on the x axis
from bokeh.models import DatetimeTickFormatter

from bokeh.layouts import column, row, gridplot, layout  # For show multiple figures


# For adding spans (vertical/horizontal lines without end points)
from bokeh.models import Span

import pandas as pd

import pickle
import progress_bar as pbar

import json
import gzip

import sys

"""
# Assign output file
________________________________________________________________________________
"""


def filename(fullname):
    """ Return the name of a file without its path or extension"""
    return os.path.splitext(os.path.split(fullname)[1])[0]


this_filename = filename(os.path.basename(os.path.splitext(__file__)[0]))
javascript_path = './' + this_filename + '_js/'
localhost_path = './plots/'
# name the output file/s after the script file
output_filename = "../../site/plots/" + this_filename
output_file(output_filename + ".html",
            title="Animated Map of World COVID19 Data, NYT Styled")  # title=filename(output_filename))

"""
# Support functions
________________________________________________________________________________
"""


def dic_nan_decode(d, nan_code):
    for k in d:
        d[k] = array_element_replace(d[k], nan_code, float('NaN'))
    return d


def array_element_replace(arr, old_value, new_value):
    for i in range(0, len(arr)):
        if isinstance(arr[i], list):
            arr[i] = array_element_replace(arr[i], old_value, new_value)
        else:
            if arr[i] == old_value:
                arr[i] = new_value
    return arr


"""
# Load key_to_filename
________________________________________________________________________________
"""
ext_datafiles = {
    'path': "../../site/plots/data/",
    'rel_path': "./data/",
}
with gzip.GzipFile(ext_datafiles['path'] + 'filename_to_location.json.gz', 'r') as fin:
    ext_datafiles['filename_to_location'] = json.loads(
        fin.read().decode('utf-8'))
with gzip.GzipFile(ext_datafiles['path'] + 'location_to_filename.json.gz', 'r') as fin:
    ext_datafiles['location_to_filename'] = json.loads(
        fin.read().decode('utf-8'))
with gzip.GzipFile(ext_datafiles['path'] + 'location_to_mapfilename.json.gz', 'r') as fin:
    ext_datafiles['location_to_mapfilename'] = json.loads(
        fin.read().decode('utf-8'))

with gzip.GzipFile(ext_datafiles['path'] + 'date_to_filename.json.gz', 'r') as fin:
    ext_datafiles['date_to_filename'] = json.loads(
        fin.read().decode('utf-8'))
with gzip.GzipFile(ext_datafiles['path'] + 'filename_to_date.json.gz', 'r') as fin:
    ext_datafiles['filename_to_date'] = json.loads(
        fin.read().decode('utf-8'))     
           

"""
# %% Load json file for initialization
________________________________________________________________________________
"""
continental_states = [
    'Alabama, US', 'Arizona, US', 'Arkansas, US', 'California, US', 'Colorado, US', 'Connecticut, US', 'Delaware, US', 'District of Columbia, US', 'Florida, US', 'Georgia, US', 'Idaho, US', 'Illinois, US', 'Indiana, US', 'Iowa, US', 'Kansas, US', 'Kentucky, US', 'Louisiana, US', 'Maine, US', 'Maryland, US', 'Massachusetts, US', 'Michigan, US', 'Minnesota, US', 'Mississippi, US', 'Missouri, US', 'Montana, US', 'Nebraska, US', 'Nevada, US', 'New Hampshire, US', 'New Jersey, US', 'New Mexico, US', 'New York, US', 'North Carolina, US', 'North Dakota, US', 'Ohio, US', 'Oklahoma, US', 'Oregon, US', 'Pennsylvania, US', 'Rhode Island, US', 'South Carolina, US', 'South Dakota, US', 'Tennessee, US', 'Texas, US', 'Utah, US', 'Vermont, US', 'Virginia, US', 'Washington, US', 'West Virginia, US', 'Wisconsin, US', 'Wyoming, US']
init_map = {
    'x':[],
    'y':[],
    'location':[],
    'name':[],
    'population':[],
}
for l in continental_states:
    with gzip.GzipFile(ext_datafiles['path'] + ext_datafiles['location_to_filename'][l] + '_map.json.gz', 'r') as fin:
        init_mapfile = json.loads(fin.read().decode('utf-8'))
    init_map['x'].extend(init_mapfile['data']['x'])
    init_map['y'].extend(init_mapfile['data']['y'])
    init_map['name'].extend([s[:-4] for s in init_mapfile['data']['location']])#init_mapfile['data']['name'])
    init_map['location'].extend(init_mapfile['data']['location'])
    init_map['population'].extend(init_mapfile['data']['population'])


init_date = pd.to_datetime(max(ext_datafiles['filename_to_date'].values()));
with gzip.GzipFile(ext_datafiles['path'] + ext_datafiles['date_to_filename'][str(init_date.value)] + '.json.gz', 'r') as fin:
    init_datafile = json.loads(fin.read().decode('utf-8'))
init_locations = init_datafile['data'].keys()
init_data = init_datafile['data']['New York City, New York, US']

for k in init_data: # initialize all the data fields
    init_map[k] = []

# Fill in missmatches 
import difflib
for n, l in enumerate(init_map['location']):
    if l not in init_locations:
        lclosest = difflib.get_close_matches(l,init_locations,n=1)[0]
        init_map['location'][n] =  lclosest
        print("  Replaced: "+l+" with "+"\t"+lclosest)

for l in init_map['location']: # 
    if l in init_locations:
        for k in init_datafile['data'][l]:
            init_map[k].extend([init_datafile['data'][l][k]])
    else:
        print("Can't find: "+l)
        for k in init_data:
            init_map[k].extend([float('NaN')])



latest_data_date = pd.to_datetime(max(ext_datafiles['filename_to_date'].values())) #pd.to_datetime('today') #max(init_data['date'])
oldest_date_date = pd.to_datetime(min(ext_datafiles['filename_to_date'].values())) #pd.to_datetime('20191101',format='%Y%m%d') #min(init_data['date'])

# init_location = 'Earth'  # get location
init_location = 'New York, US' 
with gzip.GzipFile(ext_datafiles['path'] + ext_datafiles['location_to_filename'][init_location] + '_map.json.gz', 'r') as fin:
    init_mapfile1 = json.loads(fin.read().decode('utf-8'))
init_map1 = init_mapfile1['data']




# Create source data structure and initialize state map
# source_graph = ColumnDataSource(init_data)
source_map = ColumnDataSource(init_map)
# Erase the underlying data to reduce the html filesize (will be loaded upon user tap feedback)
# source_graph.data = {k: source_graph.data[k][-2:-1] for k in source_graph.data}


"""
%% Setup color map
________________________________________________________________________________
"""
palette = Turbo256[128:-1:5]
color_mapper = LinearColorMapper(
    palette=palette, low=0, high=2 * len(palette))

color_bar = ColorBar(
    color_mapper=color_mapper,
    label_standoff=2, border_line_color=None, location=(0, 0),
    bar_line_alpha=0.5,
    major_label_text_align='left',
)

"""
# Make the map
________________________________________________________________________________
"""
p_map = figure(
    title=latest_data_date.strftime('%Y-%m-%d'),
    # x_range=minmax(DS_worlds_map.data['xc']), y_range=minmax(DS_worlds_map.data['yc']),
    # x_range=(-1.4e7,-7.4e6),
    # y_range=(2.88e6,6.28e6),
    # sizing_mode='stretch_width',
    tools="tap,pan,wheel_zoom,reset,save", active_tap='tap',
    toolbar_location='left',
    x_axis_location=None, y_axis_location=None,
    x_axis_type="mercator", y_axis_type="mercator",
    sizing_mode='scale_width',
    aspect_ratio=2,
    match_aspect=True,
)
p_map.grid.grid_line_color = None
bztool_s = BoxZoomTool(match_aspect=True)
p_map.add_tools(bztool_s)
p_map.toolbar.active_drag = None  # bztool_s

# Add the map tiles
tile_provider = get_provider(CARTODBPOSITRON_RETINA)
p_map.add_tile(tile_provider)

# Add the states1
p_map_mpoly = p_map.multi_polygons(
    xs='x', ys='y', source=source_map,
    fill_color={'field': 'cases_avg_per_100k',
                'transform': color_mapper},
    fill_alpha=0.6,
    line_color="white",
    line_width=0.5,
)
p_map.add_layout(color_bar, 'right')
# Add the hover tool to show the state name and number of counties
hoverm = HoverTool()
hoverm.tooltips = [
    ('Name', "@name"),
    ("Population", "@population{0,0.}"),
    #("Current COVID Statistics","{}".format('-'*15)),
    ('Cases', "@cases{0,0.}"),
    ('Cases Avg per 100k', "@cases_avg_per_100k{0,0.}"),
    ('Deaths Avg per 100k', "@deaths_avg_per_100k{0,0.}"),
]
p_map.add_tools(hoverm)

# # Add taptool to select from which state to show all the counties
# with open(javascript_path + 'callback_map.js', 'r') as f:
#     callback_world_map = f.read()
# callbacktap = CustomJS(args={'ext_datafiles': ext_datafiles,
#                              'p_graph_glyphs': p_graph_glyphs,
#                              'p_graph': p_graph,
#                              },
#                        code=callback_world_map)
# taptool = p_map.select(type=TapTool)
# taptool.callback = callbacktap

# Explicitly initialize x range
p_map.x_range = DataRange1d()

# Reset on doubltap
p_map.js_on_event('doubletap', CustomJS(args={'p': p_map, }, code="""
    p.reset.emit()
    """))

"""
# Map widgets
------------------------------------------------------------------------------------------------
"""
# Get the callback script used for many of the widgets
with open(javascript_path + 'callback_map_widgets.js', 'r') as f:
    callback_widgets = f.read()

# Level radio buttons
radio_labels = ["Play \u25B6", "Step \u23ef", "Pause \u23f8"]
radioGroup_play_controls = RadioButtonGroup(
    labels=radio_labels, active=2, name='radioGroup_play_controls')
radioGroup_play_controls.js_on_click(CustomJS(args={
            'event': 'radioGroup_play_controls',
            'ext_datafiles': ext_datafiles,
            'mpoly': p_map_mpoly,
            'source_map': source_map,
            'p_map': p_map,
             },
    code=callback_widgets))

# %% Make date range slider
date_range_slider = DateRangeSlider(value=((latest_data_date-pd.DateOffset(months=1)), (latest_data_date)),
                                    start=(oldest_date_date), end=(latest_data_date),
                                    name='date_range_slider')
date_range_slider.js_on_change("value", CustomJS(args={
            'event': 'date_range_slider',
            'ext_datafiles': ext_datafiles,
            'mpoly': p_map_mpoly,
            'source_map': source_map,
            'p_map': p_map,
},
    code=callback_widgets
))

# Minumum time between animations on play, Spinner
spinner_minStepTime = Spinner(title="",
    low=0, high=5, step=0.1, value=0.2, width=100,format=FuncTickFormatter(code="""
    return tick.toString()+" sec"
"""),
    name='spinner_minStepTime')

# Respond to taps on the graph
# p_graph.js_on_event('tap', CustomJS(args={
#             'event': 'graph_tap',
#             'ext_datafiles': ext_datafiles,
#             'mpoly': p_map_mpoly,
#             'source_map': source_map,
#             'p_map': p_map,
#             'source_graph': source_graph,
#             'p_graph': p_graph,
# },
#     code=callback_widgets
# ))

# Selectors for the map
selectors_map = []
opts = [k for k in init_data.keys() if isinstance(init_data[k], int)
        or isinstance(init_data[k], float)]
opts = sorted(opts)
select = Select(title="Data For Map Coloring:",
                value=p_map_mpoly.glyph.fill_color['field'],
                options=opts)
select.js_on_change("value", CustomJS(args={
    'ext_datafiles': ext_datafiles,
    'mpoly': p_map_mpoly,
}, code="""
        //console.log('select: value=' + this.value, this.toString())
        mpoly.glyph.fill_color.field = this.value
        mpoly.data_source.change.emit()
    """))
selectors_map.append(select)

# Range setting for map
map_range_widgets = []
text_input = TextInput(value=str(color_mapper.high), title="High Color")
text_input.js_on_change("value", CustomJS(args={
    'ext_datafiles': ext_datafiles,
    'color_mapper': color_mapper,
}, code="""
    color_mapper.high = Number(this.value)
"""))
map_range_widgets.append(text_input)
text_input = TextInput(value=str(color_mapper.low), title="Low Color")
text_input.js_on_change("value", CustomJS(args={
    'ext_datafiles': ext_datafiles,
    'color_mapper': color_mapper,
}, code="""
     color_mapper.low = Number(this.value)
"""))
map_range_widgets.append(text_input)



# %% Make heading for the whole thing
"""
# %% Make heading for the whole thing
"""
heading = Div(text="""
<h1> Time Animated COVID-19 Data Mapped For US Counties, NYT Styled</h1>
<p>Shows all the counties colored according to last weeks average number of new COVID-19 cases per day with county population normalization  (number of people per 100k).</p>
<ul>
	<li>Higher color number corresponds to faster spread of the virus.</li>
    <li>On the left of each graph thera are tools to zoom/pan/reset/save.</li>
	<li>On Mobile: Use two finger to scroll the page.</li>
    <li>Data last updated on: {data_update} </li>
</ul>

<h3> Tap on any country to show the COVID19 data time history graph below. </h3>
""".format(
    data_update=pd.to_datetime(latest_data_date).strftime('%Y-%m-%d'),
    graph_update=pd.Timestamp.now().strftime('%Y-%m-%d'),
))

footer = Div(text="""
<h3> Sources </h3>
<ul>
    <li>GitHub repository for this project: <a href="https://github.com/thedrdos/covid-map"> https://github.com/thedrdos/covid-map </a>. </li>
    <li>Produced using Python with Bokeh and other modules.</li>
	<li>Data sourced from <a href="https://github.com/nytimes/covid-19-data"> The New York Times COVID Data GitHub Repository</a>. </li>
</ul>
""")

data_notes = Div(text="""
<h4> Data Defintions: </h4>
<ul>
    <li>Documented at <a href="https://github.com/nytimes/covid-19-data"> The New York Times COVID Data GitHub Repository</a>. </li>
    <li>Mimics the non-animated <a href="https://www.nytimes.com/interactive/2021/us/covid-cases.html"> interactive map from The New York Times Online</a>.</li>
</ul>
""")

# %% Combine all the graphs
"""
# %% Combine all the graphs
________________________________________________________________________________
"""

# Layout the figures and show them
p_map.sizing_mode = 'scale_width'
# p_graph.sizing_mode = 'scale_width'
print('Making mobile output version')
lout_mobile = layout([
                heading,
                [selectors_map]+map_range_widgets,
                    #[radioGroup_level_select,
                    #button_continental_us_only],
                p_map,
                [spinner_minStepTime,radioGroup_play_controls ,date_range_slider],
                footer
                ])
lout_mobile.margin = (4, 20, 4, 20)  # top, right, bottom, left
lout_mobile.sizing_mode = 'scale_width'
save(lout_mobile,filename=output_filename+'_mobile.html',template=template_ext_js(['jquary', 'pako']))
