/* global ol */
// A factory to generate an OpenLayers map with a single marker on the page
// that is dragable, which then callbacks a given function with the lat/lon
// values of the marker.

function olSelectLonLat(div, initialLon, initialLat, callback, suggestedLon = null, suggestedLat = null) { // skipcq

    const marker = new ol.Feature({
        geometry: new ol.geom.Point(ol.proj.fromLonLat([initialLon, initialLat]))
    });
    const style = new ol.style.Style({
        image: new ol.style.Icon({
            anchor: [0.5, 1],
            src: '/images/marker.png',
        }),
    });

    // Set the style for the marker
    marker.setStyle(style);

    const features = [marker];
    
    // Add suggested marker if coordinates are provided
    let suggestedMarker = null;
    if (suggestedLon !== null && suggestedLat !== null) {
        suggestedMarker = new ol.Feature({
            geometry: new ol.geom.Point(ol.proj.fromLonLat([suggestedLon, suggestedLat]))
        });
        
        const suggestedStyle = new ol.style.Style({
            image: new ol.style.Circle({
                radius: 10,
                fill: new ol.style.Fill({
                    color: '#ff0000'
                }),
                stroke: new ol.style.Stroke({
                    color: '#000000',
                    width: 2
                })
            })
        });
        
        suggestedMarker.setStyle(suggestedStyle);
        features.push(suggestedMarker);
    }

    // Create a vector source and add the marker(s) to it
    const vectorSource = new ol.source.Vector({
        features
    });

    // Create a vector layer with the vector source and add it to the map
    const vectorLayer = new ol.layer.Vector({
        source: vectorSource
    });
    const bingMapsApiKey = document.getElementById(div).dataset.bingmapsapikey;
    const map = new ol.Map({
        target: div,
        layers: [
            new ol.layer.Tile({
                title: 'Global Imagery',
                source: new ol.source.BingMaps({
                    key: bingMapsApiKey,
                    imagerySet: 'AerialWithLabelsOnDemand'
                })
            }),
            vectorLayer
        ],
        view: new ol.View({
            center: ol.proj.fromLonLat([initialLon, initialLat]),
            zoom: 5
        })
    });

    const modify = new ol.interaction.Modify({
        hitDetection: vectorLayer,
        source: vectorSource,
        features: new ol.Collection([marker]) // Only the original marker is modifiable
    });
    map.addInteraction(modify);

    // Add a listener to the drag-and-drop interaction
    modify.on('modifyend', (e) => {
        const coords = e.features.getArray()[0].getGeometry().getCoordinates();
        const lonLat = ol.proj.toLonLat(coords);
        try {
            callback(lonLat[0], lonLat[1]);
        } catch {
            // pass
        }
    });

    return { map, marker, suggestedMarker };
}

window.ols = olSelectLonLat;
