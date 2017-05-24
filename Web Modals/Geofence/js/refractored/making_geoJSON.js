// all code needing to create the GeoJSON will go here.
// this will be used for all the trackers.

// generateJSON
// IN : None
// Out: NONE
// Purpose: upload the geoJSON once everything is made.
function generateJSON(mapType,temp) {
    // if all the polygons are completed, then the geoJSON can eb created.
    // alert(done ||completedPoly);

    if (done_so ||completedPoly) {

        // the HTTP method is set to post.
        propertyCfc.setHTTPMethod('POST');

        // using the method for geoJSON from google, the property polygons are uploaded to the database.
        map.data.toGeoJson(function(data) {
            propertyCfc.PropPolygons(parseInt($('#propID').val()), JSON.stringify(data),mapType);
        });
        // the user is thanked and they are notified that all the changes are saved.
        if (!temp)
        {
            alert("Thank you, your changes are saved. ");
        }

        //completedPoly=false;
    }
    else {
      // if a polygon has not been completed and the user tries to submit, they are notified that this cannot happen, and told how to fix it.
      var alert_txt;
      if (siteoutline)
      {
          alert_txt = "YOU CANNOT PROCEED UNTIL THIS PROPERTY IS GEOFENCED \nYou cannot submit this overlay because a polygon still needs to be completed. Double check you have completed your drawing, and that all points are connected.";
      }
      else
      {
        alert_txt = "NOTE:  You cannot submit this overlay because a polygon still needs to be completed. Double check you have completed your drawing, and that all points are connected.  Please ensure that the polygon is fully closed and given a unique name, then select what type it is.";
      }
      alert(alert_txt);
    }

}
