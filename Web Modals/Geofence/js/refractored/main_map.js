var routeDone;
// main file for the map
// Purpose: Draw the map and legend

// includeJs
// IN : filepath
// OUT : NONE
// Purpose: allow the program to use outside scripts such as geofence.js
function includeJs(jsFilePath) {
    var js = document.createElement("script");

    js.type = "text/javascript";
    js.src = jsFilePath;

    document.body.appendChild(js);
}

// default Geolocation error handling.
// tells the user where there is an issue.
function handleLocationError(error) {
    var container = document.getElementById('map');
    switch (error.code) {
        case error.PERMISSION_DENIED:
            container.innerHTML = "User denied the request for Geolocation.";
            break;
        case error.POSITION_UNAVAILABLE:
            container.innerHTML = "Location information is unavailable.";
            break;
        case error.TIMEOUT:
            container.innerHTML = "The request to get user location timed out.";
            break;
        case error.UNKNOWN_ERROR:
            break;
    }
}

// function clearMap
// IN : type(String) which lets the it know if it should do a full wipe or only
//      a selected wipe.
function clearMap(type) {
    // if it is a full wipe, the user is asked to  confirm thier intention, and then the entire map is wiped.
    if (type == "all") {
        if (confirm("Really delete all Polygons?")) {
            map.data.forEach(function(feature) {
                map.data.remove(feature);

            });
        }

    } else if (type === 'routing') {
        if (route2 || route) {
            route2.setMap(null);
            for (var i = 1; i <= path.length; i++) {
                map.data.remove(map.data.getFeatureById(i));
            }
            path=[];
            routingMode(true);
        }

    } else {
        // only the selected polygon and the marker is wiped
        // this is given by the unqiue ID
        map.data.remove(map.data.getFeatureById(selectedPoly));
        map.data.remove(map.data.getFeatureById(selectedPoly + "_marker"));
    }
    // all polygons are deselected
    selectedPoly = null;
    drawingManager.setMap(map);

}

// randomeName - used only in test cases
// IN : NONE
// OUT: None
// purpose: name the polygons differently every time one is made.
function randomName() {
    var random = Math.floor((Math.random() * 9999999) + 1);
    $('#areaName').attr('value', 'test' + random);

}

// makeLegend
// IN: NONE
// OUT:NONE
// Purpose: to make the legend based on the differnt types of polygons.
function makeLegend() {

    // all the required divs are selected, and a new table is made.
    var legend = document.getElementById('legend');
    var tbl = document.createElement('table');
    legend.className = " table table-responsive";


    // for each type of map polygon, the legend is populated.
    // a new row is created containing the name and the image.
    for (var key in polycolors) {
        var name = key;
        var icon = polycolors[key].slice(-1)[0];
        var div = document.createElement('tr');
        div.style.padding = "10px 10px";
        div.innerHTML += '<td><img src="' + icon + '"></td>' + "<td>" + name + " <br></td>";
        tbl.appendChild(div);
    }
    // the table is appended to the div legend.
    legend.appendChild(tbl);

    // strange behaviour on IOS has led to this. If there is a problem with the legend,
    // it refreshes the page. seems to be the only fix.
    try {
        map.controls[google.maps.ControlPosition.RIGHT_TOP].push(document.getElementById('legend'));
    } catch (e) {
        location.reload();


    }
    // the legend has the appropriate position and display.
    legend.style.display = "block";

}


// draw_map
// IN : postion object
//Out: NONE
// Purpose : based on the location of the building, draw the map as needed.
function draw_map(position) {

    // the position of the map is determined.
    // if the map is static, then the postion is based on the provided lat/lng
    // otherwise, the map is based on user location.
    var pos;
    if (map_type == 'static') {
        pos = {
            lat: position.lat,
            lng: position.lng
        };
    } else {
        pos = {
            lat: position.coords.latitude,
            lng: position.coords.longitude
        };
    }
    // the map is initalized, no tilt, and if the user wanted a starting marker (specified in globalvars),
    // it is made
    map = new google.maps.Map(document.getElementById("map"), {
        center: pos,
        zoom: setZoom,
        mapTypeId: 'satellite'
    });
    map.setTilt(0);
    if (testpoint) {
        startMarker = new google.maps.Marker({
            map: map,
            title: "User Location",
            position: map.getCenter(),
            zindex: 10000
        });


    }

    // if this is logoed, the appropriate divs are changed.
    // with the good images being there.
    if (logoed) {
        $("#company").attr('src', company);
        $("#crawford_compliance").attr('src', crawford_compliance);
    }

    // once the map is idle, the drawing mode is made and the
    // loaded geoJSON is posted.
    google.maps.event.addListenerOnce(map, 'idle', function() {
        // if this map is used for checking a geofence, the marker is put there.
        if (checker) {
            var loc = new google.maps.LatLng($('#lat').val(), $('#lon').val());

            var checkMarker = new google.maps.Marker({
                map: map,
                title: "Out of fence",
                position: loc,
                zindex: 10000
            });

        }
        if (drawingMode) enable_draw();
        routeDone = true;
        if (siteoutline) {
            postGeoJSON("siteoutline");
        } else {
            makeLegend();
            postGeoJSON("sitemap");
        }

    });




}
// initMap
function initMap() {
    // the property CFC is made, and the lat and lon is gotten from the database based on the ID.
    propertyCfc.setHTTPMethod('GET');
    lat = propertyCfc.getbuildingLoc($('#propID').val()).DATA.LAT;
    lon = propertyCfc.getbuildingLoc($('#propID').val()).DATA.LON;
    var prop_positon = {
        lat: parseFloat(lat),
        lng: parseFloat(lon)
    };
    // based on the type of map, either the property polygons are drawn or geoloation starts.
    if (map_type == 'static') draw_map(prop_positon);
    if (map_type == 'firstLoc') navigator.geolocation.getCurrentPosition(draw_map, handleLocationError);




}

// strange behaviour on IOS has led to this. If there is a problem with the legend,
// it refreshes the page. seems to be the only fix.
try {
    var siteoutline;
    google.maps.event.addDomListener(window, 'load', initMap);
} catch (e) {

    location.reload(true);
}
