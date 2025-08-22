/**
 * COOP Extremes App - Simple function-based implementation
 * Handles data fetching, table rendering, and sorting for climatology data
 */

/* global ol, Tabulator */

// Global app state
const appState = {
    config: null,
    data: null,
    sortColumn: null,
    sortDirection: null,
    isStationView: false,
    map: null,
    vectorSource: null,
    popup: null,
    currentApiUrl: null,
    labelAttribute: 'avg_high', // Default label attribute - use numeric for legend
    colorRanges: null, // Will store calculated color ranges for current attribute
    table: null, // Tabulator instance
    yearFilter: null, // Selected year for filtering
    allFeatures: null // Store all features for filtering
};

/**
 * Initialize the application
 */
function initializeApp() {
    appState.config = getConfig();
    appState.sortColumn = appState.config.sortcol;
    appState.sortDirection = appState.config.sortdir;
    appState.isStationView = Boolean(appState.config.station);
    appState.labelAttribute = appState.config.labelAttribute; // Set from URL parameter
    appState.yearFilter = appState.config.yearFilter; // Set from URL parameter
    
    // Hide/show components based on view mode
    if (appState.isStationView) {
        // Station view - hide map and form controls
        const mapContainer = document.getElementById('map-container');
        const formContainer = document.getElementById('controls-form');
        if (mapContainer) {
            mapContainer.style.display = 'none';
        }
        if (formContainer) {
            formContainer.style.display = 'none';
        }
    } else {
        // Date view - show form controls, hide form in station view
        const formContainer = document.getElementById('controls-form');
        if (formContainer) {
            formContainer.style.display = 'block';
        }
    }
    
    showLoading(true);
    
    fetchData()
        .then(() => {
            renderHeader();
            updateTable();
            showApiInfo();
            if (!appState.isStationView) {
                initializeMap();
            }
            attachEventListeners();
        })
        .catch((error) => {
            showError(`Failed to load climatology data: ${error.message}`);
        })
        .finally(() => {
            showLoading(false);
        });
}

/**
 * Extract configuration from DOM elements (form inputs, URL parameters)
 */
function getConfig() {
    // Get URL parameters
    const urlParams = new URLSearchParams(window.location.search);

    // Helper to get value from URL or fallback
    function getParamOrInput(param, selector, fallback) {
        const urlVal = urlParams.get(param);
        if (urlVal !== null && urlVal !== undefined && urlVal !== '') {
            return urlVal;
        }
        const input = document.querySelector(selector);
        if (input && input.value !== undefined && input.value !== '') {
            return input.value;
        }
        return fallback;
    }

    return {
        tbl: getParamOrInput('tbl', 'select[name="tbl"]', 'climate'),
        month: parseInt(getParamOrInput('month', 'select[name="month"]', new Date().getMonth() + 1), 10),
        day: parseInt(getParamOrInput('day', 'select[name="day"]', new Date().getDate()), 10),
        sortcol: getParamOrInput('sortcol', 'unused', 'station'),
        network: getParamOrInput('network', 'select[name="network"]', 'IACLIMATE'),
        station: urlParams.get('station') || null,
        sortdir: getParamOrInput('sortdir', 'unused', 'ASC'),
        labelAttribute: getParamOrInput('label', 'unused', 'avg_high'),
        yearFilter: getParamOrInput('year', 'unused', null)
    };
}



/**
 * Fetch climatology data from appropriate API endpoint
 */
