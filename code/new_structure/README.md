# Working on rewriting the data gathering/processing/storing
## Motivation
Make the data structures
* More consistent and simple
* Facilitate more efficient processing
* Avoid Bokeh bug where patches defined by multiple polygons separated by `NaN` seem to result in multiple overlaying patches (`fill_alpha` will look wrong).

## Proposed Data Structure
Two main types of data, ones affiliated with maps (patches) and ones with graphs (lines/bars).  Represented below with Python ish descriptive pseudo code:

```python
# List of strings, locations like names of states or full names of counties
location = ["US","Ohio, US","Montgomery, Ohio, US", ...]

# Dictionary of map data
MapData = {
  location[0]:
      {
      'location': location[0],   # string, key used here,
      'filename': '#_map.json', # string with json file for this entry
      'nan_code': -123456789,   # number, used to encode NaN in the json
      'data': { # ColumnDataSource compliant dictionary, defining patches
            'x': [[],[],[],...], # list of number lists, each a patch corresponding to a sublocation
            'y': [[],[],[],...], # same for y coordinates
            'name':['sublocation','sublocation',...]
            # names of corresponding sublocations,
            # name is non-unique as one sublocation can be tied to multiple patches
            'property with current covid data': [ , , , ...] # number for each sublocations
            :
            : # more properties
            },
      }
  :
  : # more locations
}

# Dictionary of graph data
GraphData = {
  location[0]:
      {
      'location': location[0],   # string, key used here,
      'filename': '#_graph.json', # string with json file for this entry
      'nan_code': -123456789,   # number, used to encode NaN in the json
      'data': { # ColumnDataSource compliant dictionary, defining patches
            'date': [[],[],[],...], # list of timedates corresponding to time history
            'property with covid data history': [ , , , ...] # number for each date entry
            :
            : # more properties
            },
      }
  :
  : # more locations
}

location_to_datafile = {
    location[0]: {
        'map': '#_map.json', # datafile with the MapData[location[0]], can be empty if lowest location level
        'graph': '#_graph.json',  # datafile with the GraphData[location[0]], should never be empty
    }
    :
    : # more locations
}
```
