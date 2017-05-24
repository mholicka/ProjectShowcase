var map;
// function to get a coldfusion serialized return into a JS object as rows.
var queryToObject = function(q) {
    var col, i, r, _i, _len, _ref, _ref2, _results;
    _results = [];
    for (i = 0, _ref = q.ROWCOUNT; 0 <= _ref ? i < _ref : i > _ref; 0 <= _ref ? i++ : i--) {
        r = {};
        _ref2 = q.COLUMNS;
        for (_i = 0, _len = _ref2.length; _i < _len; _i++) {
            col = _ref2[_i];
            r[col.toLowerCase()] = q.DATA[col][i];
        }
        _results.push(r);
    }
    return _results;
};

// checker to see if an object is empty.
function isEmpty(obj) {
    for (var key in obj) {
        if (obj.hasOwnProperty(key))
            return false;
    }
    return true;
}
// object is created based on the address to contain all the equipment with all the information needed regarding
// the property.
//NOTE: since this creates objects within objects, all equipment fields start with eq_, so they are easily seperated
function eqAtAddress(data) {
    var final = {};
    var eqArr = {};
    var eqKeys = [];
    for (var entry in data) {
        var curr_entry = data[entry];
        var keys = Object.getOwnPropertyNames(curr_entry);
        if (isEmpty(final[curr_entry.address])) {
            eqArr = {};
            eqArr[curr_entry.eq_equipid] = {};
            final[curr_entry.address] = {};
            // of in JS is a new way to do things, this is similar to the python "in"
            // this is just an easier way to do it..
            for (var key of keys) {
                if (key.slice(0, 2) !== 'eq') {

                    final[curr_entry.address][key] = curr_entry[key];

                } else {
                    eqKeys.push(key);
                    eqArr[curr_entry.eq_equipid][key] = curr_entry[key];
                }
            }
            final[curr_entry.address].equipment = eqArr;
        } else {
            eqArr[curr_entry.eq_equipid] = {};
            for (var key of eqKeys) {
                eqArr[curr_entry.eq_equipid][key] = curr_entry[key];
            }

        }

    }
    return final;
}

// this will open a window as needed
function openWin(windowURL, windowName, windowFeatures) {
    window.open(windowURL, windowName, windowFeatures);
}
// maps the markers an when they are clicked, the popup contianing the information of the equipment is made.
function mapData(propData) {
    var markerArr = [];
    $.each(propData, function(location) {
        // console.log(propData, location);
        location = propData[location];
        console.log(location);
        var loc = new google.maps.LatLng(location.lat, location.lon);
        var marker = new google.maps.Marker({
            position: loc,
            map: map,
            title: location.address,
            icon: 'img/equipment-tracker-map-pin-2-06.png'
        });
        map.center = new google.maps.LatLng(location.lat, location.lon);
        // marker.icon ='../../../img/equipment-tracker-map-pin.png';
        marker.addListener('click', function() {
            openWin('equipment/infoPopUp.cfm?id=' + location.propid, 'All Info', 'width=1000,height=500,toolbar=0,location=0,directories=0,status=0,menuBar=0,scrollBars=1,resizable=1');
            //  newWindow.focus();
            console.log('hai');
        });
        markerArr.push(marker);



    });
    // based on the markers, the map boundaries are changed for optimal coverage of all markers.
    var bounds = new google.maps.LatLngBounds();
    for (var i = 0; i < markerArr.length; i++) {
        bounds.extend(markerArr[i].getPosition());
    }

    map.fitBounds(bounds);


}

var map;
// init function for the map.
function initMap() {
    var eqCFC = new equipCFC();
    eqCFC.setHTTPMethod('GET');
    var propertyInfo = queryToObject(eqCFC.getAllEquips());
    var propData = eqAtAddress(propertyInfo);

    map = new google.maps.Map(document.getElementById("map1"), {
        zoom: 5,
        center: new google.maps.LatLng(51.508742, -0.120850),
        mapTypeId: 'satellite',
    });
    mapData(propData);

}
// waits for the window to complete the load.
google.maps.event.addDomListener(window, 'load', initMap);
