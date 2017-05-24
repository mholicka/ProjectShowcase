// these are all the global variables for the mapping.

var map, infoWindow; // the map and infowindow
var init = false; // has the map been initalized?
var drawingManager; // drawinmanager
var madePoly;// the made polygon
var drawnmap; // the map has been drawn
var name; // name of the polygon
var type; // type of polygon
var savedpoly; //
var startMarker; // the marker that shows the building
var completedPoly; // boolean to see if the polygon has been completed.
var mouseclicklisten; // the mouseclicklistener
var propertyCfc = new propertyCFC(); // interface with coldfusion for the CFC



// the is the dictionary of all the icons and thier labels. Change for each tracker.
var polycolors = {};
var imgdir_legend = "img/";
var imgdir_logos = "../logos/";
// adding
// do not push snow - polygon
// walkway - polygon
// fire hydrant = marker
// exhast - marker
// drainage- marker
// handicapped area
//

areacalc = true;




polycolors['No Snow Dumping'] = [imgdir_legend + "PolygonMaps/no-snow.png", "#cf5c36", imgdir_legend + "PolygonMaps/legend-no-snow.png"];
polycolors['Priority Area'] = [imgdir_legend + "PolygonMaps/priority.png", "#fcab10", imgdir_legend + "PolygonMaps/legend-priority.png"];
polycolors['General Area'] = [imgdir_legend + "PolygonMaps/general.png", "#44af69", imgdir_legend + "PolygonMaps/legend-general.png"];
polycolors['Dump Location'] = [imgdir_legend + "PolygonMaps/snow.png", "#3FA9F5", imgdir_legend + "PolygonMaps/legend-snow.png"];

// markers for routingModd
var first_route= imgdir_legend+'/Routing/path-icons-start.png';
var last_route =imgdir_legend+'/Routing/path-icons-stop.png';


// location of the logos is given

var crawford_compliance = imgdir_logos + "Crawford-Compliance-Logo-Powered-By-small.png";
var company;

// depending on the type of product, the logos are showsn as needed.
if (assID > 0) {
    company = imgdir_logos + "colliers-snowtracker-02.jpg";
} else {
    company = imgdir_logos + "snow-tracker-title-image_360.png";
    // $('#crawford_compliance').attr("style","margin-left:1%;width:30%;");
}



var drawingMode = true;// changes the ability to draw or not draw on the map.
var testpoint = true; // should there be a starting marker?
var setZoom = 18; // inital zoom level.
var clickable = true; // should the map be clickable?
// var map_type='firstLoc'; // means it get's the first position of the user.
var map_type = 'static'; // means it get's the first position of the user.
var areacalc = true;// flag to see if area of polygon needs to be calculated
var logoed = true; // does this need to be logoed.

// for checking the geofence (backend only).
checker =false;
