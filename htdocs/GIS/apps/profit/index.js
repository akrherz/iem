/**
 * Profitability Map Application
 * Simplified vanilla JavaScript implementation
 */
/* global ol */

let map = null;
let player = null;

/**
 * Initialize the map and controls
 */
function initializeMap() {
    // Create the profitability layer
    player = new ol.layer.Tile({
        title: 'Profitability',
        visible: true,
        source: new ol.source.XYZ({
            url: '/c/tile.py/1.0.0/profit2010/{z}/{x}/{y}.png'
        })
    });

    // Initialize OpenLayers map
    map = new ol.Map({
        target: 'map',
        layers: [
            new ol.layer.Tile({
                title: 'OpenStreetMap',
                visible: true,
                source: new ol.source.OSM()
            }),
            player
        ],
        view: new ol.View({
            projection: 'EPSG:3857',
            center: ol.proj.transform([-93.5, 42.1], 'EPSG:4326', 'EPSG:3857'),
            zoom: 7
        })
    });
    
    // Add layer switcher control
    map.addControl(new ol.control.LayerSwitcher());
}

/**
 * Handle year selection change
 * @param {Event} event - The change event
 */
function handleYearChange(event) {
    const year = event.target.value;
    if (player && year) {
        player.setSource(new ol.source.XYZ({
            url: `/c/tile.py/1.0.0/profit${year}/{z}/{x}/{y}.png`
        }));
    }
}

/**
 * Initialize event listeners
 */
function initializeEventListeners() {
    // Year selection radio buttons
    const yearRadios = document.querySelectorAll('input[name="whichyear"]');
    yearRadios.forEach((radio) => {
        radio.addEventListener('change', handleYearChange);
    });
}

/**
 * Application initialization
 */
document.addEventListener('DOMContentLoaded', () => {
    initializeMap();
    initializeEventListeners();
});
