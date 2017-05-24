// instructions for the mapping is done.
if ($('#mapType').val() === "so") {
    $('#skipButton').hide();
    $('.sitemap_ui').hide();
    $('#ui_instr').text("Create a site outline by clicking on the map around the buildling, as shown in the example below");
    $('#final_text').text("Once your site outline is done, please click the submit button below.");
    $('#final_submit').val("SUBMIT SITE OUTLINE");
    siteoutline = true;
    var done_so = false;
    $('#final_submit').attr('onclick', 'makeSiteOutline()');
}

// JSON is generated and then the screen changes.
function makeSiteOutline() {
     generateJSON("siteoutline",false);
     if (done_so||completedPoly)
     {
       siteoutline = false;
       done_so= false;
       if ('URLSearchParams' in window) {
           var searchParams = new URLSearchParams(window.location.search);
           searchParams.set("outline", "sm");
           window.location.search = searchParams.toString();
           google.maps.event.addDomListener(window, 'load', initMap);

       }

     }


}
