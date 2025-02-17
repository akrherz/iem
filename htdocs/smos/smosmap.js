/* global $, ol */
let feature = null;
window.app = {};
const app = window.app;
let theMap = null;

function updateMarkerPosition(lon, lat) {
    $("#lat").val(lat.toFixed(4));
    $("#lon").val(lon.toFixed(4));
}

$(document).ready(() => {
    let default_lon = -93.653;
    let default_lat = 41.53;

    olSelectLonLat("map", default_lon, default_lat, updateMarkerPosition);

}); // end of onReady()