"""
Created: July 2020
Author: TheDrDOS

Extend the json module with functions to support more actions.

Example:
    import json_extra as je
    import numpy as np
    d = {'npa':np.arange(0,10),'ar':list(range(0,4)),'str':"some string"}
    filename = 'data.json'
    # write to string, human readable
    dumped = je.dumped(d)
    # write to file, not human readable (all in one line, no sorting or indenting)
    je.dump(d,filename) # makes, opens and closes the file for you also
"""

import json
import os
import numpy as np

class NumpyEncoder(json.JSONEncoder):
    """
    Special json encoder for numpy types
    https://stackoverflow.com/questions/26646362/numpy-array-is-not-json-serializable

    Support for supporting nested numpy int/float/ndarray in json using
    json.jsdump(data,cls=NumpyEncoder)
    """
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

def dumps(data,human_readable=True,**kwargs):
    """
    Modify the json.dumps() with the NumpyEncoder
    Input the data to be converted
    Output the json string
    """
    if human_readable:
        dumped = json.dumps(data,cls=NumpyEncoder,**kwargs)
    else:
        dumped = json.dumps(data,cls=NumpyEncoder,**kwargs,indent=4, sort_keys=True)
    return dumped

def dump(data,file_path,human_readable=True,**kwargs):
    """
    Modify json.dump() with the NumpyEncoder and opens/closes file
    Input  data and outfile
    Output None (just writes to the file)
    """
    if human_readable:
        with open(file_path, 'w', encoding ='utf8') as outfile:
            json.dump(data, outfile,cls=NumpyEncoder,indent=4, sort_keys=True,**kwargs)
    else:
        with open(file_path, 'w', encoding ='utf8') as outfile:
            json.dump(data, outfile,cls=NumpyEncoder,**kwargs)
    return None