function fetchData() {
    const vars = appState.config;
    let apiUrl = '';
    
    if (vars.station) {
        // Station-specific climatology
        const syear = getStartYear(vars.tbl);
        const eyear = getEndYear(vars.tbl);
        apiUrl = `/json/climodat_stclimo.py?station=${vars.station}&syear=${syear}&eyear=${eyear}`;
    } else {
        // Day-specific climatology
        const syear = getStartYear(vars.tbl);
        const eyear = getEndYear(vars.tbl);
        apiUrl = `/geojson/climodat_dayclimo.py?network=${vars.network}&month=${vars.month}&day=${vars.day}&syear=${syear}&eyear=${eyear}`;
    }

    appState.currentApiUrl = apiUrl;
    
    return fetch(apiUrl)
        .then((response) => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then((jsonData) => {
            if (vars.station) {
                // Process station data
                appState.data = jsonData.climatology.map((item) => ({
                    ...item,
                    valid: new Date(2000, item.month - 1, item.day) // Create date for sorting
                }));
            } else {
                // Process day data from GeoJSON
                appState.data = jsonData.features.map((feature) => feature.properties);
            }
        });
};

/**
 * Get start year based on table selection
 */
function getStartYear(tbl) {
    switch (tbl) {
        case 'climate51': return 1951;
        case 'climate71': return 1971;
        case 'climate81': return 1981;
        default: return 1800;
    }
};

/**
 * Get end year based on table selection
 */
function getEndYear(tbl) {
    switch (tbl) {
        case 'climate71': return 2001;
        case 'climate81': return 2011;
        default: return new Date().getFullYear() + 1;
    }
};

/**
 * Render header section with clear mode indication
 */
function renderHeader() {
    const headerSection = document.getElementById('header-section');
    const vars = appState.config;
    
    let headerHtml = '';
    
    if (vars.station) {
        // Station mode - Daily Climatology for Single Station
        const backLink = `extremes.php?network=${vars.network}&tbl=${vars.tbl}&month=${vars.month}&day=${vars.day}&label=${appState.labelAttribute}${appState.yearFilter ? `&year=${appState.yearFilter}` : ''}`;
        headerHtml = `
            <div class="d-flex align-items-center justify-content-between mb-3">
                <div>
                    <h3 class="mb-1">🏛️ Daily Climatology for Single Station</h3>
                    <h4 class="text-primary mb-0">Station: ${vars.station}</h4>
                    <p class="text-muted mb-0">Showing records for all days of the year at this station</p>
                </div>
                <div class="text-end">
                    <a href="${backLink}" class="btn btn-outline-primary btn-sm">
                        <i class="bi bi-arrow-left" aria-hidden="true"></i><span class="visually-hidden">Back</span> Back to Date View
                    </a>
                </div>
            </div>
        `;
    } else {
        // Date mode - Single Date Climatology for State
        const date = new Date(2000, vars.month - 1, vars.day);
        const dateStr = date.toLocaleDateString('en-US', { month: 'long', day: 'numeric' });
        const networkName = getNetworkDisplayName(vars.network);
        
        headerHtml = `
            <div class="mb-3">
                <h3 class="mb-1">🌡️ Single Date Climatology for State</h3>
                <h4 class="text-primary mb-0">${dateStr} - ${networkName}</h4>
                <p class="text-muted mb-0">Showing records for all stations on this date. Click any station ID to see its full year of data.</p>
            </div>
        `;
    }
    
    headerSection.innerHTML = headerHtml;
};

/**
 * Get display name for network
 */
function getNetworkDisplayName(network) {
    const networkNames = {
        'IACLIMATE': 'Iowa',
        'ILCLIMATE': 'Illinois', 
        'INCLIMATE': 'Indiana',
        'KSCLIMATE': 'Kansas',
        'KYCLIMATE': 'Kentucky',
        'MICLIMATE': 'Michigan',
        'MNCLIMATE': 'Minnesota',
        'MOCLIMATE': 'Missouri',
        'NECLIMATE': 'Nebraska',
        'NDCLIMATE': 'North Dakota',
        'OHCLIMATE': 'Ohio',
        'SDCLIMATE': 'South Dakota',
        'WICLIMATE': 'Wisconsin'
    };
    return networkNames[network] || network;
};

/**
 * Initialize Tabulator table
 */
function initializeTable() {
    const columns = getTableColumns();
    
    appState.table = new Tabulator("#data-table", {
        data: prepareTableData(), // Use prepared data instead of raw data
        layout: "fitDataTable",
        responsiveLayout: "hide", 
        pagination: "local",
        paginationSize: 10, // Show 10 rows by default
        paginationSizeSelector: [10, 25, 50, 100],
        height: "70vh", // Set table height to 70% of viewport height
        movableColumns: true,
        resizableColumns: true,
        tooltips: true,
        columnHeaderSortMulti: false,
        scrollHorizontal: true, // Enable horizontal scrolling
        freezeFirstColumn: true, // Freeze the first column
        headerSort: true, // Make headers sticky
        columns,
        placeholder: "No climatology data available for the selected criteria",
        initialSort: [
            {column: appState.isStationView ? "date_link" : "station_link", dir: "asc"}
        ]
    });
    
    // Add export buttons after table is created
    addExportButtons();
}

/**
 * Get column definitions for Tabulator based on view type
 */
function getTableColumns() {
    let firstColumnTitle = '';
    let firstColumnField = '';
    
    if (appState.isStationView) {
        firstColumnTitle = 'Date';
        firstColumnField = 'date_link';
    } else {
        firstColumnTitle = 'Station';
        firstColumnField = 'station_link';
    }
    
    return [
        {
            title: firstColumnTitle,
            field: firstColumnField,
            formatter: "html",
            width: appState.isStationView ? 120 : 200, // Wider for station names
            headerSort: true,
            cssClass: "station-col",
            sorter(a, b, aRow, bRow) {
                // Use proper sorting for dates in station view
                if (appState.isStationView) {
                    const aSort = aRow.getData().date_sort || 0;
                    const bSort = bRow.getData().date_sort || 0;
                    return aSort - bSort;
                }
                // For station names, use the station id
                const aText = aRow.getData().station || '';
                const bText = bRow.getData().station || '';
                return aText.localeCompare(bText);
            }
        },
        {
            title: "Years",
            field: "years",
            width: 60,
            headerSort: true,
            formatter(cell) {
                return cell.getValue() || '';
            }
        },
        // High Temperature column group
        {
            title: "Avg High °F",
            field: "avg_high",
            width: 90,
            formatter(cell) {
                return formatNumber(cell.getValue(), 1);
            },
            cssClass: "temp-group",
            sorter: "number"
        },
        {
            title: "Max High °F", 
            field: "max_high",
            width: 90,
            formatter(cell) {
                return cell.getValue() || '';
            },
            cssClass: "temp-group",
            sorter: "number"
        },
        {
            title: "Max High Year",
            field: "max_high_years", 
            width: 100,
            formatter(cell) {
                return formatYears(cell.getValue());
            },
            cssClass: "temp-group",
            sorter(a, b) {
                // Custom sorter for year arrays
                const aStr = Array.isArray(a) ? a.join('') : String(a || '');
                const bStr = Array.isArray(b) ? b.join('') : String(b || '');
                return aStr.localeCompare(bStr);
            }
        },
        {
            title: "Min High °F",
            field: "min_high",
            width: 90,
            formatter(cell) {
                return cell.getValue() || '';
            },
            cssClass: "temp-group",
            sorter: "number"
        },
        {
            title: "Min High Year",
            field: "min_high_years",
            width: 100, 
            formatter(cell) {
                return formatYears(cell.getValue());
            },
            cssClass: "temp-group",
            sorter(a, b) {
                const aStr = Array.isArray(a) ? a.join('') : String(a || '');
                const bStr = Array.isArray(b) ? b.join('') : String(b || '');
                return aStr.localeCompare(bStr);
            }
        },
        // Low Temperature column group
        {
            title: "Avg Low °F",
            field: "avg_low",
            width: 90,
            formatter(cell) {
                return formatNumber(cell.getValue(), 1);
            },
            cssClass: "temp-group",
            sorter: "number"
        },
        {
            title: "Max Low °F",
            field: "max_low", 
            width: 90,
            formatter(cell) {
                return cell.getValue() || '';
            },
            cssClass: "temp-group",
            sorter: "number"
        },
        {
            title: "Max Low Year",
            field: "max_low_years",
            width: 100,
            formatter(cell) {
                return formatYears(cell.getValue());
            },
            cssClass: "temp-group",
            sorter(a, b) {
                const aStr = Array.isArray(a) ? a.join('') : String(a || '');
                const bStr = Array.isArray(b) ? b.join('') : String(b || '');
                return aStr.localeCompare(bStr);
            }
        },
        {
            title: "Min Low °F",
            field: "min_low",
            width: 90, 
            formatter(cell) {
                return cell.getValue() || '';
            },
            cssClass: "temp-group",
            sorter: "number"
        },
        {
            title: "Min Low Year", 
            field: "min_low_years",
            width: 100,
            formatter(cell) {
                return formatYears(cell.getValue());
            },
            cssClass: "temp-group",
            sorter(a, b) {
                const aStr = Array.isArray(a) ? a.join('') : String(a || '');
                const bStr = Array.isArray(b) ? b.join('') : String(b || '');
                return aStr.localeCompare(bStr);
            }
        },
        // Precipitation column group
        {
            title: "Avg Precip in",
            field: "avg_precip",
            width: 100,
            formatter(cell) {
                return formatNumber(cell.getValue(), 2);
            },
            cssClass: "precip-group",
            sorter: "number"
        },
        {
            title: "Max Precip in",
            field: "max_precip",
            width: 100,
            formatter(cell) {
                return formatNumber(cell.getValue(), 2);
            },
            cssClass: "precip-group",
            sorter: "number"
        },
        {
            title: "Max Precip Year",
            field: "max_precip_years",
            width: 110,
            formatter(cell) {
                return formatYears(cell.getValue());
            },
            cssClass: "precip-group",
            sorter(a, b) {
                const aStr = Array.isArray(a) ? a.join('') : String(a || '');
                const bStr = Array.isArray(b) ? b.join('') : String(b || '');
                return aStr.localeCompare(bStr);
            }
        }
    ];
}

/**
 * Update table with new data
 */
function updateTable() {
    if (!appState.table) {
        initializeTable();
        return;
    }
    
    // Prepare data for Tabulator
    const tableData = prepareTableData();
    appState.table.setData(tableData);
    
    // Ensure export buttons are present
    addExportButtons();
}

/**
 * Prepare data for Tabulator display
 */
function prepareTableData() {
    if (!appState.data || appState.data.length === 0) {
        return [];
    }
    
    const vars = appState.config;

    return appState.data.map((row) => {
        let linkCell = '';
        let linkField = '';
        
        if (appState.isStationView) {
            // Station view - link to date
            const date = new Date(2000, row.month - 1, row.day);
            const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            let link = `extremes.php?day=${row.day}&month=${row.month}&network=${vars.network}&tbl=${vars.tbl}`;
            if (appState.labelAttribute) {
                link += `&label=${appState.labelAttribute}`;
            }
            if (appState.yearFilter) {
                link += `&year=${appState.yearFilter}`;
            }
            linkCell = `<a href="${link}">${dateStr}</a>`;
            linkField = 'date_link';
        } else {
            // Day view - link to station with name and ID
            let link = `extremes.php?station=${row.station}&network=${vars.network}&tbl=${vars.tbl}`;
            if (appState.labelAttribute) {
                link += `&label=${appState.labelAttribute}`;
            }
            if (appState.yearFilter) {
                link += `&year=${appState.yearFilter}`;
            }
            
            // Use station name if available, otherwise fall back to station ID
            const displayText = row.name ? `${row.name} (${row.station})` : row.station;
            
            linkCell = `<a href="${link}">${displayText}</a>`;
            linkField = 'station_link';
        }
        
        // Create a new object with the link field
        const tableRow = { ...row };
        tableRow[linkField] = linkCell;
        
        // Add sortable date field for station view (month*100 + day gives proper numeric sort)
        if (appState.isStationView) {
            tableRow.date_sort = row.month * 100 + row.day;
        }
        
        return tableRow;
    });
}

/**
 * Format numeric values with specified decimal places
 */
function formatNumber(value, decimals) {
    if (value === null || value === undefined || value === '') return '';
    return parseFloat(value).toFixed(decimals);
};

/**
 * Format year arrays as comma-separated strings
 */
function formatYears(years) {
    if (!years || !Array.isArray(years)) return '';
    return years.join(', ');
};

/**
 * Show/hide loading indicator
 */
function showLoading(show) {
    const loadingIndicator = document.getElementById('loading-indicator');
    const contentArea = document.getElementById('content-area');
    
    if (loadingIndicator) {
        loadingIndicator.style.display = show ? 'block' : 'none';
    }
    if (contentArea) {
        contentArea.style.display = show ? 'none' : 'block';
    }
};

/**
 * Show API information
 */
function showApiInfo() {
    const apiInfo = document.getElementById('api-info');
    const apiUrl = document.getElementById('api-url');
    
    if (apiInfo && apiUrl) {
        if (appState.currentApiUrl) {
        apiUrl.textContent = appState.currentApiUrl;
        apiInfo.style.display = 'block';
        }
    }
};

/**
 * Show error message
 */
function showError(message) {
    const contentArea = document.getElementById('content-area');
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.innerHTML = `
        <h5>Error Loading Data</h5>
        <p>${message}</p>
        <p>Please try again or contact support if the problem persists.</p>
    `;
    
    if (contentArea) {
        contentArea.insertBefore(errorDiv, contentArea.firstChild);
    }
};

/**
 * Attach event listeners for enhanced interactions
 */
function attachEventListeners() {
    // Helper to add change listeners to form elements
    function addFormChangeListeners(form) {
        const selectors = ['select[name="network"]', 'select[name="month"]', 'select[name="day"]', 'select[name="tbl"]'];
        selectors.forEach((selector) => {
            const el = form.querySelector(selector);
            if (el) {
                el.addEventListener('change', handleFormChange);
            }
        });
    }

    // Handle form changes dynamically (don't submit, just update data)
    const form = document.getElementById('controls-form');
    const submitBtn = document.getElementById('form-submit-btn');
    const dynamicIndicator = document.getElementById('dynamic-indicator');

    if (form && !appState.isStationView) {
        // Update submit button text for dynamic mode
        if (submitBtn) {
            submitBtn.value = 'Update View';
            submitBtn.style.backgroundColor = '#0d6efd';
            submitBtn.style.color = 'white';
            submitBtn.style.border = '1px solid #0d6efd';
        }

        // Show dynamic indicator
        if (dynamicIndicator) {
            dynamicIndicator.style.display = 'block';
        }

        // Prevent form submission
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            handleFormChange();
            return false;
        });

        // Add change listeners to all form elements
        addFormChangeListeners(form);
    }

    // Handle browser back/forward navigation
    window.addEventListener('popstate', () => {
        // Reload the page to handle URL parameter changes
        window.location.reload();
    });

    // Handle label attribute changes for map
    const labelSelect = document.getElementById('label-attribute');
    if (labelSelect && !appState.isStationView) {
        // Set initial value
        labelSelect.value = appState.labelAttribute;

        labelSelect.addEventListener('change', function() {
            appState.labelAttribute = this.value;
            appState.config.labelAttribute = this.value;

            // Update year filter visibility based on new attribute
            updateYearFilterVisibility();

            // Repopulate year filter with years relevant to the new attribute
            if (appState.allFeatures && !['avg_high', 'avg_low', 'avg_precip', 'station', 'years'].includes(this.value)) {
                populateYearFilter(appState.allFeatures);
            }

            // Update URL to persist the selection
            updateUrl();

            // Update map
            updateMapLabels();

            // Re-apply year filter since filtering logic depends on selected attribute
            if (appState.yearFilter) {
                applyYearFilter();
            }
        });
    }

    // Handle year filter changes for map
    const yearFilter = document.getElementById('year-filter');
    if (yearFilter && !appState.isStationView) {
        // Set initial value from URL parameter
        if (appState.yearFilter) {
            yearFilter.value = appState.yearFilter;
        }

        // Set initial visibility based on current attribute
        updateYearFilterVisibility();

        yearFilter.addEventListener('change', function() {
            appState.yearFilter = this.value || null;
            appState.config.yearFilter = this.value || null;

            // Update URL to persist the selection
            updateUrl();

            // Apply filter
            applyYearFilter();
        });
    }
};

