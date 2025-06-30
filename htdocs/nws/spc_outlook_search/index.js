/* global ol, olSelectLonLat, Tabulator */
let marker = null;
let outlooksTable = null;
let mcdsTable = null; 
let watchesTable = null;

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

let loadingCount = 0;

function showLoading() {
    loadingCount++;
    if (loadingCount === 1) {
        // Only show loading on first request to prevent flicker
        document.getElementById('central-loading').style.display = 'block';
        document.getElementById('thetabs').classList.add('loading');
    }
}

function hideLoading() {
    loadingCount--;
    if (loadingCount <= 0) {
        loadingCount = 0;
        // Small delay to ensure user sees the loading indicator
        setTimeout(() => {
            document.getElementById('central-loading').style.display = 'none';
            document.getElementById('thetabs').classList.remove('loading');
        }, 100);
    }
}

function workflow() {
    const lon = parseFloat(document.getElementById("lon").value);
    const lat = parseFloat(document.getElementById("lat").value);
    if (isNaN(lon) || isNaN(lat)) {
        return;
    }
    updateSearchResultsHeader(lon, lat);
    doOutlook(lon, lat);
    doMCD(lon, lat);
    doWatch(lon, lat);
}

function updateURLParams(params = {}) {
    const url = new URL(window.location.href);
    // Update provided parameters
    Object.entries(params).forEach(([key, value]) => {
        if (value !== null) {
            url.searchParams.set(key, value);
        }
    });
    window.history.replaceState({}, '', url);
}

function updateMarkerPosition(lon, lat) {
    // Round lat/lon to 4 decimal places for URL params
    const roundedLon = parseFloat(lon.toFixed(4));
    const roundedLat = parseFloat(lat.toFixed(4));
    
    // Update input fields with rounded values
    document.getElementById("lon").value = roundedLon;
    document.getElementById("lat").value = roundedLat;
    
    updateURLParams({lon: roundedLon, lat: roundedLat});
    workflow();
}

function buildUI() {
    document.getElementById("manualpt").addEventListener("click", () => {
        const la = parseFloat(document.getElementById("lat").value);
        const lo = parseFloat(document.getElementById("lon").value);
        marker.setGeometry(new ol.geom.Point(ol.proj.fromLonLat([lo, la])));
        updateMarkerPosition(lo, la);
    });
    document.getElementById('last').addEventListener('change', () => {
        const last = document.getElementById('last').checked ? '1' : '0';
        updateURLParams({last});
        workflow();
    });
    document.getElementById('events').addEventListener('change', () => {
        const events = document.getElementById('events').value;
        updateURLParams({events});
        workflow();
    });
    document.querySelectorAll('input[type=radio][name=day]').forEach(radio => {
        radio.addEventListener('change', () => {
            const day = document.querySelector("input[name='day']:checked").value;
            updateURLParams({day});
            workflow();
        });
    });
    document.querySelectorAll('input[type=radio][name=cat]').forEach(radio => {
        radio.addEventListener('change', () => {
            const cat = document.querySelector("input[name='cat']:checked").value;
            updateURLParams({cat});
            workflow();
        });
    });
}


function updateSearchResultsHeader(lon, lat) {
    const header = document.getElementById('search-results-header');
    if (header) {
        header.textContent = `Results of Point Search (${lat.toFixed(4)}°N, ${lon.toFixed(4)}°E)`;
    }
}

