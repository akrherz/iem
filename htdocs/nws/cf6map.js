/* global ol */
// CF6 Map Application - Modernized without jQuery
let renderattr = "high";
let vectorLayer = null;
let map = null;
let element = null;
let fontSize = 14;
let popup = null;

// Utility function to format date as YYYY-MM-DD
function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

// Parse date from YYMMDD format (for legacy hash links)
function parseDateShort(dateStr) {
    if (dateStr.length !== 6) return null;
    const year = 2000 + parseInt(dateStr.slice(0, 2));
    const month = parseInt(dateStr.slice(2, 4)) - 1;
    const day = parseInt(dateStr.slice(4, 6));
    return new Date(year, month, day);
}

function updateURL() {
    const dateInput = document.getElementById("datepicker");
    
    const url = new URL(window.location);
    url.searchParams.set('date', dateInput.value); // Store as YYYY-MM-DD
    url.searchParams.set('var', renderattr);
    window.history.pushState({}, '', url);
}

// Handle legacy hash links and convert to URL parameters
function handleLegacyHashLinks() {
    const hash = window.location.hash;
    if (hash) {
        const tokens = hash.substring(1).split("/"); // Remove # and split
        if (tokens.length === 2) {
            const tpart = tokens[0];
            const variable = tokens[1];
            
            // Parse date from YYMMDD format
            const parsedDate = parseDateShort(tpart);
            if (parsedDate && variable) {
                // Convert hash to URL params and redirect
                const url = new URL(window.location);
                url.hash = ''; // Remove hash
                url.searchParams.set('date', formatDate(parsedDate));
                url.searchParams.set('var', variable);
                window.history.replaceState({}, '', url);
                return { date: formatDate(parsedDate), variable };
            }
        }
    }
    return null;
}

// Read URL parameters and set initial state
function readURLParams() {
    const urlParams = new URLSearchParams(window.location.search);
    
    const date = urlParams.get('date');
    const variable = urlParams.get('var');
    
    return {
        date: date || null,
        variable: variable || null
    };
}

/**
 * Replace HTML special characters with their entity equivalents
 * @param string val 
 * @returns string converted string
 */
