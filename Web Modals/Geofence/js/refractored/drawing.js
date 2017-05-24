var center_poly; // variable for the center of the polygon

// makeMarker : IN-> NONE
// Purpose: create the polygon which is made by the user,finfd the middle, and add it all to the map.data
function makeMarker() {

    // there is a polygon completed.
    completedPoly = true;

    // vars for the name and type
    var poly_sel, poly_sel_m;
    var e = document.getElementById("polytype");
    var n = document.getElementById("areaName");
    name = n.value;
    type = e.value;

    // if the selected poly is defined, select both the poly and the marker, change the
    // name and type of both poly and marker.
    if (typeof selectedPoly !== 'undefined') {
        poly_sel = map.data.getFeatureById(selectedPoly);
        poly_sel_m = map.data.getFeatureById(selectedPoly + "_marker");
        poly_sel.setProperty('name', n.value);
        poly_sel.setProperty('type', e.value);
        poly_sel_m.setProperty('name', n.value);
        poly_sel_m.setProperty('type', e.value);
        map.data.revertStyle(poly_sel);
        selectedPoly = null;
    } else {

        // a random number is chosen to be the unique ID of the polygon and the marker.
        var id_rand = Math.floor((Math.random() * 9999999) + 1);

        // maker is made in the middle of the polygon.
        var marker = new google.maps.Marker({
            position: center_poly,
            map: map,
            draggable: true,
        });
        // the polygons and points are made and thier properties are given based on the user preferences.
        // the ID is assigned as set up previously. The marker location is made to be in the calculated middle of the polygon.
        map.data.add(new google.maps.Data.Feature({
            geometry: new google.maps.Data.Polygon([madePoly.getPath().getArray()]),
            properties: {
                "name": name,
                "type": type,
                "markerloc": marker.getPosition()
            },
            id: id_rand
        }));
        map.data.add(new google.maps.Data.Feature({
            geometry: new google.maps.Data.Point(marker.position),
            properties: {
                "name": name,
                "type": type
            },
            id: id_rand + "_marker"
        }));
        if (areacalc) areaCalculator("all");
        // in order to not have multiple layers of the same thing, the marker and polygon are set to null
        // makses it so that only the google.maps.data objects are shown.
        marker.setMap(null);
        madePoly.setMap(null);
    }
    // the google.maps.data objects are assigned thier style.
    setPolyStyle();





}
// function calcCenter
// IN : polygon object
// OUT: NONE
// purpose: find the center of the polygon and assign
// the coordinates to center_poly
function calcCenter(polygon) {

    // a new array of the coordinates s made and the bounds are calculated
    var coordinatesArray = [];
    var poly_bounds = new google.maps.LatLngBounds();
    coordinatesArray = polygon.getPath().getArray();
    for (var i = 0; i < coordinatesArray.length; i++) {
        poly_bounds.extend(coordinatesArray[i]);

    }
    center_poly = poly_bounds.getCenter();

}

// function enable_draw
// IN: NONE
// OUT:NONE
// Purpose: enable to drawing manager and listen for the completed polygon when the user is done.
function enable_draw() {
    if (!drawingManager) {
        drawingManager = new google.maps.drawing.DrawingManager({
            drawingMode: google.maps.drawing.OverlayType.polygon,
            drawingControl: true,
            drawingControlOptions: {
                position: google.maps.ControlPosition.BOTTOM_CENTER,
                drawingModes: ['polygon']
            }
        });
        drawingManager.setMap(map);
    }

    // when the user is finished with the polygon, select it, and calculate the center
    // set it as the made polygon for future use.
    google.maps.event.addListener(drawingManager, 'polygoncomplete', function(polygon) {
        madePoly = polygon;
        if (siteoutline) {
            if (!done_so) {
                map.data.add(new google.maps.Data.Feature({
                    geometry: new google.maps.Data.Polygon([madePoly.getPath().getArray()]),
                    id: $('#propID').val()
                }));
                map.data.setStyle({
                    fillColor: 'blue',
                    editable: true
                });
                done_so = true;
                madePoly.setMap(null);
            }
            map.data.addListener('setgeometry', function(event) {
                event.feature.setProperty('geometry', event.feature.getGeometry());
            });
        }
        selectedPoly = undefined;
        completedPoly = false;
        startMarker.setMap(null);
        calcCenter(madePoly);
        drawingManager.setDrawingMode(null);

    });

}
