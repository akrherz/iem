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

(function() {
    'use strict';

    // Helper functions for olSelectLonLat complexity reduction - encapsulated to avoid conflicts
    function extractConfig(element) {
        return {
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
    }

    function validateConfig(config, callback) {
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
    }

    function createMarker(config) {
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
        return marker;
    }

    function createSuggestedMarker(config) {
        if (config.suggestedLon === null || config.suggestedLat === null) {
            return null;
        }
        
        const suggestedMarker = new ol.Feature({
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
        return suggestedMarker;
    }

    function createMapWithMarkers(element, config) {
        const marker = createMarker(config);
        const suggestedMarker = createSuggestedMarker(config);
        
        const features = [marker];
        if (suggestedMarker) {
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
        
        return { marker, suggestedMarker, vectorSource, map };
    }

    function updateFormInputs(lonInput, latInput, config, lon, lat) {
        // Update input fields if they exist
        if (lonInput) {
            lonInput.value = lon.toFixed(config.precision);
        }
        if (latInput) {
            latInput.value = lat.toFixed(config.precision);
        }
    }

    // Utility function to update coordinates
    function updateCoordinates(callback, config, lonInput, latInput, lon, lat) {
        updateFormInputs(lonInput, latInput, config, lon, lat);
        
        // Call the custom callback if provided
        if (callback) {
            try {
                callback(lon, lat);
            } catch {
                // pass
            }
        }
    }

    function syncFromInputs(marker, map, lonInput, latInput) {
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

    function setupMapInteractions(map, marker, vectorSource, callback, config, lonInput, latInput) {
        const modify = new ol.interaction.Modify({
            hitDetection: map.getLayers().getArray()[1], // vectorLayer
            source: vectorSource,
            features: new ol.Collection([marker]) // Only the original marker is modifiable
        });
        map.addInteraction(modify);

        // Add a listener to the drag-and-drop interaction
        modify.on('modifyend', (e) => {
            const coords = e.features.getArray()[0].getGeometry().getCoordinates();
            const lonLat = ol.proj.toLonLat(coords);
            updateCoordinates(callback, config, lonInput, latInput, lonLat[0], lonLat[1]);
        });
        
        // Add bidirectional sync: input fields → map marker
        if (lonInput && latInput) {
            // Set initial values in inputs before any listeners are added
            updateFormInputs(lonInput, latInput, config, config.initialLon, config.initialLat);

            // Add event listeners to input fields
            lonInput.addEventListener('input', () => syncFromInputs(marker, map, lonInput, latInput));
            lonInput.addEventListener('change', () => syncFromInputs(marker, map, lonInput, latInput));
            latInput.addEventListener('input', () => syncFromInputs(marker, map, lonInput, latInput));
            latInput.addEventListener('change', () => syncFromInputs(marker, map, lonInput, latInput));
        }
    }

    // Main function - the only global export
    function olSelectLonLat(div, callback) {
        const element = typeof div === 'string' ? document.getElementById(div) : div;
        
        if (!element) {
            throw new Error(`Element with ID '${div}' not found`);
        }
        
        // Extract configuration from data attributes
        const config = extractConfig(element);
        
        // Get input elements if specified
        const lonInput = config.lonInputId ? document.getElementById(config.lonInputId) : null;
        const latInput = config.latInputId ? document.getElementById(config.latInputId) : null;
        
        // Validate configuration
        validateConfig(config, callback);
        
        // Create markers and map
        const { marker, suggestedMarker, vectorSource, map } = createMapWithMarkers(element, config);
        
        // Setup interactions
        setupMapInteractions(map, marker, vectorSource, callback, config, lonInput, latInput);
        
        return { map, marker, suggestedMarker, config, lonInput, latInput };
    }

    // Export to global scope
    window.olSelectLonLat = olSelectLonLat;

})();
