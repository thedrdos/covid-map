// CustomJS: Tap callback for the state map
//
// Provided arguments:
// args={'patches_counties': patches_counties,
//      'glyphs_covid_state':glyphs_covid_state,
       // 'state_data': state_data,
       // 'county_map': county_map,
       // 'nan_code': nan_code,
//      'p_county_map':p_county_map,
//      'p_state_covid':p_state_covid, # state covid data plot
//      'tb':[buttons['state_covid_data'],buttons['reset_state_covid_data'],buttons['reset_county_map']],
//      'datetime_made': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
if (cb_data.source.selected.indices.length > 0) {
  var ind = cb_data.source.selected.indices[0]
  var location = cb_data.source.data['location'][ind]
  var state_name = cb_data.source.data['name'][ind]
  // console.log(location)

  // Read the data  and Update
  var data = state_data[location]
  data = rep_nan_code(data, nan_code)
  data = correct_date_format(data)
  for (var i = 0; i < glyphs_covid_state.length; i++) {
    glyphs_covid_state[i].data_source.data = data //DS_States_COVID[state_name].data
    glyphs_covid_state[i].data_source.change.emit();
  }

  // Read the map and Update
  var map = county_map[location]
  map = rep_nan_code(map, nan_code)
  patches_counties.data_source.data = map
  patches_counties.data_source.change.emit(); // Update the county patches
  p_county_map.reset.emit(); // Reset the county figure, otherwise panning and zooming on that fig will persist despite the change
  p_county_map.visible = true
  // Enable buttons
  for (var i = 0; i < tb.length; i++) {
    tb[i].visible = true
  }
  // Update title
  p_state_covid.title.text = state_name + ": COVID data time history, population normalized" //   (Tap a state on the map above to show the corresponding data here)"
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
