/* global olSelectLonLat */

/**
 * Update the latitude and longitude input fields when marker position changes
 * @param {number} lon - Longitude value
 * @param {number} lat - Latitude value
 */
function updateMarkerPosition(lon, lat) {
    const latElement = document.getElementById("lat");
    const lonElement = document.getElementById("lon");
    
    if (latElement) {
        latElement.value = lat.toFixed(4);
    }
    if (lonElement) {
        lonElement.value = lon.toFixed(4);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const default_lon = -93.653;
    const default_lat = 41.53;

    olSelectLonLat("map", default_lon, default_lat, updateMarkerPosition);
});