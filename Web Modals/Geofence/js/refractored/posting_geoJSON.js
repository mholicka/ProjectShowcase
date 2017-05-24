// All GeoJSON methods will go here. This may get long when adding in multiple differnt types of polygons

// areaCalculator
// Purpose: calculates the area of the polygon.
// not really used right now, but can be used in the future.
function areaCalculator(type) {
    if (type == "all") {
        map.data.forEach(function(feature) {
            if (feature.getGeometry().getType() == "Polygon") {
                var bounds = [];
                feature.getGeometry().forEachLatLng(function(path) {
                    bounds.push(path);
                });
            }
        });
    }

}
var route2;

// this function will render the path and set up all the needed options for it.
// the options are set up, and from there, the path is created based on the location of the markers.
function renderPath() {
    var lineSymbol = {
        path: google.maps.SymbolPath.FORWARD_OPEN_ARROW,

    };
    var polyOptions = {
        strokeColor: 'white',
        strokeOpacity: 1.0,
        strokeWeight: 3,
        zIndex: 9998,
        icons: [{
            repeat: '100px',
            icon: lineSymbol,
            offset: '100%'
        }]
    };
    route2 = new google.maps.Polyline(polyOptions);
    route2.setMap(map);
    path = route2.getPath();
    map.data.forEach(function(feature) {
        if (feature.getProperty('type') === 'routing') {
            path.push(new google.maps.LatLng(feature.getGeometry().get().lat(), feature.getGeometry().get().lng()));
        }
    });

}

// setPolyStyle
// Purpose: to set the style of the loaded data as needed.
function setPolyStyle() {
    // establising the polyline
    if (route === null || routeDone) {
        renderPath();

    }

    // goes through all the featues and sets the style up as need.
    map.data.setStyle(function(feature) {
        if (routeDone && feature.getProperty('type') === 'routing') {
            routeDone = true;
            if (feature.getId() === 1) {
                return {
                    title: 'First' + feature.getId(),
                    icon: {
                        url: first_route,
                        scaledSize: new google.maps.Size(50, 50)

                    },
                    label: {
                        text: "START",
                        color: "white"
                    },
                    // draggable: true,
                    zIndex: 9999

                };
            } else if (feature.getId() === path.length) {
                return {
                    title: 'Last' + feature.getId(),
                    label: {
                        text: "FINISH",
                        color: "white"
                    },
                    icon: {
                        url: last_route,
                        scaledSize: new google.maps.Size(50, 50)

                    },
                    // draggable: true,
                    zIndex: 9999
                };

            } else {
                return {
                    title: feature.getId(),
                    visible: false
                };
            }

        }


        // the use and type (polygon/point) is established.
        var use = feature.getProperty('type');
        var type = feature.getGeometry().getType();

        for (var key in polycolors) {
            if (type == "Point") {
                if (use == key) {
                    if (drawingMode) {
                        return {
                            icon: polycolors[key][0],
                            draggable: true
                        };
                    } else {
                        return {
                            icon: polycolors[key][0],
                            draggable: false
                        };
                    }

                }
            } else {
                if (use == key) {
                    if (drawingMode) {
                        return {
                            strokeWeight: 2.0,
                            strokeColor: polycolors[key][1],
                            fillColor: polycolors[key][1],
                            fillOpacity: 0.85,
                            editable: true
                        };
                    } else {
                        return {
                            strokeWeight: 2.0,
                            strokeColor: polycolors[key][1],
                            fillColor: polycolors[key][1],
                            fillOpacity: 0.85,
                            editable: false
                        };
                    }
                }
            }

        }
    });
}

// when the user goes back to polygon mode from routing mode, this is run and it changes the screen to reflect polygon mode.
function re_init() {
    routeDone = true;
    generateJSON("sitemap", true);
    changeText("poly");
    drawingManager.setDrawingMode(google.maps.drawing.OverlayType.POLYGON);
    drawingManager.setOptions({
        drawingControlOptions: {
            position: google.maps.ControlPosition.BOTTOM_CENTER,
            drawingModes: ['polygon']
        }
    });
    drawingManager.setDrawingMode(null);
    postGeoJSON('sitemap');
}

// this will post the geojson to the databae.
function postGeoJSON(mapType) {
    propertyCfc.setHTTPMethod('GET');
    var inJSON;
    if (mapType === "sitemap") {
        inJSON = JSON.parse(propertyCfc.getpropJSON(parseInt($('#propID').val()), mapType).DATA.BUILDINGPOLY[0]);
    } else {
        inJSON = JSON.parse(propertyCfc.getpropJSON(parseInt($('#propID').val()), mapType).DATA.BUILDINGOUTLINE[0]);

    }
    if (inJSON === null || inJSON.features == []) {
        completedPoly = false;
        // return 0;
    } else {
        completedPoly = true;
    }
    map.data.addGeoJson(inJSON);
    if (!siteoutline) {
        setPolyStyle();
        if (clickable) {
            //Set mouseover event for each feature.
            var info = new google.maps.InfoWindow();
            //var tempPoly;
            map.data.addListener('mouseover', function(event) {
                if (event.feature.getProperty('type') !== 'routing') {
                    info.setOptions({
                        map: map,
                        position: event.feature.getProperty("markerloc"),
                        content: event.feature.getProperty('name')
                    });
                }


            });

            map.data.addListener('mouseout', function(event) {
                info.setMap(null);
            });

            // click listener to be able to define and change the polygon as needed.
            mouseclicklisten = map.data.addListener('click', function(event) {
                $('#areaName').val(event.feature.getProperty('name'));
                $('#polytype').val(event.feature.getProperty('type'));

                if (event.feature.getGeometry().getType() == "Polygon") {
                    if (typeof selectedPoly !== 'undefined' && selectedPoly == event.feature.getId()) {
                        map.data.revertStyle(event.feature);
                        selectedPoly = null;
                    } else if (typeof selectedPoly !== 'undefined' && (selectedPoly !== event.feature.getId() && selectedPoly !== null)) {

                        map.data.revertStyle(map.data.getFeatureById(selectedPoly));
                        selectedPoly = event.feature.getId();
                        map.data.overrideStyle(event.feature, {
                            fillColor: 'red'

                        });

                    } else {
                        selectedPoly = event.feature.getId();
                        map.data.overrideStyle(event.feature, {
                            fillColor: 'red'

                        });
                    }
                }


            });
            // on double click, the zoom of the map will be adjusted to match the polygon boundaries.
            map.data.addListener('dblclick', function(event) {
                var type = event.feature.getGeometry().getType();
                if (type == "Polygon") {
                    var bounds = new google.maps.LatLngBounds();
                    event.feature.getGeometry().getArray().forEach(function(path) {
                        path.getArray().forEach(function(latLng) {
                            bounds.extend(latLng);
                        });
                    });
                    map.fitBounds(bounds);
                }
            });

            // clicking outside on the map will deselect all the polygons, reverting all style changes.
            google.maps.event.addListener(map, 'click', function() {
                if (typeof selectedPoly !== 'undefined') {
                    poly_sel = map.data.getFeatureById(selectedPoly);
                    map.data.revertStyle(poly_sel);
                    selectedPoly = null;
                }

            });
        }





    } else {
      // site outline is just blue, so this is set here.
        map.data.setStyle({
            fillColor: 'blue',
            editable: true
        });
    }








}
