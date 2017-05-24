// globalvars.js will explain all this, this is a copy for the fence checking.

var map, infoWindow;
var init = false;
var drawingManager;
var madePoly;
var drawnmap;
var name;
var oldpos;
var type;
var savedpoly;
var startMarker;
var completedPoly;
var mouseclicklisten;
var propertyCfc = new propertyCFC();



// the is the dictionary of all the icons and thier labels. Change for each tracker.
var polycolors = {};
var imgdir_legend = "img/";
polycolors['No Snow Dumping'] = [imgdir_legend + "PolygonMaps/no-snow.png", "#cf5c36", imgdir_legend + "PolygonMaps/legend-no-snow.png"];
polycolors['Priority Area'] = [imgdir_legend + "PolygonMaps/priority.png", "#fcab10", imgdir_legend + "PolygonMaps/legend-priority.png"];
polycolors['General Area'] = [imgdir_legend + "PolygonMaps/general.png", "#44af69", imgdir_legend + "PolygonMaps/legend-general.png"];
polycolors['Dump Location'] = [imgdir_legend + "PolygonMaps/snow.png", "#3FA9F5", imgdir_legend + "PolygonMaps/legend-snow.png"];




var imgdir_logos = "../logos/";
var crawford_compliance = imgdir_logos + "powered-by-cc-padded.png";
var company;



// changes the ability to draw or not draw on the map.
var drawingMode = false;
var testpoint = false;
var checker = true;
var setZoom = 5;
var clickable = false;
// var map_type='firstLoc'; // means it get's the first position of the user.
var map_type = 'static'; // means it get's the first position of the user.
var areacalc = true;
var logoed = false;
if (logoed)
{
  if (assID > 0) {
      company = imgdir_logos + "colliers-snowtracker-02.jpg";
  } else {
      company = imgdir_logos + "snow-tracker-title-image_360.png";
      $('#crawford_compliance').attr("style","margin-left:1%;width:30%;");
  }
}
