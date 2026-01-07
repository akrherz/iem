/* global ol */
let renderattr = 'high';
let vectorLayer = null;
let map = null;
let popup = null;
let fontSize = 14;

/**
 * Replace HTML special characters with their entity equivalents
 */
function escapeHTML(val) {
    return val
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

/**
 * Get current date string from date picker (YYYY-MM-DD format)
 * Avoids timezone issues by working directly with the string value
 */
function getCurrentDateString() {
    const datePicker = document.getElementById('datepicker');
    return escapeHTML(datePicker.value); // Already in YYYY-MM-DD format
}

/**
 * Update URL parameters with current state
 */
function updateURL() {
    const dateStr = getCurrentDateString();
    const url = new URL(window.location);
    url.searchParams.set('date', dateStr);
    url.searchParams.set('var', renderattr);

    // Add map position
    if (map) {
        const view = map.getView();
        const center = ol.proj.toLonLat(view.getCenter());
        url.searchParams.set('lon', center[0].toFixed(4));
        url.searchParams.set('lat', center[1].toFixed(4));
        url.searchParams.set('zoom', view.getZoom().toFixed(0));
    }

    window.history.pushState({}, '', url);
}

/**
 * Update map with new render attribute
 */
function updateMap() {
    const selectElement = document.getElementById('renderattr');
    renderattr = escapeHTML(selectElement.value);
    vectorLayer.setStyle(vectorLayer.getStyle());
    updateURL();
}

/**
 * Update map with new date
 */
function updateDate() {
    const dateStr = getCurrentDateString();

    // Show loading state
    const mapElement = document.getElementById('map');
    mapElement.classList.add('loading');

    map.removeLayer(vectorLayer);
    vectorLayer = makeVectorLayer(dateStr);
    map.addLayer(vectorLayer);

    // Remove loading state after a brief delay
    setTimeout(() => {
        mapElement.classList.remove('loading');
    }, 500);

    updateURL();
}

/**
 * Style function for vector features
 */
const vectorStyleFunction = feature => {
    let style = null;
    const value = feature.get(renderattr);
    const outlinecolor = '#000000';
    if (value !== null && !isNaN(value)) {
        style = [
            new ol.style.Style({
                fill: new ol.style.Fill({
                    color: 'rgba(255, 255, 255, 0.6)',
                }),
                text: new ol.style.Text({
                    font: `${fontSize}px Calibri,sans-serif`,
                    text: value.toString(),
                    fill: new ol.style.Fill({
                        color: '#FFFFFF',
                        width: 1,
                    }),
                    stroke: new ol.style.Stroke({
                        color: outlinecolor,
                        width: 3,
                    }),
                }),
            }),
        ];
    } else {
        style = [
            new ol.style.Style({
                image: new ol.style.Circle({
                    fill: new ol.style.Fill({
                        color: 'rgba(255,255,255,0.4)',
                    }),
                    stroke: new ol.style.Stroke({
                        color: '#3399CC',
                        width: 1.25,
                    }),
                    radius: 5,
                }),
                fill: new ol.style.Fill({
                    color: 'rgba(255,255,255,0.4)',
                }),
                stroke: new ol.style.Stroke({
                    color: '#3399CC',
                    width: 1.25,
                }),
            }),
        ];
    }
    return style;
};

/**
 * Create vector layer for given date
 */
function makeVectorLayer(dt) {
    return new ol.layer.Vector({
        source: new ol.source.Vector({
            format: new ol.format.GeoJSON(),
            projection: ol.proj.get('EPSG:3857'),
            url: `/geojson/coopobs.py?valid=${dt}`,
        }),
        style: vectorStyleFunction,
    });
}

/**
 * Extract feature data with defaults
 */
function getFeatureData(feature) {
    const get = (key, defaultValue = 'N/A') => feature.get(key) ?? defaultValue;

    return {
        station: feature.get('station'),
        network: feature.get('network'),
        name: get('name'),
        utcValid: get('utc_valid'),
        coopTmpf: get('coop_tmpf'),
        hour: get('hour'),
        high: get('high', 'M'),
        low: get('low', 'M'),
        precip: get('precip', 'M'),
        snow: get('snow', 'M'),
        snowd: get('snowd', 'M'),
        report: get('report')
    };
}

/**
 * Create and show popover with feature information
 */
function showPopover(feature, coordinate) {
    const data = getFeatureData(feature);

    const content = `
        <div class="p-2" style="font-family: monospace; white-space: pre-wrap; font-size: 12px;">
<strong>NWSLI:</strong> <a target="_blank" href="/sites/site.php?station=${data.station}&network=${data.network}">${data.station}</a>
<strong>Name:</strong> ${data.name}
<strong>Reported At:</strong> ${data.utcValid}
<strong>Report Local Hour:</strong> ${data.hour}
<strong>Air Temp:</strong> ${data.coopTmpf} <strong>High:</strong> ${data.high} <strong>Low:</strong> ${data.low}
<strong>Precip:</strong> ${data.precip}
<strong>Snow:</strong> ${data.snow} <strong>Snow Depth:</strong> ${data.snowd}
<strong>SHEF Report:</strong> ${data.report}
        </div>
    `;

    // Use the OpenLayers popup element directly
    const popupElement = document.getElementById('popup');
    popupElement.innerHTML = `
        <div class="popover bs-popover-top show">
            <div class="popover-arrow"></div>
            <div class="popover-body">${content}</div>
        </div>
    `;

    // Position the popup using OpenLayers
    popup.setPosition(coordinate);
}

/**
 * Hide popover
 */
function hidePopover() {
    const popupElement = document.getElementById('popup');
    popupElement.innerHTML = '';
    popup.setPosition(null);
}

/**
 * Fetch and display CLI report
 */
async function fetchCLIReport(url) {
    const reportDiv = document.getElementById('clireport');
    reportDiv.innerHTML =
        '<div class="d-flex align-items-center"><div class="spinner-border spinner-border-sm me-2" role="status"></div>Loading CLI report...</div>';

    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.text();
        reportDiv.innerHTML = `<pre class="mb-0">${data}</pre>`;
    } catch (error) {
        reportDiv.innerHTML = `<div class="alert alert-warning mb-0">Failed to fetch CLI report. ${error} Please try again.</div>`;
    }
}