/**
 * Initialize OpenLayers map
 */
function initializeMap() {
    // Create vector source for station data
    appState.vectorSource = new ol.source.Vector();
    
    // Create popup overlay
    const container = document.getElementById('popup');
    const closer = document.getElementById('popup-closer');
    
    appState.popup = new ol.Overlay({
        element: container,
        autoPan: {
            animation: {
                duration: 250
            }
        }
    });
    
    // Close popup when X is clicked
    closer.onclick = function() {
        appState.popup.setPosition();
        closer.blur();
        return false;
    };
    
    // Initialize map
    appState.map = new ol.Map({
        target: 'map-container',
        layers: [
            // Base layers group
            new ol.layer.Group({
                title: 'Base Maps',
                layers: [
                    new ol.layer.Tile({
                        title: 'OpenStreetMap',
                        type: 'base',
                        visible: true,
                        source: new ol.source.OSM()
                    }),
                    new ol.layer.Tile({
                        title: 'Satellite',
                        type: 'base',
                        visible: false,
                        source: new ol.source.XYZ({
                            url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                            attributions: 'Tiles © Esri'
                        })
                    })
                ]
            }),
            // Vector layer for stations
            new ol.layer.Vector({
                title: 'Climate Stations',
                source: appState.vectorSource,
                style: getStationStyle
            })
        ],
        overlays: [appState.popup],
        view: new ol.View({
            center: ol.proj.fromLonLat([-93.5, 42.0]), // Default to Iowa
            zoom: 7
        })
    });
    
    // Add layer switcher control
    const layerSwitcher = new ol.control.LayerSwitcher({
        tipLabel: 'Toggle layer visibility',
        groupSelectStyle: 'children'
    });
    appState.map.addControl(layerSwitcher);
    
    // Add click handler for station popups
    appState.map.on('singleclick', (evt) => {
        const clickedFeature = appState.map.forEachFeatureAtPixel(evt.pixel, (feature) => feature);
        if (clickedFeature) {
            showStationPopup(clickedFeature, evt.coordinate);
        } else {
            appState.popup.setPosition();
        }
    });
    
    // Change cursor when hovering over stations
    appState.map.on('pointermove', (evt) => {
        if (evt.dragging) return;
        const pixel = appState.map.getEventPixel(evt.originalEvent);
        const hit = appState.map.hasFeatureAtPixel(pixel);
        const target = appState.map.getTarget();
        if (target?.style) {
            target.style.cursor = hit ? 'pointer' : '';
        }
    });
    
    // Add stations to map if data is available
    if (appState.data) {
        addStationsToMap();
    }
};

