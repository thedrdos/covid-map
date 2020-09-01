# "New" data gathering/processing/storing
## Motivation
Make the data structures
* More consistent and simple
* Facilitate more efficient processing
* Avoid Bokeh bug where patches defined by multiple polygons separated by `NaN` seem to result in multiple overlaying patches (`fill_alpha` will look wrong). This dataset will rely on using multi_polygons instead.

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
            'x': list-of-list-of-list-of-lists MultiPolygon Bokeh input, # list of number lists, each a patch corresponding to a sublocation
            # Format description:
            # [multipolygon[0], multipolygon[1], ...]
            # multipolygon[i] correspond to sublocation[i]
            # multipolyton[i] = [polygon[0],polygon[1],...]
            # polygon[k] is the k-th polygon in multipolygon[i]
            # polygon[k] = [exterior_x,interior_x[0],interior_x[1],...]
            # exterior_x is a list of exterior points of polygon[k]
            # interior_x[n] is the n-th list of interior points of polygon[k], interior_x can be empty
            # In summary: (numbering brackets for clarity)
            # 1[multipolygons
            #   2[multipolygon
            #     3[polygon
            #         4[exterior_boundary_points
            #           4],
            #         4[interior_boundary_points
            #           4],
            # there can be many or no lists of interior boundaries
            #          ... 3],... 2],... 1]
            'y': [[[[],...],...],...], # same for y coordinates
            'name':[sublocation[0],sublocation[1],...]
            # names of corresponding sublocations,
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
      'extra': {# additional data that doesn't fit the ColumnDataSource structure, includes population}
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
