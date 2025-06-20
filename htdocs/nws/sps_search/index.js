/* global ol, olSelectLonLat, Tabulator */
let marker = null;
let table1 = null;
let edate = null;
let sdate = null;
const BACKEND_SPS_BYPOINT = '/json/sps_by_point.py';

// Utility function to format date as YYYY-MM-DD
function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

// Update marker position and trigger table update
function updateMarkerPosition(lon, lat) {
    document.getElementById("lat").value = lat.toFixed(4);
    document.getElementById("lon").value = lon.toFixed(4);
    updateURLParams(lon, lat);
    marker.setGeometry(new ol.geom.Point(ol.proj.fromLonLat([lon, lat])));
    updateTable();
}

// Update URL parameters with current state
function updateURLParams(lon, lat) {
    const url = new URL(window.location);
    url.searchParams.set('lon', lon.toFixed(4));
    url.searchParams.set('lat', lat.toFixed(4));
    url.searchParams.set('sdate', sdate.value);
    url.searchParams.set('edate', edate.value);
    window.history.pushState({}, '', url);
}

// Handle legacy hash links and convert to URL parameters
function handleLegacyHashLinks() {
    const hash = window.location.hash;
    if (hash) {
        const tokens = hash.substring(1).split("/"); // Remove # and split
        if (tokens.length === 3 && tokens[0] === 'bypoint') {
            const lon = parseFloat(tokens[1]);
            const lat = parseFloat(tokens[2]);
            if (!isNaN(lon) && !isNaN(lat)) {
                // Convert hash to URL params and redirect
                const url = new URL(window.location);
                url.hash = ''; // Remove hash
                url.searchParams.set('lon', lon.toFixed(4));
                url.searchParams.set('lat', lat.toFixed(4));
                url.searchParams.set('sdate', sdate.value);
                url.searchParams.set('edate', edate.value);
                window.history.replaceState({}, '', url);
                return { lon, lat };
            }
        }
    }
    return null;
}

// Read URL parameters and set initial state
function readURLParams() {
    const urlParams = new URLSearchParams(window.location.search);
    
    const lon = urlParams.get('lon');
    const lat = urlParams.get('lat');
    const startDate = urlParams.get('sdate');
    const endDate = urlParams.get('edate');
    
    // Set dates if provided in URL
    if (startDate) {
        sdate.value = startDate;
    }
    if (endDate) {
        edate.value = endDate;
    }
    
    // Return coordinates if provided
    if (lon && lat) {
        const longitude = parseFloat(lon);
        const latitude = parseFloat(lat);
        if (!isNaN(longitude) && !isNaN(latitude)) {
            return { lon: longitude, lat: latitude };
        }
    }
    
    return null;
}

// Update table with SPS data
function updateTable(){
    const lat = document.getElementById("lat").value;
    const lon = document.getElementById("lon").value;
    
    // Show loading state
    const loadingIndicator = document.getElementById("loading-indicator");
    if (loadingIndicator) {
        loadingIndicator.classList.remove("d-none");
    }
    
    document.getElementById("table1title").innerHTML = `
        <i class="bi bi-table me-2"></i>SPS for Point: ${lon}°E ${lat}°N
        <span id="result-count" class="badge bg-light text-dark ms-2">Loading...</span>
    `;
    
    // Prepare request data
    const params = new URLSearchParams({
        lat: lat,
        lon: lon,
        sdate: sdate.value,
        edate: edate.value
    });
    
    // Fetch data from API
    fetch(`${BACKEND_SPS_BYPOINT}?${params}`)
        .then(response => response.json())
        .then(data => {
            // Clear and populate table
            const tableData = data.data.map(row => ({
                link: `<a href="${row.uri}" target="_blank" class="btn btn-sm btn-outline-primary">
                    <i class="bi bi-file-text me-1"></i>View Text
                </a>`,
                issue: row.issue,
                landspout: row.landspout ? 
                    `<span class="badge bg-warning text-dark">${row.landspout}</span>` : 
                    '<span class="text-muted">—</span>',
                waterspout: row.waterspout ? 
                    `<span class="badge bg-info text-dark">${row.waterspout}</span>` : 
                    '<span class="text-muted">—</span>',
                max_hail_size: row.max_hail_size || '<span class="text-muted">—</span>',
                max_wind_gust: row.max_wind_gust || '<span class="text-muted">—</span>'
            }));
            
            table1.setData(tableData);
            
            // Update result count
            document.getElementById("result-count").textContent = `${tableData.length} results`;
            document.getElementById("result-count").className = 
                `badge ${tableData.length > 0 ? 'bg-success' : 'bg-secondary'} ms-2`;
            
            // Update last update time
            const lastUpdateElement = document.getElementById("last-update");
            if (lastUpdateElement) {
                lastUpdateElement.textContent = new Date().toLocaleString();
            }
            
            // Hide loading indicator
            if (loadingIndicator) {
                loadingIndicator.classList.add("d-none");
            }
        })
        .catch(() => {
            // Handle error
            table1.setData([]);
            document.getElementById("result-count").textContent = "Error";
            document.getElementById("result-count").className = "badge bg-danger ms-2";
            
            // Hide loading indicator
            if (loadingIndicator) {
                loadingIndicator.classList.add("d-none");
            }
        });
}

