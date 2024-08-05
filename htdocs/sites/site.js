/* global CONFIG, olSelectLonLat */

//callback on when the marker is done moving    		
function displayCoordinates(lon, lat) {
    $("#newlat").val(lat.toFixed(8));
    $("#newlon").val(lon.toFixed(8));
}

$(document).ready(() => {
    const res = olSelectLonLat("mymap", CONFIG.lon, CONFIG.lat, displayCoordinates);
    // zoom in
    res.map.getView().setZoom(14);
});