function doOutlook(lon, lat) {
    const last = document.getElementById('last').checked ? escapeHTML(document.getElementById('events').value) : '0';
    const day = escapeHTML(document.querySelector("input[name='day']:checked").value);
    const cat = escapeHTML(document.querySelector("input[name='cat']:checked").value);
    
    showLoading();
    const jsonurl = `/json/spcoutlook.py?lon=${lon}&lat=${lat}&last=${last}&day=${day}&cat=${cat}`;
    document.getElementById("outlooks_link").href = jsonurl;
    const excelurl = `/json/spcoutlook.py?lon=${lon}&lat=${lat}&last=${last}&day=${day}&cat=${cat}&fmt=excel`;
    document.getElementById("outlooks_excel").href = excelurl;
    const csvurl = `/json/spcoutlook.py?lon=${lon}&lat=${lat}&last=${last}&day=${day}&cat=${cat}&fmt=csv`;
    document.getElementById("outlooks_csv").href = csvurl;
    
    fetch(jsonurl)
        .then(response => response.json())
        .then(data => {
            hideLoading();
            outlooksTable.replaceData(data.outlooks || []);
        })
        .catch(() => {
            hideLoading();
        });
}
function doMCD(lon, lat) {
    showLoading();
    const jsonurl = `/json/spcmcd.py?lon=${lon}&lat=${lat}`;
    document.getElementById("mcds_link").href = jsonurl;
    const excelurl = `/json/spcmcd.py?lon=${lon}&lat=${lat}&fmt=excel`;
    document.getElementById("mcds_excel").href = excelurl;
    const csvurl = `/json/spcmcd.py?lon=${lon}&lat=${lat}&fmt=csv`;
    document.getElementById("mcds_csv").href = csvurl;
    
    fetch(jsonurl)
        .then(response => response.json())
        .then(data => {
            hideLoading();
            mcdsTable.replaceData(data.mcds || []);
        })
        .catch(() => {
            hideLoading();
        });
}

function doWatch(lon, lat) {
    showLoading();
    const jsonurl = `/json/spcwatch.py?lon=${lon}&lat=${lat}`;
    document.getElementById("watches_link").href = jsonurl;
    const excelurl = `/json/spcwatch.py?lon=${lon}&lat=${lat}&fmt=excel`;
    document.getElementById("watches_excel").href = excelurl;
    const csvurl = `/json/spcwatch.py?lon=${lon}&lat=${lat}&fmt=csv`;
    document.getElementById("watches_csv").href = csvurl;
    
    fetch(jsonurl)
        .then(response => response.json())
        .then(data => {
            hideLoading();
            // Extract properties from features array for Tabulator
            const watchData = data.features ? data.features.map(f => f.properties) : [];
            watchesTable.replaceData(watchData);
        })
        .catch(() => {
            hideLoading();
        });
}

function convertLegacyHashLink() {
    // Do the anchor tag linking, please
    const tokens = window.location.href.split("#");
    if (tokens.length === 2) {
        const tokens2 = tokens[1].split("/");
        if (tokens2.length === 3) {
            if (tokens2[0] === 'bypoint') {
                const lon = parseFloat(tokens2[1]);
                const lat = parseFloat(tokens2[2]);
                marker.setGeometry(new ol.geom.Point(ol.proj.fromLonLat([lon, lat])));
                updateMarkerPosition(lon, lat);
            }
        }
        // Remove the hash from the URL
        window.history.replaceState({}, '', tokens[0]);
    }
}

function restoreCoordinatesFromURL(urlParams) {
    const lon = parseFloat(urlParams.get('lon'));
    const lat = parseFloat(urlParams.get('lat'));
    if (!isNaN(lon) && !isNaN(lat)) {
        // Update input fields with rounded values
        document.getElementById("lon").value = lon.toFixed(4);
        document.getElementById("lat").value = lat.toFixed(4);
        marker.setGeometry(new ol.geom.Point(ol.proj.fromLonLat([lon, lat])));
        // Don't call updateMarkerPosition here as it triggers workflow()
        // The workflow will be called once from readURLParams() if needed
    }
}

function restoreFormSelectionFromURL(urlParams) {
    // Set the day selection if provided in URL
    const day = urlParams.get('day');
    if (day) {
        const dayRadio = document.querySelector(`input[name='day'][value='${escapeHTML(day)}']`);
        if (dayRadio) {
            dayRadio.checked = true;
        }
    }
    // Set the category selection if provided in URL
    const cat = urlParams.get('cat');
    if (cat) {
        const catRadio = document.querySelector(`input[name='cat'][value='${escapeHTML(cat)}']`);
        if (catRadio) {
            catRadio.checked = true;
        }
    }
    // Set the "List Most Recent" checkbox if provided in URL
    const last = urlParams.get('last');
    if (last === '1') {
        document.getElementById('last').checked = true;
    }
    // Set the event count if provided in URL
    const events = urlParams.get('events');
    if (events) {
        const eventCount = parseInt(events, 10);
        if (!isNaN(eventCount) && eventCount >= 1 && eventCount <= 100) {
            document.getElementById('events').value = eventCount;
        }
    }
    return { day, cat, last };
}