/**
 * Add station data to map as features
 */
function addStationsToMap() {
    if (!appState.vectorSource || appState.isStationView) return;
    
    appState.vectorSource.clear();
    
    // Get the original GeoJSON features (we need to fetch again to get coordinates)
    // Since we already processed the data, we need the original GeoJSON
    fetchGeoJSONForMap();
}

/**
 * Fetch GeoJSON data specifically for map display
 */
function fetchGeoJSONForMap() {
    const vars = appState.config;
    const syear = getStartYear(vars.tbl);
    const eyear = getEndYear(vars.tbl);
    const apiUrl = `/geojson/climodat_dayclimo.py?network=${vars.network}&month=${vars.month}&day=${vars.day}&syear=${syear}&eyear=${eyear}`;
    
    fetch(apiUrl)
        .then((response) => {
            return response.json();
        })
        .then((geoJsonData) => {
            addGeoJSONToMap(geoJsonData);
        })
        .catch(() => {
            // Silently handle error - map will remain empty
        });
}

/**
 * Add GeoJSON features to the map
 */
function addGeoJSONToMap(geoJsonData) {
    const format = new ol.format.GeoJSON();
    const features = format.readFeatures(geoJsonData, {
        featureProjection: 'EPSG:3857' // Web Mercator for display
    });
    
    // Store all features for filtering
    appState.allFeatures = features;
    
    // Apply current filter
    const filteredFeatures = filterFeaturesByYear(features);
    appState.vectorSource.addFeatures(filteredFeatures);
    
    // Populate year filter dropdown
    populateYearFilter(features);
    
    // Calculate initial color ranges and update legend
    appState.colorRanges = calculateColorRanges();
    updateLegend();
    
    // Fit map to show all stations
    if (filteredFeatures.length > 0) {
        const extent = appState.vectorSource.getExtent();
        appState.map.getView().fit(extent, {
            padding: [20, 20, 20, 20],
            maxZoom: 10
        });
    }
}

