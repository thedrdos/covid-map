// CustomJS: Tap callback for the state map
//
// Provided arguments:
// args={'patches_counties': patches_counties,
//      'index_to_world_name':init_map['name'],
//      'glyphs_covid_world':glyphs_covid_world,
//      'ext_datafiles':ext_datafiles,
//      'p_county_map':p_county_map,
//      'p_world_covid':p_world_covid, # state covid data plot
//      'tb':[buttons['state_covid_data'],buttons['reset_world_covid_data'],buttons['reset_county_map']],
//      'datetime_made': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
if (cb_data.source.selected.indices.length > 0) {
  var ind = cb_data.source.selected.indices[0]
  var location = cb_data.source.data['location'][ind]
  var state_name = cb_data.source.data['name'][ind]
  var filename_data = ext_datafiles['rel_path'] + ext_datafiles['location_to_filename'][location] + '.json.gz'
  var filename_map = ext_datafiles['rel_path'] + ext_datafiles['location_to_filename'][location] + '_map.json.gz'
  // console.log(location)

  // Read the data file and Update
  readJSONgz_fun(filename_data, function() {
    var from_datafile = JSON.parse(pako.inflate(this.response, {
      to: 'string'
    }));
    // console.log('Datafile read: ' + location + ' at ' + filename_data)
    from_datafile['data'] = rep_nan_code(from_datafile['data'], from_datafile['nan_code'])
    from_datafile['data'] = correct_date_format(from_datafile['data'])
    for (var i = 0; i < glyphs_covid_world.length; i++) {
      glyphs_covid_world[i].data_source.data = from_datafile['data'] //DS_worlds_COVID[state_name].data
      glyphs_covid_world[i].data_source.change.emit();
    }
  })

  // // Read the map file and Update
  // readJSONgz_fun(filename_map, function() {
  //   var from_datafile = JSON.parse(pako.inflate(this.response, {
  //     to: 'string'
  //   }));
  //   // console.log('Datafile read: ' + location + ' at ' + filename_map)
  //   from_datafile['data'] = rep_nan_code(from_datafile['data'], from_datafile['nan_code'])
  //   patches_counties.data_source.data = from_datafile['data']
  //   patches_counties.data_source.change.emit(); // Update the county patches
  //   p_county_map.reset.emit(); // Reset the county figure, otherwise panning and zooming on that fig will persist despite the change
  // })
  // p_county_map.visible = true

  // Enable buttons
  for (var i = 0; i < tb.length; i++) {
    tb[i].visible = true
  }
  // Update title
  p_world_covid.title.text = state_name + ": COVID data time history, population normalized" //   (Tap a state on the map above to show the corresponding data here)"
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
