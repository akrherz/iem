/* global $, ol, olSelectLonLat */

function updateMarkerPosition(lon, lat) {
    $("#lat").val(lat.toFixed(4));
    $("#lon").val(lon.toFixed(4));
}

$(document).ready(() => {
    const default_lon = -93.653;
    const default_lat = 41.53;

    olSelectLonLat("map", default_lon, default_lat, updateMarkerPosition);

}); // end of onReady()