function readURLParams(){
    // Read the URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    restoreCoordinatesFromURL(urlParams);
    const { day, cat, last } = restoreFormSelectionFromURL(urlParams);
    
    // Trigger workflow if we have coordinates and any search parameters
    const lon = parseFloat(urlParams.get('lon'));
    const lat = parseFloat(urlParams.get('lat'));
    const hasValidCoordinates = !isNaN(lon) && !isNaN(lat);
    
    if (hasValidCoordinates && (day || cat || last)) {
        workflow();
    }
}

function initializeTables() {
    // Initialize Outlooks table
    outlooksTable = new Tabulator("#outlooks", {
        layout: "fitColumns",
        height: "70vh",
        placeholder: "Click 'Update' or select a point on the map to search for convective outlooks",
        columns: [
            {title: "Day", field: "day", width: 80},
            {title: "Threshold", field: "threshold", width: 120},
            {title: "Outlook Issued At (UTC)", field: "utc_product_issue", widthGrow: 1},
            {title: "Outlook Begins (UTC)", field: "utc_issue", widthGrow: 1},
            {title: "Outlook Expires (UTC)", field: "utc_expire", widthGrow: 1}
        ]
    });

    // Initialize MCDs table
    mcdsTable = new Tabulator("#mcds", {
        layout: "fitColumns",
        height: "70vh",
        placeholder: "Click 'Update' or select a point on the map to search for mesoscale convective discussions",
        columns: [
            {
                title: "Discussion Number", 
                field: "product_num", 
                width: 150,
                formatter: (cell) => {
                    const data = cell.getRow().getData();
                    return `<a href="${data.spcurl}" target="_blank">${data.year} ${data.product_num}</a>`;
                }
            },
            {title: "UTC Valid", field: "utc_issue", widthGrow: 1},
            {title: "UTC Expire", field: "utc_expire", widthGrow: 1},
            {title: "Watch Confidence", field: "watch_confidence", width: 130},
            {title: "Concerning", field: "concerning", widthGrow: 1},
            {title: "Most Prob Tornado", field: "most_prob_tornado", width: 140},
            {title: "Most Prob Hail", field: "most_prob_hail", width: 130},
            {title: "Most Prob Gust", field: "most_prob_gust", width: 130}
        ]
    });

    // Initialize Watches table
    watchesTable = new Tabulator("#watches", {
        layout: "fitColumns",
        height: "70vh",
        placeholder: "Click 'Update' or select a point on the map to search for convective watches",
        columns: [
            {
                title: "Watch Number", 
                field: "number", 
                width: 130,
                formatter: (cell) => {
                    const data = cell.getRow().getData();
                    return `<a href="${data.spcurl}" target="_blank">${data.year} ${data.number}</a>`;
                }
            },
            {title: "Type", field: "type", width: 80},
            {title: "UTC Valid", field: "issue", widthGrow: 1},
            {title: "UTC Expire", field: "expire", widthGrow: 1},
            {title: "Max Hail Size", field: "max_hail_size", width: 120},
            {title: "Max Wind Speed", field: "max_wind_gust_knots", width: 130},
            {
                title: "Is PDS?", 
                field: "is_pds", 
                width: 80,
                formatter: (cell) => {
                    const value = cell.getValue();
                    if (value === 'YES') {
                        return '<span class="badge bg-danger pds-badge">PDS</span>';
                    }
                    return value || '';
                }
            }
        ]
    });
}

document.addEventListener("DOMContentLoaded", () => {
    initializeTables();
    buildUI();
    const res = olSelectLonLat("map", updateMarkerPosition);
    marker = res.marker;

    // Legacy URLs used anchor tags, which we want to migrate to url parameters
    convertLegacyHashLink();
    readURLParams();

});