/**
 * Set date picker to specific date string (YYYY-MM-DD format)
 * Avoids timezone issues by working directly with string values
 */
function setDatePickerValue(dateStr) {
    const datePicker = document.getElementById('datepicker');
    datePicker.value = dateStr;
}

/**
 * Parse URL parameters and update interface
 * Handles migration from legacy hash-based URLs to modern URL parameters
 * Legacy format: #YYMMDD/variable -> Modern format: ?date=YYYY-MM-DD&var=variable
 */
function parseURLParameters() {
    const urlParams = new URLSearchParams(window.location.search);

    // Check for legacy hash parameters first and migrate them
    const tokens = window.location.href.split('#');
    if (tokens.length === 2) {
        const hashTokens = tokens[1].split('/');
        if (hashTokens.length === 2) {
            const tpart = escapeHTML(hashTokens[0]);
            const hashRenderattr = escapeHTML(hashTokens[1]);

            // Parse date from hash (YYMMDD format) and convert to YYYY-MM-DD
            if (tpart.length === 6) {
                const year = 2000 + parseInt(tpart.substring(0, 2));
                const month = String(parseInt(tpart.substring(2, 4))).padStart(2, '0');
                const day = String(parseInt(tpart.substring(4, 6))).padStart(2, '0');
                const dateStr = `${year}-${month}-${day}`;

                // Redirect to new URL format
                const newUrl = new URL(window.location);
                newUrl.hash = '';
                newUrl.searchParams.set('date', dateStr);
                newUrl.searchParams.set('var', hashRenderattr);
                window.location.replace(newUrl.toString());
                return;
            }
        }
    }

    // Handle modern URL parameters
    const dateParam = urlParams.get('date');
    const varParam = urlParams.get('var');

    if (varParam) {
        renderattr = escapeHTML(varParam);
        const selectElement = document.getElementById('renderattr');
        selectElement.value = renderattr;
    }

    if (dateParam) {
        // Validate date format (YYYY-MM-DD) and set directly to avoid timezone issues
        if (/^\d{4}-\d{2}-\d{2}$/.test(dateParam)) {
            setDatePickerValue(dateParam);
            updateDate();
        }
    }
}

