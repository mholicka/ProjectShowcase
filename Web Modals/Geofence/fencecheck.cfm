<cfajaxproxy cfc="#application.propertyCFC#" jsclassname="propertyCFC">
<cfajaxproxy cfc="#application.trackerCFC#" jsclassname="trackerCFC">
<cfajaxproxy cfc="#application.miscCFC#" jsclassname="miscCFC">
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, shrink-to-fit=no, initial-scale=1">
        <title>geofenceCheck
        </title>
        <link href="css/bootstrap.css" rel="stylesheet">
        <link href="css/map.css" rel="stylesheet">
        <script src="https://code.jquery.com/jquery-3.1.1.min.js"></script>
        <!--- <script async defer src="https://maps.googleapis.com/maps/api/js?key=AIzaSyAl8lwM6B2AZsYwoOU1QLCz3Eqgbsub1oM&?v=3&libraries=drawing,geometry"></script> --->

    </head>
    <body>
        <div class="container-fluid">
            <div class="col-sm-12">
                <CFOUTPUT>
                    <cfset buildID=#url.id#>
                    <cfset lat=#url.lat#>
                    <cfset lon=#url.lon#>

                    <INPUT NAME="propID" TYPE="hidden" id="propID" VALUE="#buildID#">
                    <INPUT NAME="lat" TYPE="hidden" id="lat" VALUE="#lat#">
                    <INPUT NAME="lon" TYPE="hidden" id="lon" VALUE="#lon#">

                </CFOUTPUT>
                <div id="map"></div>
                <div class="row-fluid">
                    <div id="legend">
                        <h3>Legend</h3>
                    </div>
                </div>
            </div>
        </div>
        <script  src="https://maps.googleapis.com/maps/api/js?key=AIzaSyAl8lwM6B2AZsYwoOU1QLCz3Eqgbsub1oM&?v=3&libraries=drawing,geometry"></script>
        <script sync src="js/refractored/fencecheckvars.js"></script>
        <script sync type="text/javascript" src="js/refractored/main_map.js"></script>
        <script sync type="text/javascript" src="js/refractored/posting_geoJSON.js"></script>


    </body>
</html>
