// creating the routing variables and the path.
var route = null,
    path = [];

// since the text on the sidebar is different on site outline and site map, this is changed.
function changeText(mode) {
    if (mode==="routing")
    {
      document.getElementById('s1').innerHTML = "Select the marker tool <img src='img/Misc/poly_marker.png' alt='Polygon make'>  at the bottom of the map";
      $('#ui_instr').text("Create a route  by clicking on the map within the road, as shown in the example below");
      $('#s6').text("Step 3");
      $('#del').attr("value", "SUBMIT ROUTE");
      $('#delAll').attr("value", "CLEAR ROUTE");
      $('#del').attr("onclick", "submitRouting()");
      $('#delAll').attr("onclick","clearMap('routing')");
      $('.sitemap_ui').hide();
      $('.sitemap_ctrl').show();
    }
  else if (mode==="poly")
  {
    document.getElementById('s1').innerHTML = "Select the polygon tool <img src='img/Misc/poly_shape.png' alt='Polygon make'>at the bottom of the map";
    $('#ui_instr').text("Create a polygon by clicking on the map around the area you would like to designate.");
    $('#s6').text("Step 6");
    $('#del').attr("value", "DELETE POLYGON");
    $('#delAll').attr("value", "CLEAR ALL POLYGONS");
    $('#del').attr("onclick", "clearMap('')");
    $('#delALL').attr("onclick", "clearMap('all')");
    // $('#delAll').attr("value","CLEAR ROUTE");
    $('.sitemap_ui').show();
    $('.sitemap_ctrl').show();
  }

}

// routing mode is created here. the drawing manager is told to go into marker mode and a pat is created.
function routingMode(done) {
    if (!done)
    {
      changeText("routing");
      var lineSymbol = {
          path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW
      };
      // set the drawingManager to marker mode.
      drawingManager.setDrawingMode(null);
      drawingManager.setOptions({
          drawingControlOptions: {
              position: google.maps.ControlPosition.BOTTOM_CENTER,
              drawingModes: ['marker']
          }
      });
    }

    route = new google.maps.Polyline({
        strokeColor: '#000000',
        strokeOpacity: 1.0,
        strokeWeight: 3,
        zIndex: 10,

    });
    route.setMap(map);
    google.maps.event.clearInstanceListeners(map.data);
    google.maps.event.clearInstanceListeners(map);
    routeDone = false;
    google.maps.event.addListener(drawingManager, 'markercomplete', function(marker) {
        if(routeDone)
        {
          clearMap('routing');
        }

        path = route.getPath();
        path.push(marker.getPosition());

        map.data.add(new google.maps.Data.Feature({
            geometry: new google.maps.Data.Point(marker.getPosition()),
            properties: {
                "type": "routing",
            },
            id: path.getLength()
        }));
        marker.setMap(null);
    });

}
// the route is submited to the database.
function submitRouting() {
    routeDone = true;
    completedPoly= true;
    setPolyStyle();
    route.setMap(null);
    drawingManager.setDrawingMode(null);
}
