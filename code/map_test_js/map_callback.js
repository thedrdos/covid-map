// Available arguments:
//             'event':ev,
//             'mpoly':mpoly,
//             'ext_datafiles': ext_datafiles,
//             'source_map': source_map,
//             'line':line,

// Some basics:
console.log('Tap Event Callback:')
// console.log(cb_obj)
// console.log(cb_obj.event_name)
// console.log('Look at range')
// console.log(this)
// console.log(this.origin)
console.log(this.origin.x_range)
// console.log(this.origin.x_range.range_padding)
console.log(this.origin.x_range.start)
console.log(this.origin.x_range.end)
// console.log(this.origin.x_range.bounds)
// console.log(this.origin.x_scale)
// var xend = this.origin.x_range.end
// if (xend>0){
//   this.origin.x_range.end = 0
// }
// else{
//   this.origin.x_range.end=undefined
// }

this.origin.change.emit()
console.log('Done looking at range')
// These two are equivalent, both yield the index of the selected glyph or empty if none
//console.log(source_map.selected.indices)
//console.log(mpoly.data_source.selected.indices)

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

// Interprete and respond to the tap
var ind = mpoly.data_source.selected.indices
var location = 'None'
var filename_data = ''
var filename_map = ''
var hash = ''
if (ind.length > 0) {
  location = mpoly.data_source.data['location'][ind[0]]
  console.log(location + ' selected')
  if (location in ext_datafiles['location_to_filename']) {
    hash = ext_datafiles['location_to_filename'][location]
    filename_data = hash + '.json.gz'
    console.log(filename_data)
    console.log(ext_datafiles['rel_path'] + filename_data)
    readJSONgz_fun(ext_datafiles['rel_path'] + filename_data, function() {
      var data = JSON.parse(pako.inflate(this.response, {
        to: 'string'
      }));
      console.log('Datafile read: '+location+' at '+filename_data)
      data['data'] = rep_nan_code(data['data'], data['nan_code'])
      data['data'] = correct_date_format(data['data'])
      console.log(data)
      line.data_source.data = data['data']
      line.data_source.change.emit()
    })
  }
  if (location in ext_datafiles['location_to_mapfilename']) {
    filename_map = ext_datafiles['location_to_mapfilename'][location] + '.json.gz'
    console.log(filename_map)
    console.log(ext_datafiles['rel_path'] + filename_map)
    readJSONgz_fun(ext_datafiles['rel_path'] + filename_map, function() {
      var data = JSON.parse(pako.inflate(this.response, {
        to: 'string'
      }));
      console.log('Mapfile read:')
      console.log(data)
      if (data['data']['x'].length < 1) {
        console.log('Map Empty')

      } else {
        console.log('Map Provided')
        if (cb_obj.event_name == 'doubletap') {
          mpoly.data_source.data = data['data']
          mpoly.data_source.change.emit()
          if (location == 'US'){
            // cb_obj.origin.x_range.follow = "start"
            // cb_obj.origin.x_range.follow_interval = 16600000
            cb_obj.origin.names = ['DummyNothing']
            cb_obj.origin.x_range.end = -0.7e7
            cb_obj.origin.x_range.start = -3.7e7
            cb_obj.origin.y_range.start = 2.88e6
            cb_obj.origin.change.emit()
          }
          else{
            // cb_obj.origin.x_range.follow = null
            // cb_obj.origin.x_range.follow_interval = null
            cb_obj.origin.names = []
            cb_obj.origin.x_range.end = null
            cb_obj.origin.x_range.start = null
            cb_obj.origin.y_range.start = null
            cb_obj.origin.y_range.end = null
            cb_obj.origin.change.emit()
          }
          console.log(cb_obj.origin.x_range)
          console.log(cb_obj.origin.x_range.follow)
          console.log(cb_obj.origin.x_range.follow_interval)
          console.log(cb_obj.origin.x_range.names)
        }
      }
    })
  }

// setTimeout(function ()
// {  // if (location == 'US'){
//       // cb_obj.origin.x_range.start = -1.39e7
//       // cb_obj.origin.x_range.end   = -0.73e7
//       console.log('Change to manual bounds')
//       var yr = [cb_obj.origin.y_range.start,cb_obj.origin.y_range.end]
//       var xr = [cb_obj.origin.x_range.start,cb_obj.origin.x_range.end]
//       var xrnew = [-1.4e7,-7.4e6]
//       var ar = cb_obj.origin.aspect_ratio
//       var yrnew = [0.66e7-((xrnew[1]-xrnew[0])/ar), 0.66e7]
//       // console.log(xr)
//       // console.log(yr)
//       // console.log(ar)
//       cb_obj.origin.x_range.setv({'start':xrnew[0],'end':xrnew[1]})
//       cb_obj.origin.y_range.setv({'start':yrnew[0],'end':yrnew[1]})
//       // cb_obj.origin.x_range.end = xrnew[0]
//       // cb_obj.origin.x_range.end = xrnew[1]
//       // cb_obj.origin.y_range.end = yrnew[0]
//       // cb_obj.origin.y_range.end = yrnew[1]
//
//       console.log(xrnew)
//       console.log(yrnew)
//   // }
//   // else{
//   //       console.log('Change to automatic bounds')
//   //       cb_obj.origin.x_range.start = undefined
//   //       cb_obj.origin.x_range.end   = undefined
//   // }
//   cb_obj.origin.change.emit()
//   // yr = [cb_obj.origin.y_range.start,cb_obj.origin.y_range.end]
//   // xr = [cb_obj.origin.x_range.start,cb_obj.origin.x_range.end]
//   // console.log(xr)
//   // console.log(yr)
// //  cb_obj.origin.x_range.change.emit()
// //  cb_obj.origin.y_range.change.emit()
// }, 2000)

}
else{
  console.log(location + ' selected')
  if (cb_obj.event_name == 'doubletap') {
    readJSONgz_fun(ext_datafiles['rel_path'] + ext_datafiles['location_to_mapfilename']['Earth'] + '.json.gz', function() {
      var data = JSON.parse(pako.inflate(this.response, {
        to: 'string'
      }));
      console.log('Mapfile read: Earth')
      mpoly.data_source.data = data['data']
      mpoly.data_source.change.emit()
      // cb_obj.origin.x_range.start = undefined
      // cb_obj.origin.x_range.end   = undefined;
      // cb_obj.origin.change.emit()
    })
  }
}
