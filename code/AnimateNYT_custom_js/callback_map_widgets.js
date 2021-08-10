// CustomJS: Tap callback for the state map
//
// Provided arguments:
// args={      'event':ev,
//             'mpoly':mpoly,
//             'ext_datafiles': ext_datafiles,
//             'source_map': source_map,
//             'p_map':p_map,
// ),
// Interprete and respond
var ind = mpoly.data_source.selected.indices
var location = 'None'
var filename_data = ''
var filename_map = ''
var hash = ''
// Get other models/tooltips
const button_continental_us_only = window.Bokeh.documents[0].get_model_by_name('button_continental_us_only')
const radioGroup_level_select = window.Bokeh.documents[0].get_model_by_name('radioGroup_level_select')
// const span_play_position = window.Bokeh.documents[0].get_model_by_name('span_play_position')
const date_range_slider = window.Bokeh.documents[0].get_model_by_name('date_range_slider')
const spinner_minStepTime = window.Bokeh.documents[0].get_model_by_name('spinner_minStepTime')
const radioGroup_play_controls = window.Bokeh.documents[0].get_model_by_name('radioGroup_play_controls')
const button_toggle_states_outline = window.Bokeh.documents[0].get_model_by_name('button_toggle_states_outline')
const play_controls = {
  'play': 0,
  'step': 1,
  'pause': 2,
}