/**
 * Get style for station features based on selected attribute
 */
function getStationStyle(feature) {
    const props = feature.getProperties();
    const value = props[appState.labelAttribute];
    const backgroundColor = getColorForValue(value);

    // Refactored for complexity: split getLabelText into smaller helpers (Rule: complexity, refactoring)
    function isNullOrUndefined(val) {
        return val === null || val === undefined;
    }

    function formatStationOrYears(val) {
        return String(val);
    }

    function formatPrecip(val) {
        return typeof val === 'number' ? `${val.toFixed(2)}"` : String(val);
    }

    function formatHighLow(val) {
        return typeof val === 'number' ? `${Math.round(val)}°` : String(val);
    }

    function formatArray(val) {
        return val.join(',');
    }

    function formatNumber1(val) {
        return val.toFixed(1);
    }

    function getLabelText(val, attr) {
        if (isNullOrUndefined(val)) return '';
        if (attr === 'station' || attr === 'years') {
            return formatStationOrYears(val);
        }
        if (attr.includes('precip')) {
            return formatPrecip(val);
        }
        if (attr.includes('high') || attr.includes('low')) {
            return formatHighLow(val);
        }
        if (Array.isArray(val)) {
            return formatArray(val);
        }
        if (typeof val === 'number') {
            return formatNumber1(val);
        }
        return String(val);
    }

    const labelText = getLabelText(value, appState.labelAttribute);

    return new ol.style.Style({
        text: new ol.style.Text({
            text: labelText,
            font: 'bold 12px Arial',
            fill: new ol.style.Fill({ color: '#333333' }),
            stroke: new ol.style.Stroke({ color: '#ffffff', width: 2 }),
            backgroundFill: new ol.style.Fill({ color: backgroundColor }),
            backgroundStroke: new ol.style.Stroke({ color: '#ffffff', width: 1 }),
            padding: [3, 6, 3, 6]
        })
    });
};

/**
 * Show popup with station information


/**
 * Helper to generate a table row with optional highlight if year matches
 * Exported for use in other functions.
 */
window.popupRow = function popupRow(label, value, yearsArr, yearFilter, valueSuffix = '', formatYearsFn = null) {
    let highlight = '';
    if (yearFilter) {
        if (yearsArr?.includes?.(parseInt(yearFilter))) {
            highlight = ' style="background: #fff3cd; font-weight: bold;"';
        }
    }
    let yearsStr = '';
    if (yearsArr) {
        if (formatYearsFn) {
            yearsStr = formatYearsFn(yearsArr);
        } else {
            yearsStr = yearsArr;
        }
    }
    let suffixYears = '';
    if (yearsArr) {
        suffixYears = ` (${yearsStr})`;
    }
    return `<tr${highlight}><td class="label">${label}:</td><td>${value}${valueSuffix}${suffixYears}</td></tr>`;
};