/**
 * Initialize the application
 */
document.addEventListener('DOMContentLoaded', () => {
    // Initialize renderattr from the form's selected value
    const selectElement = document.getElementById('renderattr');
    renderattr = selectElement.value;

    // Set up date picker (PHP already sets the initial value)
    const datePicker = document.getElementById('datepicker');

    // Set up date picker change handler
    datePicker.addEventListener('change', () => {
        updateDate();
    });

    // Initialize vector layer with current date picker value
    const currentDateStr = getCurrentDateString();
    vectorLayer = makeVectorLayer(currentDateStr);

    // Get map position from URL or use defaults
    const urlParams = new URLSearchParams(window.location.search);
    const lon = parseFloat(urlParams.get('lon')) || -95.0;
    const lat = parseFloat(urlParams.get('lat')) || 42.0;
    const zoom = parseInt(urlParams.get('zoom')) || 3;
    const center = ol.proj.fromLonLat([lon, lat]);

    // Set up map
    map = new ol.Map({
        target: 'map',
        layers: [
            new ol.layer.Tile({
                title: 'Global Imagery',
                source: new ol.source.XYZ({
                    attributions:
                        'Tiles © <a href="https://services.arcgisonline.com/ArcGIS/' +
                        'rest/services/World_Imagery/MapServer">ArcGIS</a>',
                    url:
                        'https://server.arcgisonline.com/ArcGIS/rest/services/' +
                        'World_Imagery/MapServer/tile/{z}/{y}/{x}',
                }),
            }),
            new ol.layer.Tile({
                title: 'State Boundaries',
                source: new ol.source.XYZ({
                    url: '/c/tile.py/1.0.0/usstates/{z}/{x}/{y}.png',
                }),
            }),
            vectorLayer,
        ],
        view: new ol.View({
            projection: 'EPSG:3857',
            center,
            zoom,
        }),
    });

    map.addControl(new ol.control.LayerSwitcher());

    // Update URL when map is moved or zoomed
    map.on('moveend', () => {
        updateURL();
    });

    // Set up popup overlay
    const element = document.getElementById('popup');
    popup = new ol.Overlay({
        element,
        positioning: 'bottom-center',
        stopEvent: true, // Allow clicks on links inside the popup
    });
    map.addOverlay(popup);

    // Handle map clicks
    map.on('click', evt => {
        const feature = map.forEachFeatureAtPixel(evt.pixel, feature2 => {
            return feature2;
        });

        if (feature) {
            const geometry = feature.getGeometry();
            const coord = geometry.getCoordinates();
            showPopover(feature, coord);

            // Fetch CLI report
            const link = feature.get('link');
            if (link) {
                fetchCLIReport(link);
            }
        } else {
            hidePopover();
        }
    });

    // Parse URL parameters if present
    parseURLParameters();

    // Font size buttons
    document.getElementById('fplus').addEventListener('click', () => {
        fontSize += 2;
        vectorLayer.setStyle(vectorStyleFunction);
    });

    document.getElementById('fminus').addEventListener('click', () => {
        fontSize -= 2;
        vectorLayer.setStyle(vectorStyleFunction);
    });

    // Render attribute change handler
    document.getElementById('renderattr').addEventListener('change', () => {
        updateMap();
    });
});