function escapeHTML(val) {
    return val.replace(/&/g, '&amp;')
              .replace(/</g, '&lt;')
              .replace(/>/g, '&gt;')
              .replace(/"/g, '&quot;')
              .replace(/'/g, '&#039;');
}
 
function updateMap() {
    renderattr = escapeHTML(document.getElementById('renderattr').value);
    vectorLayer.setStyle(vectorStyleFunction);
    updateURL();
}

function updateDate() {
    const dateInput = document.getElementById("datepicker");
    const fullDate = dateInput.value; // Already in YYYY-MM-DD format
    
    // Add loading class
    const mapElement = document.getElementById('map');
    mapElement.classList.add('loading');
    
    map.removeLayer(vectorLayer);
    vectorLayer = makeVectorLayer(fullDate);
    map.addLayer(vectorLayer);
    
    // Remove loading class after a delay
    setTimeout(() => {
        mapElement.classList.remove('loading');
    }, 1000);
    
    updateURL();
}

const vectorStyleFunction = function (feature) {
    let style = null;
    const value = feature.get(renderattr);
    let color = "#FFFFFF";
    const outlinecolor = "#000000";
    if (value !== "M") {
        if (renderattr.indexOf("depart") > -1) {
            if (renderattr.indexOf("high") > -1 || renderattr.indexOf("low") > -1) {
                if (value > 0) {
                    color = "#FF0000";
                } else if (value < 0) {
                    color = "#00FFFF";
                }
            } else {
                if (value < 0) {
                    color = "#FF0000";
                } else if (value > 0) {
                    color = "#00FFFF";
                }
            }
        }
        style = [new ol.style.Style({
            fill: new ol.style.Fill({
                color: 'rgba(255, 255, 255, 0.6)'
            }),
            text: new ol.style.Text({
                font: `${fontSize}px Calibri,sans-serif`,
                text: value.toString(),
                fill: new ol.style.Fill({
                    color,
                    width: 1
                }),
                stroke: new ol.style.Stroke({
                    color: outlinecolor,
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

function makeVectorLayer(dt) {
    return new ol.layer.Vector({
        source: new ol.source.Vector({
            format: new ol.format.GeoJSON(),
            projection: ol.proj.get('EPSG:3857'),
            url: `/geojson/cf6.py?dt=${dt}`
        }),
        style: vectorStyleFunction
    });
}

// Show popover with content
function showPopover(content) {
    const popoverContent = document.getElementById('popover-content');
    popoverContent.innerHTML = content;
    
    if (window.bootstrap?.Popover) {
        // Use Bootstrap 5 popover
        const popoverInstance = window.bootstrap.Popover.getInstance(element) || 
                               new window.bootstrap.Popover(element, {
                                   placement: 'top',
                                   html: true,
                                   content: () => popoverContent.innerHTML
                               });
        popoverInstance.show();
    }
}

// Hide popover
function hidePopover() {
    if (window.bootstrap?.Popover) {
        const popoverInstance = window.bootstrap.Popover.getInstance(element);
        if (popoverInstance) {
            popoverInstance.hide();
        }
    }
}

// Load CF6 report
function loadCF6Report(url) {
    const cf6report = document.getElementById('cf6report');
    cf6report.innerHTML = '<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div><p class="mt-2">Loading CF6 report...</p></div>';
    
    fetch(url)
        .then(response => response.text())
        .then(data => {
            cf6report.innerHTML = `<pre>${data}</pre>`;
        })
        .catch(() => {
            cf6report.innerHTML = '<div class="alert alert-danger"><i class="bi bi-exclamation-triangle me-2"></i>Error loading CF6 report</div>';
        });
}

// Initialize the application
function initializeApp() {
    // Set initial date to today
    const today = new Date();
    const dateInput = document.getElementById("datepicker");
    dateInput.value = formatDate(today);
    dateInput.max = formatDate(today); // Set max date to today
    dateInput.min = "2001-01-01"; // Set min date
    
    // Date change handler
    dateInput.addEventListener('change', updateDate);
    
    // Initialize vector layer
    vectorLayer = makeVectorLayer(formatDate(today));
    
    // Initialize map
    const key = document.getElementById("map").dataset.bingmapsapikey;
    map = new ol.Map({
        target: 'map',
        layers: [
            new ol.layer.Tile({
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

    // Add layer switcher
    map.addControl(new ol.control.LayerSwitcher());

    // Initialize popup
    element = document.getElementById('popup');
    popup = new ol.Overlay({
        element,
        positioning: 'bottom-center',
        stopEvent: false
    });
    map.addOverlay(popup);

    // Map click handler
    map.on('click', (evt) => {
        const feature = map.forEachFeatureAtPixel(evt.pixel, (feature2) => feature2);
        
        if (feature) {
            const geometry = feature.getGeometry();
            const coord = geometry.getCoordinates();
            popup.setPosition(coord);
            
            const content = `
                <div class="p-2">
                    <h6 class="mb-2"><strong>${feature.get('name') || 'Unknown Station'}</strong></h6>
                    <div class="row g-1 small">
                        <div class="col-6"><strong>High:</strong> ${feature.get('high') || 'N/A'}</div>
                        <div class="col-6"><strong>Low:</strong> ${feature.get('low') || 'N/A'}</div>
                        <div class="col-6"><strong>Precip:</strong> ${feature.get('precip') || 'N/A'}</div>
                        <div class="col-6"><strong>Snow:</strong> ${feature.get('snow') || 'N/A'}</div>
                    </div>
                </div>
            `;
            
            showPopover(content);
            
            // Load CF6 report
            const reportUrl = feature.get('link');
            if (reportUrl) {
                loadCF6Report(reportUrl);
            }
        } else {
            hidePopover();
        }
    });

    // Handle legacy hash links and URL parameters
    let initialParams = handleLegacyHashLinks();
    if (!initialParams) {
        initialParams = readURLParams();
    }
    
    // Set initial values from URL parameters or use defaults
    if (initialParams.date) {
        dateInput.value = initialParams.date;
    }
    
    if (initialParams.variable) {
        renderattr = initialParams.variable;
        const selectElement = document.getElementById('renderattr');
        selectElement.value = renderattr;
    }
    
    // Update map if we have parameters
    if (initialParams.date || initialParams.variable) {
        updateDate();
    }

    // Font size controls
    document.getElementById('fplus').addEventListener('click', () => {
        fontSize += 2;
        vectorLayer.setStyle(vectorStyleFunction);
    });
    
    document.getElementById('fminus').addEventListener('click', () => {
        fontSize = Math.max(8, fontSize - 2); // Minimum font size of 8
        vectorLayer.setStyle(vectorStyleFunction);
    });

    // Render attribute change handler
    document.getElementById('renderattr').addEventListener('change', updateMap);
}

// Initialize when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}
