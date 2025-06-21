/* global ol */
// A factory to generate an OpenLayers map with a single marker on the page
// that is draggable, which then callbacks a given function with the lat/lon
// values of the marker.
//
// Modern API using data attributes:
// - data-initial-lon: Initial longitude (required)
// - data-initial-lat: Initial latitude (required)
// - data-suggested-lon: Optional suggested longitude
// - data-suggested-lat: Optional suggested latitude
// - data-zoom: Initial zoom level (default: 5)
// - data-marker-src: Custom marker image source (default: '/images/marker.png')
// - data-bingmapsapikey: Bing Maps API key (required)
// - data-lon-input: ID of longitude input field for bidirectional sync (optional)
// - data-lat-input: ID of latitude input field for bidirectional sync (optional)
// - data-precision: Number of decimal places for input values (default: 4)

function olSelectLonLat(div, callback) {
    const element = typeof div === 'string' ? document.getElementById(div) : div;
    
    if (!element) {
        throw new Error(`Element with ID '${div}' not found`);
    }
    
    // Extract configuration from data attributes
    const config = {
        initialLon: parseFloat(element.dataset.initialLon),
        initialLat: parseFloat(element.dataset.initialLat),
        suggestedLon: element.dataset.suggestedLon ? parseFloat(element.dataset.suggestedLon) : null,
        suggestedLat: element.dataset.suggestedLat ? parseFloat(element.dataset.suggestedLat) : null,
        zoom: element.dataset.zoom ? parseInt(element.dataset.zoom) : 5,
        markerSrc: element.dataset.markerSrc || '/images/marker.png',
        bingMapsApiKey: element.dataset.bingmapsapikey,
        lonInputId: element.dataset.lonInput,
        latInputId: element.dataset.latInput,
        precision: element.dataset.precision ? parseInt(element.dataset.precision) : 4
    };
    
    // Get input elements if specified
    const lonInput = config.lonInputId ? document.getElementById(config.lonInputId) : null;
    const latInput = config.latInputId ? document.getElementById(config.latInputId) : null;
    
    // Validate required parameters
    if (isNaN(config.initialLon) || isNaN(config.initialLat)) {
        throw new Error('Initial longitude and latitude must be provided via data-initial-lon and data-initial-lat attributes');
    }
    
    if (!config.bingMapsApiKey) {
        throw new Error('Bing Maps API key must be provided via data-bingmapsapikey attribute');
    }
    
    if (callback && typeof callback !== 'function') {
        throw new Error('Callback must be a function');
    }
    
    const marker = new ol.Feature({
        geometry: new ol.geom.Point(ol.proj.fromLonLat([config.initialLon, config.initialLat]))
    });
    const style = new ol.style.Style({
        image: new ol.style.Icon({
            anchor: [0.5, 1],
            src: config.markerSrc,
        }),
    });

    // Set the style for the marker
    marker.setStyle(style);

    const features = [marker];
    
    // Add suggested marker if coordinates are provided
    let suggestedMarker = null;
    if (config.suggestedLon !== null && config.suggestedLat !== null) {
        suggestedMarker = new ol.Feature({
            geometry: new ol.geom.Point(ol.proj.fromLonLat([config.suggestedLon, config.suggestedLat]))
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
    
    const map = new ol.Map({
        target: element,
        layers: [
            new ol.layer.Tile({
                title: 'Global Imagery',
                source: new ol.source.BingMaps({
                    key: config.bingMapsApiKey,
                    imagerySet: 'AerialWithLabelsOnDemand'
                })
            }),
            vectorLayer
        ],
        view: new ol.View({
            center: ol.proj.fromLonLat([config.initialLon, config.initialLat]),
            zoom: config.zoom
        })
    });

    // If both markers exist, fit the view to show both
    if (suggestedMarker) {
        // Calculate extent that includes both markers
        const extent = vectorSource.getExtent();
        map.getView().fit(extent, {
            size: map.getSize(),
            padding: [20, 20, 20, 20], // Optional padding around the extent
            maxZoom: 15 // Optional: limit the maximum zoom level
        });
    }

    const modify = new ol.interaction.Modify({
        hitDetection: vectorLayer,
        source: vectorSource,
        features: new ol.Collection([marker]) // Only the original marker is modifiable
    });
    map.addInteraction(modify);

    function updateFormInputs(lon, lat) {
        // Update input fields if they exist
        if (lonInput) {
            lonInput.value = lon.toFixed(config.precision);
        }
        if (latInput) {
            latInput.value = lat.toFixed(config.precision);
        }
    }
    // Utility function to update coordinates
    function updateCoordinates(lon, lat) {
        updateFormInputs(lon, lat);
        
        // Call the custom callback if provided
        if (callback) {
            try {
                callback(lon, lat);
            } catch {
                // pass
            }
        }
    }

    // Add a listener to the drag-and-drop interaction
    modify.on('modifyend', (e) => {
        const coords = e.features.getArray()[0].getGeometry().getCoordinates();
        const lonLat = ol.proj.toLonLat(coords);
        updateCoordinates(lonLat[0], lonLat[1]);
    });
    
    // Add bidirectional sync: input fields → map marker
    if (lonInput && latInput) {
        // Set initial values in inputs before any listeners are added
        updateFormInputs(config.initialLon, config.initialLat);

        function syncFromInputs() {
            const lon = parseFloat(lonInput.value);
            const lat = parseFloat(latInput.value);
            
            if (!isNaN(lon) && !isNaN(lat)) {
                // Update marker position
                const newCoords = ol.proj.fromLonLat([lon, lat]);
                marker.getGeometry().setCoordinates(newCoords);
                
                // Center map on new position
                map.getView().setCenter(newCoords);
            }
        }
        
        // Add event listeners to input fields
        lonInput.addEventListener('input', syncFromInputs);
        lonInput.addEventListener('change', syncFromInputs);
        latInput.addEventListener('input', syncFromInputs);
        latInput.addEventListener('change', syncFromInputs);
        
    }

    return { map, marker, suggestedMarker, config, lonInput, latInput };
}

window.ols = olSelectLonLat;
