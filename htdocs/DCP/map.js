/* global ol */
let physical_code = "EP";
let duration = "D";
let days = 2;
let vectorLayer = null;
let map = null;
let fontSize = 14;

/**
 * Replace HTML special characters with their entity equivalents
 */
function escapeHTML(val) {
    return val.replace(/&/g, '&amp;')
              .replace(/</g, '&lt;')
              .replace(/>/g, '&gt;')
              .replace(/"/g, '&quot;')
              .replace(/'/g, '&#039;');
}

/**
 * Update the URL with current parameters using URLSearchParams
 */
function updateURL() {
    const url = new URL(window.location);
    url.searchParams.set('pe', physical_code);
    url.searchParams.set('duration', duration);
    url.searchParams.set('days', days);
    // Clear any legacy hash
    url.hash = '';
    window.history.replaceState({}, '', url);
}

/**
 * Update the map with current form values
 */
function updateMap() {
    const peSelect = document.getElementById('pe');
    const durationSelect = document.getElementById('duration');
    const daysInput = document.getElementById('days');
    
    // Validate that all required fields have values
    if (!peSelect.value || !durationSelect.value || !daysInput.value.trim()) {
        return; // Don't update if any field is empty
    }
    
    // Validate that days is a positive number
    const daysValue = parseInt(daysInput.value.trim(), 10);
    if (isNaN(daysValue) || daysValue <= 0) {
        return; // Don't update if days is not a valid positive number
    }
    
    physical_code = escapeHTML(peSelect.value);
    duration = escapeHTML(durationSelect.value);
    days = daysValue; // Use the validated number
    
    map.removeLayer(vectorLayer);
    vectorLayer = makeVectorLayer();
    map.addLayer(vectorLayer);
    updateURL();
}

const vectorStyleFunction = (feature) => {
    let style = null;
    if (feature.get("value") !== "M") {
        style = [new ol.style.Style({
            fill: new ol.style.Fill({
                color: 'rgba(255, 255, 255, 0.6)'
            }),
            text: new ol.style.Text({
                font: `${fontSize}px Calibri,sans-serif`,
                text: feature.get("value").toString(),
                fill: new ol.style.Fill({
                    color: '#FFFFFF',
                    width: 1
                }),
                stroke: new ol.style.Stroke({
                    color: '#000000',
                    width: 3
                })
            })
        })];
    } else {
        style = [new ol.style.Style({
            image: new ol.style.Circle({
                fill: new ol.style.Fill({
                    color: 'rgba(255,255,255,0.4)'
                }),
                stroke: new ol.style.Stroke({
                    color: '#3399CC',
                    width: 1.25
                }),
                radius: 5
            }),
            fill: new ol.style.Fill({
                color: 'rgba(255,255,255,0.4)'
            }),
            stroke: new ol.style.Stroke({
                color: '#3399CC',
                width: 1.25
            })
        })
        ];
    }
    return style;
};

/**
 * Create and return a vector layer with current parameters
 */
function makeVectorLayer() {
    const vs = new ol.source.Vector({
        format: new ol.format.GeoJSON(),
        projection: ol.proj.get('EPSG:3857'),
        url: `/api/1/shef_currents.geojson?duration=${duration}&pe=${physical_code}&days=${days}`
    });
    vs.on('change', () => {
        if (vs.getFeatures().length === 0) {
            alert("No Data Found!");  // skipcq
        }
    });
    return new ol.layer.Vector({
        source: vs,
        style: vectorStyleFunction
    });
}

/**
 * Show a popup with station information
 */
function showPopup(coord, content) {
    // Create a simple popup div if it doesn't exist
    let popupDiv = document.getElementById('simple-popup');
    if (!popupDiv) {
        popupDiv = document.createElement('div');
        popupDiv.id = 'simple-popup';
        popupDiv.className = 'simple-popup';
        document.body.appendChild(popupDiv);
    }
    
    // Create close button element
    const closeButton = document.createElement('div');
    closeButton.innerHTML = '×';
    closeButton.className = 'popup-close-button';
    closeButton.addEventListener('click', hidePopup);
    
    // Set content with close button
    popupDiv.innerHTML = '';
    popupDiv.appendChild(closeButton);
    const contentDiv = document.createElement('div');
    contentDiv.innerHTML = content;
    popupDiv.appendChild(contentDiv);
    
    popupDiv.style.display = 'block';
    
    // Position the popup near the click location
    const pixel = map.getPixelFromCoordinate(coord);
    const mapElement = document.getElementById('map');
    const rect = mapElement.getBoundingClientRect();
    
    // Add scroll offsets to handle page scrolling
    const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    
    // Calculate popup position with proper offsets
    const left = rect.left + scrollLeft + pixel[0] + 10;
    const top = rect.top + scrollTop + pixel[1] - 60;
    
    popupDiv.style.left = `${left}px`;
    popupDiv.style.top = `${top}px`;
}

/**
 * Hide the popup
 */
function hidePopup() {
    const popupDiv = document.getElementById('simple-popup');
    if (popupDiv) {
        popupDiv.style.display = 'none';
    }
}

/**
 * Initialize the map and UI components
 */
function initializeMap() {
    vectorLayer = makeVectorLayer();
    const key = document.getElementById('map').dataset.bingmapsapikey;
    map = new ol.Map({
        target: 'map',
        layers: [new ol.layer.Tile({
            title: 'Global Imagery',
            source: new ol.source.BingMaps({ key, imagerySet: 'Aerial' })
        }),
        new ol.layer.Tile({
            title: 'State Boundaries',
            source: new ol.source.XYZ({
                url: '/c/tile.py/1.0.0/usstates/{z}/{x}/{y}.png'
            })
        }),
            vectorLayer
        ],
        view: new ol.View({
            projection: 'EPSG:3857',
            center: [-10575351, 5160979],
            zoom: 3
        })
    });

    const layerSwitcher = new ol.control.LayerSwitcher();
    map.addControl(layerSwitcher);

    // Handle map clicks for popup display
    map.on('click', (evt) => {
        const feature = map.forEachFeatureAtPixel(evt.pixel,
            (feature2) => {
                return feature2;
            });
        if (feature) {
            const geometry = feature.getGeometry();
            const coord = geometry.getCoordinates();
            const content = `<p><strong>ID:</strong> ${feature.get('station')}<br /><strong>Value:</strong> ${feature.get('value')}<br /><strong>UTC Valid:</strong> ${feature.get('utc_valid')}</p>`;
            showPopup(coord, content);
        } else {
            hidePopup();
        }
    });
}

/**
 * Parse URL parameters and set form values, handling legacy hash format
 */
// Refactored for ESLint complexity: break into focused helpers (Rule: module-specific orchestration, legacy/Non-ESM)
function parseLegacyHashParams() {
    const url = new URL(window.location);
    if (url.hash && url.hash.includes('.')) {
        const hashTokens = url.hash.substring(1).split('.');
        if (hashTokens.length === 3) {
            const pe = escapeHTML(hashTokens[0]);
            const dur = escapeHTML(hashTokens[1]);
            const daysParam = parseInt(hashTokens[2], 10);
            if (!isNaN(daysParam) && daysParam > 0) {
                return { pe, dur, days: daysParam, migrated: true };
            }
        }
    }
    return { migrated: false };
}

function parseModernUrlParams() {
    const url = new URL(window.location);
    const pe = url.searchParams.has('pe') ? escapeHTML(url.searchParams.get('pe')) : null;
    const dur = url.searchParams.has('duration') ? escapeHTML(url.searchParams.get('duration')) : null;
    let daysVal = null;
    if (url.searchParams.has('days')) {
        const daysParam = parseInt(url.searchParams.get('days'), 10);
        if (!isNaN(daysParam) && daysParam > 0) {
            daysVal = daysParam;
        }
    }
    return { pe, dur, days: daysVal };
}

function parseURLParams() {
    // Try legacy hash first
    const legacy = parseLegacyHashParams();
    let migrated = false;
    if (legacy.migrated) {
        physical_code = legacy.pe;
        duration = legacy.dur;
        days = legacy.days;
        migrated = true;
    }

    // Modern URL params override hash
    const modern = parseModernUrlParams();
    if (modern.pe) {
        physical_code = modern.pe;
        migrated = false;
    }
    if (modern.dur) {
        duration = modern.dur;
        migrated = false;
    }
    if (modern.days) {
        days = modern.days;
        migrated = false;
    }

    if (migrated) {
        updateURL();
    }

    // Set form values based on parsed or default values
    const peSelect = document.getElementById('pe');
    const durationSelect = document.getElementById('duration');
    const daysInput = document.getElementById('days');

    if (peSelect) peSelect.value = physical_code;
    if (durationSelect) durationSelect.value = duration;
    if (daysInput) daysInput.value = days;
}

/**
 * Initialize font size controls
 */
function initializeFontControls() {
    const fplusButton = document.getElementById('fplus');
    const fminusButton = document.getElementById('fminus');
    
    if (fplusButton) {
        fplusButton.addEventListener('click', () => {
            fontSize += 2;
            vectorLayer.setStyle(vectorStyleFunction);
        });
    }
    
    if (fminusButton) {
        fminusButton.addEventListener('click', () => {
            fontSize -= 2;
            vectorLayer.setStyle(vectorStyleFunction);
        });
    }
}

/**
 * Initialize the application
 */
function init() {
    initializeMap();
    parseURLParams();
    initializeFontControls();
    initializeFormHandlers();
    updateMap();
}

/**
 * Initialize form event handlers for real-time updates
 */
function initializeFormHandlers() {
    const peSelect = document.getElementById('pe');
    const durationSelect = document.getElementById('duration');
    const daysInput = document.getElementById('days');
    
    let inputTimeout = null;
    
    if (peSelect) {
        peSelect.addEventListener('change', updateMap);
    }
    if (durationSelect) {
        durationSelect.addEventListener('change', updateMap);
    }
    if (daysInput) {
        // Use debounced input to prevent updates while user is typing
        daysInput.addEventListener('input', () => {
            clearTimeout(inputTimeout);
            inputTimeout = setTimeout(updateMap, 500); // Wait 500ms after user stops typing
        });
        
        // Also update on blur (when user clicks away)
        daysInput.addEventListener('blur', updateMap);
    }
}

// Initialize when DOM is loaded
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
} else {
    init();
}
