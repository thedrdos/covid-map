// CustomJS: Tap callback for the county map
//
// Provided arguments:
// args={'index_to_state_name':init_map['name'],
//                              'glyphs_covid_county':glyphs_covid_county,
//                              'ext_datafiles': ext_datafiles,
//                              'p_county_covid': p_county_covid,
//                              'tb':[buttons['county_covid_data'],buttons['reset_county_covid_data']],
//                              }
if (cb_data.source.selected.indices.length > 0) {
  var ind = cb_data.source.selected.indices[0]
  var location = cb_data.source.data['location'][ind]
  var county_name = cb_data.source.data['name'][ind]
  var county_state_name = location.substring(0, location.length - 4)
  var filename_data = ext_datafiles['rel_path'] + ext_datafiles['location_to_filename'][location] + '.json.gz'
  // console.log(location)

  // Read the data file and Update
  readJSONgz_fun(filename_data, function() {
    var from_datafile = JSON.parse(pako.inflate(this.response, {
      to: 'string'
    }));
    // console.log('Datafile read: ' + location + ' at ' + filename_data)
    from_datafile['data'] = rep_nan_code(from_datafile['data'], from_datafile['nan_code'])
    from_datafile['data'] = correct_date_format(from_datafile['data'])
    for (var i = 0; i < glyphs_covid_county.length; i++) {
      glyphs_covid_county[i].data_source.data = from_datafile['data'] //DS_States_COVID[state_name].data
      glyphs_covid_county[i].data_source.change.emit();
    }
  })

  // Enable Buttons
  for (var i = 0; i < tb.length; i++) {
    tb[i].visible = true
  }
  // Update title
  p_county_covid.title.text = county_state_name + ": COVID data time history, population normalized"
}


// ----------------------------------------
// Support Functions:
// ----------------------------------------

// Replace nan with nan_code in a dictionary of arrays
function rep_nan_code(dic, nan_code) {
  var inds
  for (var key in dic) {
    if (Array.isArray(dic[key])) {
      dic[key] = array_element_replace(dic[key], nan_code, NaN)
    }
  }
  return dic;
}

// Replace old_value with new_value in an array
function array_element_replace(arr, old_value, new_value) {
  for (var i = 0; i < arr.length; i++) {
    if (Array.isArray(arr[i])) {
      if (arr[i].length > 1) {
        arr[i] = array_element_replace(arr[i], old_value, new_value)
      } else {
        if (arr[i] === old_value) {
          arr[i] = new_value;
        }
      }
    } else {
      if (arr[i] === old_value) {
        arr[i] = new_value;
      }
    }
  }
  return arr;
}

// Correct dates for date data interetation
function correct_date_format(dic, key = 'date') {
  const mul = 1e-6
  dic[key] = dic[key].map(function(a) {
    return a * mul;
  })
  return dic
}

// Reading gzip json data
function readJSONgz_fun(file, fun_onload, timeout = 2000) {
  // Based on https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest/Synchronous_and_Asynchronous_Requests
  var data;
  var request = new XMLHttpRequest();
  request.responseType = 'arraybuffer';
  request.ontimeout = function() {
    console.error("The request for " + file + " timed out.");
  };
  request.timeout = timeout;
  request.onload = fun_onload;
  request.open('GET', file);
  request.send();
  return request;
}
