/* global ol */
const style = new ol.style.Style({
    fill: new ol.style.Fill({
        color: 'rgba(255, 255, 255, 0)'
    }),
    stroke: new ol.style.Stroke({
        color: '#000000',
        width: 2
    })
});

// Lookup 'table' for styling of road conditions based on cond_code
const rcLookup = {
    0: '#000000',
    1: '#00CC00',
    3: '#F0F000',
    7: '#F0F000',
    11: '#F0F000',
    15: '#FFC5C5',
    19: '#FE3299',
    23: '#B500B5',
    27: '#FFC5C5',
    31: '#FE3399',
    35: '#B500B5',
    39: '#99FFFF',
    43: '#0099FE',
    47: '#00009E',
    51: '#E85F01',
    56: '#FFC5C5',
    60: '#FE3399',
    64: '#B500B5',
    86: '#FF0000'
};

document.addEventListener('DOMContentLoaded', () => {

    const roadLayer = new ol.layer.Vector({
        title: 'Winter Road Conditions',
        source: new ol.source.Vector({
            url: '/geojson/winter_roads.geojson',
            format: new ol.format.GeoJSON()
        }),
        style: (feature) => {
            try{
                style.getStroke().setColor(rcLookup[feature.get('code')]);
            } catch {
                // empty
            }
            return [style];
        }
    });
    
    const map = new ol.Map({
        target: 'map',
        layers: [new ol.layer.Tile({
            title: 'OpenStreetMap',
            visible: true,
            source: new ol.source.OSM()
        }), roadLayer],
        view: new ol.View({
            projection: 'EPSG:3857',
            center: ol.proj.transform([-93.5, 42.1], 'EPSG:4326', 'EPSG:3857'),
            zoom: 7
        })
    });

    // Create a LayerSwitcher instance and add it to the map
    map.addControl(new ol.control.LayerSwitcher());

}); // End of onready
