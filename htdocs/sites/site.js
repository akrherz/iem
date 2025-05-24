/* global olSelectLonLat */

function displayCoordinates(lon, lat) {
    document.getElementById('newlat').value = lat.toFixed(8);
    document.getElementById('newlon').value = lon.toFixed(8);
}

document.addEventListener('DOMContentLoaded', () => {
    const mapEl = document.getElementById("mymap");
    const lon = parseFloat(mapEl.dataset.lon);
    const lat = parseFloat(mapEl.dataset.lat);
    const suggestedLon = mapEl.dataset.suggestedLon && mapEl.dataset.suggestedLon !== 'null' ? parseFloat(mapEl.dataset.suggestedLon) : null;
    const suggestedLat = mapEl.dataset.suggestedLat && mapEl.dataset.suggestedLat !== 'null' ? parseFloat(mapEl.dataset.suggestedLat) : null;
    
    const res = olSelectLonLat("mymap", lon, lat, displayCoordinates, suggestedLon, suggestedLat);
    
    // zoom in
    res.map.getView().setZoom(14);
});
