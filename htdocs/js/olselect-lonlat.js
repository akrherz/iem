/* global ol */
// A factory to generate an OpenLayers map with a single marker on the page
// that is dragable, which then callbacks a given function with the lat/lon
// values of the marker.

function olSelectLonLat(div, initialLon, initialLat, callback) {

    let marker = new ol.Feature({
        geometry: new ol.geom.Point(ol.proj.fromLonLat([initialLon, initialLat]))
    });
    let style = new ol.style.Style({
        image: new ol.style.Icon({
            anchor: [0.5, 1],
            src: '/images/marker.png',
        }),
    });

    // Set the style for the marker
    marker.setStyle(style);

    // Create a vector source and add the marker to it
    let vectorSource = new ol.source.Vector({
        features: [marker]
    });

    // Create a vector layer with the vector source and add it to the map
    let vectorLayer = new ol.layer.Vector({
        source: vectorSource
    });

    let map = new ol.Map({
        target: div,
        layers: [
            new ol.layer.Tile({
                source: new ol.source.OSM()
            }),
            vectorLayer
        ],
        view: new ol.View({
            center: ol.proj.fromLonLat([initialLon, initialLat]),
            zoom: 5
        })
    });

    let modify = new ol.interaction.Modify({
        hitDetection: vectorLayer,
        source: vectorSource
    });
    map.addInteraction(modify);

    // Add a listener to the drag-and-drop interaction
    modify.on('modifyend', (e) => {
        let coords = e.features.getArray()[0].getGeometry().getCoordinates();
        let lonLat = ol.proj.toLonLat(coords);
        try {
            callback(lonLat[0], lonLat[1]);
        } catch (e) {
            console.log(e);
        }
    });

    return { map: map, marker: marker };
}