switch (event) {
  // case 'graph_tap':
  //   // Find nearest date in data and its index
  //   var near_date = find_in_sorted_array(cb_obj.x, source_graph.data['date'])
  //   var day = new Date(near_date['value'])
  //   var sval = date_range_slider.value;
  //   date_range_slider.value = [day.getTime(), sval[1]];
  //   break;

  // case 'button_continental_us_only':
  //   if (button_continental_us_only.active) {
  //     radioGroup_level_select.active = 1;
  //     var data = source_map.data;
  //     var new_data = {};
  //     for (var key in data) {
  //       new_data[key] = data[key];
  //     }

  //     for (var i = 0; i < new_data['location'].length; i++) {
  //       if (continental_states.includes(new_data['location'][i])) {
  //         // do nothing
  //       } else {
  //         // remove non-continental state
  //         for (var key in new_data) {
  //           new_data[key].splice(i, 1)
  //         }
  //       }
  //     }
  //     source_map.data = new_data;
  //     source_map.change.emit();
  //   }

  //   break;

  // case 'level_select':
  //   switch (radioGroup_level_select.active) { // 0 world, 1 states, 2 counties
  //     case 0:
  //       location = 'Earth'
  //       p_map.x_range.names = [];
  //       p_map.reset.emit();
  //       break;
  //     case 1:
  //       location = 'US';
  //       break;
  //     case 2:
  //       if (ind.length > 0) {
  //         location = mpoly.data_source.data['location'][ind[0]]
  //         if (location.endsWith(', US')) {
  //           p_map.x_range.names = [];
  //           p_map.reset.emit();
  //         } else {
  //           location = '';
  //         }
  //       } else {
  //         location = '';
  //       }
  //       if (location.length < 1) {
  //         alert('First Select a State On The Map')
  //         this.active = 1;
  //       }
  //       break;
  //   }

  //   if (location.length > 0) {
  //     //console.log(location + ' selected')
  //     if (location in ext_datafiles['location_to_mapfilename']) {
  //       filename_map = ext_datafiles['location_to_mapfilename'][location] + '.json.gz'
  //       //console.log(filename_map)
  //       //console.log(ext_datafiles['rel_path'] + filename_map)
  //       readJSONgz_fun(ext_datafiles['rel_path'] + filename_map, function() {
  //         var data = JSON.parse(pako.inflate(this.response, {
  //           to: 'string'
  //         }));
  //         //console.log('Mapfile read:')
  //         //console.log(data)
  //         if (data['data']['x'].length < 1) {
  //           //Map is empty
  //         } else {
  //           // Map is provided
  //           mpoly.data_source.data = data['data']
  //           // Show the right date in the title
  //           var day = new Date(data['data']['latestDate'][0] / 1e6);
  //           const date_format_options = {
  //             year: 'numeric',
  //             month: 'short',
  //             day: 'numeric',
  //             timeZone: 'UTC'
  //           };
  //           const date_format_options2 = {
  //             weekday: 'long',
  //             timeZone: 'UTC'
  //           };
  //           // Including UTC as the timezone is important
  //           var day_str = day.toLocaleDateString("en-US", date_format_options) + ", " + day.toLocaleDateString("en-US", date_format_options2)
  //           p_map.title.text = day_str;

  //           mpoly.data_source.change.emit()

  //           if (location == 'US') {
  //             if (button_continental_us_only.active) {
  //               button_continental_us_only.active = false;
  //               button_continental_us_only.active = true;
  //             }
  //           }
  //         }
  //       })
  //     }
  //   }
  //   break;

  case 'button_toggle_states_outline':
    p_statesmap_mpoly.visible = !p_statesmap_mpoly.visible;
    break;

  case 'date_range_slider':
    var start_date = new Date(date_range_slider.value[0])
    var end_date = new Date(date_range_slider.value[1])
    var day = start_date;
    // span_play_position.location = day.getTime();

    switch (radioGroup_play_controls.active) {
      case play_controls.step:
        radioGroup_play_controls.active = play_controls.pause;
        break;
      case play_controls.play:
      case play_controls.pause:
        break;
    }

    // No break from date_range_slider, directly into radioGroup_play_controls
    case 'radioGroup_play_controls':
      switch (radioGroup_play_controls.active) {
        case play_controls.pause:
          date_range_slider.disabled = false;
          break;
        case play_controls.step:
        case play_controls.play:
          date_range_slider.disabled = true;
          var start_date = new Date(date_range_slider.value[0])
          var end_date = new Date(date_range_slider.value[1])
          var day = start_date;

          var date_format_options = {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            timeZone: 'UTC'
          };
          var date_format_options2 = {
            weekday: 'long',
            timeZone: 'UTC'
          };
          // Including UTC as the timezone is important
          var day_str = day.toLocaleDateString("en-US", date_format_options) + ", " + day.toLocaleDateString("en-US", date_format_options2)

          var next_day = new Date(day)
          next_day.setDate(next_day.getDate() + 1)


          // Find all locations on the map
          var locations = mpoly.data_source.data['location']
          var cnt = 0
          var t0 = performance.now()
          
          // Load data for each location, and update the map with the data for the given date
          //for (const [n, loc] of locations.entries()) 
          
          const sel_date = find_in_sorted_array(day.getTime()*1e6, ext_datafiles['date_to_filename']['dates'])
          {
              readJSONgz_fun(ext_datafiles['rel_path'] + ext_datafiles['date_to_filename'][sel_date['value'].toString()] + '.json.gz', function() {
              var data = JSON.parse(pako.inflate(this.response, {
                to: 'string'
              }));
              // data['data'] = rep_nan_code(data['data'], data['nan_code'])
              // data['data'] = correct_date_format(data['data'])

              // Load data for each location, and update the map with the data for the given date
              for (const [n, loc] of locations.entries()) {
                if (loc in data['data']){
                  for (const k in mpoly.data_source.data) {
                    if (k in data['data'][loc]) {
                      mpoly.data_source.data[k][n] = data['data'][loc][k]
                    }
                  }
                }
              }
              mpoly.data_source.data = rep_nan_code(mpoly.data_source.data, data['nan_code'])

              // Update the map data with the data for the selected date
              // for (const k in mpoly.data_source.data) {
              //   if (k in data['data']) {
              //     mpoly.data_source.data[k][n] = data['data'][k][sel_date['index']]
              //   }
              // }

              cnt += 1
              // if (cnt >= locations.length) 
              {
                // Finished updating map, set map title
                p_map.title.text = day_str;
                mpoly.data_source.change.emit()

                // Finish up step and ready for next, when minimum time elapsed
                var dt = performance.now() - t0
                setTimeout(function() {
                  // Update DateRangeSlider and play controls
                  if (next_day.getTime() > end_date.getTime()) {
                    date_range_slider.value = [end_date.getTime(), end_date.getTime()];
                    radioGroup_play_controls.active = play_controls.pause;
                  } else {
                    date_range_slider.value = [next_day.getTime(), end_date.getTime()];
                  }
                  date_range_slider.change.emit()

                  switch (radioGroup_play_controls.active) {
                    case play_controls.step:
                      // if stepping, then goto pause which will trigger enabling the DateRangeSlider
                      radioGroup_play_controls = play_controls.pause;
                      break;
                  }
                }, spinner_minStepTime.value*1000 - dt);
              }
            }, 10000)
          }
          break;
      }
      break;
}


// ----------------------------------------
// Support Functions:
// ----------------------------------------


// Find nearest value and index
function find_in_sorted_array(x, sorted_array) {
  var i = 0;
  while (x > sorted_array[i] & i < sorted_array.length - 1) {
    i += 1
  }
  return {
    'value1e6': sorted_array[i]*1e6,
    'value': sorted_array[i],
    'index': i
  }
}

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
