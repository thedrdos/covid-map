// Available arguments:
// 'mpoly': mpoly,
// 'ext_datafiles': ext_datafiles,
// 'line': line,

//console.log(cb_obj)
//console.log(cb_obj.x)

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
// Correct the date format of dates (not sure if I'll need this)
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

// Find nearest value and index
function find_in_sorted_array(x, sorted_array) {
  var i = 0;
  while (x > sorted_array[i] & i < sorted_array.length - 1) {
    i += 1
  }
  return {
    'value': sorted_array[i],
    'index': i
  }
}

// Find nearest date in data and its index
var near_date = find_in_sorted_array(cb_obj.x, line.data_source.data['date'])
//console.log(near_date)
var day = new Date(near_date['value']).toLocaleDateString("en-US")
console.log("Chosen day: " + day)

// Find all locations on the map
var locations = mpoly.data_source.data['location']
var cnt = 0
var t0 = performance.now()
// Load data for each location, and update the map with the data for the given date
for (const [n, loc] of locations.entries()) {
  readJSONgz_fun(ext_datafiles['rel_path'] + ext_datafiles['location_to_filename'][loc] + '.json.gz', function() {
    var data = JSON.parse(pako.inflate(this.response, {
      to: 'string'
    }));
    data['data'] = rep_nan_code(data['data'], data['nan_code'])
    data['data'] = correct_date_format(data['data'])

    const sel_date = find_in_sorted_array(cb_obj.x, data['data']['date'])

    // Update the map data with the data for the selected date
    for (const k in mpoly.data_source.data) {
      if (k in data['data']) {
        mpoly.data_source.data[k][n] = data['data'][k][sel_date['index']]
      }
    }

    cnt += 1
    if (cnt >= locations.length) {
      //console.log('count: '+cnt.toString())
      //console.log('time: '+(performance.now()-t0).toString())
      mpoly.data_source.change.emit()
    }
  }, 10000)
}
