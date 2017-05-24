// depending on the session variable, the id is established, this is used in the marker.
function makeMarkers(lat, long, name, addr, id, city, manager, company) {
    var id_s ;
    switch (session_ID) {
        case 1:
            id_s = 'S';
            break;
        case 2:
            id_s = 'G';
            break;
        case 3:
            id_s = 'J';
            break;
        default:
            //alert('Session ID is not defined. Markers will not link.');
            break;
    }

    // this is all to make the markers and populate them with all the needed information from the database.
    var pos = new google.maps.LatLng(lat, long);
    var infopop_admin = "Property Code: \nName:" + name + "\nAddress: " + addr + "\nCity: " + city + "\nPM: " + manager + "\nContractor:" + company;
    var infopop_contract = "Name:" + name + "\nAddress: " + addr + "\nCity: " + city + "\nPM: " + manager;
    var url = (contractor === true) ? "dashboard-" + id_s + ".cfm?id=" + id + "&daction=3" : "dashboardmaster.cfm?id=" + id + "&daction=3";
    var infopop = (contractor === true) ? infopop_contract : infopop_admin;
    var marker = new google.maps.Marker({
        position: pos,
        map: map,
        title: infopop,
        url: url,
        icon: "img/mapicons/compliance-map-pins-s.png"


    });
    // when the user clicks on the marker, it takes them to the url defined by the marker property
    google.maps.event.addListener(marker, 'click', function() {
        window.location.href = this.url;
    });
    return pos;
}
// Change the  icon based on open log.
function getProps() {
    var propertyCfc = new propertyCFC();
    propertyCfc.setHTTPMethod('GET');
    var inJSON = (contractor === true) ? propertyCfc.getAllOpenMarkerLocs(dbowner).DATA : propertyCfc.getAllOpenMarkerLocs().DATA;
    if (inJSON.ID.length ===0) {
        $("#map1").html("<img src='img/no-active-properties.png' style='width:100%;'  >");
        return 0;
    }
    var bounds = new google.maps.LatLngBounds();
    // each variable is made.and passed to the makeMarkers function to make the marker.
    for (var i = 0; i < inJSON.ID.length; i++) {
        var lat = inJSON.LAT[i];
        var lon = inJSON.LON[i];
        var city = inJSON.CITY[i];
        var property_name = inJSON.PROPERTY_NAME[i];
        var address = inJSON.ADDRESS[i];
        var id = inJSON.ID[i];
        var manager = inJSON.MANAGER[i];
        var company = inJSON.COMPANYNAME[i];
        bounds.extend(makeMarkers(lat, lon, property_name, address, id, city, manager, company));

    }
    map.fitBounds(bounds);


}

// default place for the map, as well as the init script for the map. This gets all the needed markers through the getProps() function.
function initMap() {

    var uluru = {
        lat: 43.645,
        lng: -79.3836
    };
    map = new google.maps.Map(document.getElementById('map1'), {
        zoom: 7,
        center: uluru,
        minZoom: 4,
        mapTypeId: google.maps.MapTypeId.SATELLITE

    });
    map.setTilt(0);
    getProps();
}
// init on window load.
window.onload = function() {
    initMap();
};
