/* global olSelectLonLat */

function displayCoordinates(lon, lat) {
    document.getElementById('newlat').value = lat.toFixed(8);
    document.getElementById('newlon').value = lon.toFixed(8);
}

document.addEventListener('DOMContentLoaded', () => {
    const mapEl = document.getElementById("mymap");
    const lon = parseFloat(mapEl.dataset.lon);
    const lat = parseFloat(mapEl.dataset.lat);
    
    const res = olSelectLonLat("mymap", lon, lat, displayCoordinates);
    // zoom in
    res.map.getView().setZoom(14);
});