function showStationPopup(feature, coordinate) {
    const props = feature.getProperties();
    const content = document.getElementById('popup-content');

    // Use station name if available, otherwise fall back to station ID
    const stationDisplayName = props.name ? `${props.name} (${props.station})` : props.station;

    let popupHtml = `<h5>${stationDisplayName}</h5>`;

    // If year filter is active, highlight records from that year
    if (appState.yearFilter) {
        const filterYear = parseInt(appState.yearFilter);
        popupHtml += `<div style="background: #d1ecf1; padding: 4px 8px; border-radius: 4px; margin-bottom: 8px; font-size: 11px;">
            <strong>Showing records from ${filterYear}</strong>
        </div>`;
    }


    popupHtml += '<table class="popup-data-table">';
    popupHtml += `<tr><td class="label">Years:</td><td>${props.years || 'N/A'}</td></tr>`;
    popupHtml += `<tr><td class="label">Avg High:</td><td>${formatNumber(props.avg_high, 1)}°F</td></tr>`;

    // Use helper for rows with year highlighting
    popupHtml += window.popupRow('Max High', props.max_high || 'N/A', props.max_high_years, appState.yearFilter, '°F', formatYears);
    popupHtml += window.popupRow('Min High', props.min_high || 'N/A', props.min_high_years, appState.yearFilter, '°F', formatYears);
    popupHtml += `<tr><td class="label">Avg Low:</td><td>${formatNumber(props.avg_low, 1)}°F</td></tr>`;
    popupHtml += window.popupRow('Max Low', props.max_low || 'N/A', props.max_low_years, appState.yearFilter, '°F', formatYears);
    popupHtml += window.popupRow('Min Low', props.min_low || 'N/A', props.min_low_years, appState.yearFilter, '°F', formatYears);
    popupHtml += `<tr><td class="label">Avg Precip:</td><td>${formatNumber(props.avg_precip, 2)}"</td></tr>`;
    popupHtml += window.popupRow('Max Precip', formatNumber(props.max_precip, 2), props.max_precip_years, appState.yearFilter, '"', formatYears);

    popupHtml += `</table>
        <p style="margin-top: 8px; font-size: 11px;">
            <a href="extremes.php?station=${props.station}&network=${appState.config.network}&tbl=${appState.config.tbl}${appState.labelAttribute ? `&label=${appState.labelAttribute}` : ''}${appState.yearFilter ? `&year=${appState.yearFilter}` : ''}" 
               target="_blank">View station details →</a>
        </p>`;

    content.innerHTML = popupHtml;
    appState.popup.setPosition(coordinate);
}

/**
 * Update map labels when attribute selection changes
 */
function updateMapLabels() {
    if (appState.vectorSource) {
        // Recalculate color ranges for new attribute
        appState.colorRanges = calculateColorRanges();
        
        // Update legend
        updateLegend();
        
        // Force redraw of all features by changing the style
        const features = appState.vectorSource.getFeatures();
        features.forEach((feature) => {
            feature.changed();
        });
    }
}

/**
 * Update the legend based on current attribute and data
 */
function updateLegend() {
    const legendElement = document.querySelector('.map-legend');
    
    if (!legendElement) {
        return;
    }
    
    let legendHtml = '';
    
    if (!appState.colorRanges) {
        // No color ranges (e.g., station names) - show info message instead
        legendElement.style.display = 'block';
        legendElement.innerHTML = `
            <div style="font-size: 11px; color: #666;">
                ${getAttributeLabel(appState.labelAttribute)} (no color coding)
            </div>
        `;
        return;
    }
    
    // Show legend with current attribute info
    legendElement.style.display = 'block';
    
    const attributeLabel = getAttributeLabel(appState.labelAttribute);
    
    legendHtml = `
        <div style="font-size: 11px; color: #666; margin-bottom: 4px;">
            ${attributeLabel} ranges:
        </div>
    `;
    
    appState.colorRanges.ranges.forEach((range) => {
        legendHtml += `
            <div class="legend-item">
                <div class="legend-color" style="background: ${range.color};"></div>
                <span style="font-size: 10px;">${range.label}${appState.colorRanges.units}</span>
            </div>
        `;
    });
    
    legendElement.innerHTML = legendHtml;
}

/**
 * Get human-readable label for attribute
 */
function getAttributeLabel(attribute) {
    const labels = {
        'station': 'Station ID',
        'avg_high': 'Average High Temperature',
        'max_high': 'Maximum High Temperature',
        'min_high': 'Minimum High Temperature',
        'avg_low': 'Average Low Temperature',
        'max_low': 'Maximum Low Temperature',
        'min_low': 'Minimum Low Temperature',
        'avg_precip': 'Average Precipitation',
        'max_precip': 'Maximum Precipitation',
        'years': 'Years of Data'
    };
    return labels[attribute] || attribute;
}

/**
 * Calculate color ranges for the currently selected attribute
 */
function calculateColorRanges() {
    if (!appState.data || appState.data.length === 0) return null;
    
    // Skip color calculation for non-numeric attributes
    if (appState.labelAttribute === 'station') return null;
    
    // Get all numeric values for the selected attribute
    const values = appState.data
        .map((item) => item[appState.labelAttribute])
        .filter((val) => typeof val === 'number' && !isNaN(val))
        .sort((a, b) => a - b);

    if (values.length === 0) return null;
    
    const min = values[0];
    const max = values[values.length - 1];
    const range = max - min;
    
    if (range === 0) return null;
    
    // For temperature data, use appropriate decimal places
    const isTemp = appState.labelAttribute.includes('high') || appState.labelAttribute.includes('low');
    const isPrecip = appState.labelAttribute.includes('precip');
    const decimals = isPrecip ? 2 : (isTemp ? 0 : 1);
    
    // Create 5 equal ranges
    const step = range / 5;
    
    return {
        min,
        max,
        ranges: [
            { min, max: min + step, color: '#3388ff', label: `${min.toFixed(decimals)} - ${(min + step).toFixed(decimals)}` },
            { min: min + step, max: min + 2 * step, color: '#44bb44', label: `${(min + step).toFixed(decimals)} - ${(min + 2 * step).toFixed(decimals)}` },
            { min: min + 2 * step, max: min + 3 * step, color: '#ffbb44', label: `${(min + 2 * step).toFixed(decimals)} - ${(min + 3 * step).toFixed(decimals)}` },
            { min: min + 3 * step, max: min + 4 * step, color: '#ff8844', label: `${(min + 3 * step).toFixed(decimals)} - ${(min + 4 * step).toFixed(decimals)}` },
            { min: min + 4 * step, max, color: '#ff4444', label: `${(min + 4 * step).toFixed(decimals)} - ${max.toFixed(decimals)}` }
        ],
        units: getAttributeUnits(appState.labelAttribute)
    };
}