// Initialize UI components
function buildUI(){
    // Initialize Tabulator table
    table1 = new Tabulator("#table1", {
        layout: "fitColumns",
        placeholder: "Drag marker on map to auto-populate this table",
        height: "600px",
        columns: [
            {
                title: "Actions", 
                field: "link", 
                formatter: "html", 
                width: 120,
                headerSort: false,
                cssClass: "text-center"
            },
            {
                title: "Issue Time", 
                field: "issue", 
                sorter: "string",
                width: 180
            },
            {
                title: "Landspout", 
                field: "landspout", 
                formatter: "html",
                width: 120,
                headerSort: false,
                cssClass: "text-center"
            },
            {
                title: "Waterspout", 
                field: "waterspout", 
                formatter: "html",
                width: 120,
                headerSort: false,
                cssClass: "text-center"
            },
            {
                title: "Max Hail Size (in)", 
                field: "max_hail_size", 
                sorter: "number",
                formatter: "html",
                cssClass: "text-center"
            },
            {
                title: "Max Wind Gust (mph)", 
                field: "max_wind_gust", 
                sorter: "number",
                formatter: "html",
                cssClass: "text-center"
            }
        ],
        initialSort: [
            {column: "issue", dir: "desc"}
        ]
    });

    // Export button handlers
    document.getElementById('export-excel').addEventListener('click', () => {
        const lat = document.getElementById("lat").value;
        const lon = document.getElementById("lon").value;
        const params = new URLSearchParams({
            fmt: "xlsx",
            lat: lat,
            lon: lon,
            sdate: sdate.value,
            edate: edate.value
        });
        window.location = `${BACKEND_SPS_BYPOINT}?${params}`;
    });

    document.getElementById('export-csv').addEventListener('click', () => {
        const lat = document.getElementById("lat").value;
        const lon = document.getElementById("lon").value;
        const params = new URLSearchParams({
            fmt: "csv",
            lat: lat,
            lon: lon,
            sdate: sdate.value,
            edate: edate.value
        });
        window.location = `${BACKEND_SPS_BYPOINT}?${params}`;
    });

    // Get date input elements
    sdate = document.getElementById('sdate');
    edate = document.getElementById('edate');
    
    // Set default dates
    const startDate = new Date(1986, 0, 1);
    const endDate = new Date();
    endDate.setDate(endDate.getDate() + 1);
    
    sdate.type = 'date';
    edate.type = 'date';
    sdate.value = formatDate(startDate);
    edate.value = formatDate(endDate);
    sdate.min = '1986-01-01';
    edate.min = '1986-01-01';
    sdate.max = formatDate(new Date());
    edate.max = formatDate(endDate);
    
    // Add event listeners for date changes
    sdate.addEventListener('change', () => {
        const lat = parseFloat(document.getElementById("lat").value);
        const lon = parseFloat(document.getElementById("lon").value);
        if (!isNaN(lat) && !isNaN(lon)) {
            updateURLParams(lon, lat);
        }
        updateTable();
    });
    
    edate.addEventListener('change', () => {
        const lat = parseFloat(document.getElementById("lat").value);
        const lon = parseFloat(document.getElementById("lon").value);
        if (!isNaN(lat) && !isNaN(lon)) {
            updateURLParams(lon, lat);
        }
        updateTable();
    });

    // Manual Point Entry
    document.getElementById("manualpt").addEventListener('click', () => {
        const la = parseFloat(document.getElementById("lat").value);
        const lo = parseFloat(document.getElementById("lon").value);
        if (isNaN(la) || isNaN(lo)){
            return;
        }
        marker.setGeometry(new ol.geom.Point(ol.proj.fromLonLat([lo, la])));
        updateMarkerPosition(lo, la);
    });
}
// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    buildUI();
    let default_lon = -93.653;
    let default_lat = 41.53;

    const res = olSelectLonLat("map", default_lon, default_lat, updateMarkerPosition);
    marker = res.marker;

    // Handle legacy hash links first (convert to URL params)
    const legacyCoords = handleLegacyHashLinks();
    
    // Read URL parameters for initial state
    const urlCoords = readURLParams();
    
    // Use coordinates from URL params or legacy hash, fallback to defaults
    const coords = urlCoords || legacyCoords;
    if (coords) {
        default_lon = coords.lon;
        default_lat = coords.lat;
        updateMarkerPosition(default_lon, default_lat);
    } else {
        // Set initial URL params with default values
        updateURLParams(default_lon, default_lat);
    }
});
