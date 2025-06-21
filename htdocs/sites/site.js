/* global olSelectLonLat */

document.addEventListener('DOMContentLoaded', () => {
    // The olSelectLonLat widget now handles bidirectional sync automatically
    // via data attributes on the map div
    const res = olSelectLonLat("mymap");
    window.marker = res.marker; // Store the marker globally if needed
});