/**
 * Get appropriate units for display based on attribute type
 */
function getAttributeUnits(attribute) {
    if (attribute.includes('precip')) return '"';
    if (attribute.includes('high') || attribute.includes('low')) return '°F';
    return '';
}

/**
 * Get color for a value based on current color ranges
 */
function getColorForValue(value) {
    if (!appState.colorRanges || typeof value !== 'number') {
        return '#cccccc'; // Default gray for non-numeric or missing data
    }
    
    for (let i = 0; i < appState.colorRanges.ranges.length; i++) {
        const range = appState.colorRanges.ranges[i];
        if (i === appState.colorRanges.ranges.length - 1) {
            // Last range includes max value
            if (value >= range.min && value <= range.max) {
                return range.color;
            }
        } else {
            if (value >= range.min && value < range.max) {
                return range.color;
            }
        }
    }
    
    return '#cccccc'; // Default
}

/**
 * Handle form changes - update URL and reload data dynamically
 */
function handleFormChange() {
    // Get current form values
    const form = document.getElementById('controls-form');
    const networkSelect = form.querySelector('select[name="network"]');
    const monthSelect = form.querySelector('select[name="month"]');
    const daySelect = form.querySelector('select[name="day"]');
    const tblSelect = form.querySelector('select[name="tbl"]');
    
    // Build new URL parameters
    const params = new URLSearchParams(window.location.search);
    
    if (networkSelect) params.set('network', networkSelect.value);
    if (monthSelect) params.set('month', monthSelect.value);
    if (daySelect) params.set('day', daySelect.value);
    if (tblSelect) params.set('tbl', tblSelect.value);
    
    // Keep existing sort parameters
    if (appState.config.sortcol) params.set('sortcol', appState.config.sortcol);
    if (appState.config.sortdir) params.set('sortdir', appState.config.sortdir);
    
    // Keep current label attribute setting
    if (appState.labelAttribute) params.set('label', appState.labelAttribute);
    
    // Clear year filter when switching to different dataset (network/date change)
    // The year filter is specific to a particular dataset combination
    appState.yearFilter = null;
    appState.config.yearFilter = null;
    
    // Make sure year parameter is not included in the new URL
    params.delete('year');
    
    // Update URL without page reload
    const newUrl = `${window.location.pathname}?${params.toString()}`;
    window.history.pushState({}, '', newUrl);
    
    // Update app config
    appState.config = getConfig();
    
    // Show loading and reload data
    showLoading(true);
    
    // Clear any existing error messages
    const existingErrors = document.querySelectorAll('.error-message');
    existingErrors.forEach((error) => {
        error.remove();
    });
    
    fetchData()
        .then(() => {
            renderHeader();
            updateTable();
            showApiInfo();
            if (!appState.isStationView) {
                // Clear and reload map data
                if (appState.vectorSource) {
                    appState.vectorSource.clear();
                }
                addStationsToMap();
                
                // Reset year filter UI since we have a new dataset
                const yearSelect = document.getElementById('year-filter');
                if (yearSelect) {
                    yearSelect.value = '';
                }
                
                // Update year filter visibility for current attribute
                updateYearFilterVisibility();
            }
        })
        .catch((error) => {
            showError(`Failed to load climatology data: ${error.message}`);
        })
        .finally(() => {
            showLoading(false);
        });
}

/**
 * Update URL with current application state
 */
function updateUrl() {
    const params = new URLSearchParams();
    
    // Add all current config values to ensure they're preserved
    params.set('network', appState.config.network);
    params.set('month', appState.config.month);
    params.set('day', appState.config.day);
    params.set('tbl', appState.config.tbl);
    
    // Only add non-default values to keep URLs clean
    if (appState.config.sortcol && appState.config.sortcol !== 'station') {
        params.set('sortcol', appState.config.sortcol);
    }
    if (appState.config.sortdir && appState.config.sortdir !== 'ASC') {
        params.set('sortdir', appState.config.sortdir);
    }
    if (appState.labelAttribute && appState.labelAttribute !== 'avg_high') {
        params.set('label', appState.labelAttribute);
    }
    if (appState.yearFilter) {
        params.set('year', appState.yearFilter);
    }
    
    const newUrl = `${window.location.pathname}?${params.toString()}`;
    window.history.pushState({}, '', newUrl);
}

/**
 * Populate the year filter dropdown with available years
 */
function populateYearFilter(features) {
    const yearSelect = document.getElementById('year-filter');
    if (!yearSelect) return;
    
    // Collect years based on the currently selected attribute
    const allYears = new Set();
    
    // Determine which year field to use based on current label attribute
    let yearField = null;
    switch (appState.labelAttribute) {
        case 'max_high':
            yearField = 'max_high_years';
            break;
        case 'min_high':
            yearField = 'min_high_years';
            break;
        case 'max_low':
            yearField = 'max_low_years';
            break;
        case 'min_low':
            yearField = 'min_low_years';
            break;
        case 'max_precip':
            yearField = 'max_precip_years';
            break;
        default:
            // For non-record attributes, collect from all year arrays
            yearField = null;
    }
    
    features.forEach((feature) => {
        const props = feature.getProperties();
        
        if (yearField) {
            // Collect years from specific field only
            const years = props[yearField];
            if (Array.isArray(years)) {
                years.forEach((year) => {
                    allYears.add(year);
                });
            }
        } else {
            // Collect from all year arrays (for avg attributes)
            const yearArrays = [
                'max_high_years', 'min_high_years', 'max_low_years', 
                'min_low_years', 'max_precip_years'
            ];

            yearArrays.forEach((yearArrayField) => {
                const years = props[yearArrayField];
                if (Array.isArray(years)) {
                    years.forEach((year) => {
                        allYears.add(year);
                    });
                }
            });
        }
    });
    
    // Sort years in descending order
    const sortedYears = Array.from(allYears).sort((a, b) => b - a);

    // Clear existing options except "All Years"
    yearSelect.innerHTML = '<option value="">All Years</option>';
    
    // Add year options
    sortedYears.forEach((year) => {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = year;
        if (appState.yearFilter && parseInt(appState.yearFilter) === year) {
            option.selected = true;
        }
        yearSelect.appendChild(option);
    });
}

/**
 * Filter features by selected year
 */
function filterFeaturesByYear(features) {
    if (!appState.yearFilter) {
        return features; // No filter applied
    }
    
    // Determine which year field to check based on the currently selected attribute
    let yearField = null;
    switch (appState.labelAttribute) {
        case 'max_high':
            yearField = 'max_high_years';
            break;
        case 'min_high':
            yearField = 'min_high_years';
            break;
        case 'max_low':
            yearField = 'max_low_years';
            break;
        case 'min_low':
            yearField = 'min_low_years';
            break;
        case 'max_precip':
            yearField = 'max_precip_years';
            break;
        default:
            // For non-record attributes (avg_high, avg_low, avg_precip, station, years),
            // check if ANY record was set in the selected year
            return features.filter((feature) => {
                const props = feature.getProperties();
                const yearArrays = [
                    'max_high_years', 'min_high_years', 'max_low_years', 
                    'min_low_years', 'max_precip_years'
                ];
                
                for (let i = 0; i < yearArrays.length; i++) {
                    const years = props[yearArrays[i]];
                    if (years?.includes?.(parseInt(appState.yearFilter))) {
                        return true;
                    }
                }
                return false;
            });
    }
    
    // Filter by specific record type
    return features.filter((feature) => {
        const props = feature.getProperties();
        const years = props[yearField];
        return Boolean(years?.includes?.(parseInt(appState.yearFilter)));
    });
}

/**
 * Apply year filter to the map
 */
function applyYearFilter() {
    if (!appState.allFeatures || !appState.vectorSource) return;
    
    // Clear current features first
    appState.vectorSource.clear();
    
    // Filter features based on selected year
    const filteredFeatures = filterFeaturesByYear(appState.allFeatures);
    
    // Add filtered features to the map (even if it's an empty array)
    if (filteredFeatures.length > 0) {
        appState.vectorSource.addFeatures(filteredFeatures);
    }
    
    // Note: We don't zoom/fit the map view when filtering - this preserves
    // the user's current view and spatial context
    // Note: Color ranges and legend are NOT updated here - they should remain 
    // consistent based on the full dataset, not the filtered subset
}

/**
 * Update year filter visibility based on selected attribute
 */
function updateYearFilterVisibility() {
    const yearFilterRow = document.querySelector('#year-filter').closest('.control-row');
    if (!yearFilterRow) return;
    
    // Hide year filter for average attributes since they don't have specific record years
    const isAverageAttribute = ['avg_high', 'avg_low', 'avg_precip', 'station', 'years'].includes(appState.labelAttribute);
    
    if (isAverageAttribute) {
        yearFilterRow.style.display = 'none';
        // Clear any active year filter when hiding
        if (appState.yearFilter) {
            appState.yearFilter = null;
            appState.config.yearFilter = null;
            const yearSelect = document.getElementById('year-filter');
            if (yearSelect) {
                yearSelect.value = '';
            }
            // Update URL to remove year parameter
            updateUrl();
            // Apply the cleared filter (show all features)
            if (appState.allFeatures) {
                applyYearFilter();
            }
        }
    } else {
        yearFilterRow.style.display = 'flex';
    }
}

/**
 * Add export buttons for CSV and Excel download
 */
function addExportButtons() {
    // Create export buttons container
    const tableContainer = document.getElementById('data-table');
    let exportContainer = document.getElementById('table-export-buttons');
    
    if (!exportContainer) {
        exportContainer = document.createElement('div');
        exportContainer.id = 'table-export-buttons';
        exportContainer.className = 'mb-2 d-flex gap-2';
        exportContainer.innerHTML = `${''}
            <button id="download-csv" class="btn btn-outline-success btn-sm">
                <i class="bi bi-download" aria-hidden="true"></i><span class="visually-hidden">Download CSV</span> Download CSV
            </button>
            <button id="download-xlsx" class="btn btn-outline-primary btn-sm">
                <i class="bi bi-download" aria-hidden="true"></i><span class="visually-hidden">Download Excel</span> Download Excel
            </button>
        `;
        
        // Insert before the table
        tableContainer.parentNode.insertBefore(exportContainer, tableContainer);
    }
    
    // Add event listeners for export buttons
    document.getElementById('download-csv').addEventListener('click', () => {
        const filename = generateExportFilename('csv');
        appState.table.download("csv", filename);
    });

    document.getElementById('download-xlsx').addEventListener('click', () => {
        const filename = generateExportFilename('xlsx');
        appState.table.download("xlsx", filename, {sheetName: "Climate Data"});
    });
}

/**
 * Generate appropriate filename for exports
 */
function generateExportFilename(extension) {
    const vars = appState.config;
    let filename = '';
    
    if (appState.isStationView) {
        filename = `climate_station_${vars.station}`;
    } else {
        const monthStr = vars.month.toString().padStart(2, '0');
        const dayStr = vars.day.toString().padStart(2, '0');
        const networkStr = vars.network.toLowerCase();
        filename = `climate_${networkStr}_${monthStr}-${dayStr}`;
    }
    
    return `${filename}.${extension}`;
}

// Initialize the app when DOM is ready
document.addEventListener('DOMContentLoaded', initializeApp);
