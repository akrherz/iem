/* global iemdata, ol, olSelectLonLat, Tabulator, bootstrap */

let stateSelect = null;
let stateSelect3 = null;
let ugcSelect = null;
let table1 = null;
let table2 = null;
let table3 = null;
let table2IsByPoint = true;
let marker1 = null;
let marker2 = null;
let edate = null;
let sdate = null;
let edate1 = null;
let sdate1 = null;
const BACKEND_EVENTS_BYPOINT = '/json/vtec_events_bypoint.py';
const BACKEND_EVENTS_BYUGC = '/json/vtec_events_byugc.py';
const BACKEND_SBW_BYPOINT = '/json/sbw_by_point.py';
const BACKEND_EVENTS = "/json/vtec_events.py";
const BACKEND_EVENTS_BYSTATE = "/json/vtec_events_bystate.py";

const states = [["AL", "Alabama"], ["AK", "Alaska"], ["AZ", "Arizona"],
        ["AR", "Arkansas"], ["CA", "California"], ["CO", "Colorado"],
        ["CT", "Connecticut"], ["DE", "Delaware"], ["FL", "Florida"],
        ["GA", "Georgia"], ["HI", "Hawaii"], ["ID", "Idaho"],
        ["IL", "Illinois"], ["IN", "Indiana"], ["IA", "Iowa"],
        ["KS", "Kansas"], ["KY", "Kentucky"], ["LA", "Louisiana"],
        ["ME", "Maine"], ["MD", "Maryland"], ["MA", "Massachusetts"],
        ["MI", "Michigan"], ["MN", "Minnesota"], ["MS", "Mississippi"],
        ["MO", "Missouri"], ["MT", "Montana"], ["NE", "Nebraska"],
        ["NV", "Nevada"], ["NH", "New Hampshire"], ["NJ", "New Jersey"],
        ["NM", "New Mexico"], ["NY", "New York"], ["NC", "North Carolina"],
        ["ND", "North Dakota"], ["OH", "Ohio"], ["OK", "Oklahoma"],
        ["OR", "Oregon"], ["PA", "Pennsylvania"], ["RI", "Rhode Island"],
        ["SC", "South Carolina"], ["SD", "South Dakota"], ["TN", "Tennessee"],
        ["TX", "Texas"], ["UT", "Utah"], ["VT", "Vermont"], ["VA", "Virginia"],
        ["WA", "Washington"], ["WV", "West Virginia"], ["WI", "Wisconsin"],
        ["WY", "Wyoming"],
        ["AM", "Atlantic Ocean AM"],
        ["AN", "Atlantic Ocean AN"],
        ["AS", "AS"],
        ["DC", "Distict of Columbia"],
        ["GM", "Gulf of Mexico"],
        ["GU", "Guam"],
        ["LC", "Lake St. Clair"],
        ["LE", "Lake Erie"],
        ["LH", "Lake Huron"],
        ["LM", "Lake Michigan"],
        ["LO", "Lake Ontario"],
        ["LS", "Lake Superior"],
        ["PH", "Hawaii PH Zones"],
        ["PK", "Alaska PK Zones"],
        ["PM", "Zones PM"],
        ["PR", "Puerto Rico"],
        ["PS", "Zones PS"],
        ["PZ", "Pacific Ocean PZ"],
        ["SL", "St. Lawrence River"]
];

// URL parameter management functions - removing hash linking approach
function getURLParams() {
    return new URLSearchParams(window.location.search);
}

function updateURL(params) {
    const url = new URL(window.location);
    url.search = params.toString();
    window.history.replaceState({}, '', url);
}

function addByPointParams(params, newParams) {
    if (newParams.lon) params.set('lon', newParams.lon);
    if (newParams.lat) params.set('lat', newParams.lat);
    if (newParams.buffer) params.set('buffer', newParams.buffer);
    if (newParams.sdate1) params.set('sdate1', newParams.sdate1);
    if (newParams.edate1) params.set('edate1', newParams.edate1);
}

function addByUGCParams(params, newParams) {
    if (newParams.state) params.set('state', newParams.state);
    if (newParams.ugc) params.set('ugc', newParams.ugc);
    if (newParams.lon) params.set('lon', newParams.lon);
    if (newParams.lat) params.set('lat', newParams.lat);
    if (newParams.buffer) params.set('buffer', newParams.buffer);
    if (newParams.sdate) params.set('sdate', newParams.sdate);
    if (newParams.edate) params.set('edate', newParams.edate);
}

function addListParams(params, newParams) {
    if (newParams.by) params.set('by', newParams.by);
    if (newParams.datum) params.set('datum', newParams.datum);
    if (newParams.year) params.set('year', newParams.year);
    if (newParams.phenomena) params.set('phenomena', newParams.phenomena);
    if (newParams.significance) params.set('significance', newParams.significance);
}

// Clean URL parameters to only include those relevant to the current mode
function setModeParams(mode, newParams = {}) {
    const params = new URLSearchParams();
    params.set('mode', mode);
    
    // Add only relevant parameters for each mode
    switch (mode) {
        case 'bypoint':
            addByPointParams(params, newParams);
            break;
            
        case 'byugc':
        case 'eventsbypoint':
            addByUGCParams(params, newParams);
            break;
            
        case 'list':
            addListParams(params, newParams);
            break;
            
        default:
            // No additional parameters for unknown modes
            break;
    }
    
    updateURL(params);
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

/**
 * Format date for API calls - works with native HTML date inputs
 * @param {HTMLInputElement} dateInput - Native date input element
 * @returns {string} formatted date string (YYYY-MM-DD)
 */
function formatDatePicker(dateInput) {
    if (dateInput?.value) {
        return dateInput.value; // Native date inputs already return YYYY-MM-DD format
    }
    // Fallback to current date
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

function updateMarkerPosition(lon, lat) {
    document.getElementById("lat").value = lat.toFixed(4);
    document.getElementById("lon").value = lon.toFixed(4);
    const buffer = parseFloat(document.querySelector('select[name="buffer"]').value);
    const sdate1Value = document.getElementById("sdate1").value;
    const edate1Value = document.getElementById("edate1").value;
    // Set clean URL parameters for this mode only
    setModeParams('bypoint', {
        lon: lon.toFixed(4),
        lat: lat.toFixed(4),
        buffer: buffer.toFixed(2),
        sdate1: sdate1Value,
        edate1: edate1Value
    });
    updateTable();
}
function updateMarkerPosition2(lon, lat) {
    document.getElementById("lat2").value = lat.toFixed(4);
    document.getElementById("lon2").value = lon.toFixed(4);
    updateTable2ByPoint();
}
function updateTable(){
    const buffer = parseFloat(document.querySelector('select[name="buffer"]').value);
    let title = `Storm Based Warnings for Point: ${document.getElementById("lon").value}E ${document.getElementById("lat").value}N`;
    if (buffer > 0){
        title += ` with ${buffer} degree buffer`;
    }
    document.getElementById("table1title").textContent = title;
    // Do what we need to for table 1
    const urlparams = new URLSearchParams({
        lat: document.getElementById("lat").value,
        lon: document.getElementById("lon").value,
        buffer,
        sdate: formatDatePicker(sdate1),
        edate: formatDatePicker(edate1)
    });
    fetch(`${BACKEND_SBW_BYPOINT}?${urlparams}`)
    .then(response => response.json())
    .then(data => {
        const tableData = data.sbws.map(row => ({
            event: `<a href="${row.url}" target="_blank">${row.eventid}</a>`,
            phenomena: row.ph_name,
            significance: row.sig_name,
            phenomena_code: row.phenomena || '',
            significance_code: row.significance || '',
            issued: row.issue,
            expired: row.expire,
            issue_hailtag: row.issue_hailtag,
            issue_windtag: row.issue_windtag,
            issue_tornadotag: row.issue_tornadotag,
            issue_damagetag: row.issue_damagetag
        }));
        table1.setData(tableData);
        // Update phenomena summary
        createPhenomenaSummary(tableData, 'table1title');
        // Update toolbar count
        updateTableToolbar('table1title', tableData);
        // Update table toolbar with record count
        updateTableToolbar('table1title', tableData);
    })
    .catch(() => {
        // Handle error silently
    });
}

function updateTable2ByUGC(){
    table2IsByPoint = false;
    document.getElementById("table2title").textContent = `Events for UGC: ${ugcSelect.value}`;
    
    // Set clean URL parameters for this mode only
    setModeParams('byugc', { 
        state: stateSelect.value,
        ugc: ugcSelect.value,
        sdate: sdate.value,
        edate: edate.value
    });
    
    // Do what we need to for table 2
    const urlparams = new URLSearchParams({
        ugc: ugcSelect.value,
        sdate: formatDatePicker(sdate),
        edate: formatDatePicker(edate)
    });
    fetch(`${BACKEND_EVENTS_BYUGC}?${urlparams}`)
    .then(response => response.json())
    .then(data => {
        const tableData = data.events.map(row => ({
            event: `<a href="${row.url}" target="_blank">${row.eventid}</a>`,
            phenomena: row.ph_name,
            significance: row.sig_name,
            phenomena_code: row.phenomena || '',
            significance_code: row.significance || '',
            issued: row.issue,
            expired: row.expire
        }));
        table2.setData(tableData);
        // Update phenomena summary
        createPhenomenaSummary(tableData, 'table2title');
        // Update table toolbar with record count
        updateTableToolbar('table2title', tableData);
    })
    .catch(() => {
        // Handle error silently
    });
}

function updateTable2ByPoint(){
    const buffer = parseFloat(document.querySelector('select[name="buffer2"]').value);
    table2IsByPoint = true;
    let title = `Events for Point: ${document.getElementById("lon2").value}E ${document.getElementById("lat2").value}N`;
    if (buffer > 0){
        title += ` with ${buffer} degree buffer`;
    }
    document.getElementById("table2title").textContent = title;
    
    // Set clean URL parameters for this mode only
    setModeParams('eventsbypoint', { 
        lat: document.getElementById("lat2").value,
        lon: document.getElementById("lon2").value,
        buffer: buffer.toString(),
        sdate: sdate.value,
        edate: edate.value
    });
    
    // Do what we need to for table 2
    const urlparams = new URLSearchParams({
        lat: document.getElementById("lat2").value,
        lon: document.getElementById("lon2").value,
        buffer,
        sdate: formatDatePicker(sdate),
        edate: formatDatePicker(edate)
    });
    fetch(`${BACKEND_EVENTS_BYPOINT}?${urlparams}`)
    .then(response => response.json())
    .then(data => {
        const tableData = data.events.map(row => ({
            event: `<a href="${row.url}" target="_blank">${row.eventid}</a>`,
            phenomena: row.ph_name,
            significance: row.sig_name,
            phenomena_code: row.phenomena || '',
            significance_code: row.significance || '',
            issued: row.issue,
            expired: row.expire
        }));
        table2.setData(tableData);
        // Update phenomena summary
        createPhenomenaSummary(tableData, 'table2title');
        // Update table toolbar with record count
        updateTableToolbar('table2title', tableData);
    })
    .catch(() => {
        // Handle error silently
    });
}

function updateTable3(){
    // get currently selected by3 radio button
    const by = escapeHTML(document.querySelector("input[name='by3']:checked").value);
    const single = escapeHTML(document.querySelector("input[name='single3']:checked").value);
    const datum = (by === "state") ? escapeHTML(stateSelect3.value) : escapeHTML(document.getElementById("wfo3").value);
    const year = escapeHTML(document.getElementById("year3").value);
    const params = {
        wfo: document.getElementById("wfo3").value,
        state: stateSelect3.value,
        year,
    };
    
    // Set clean URL parameters for this mode only
    const urlParams = {
        by,
        datum,
        year
    };
    if (single === "single"){
        params.phenomena = escapeHTML(document.getElementById("ph3").value);
        params.significance = escapeHTML(document.getElementById("sig3").value);
        urlParams.phenomena = params.phenomena;
        urlParams.significance = params.significance;
    }
    setModeParams('list', urlParams);
    
    // Create descriptive title based on selection type
    let title = `Events for ${by} ${datum} in ${year}`;
    if (single === "single") {
        const phenText = document.getElementById("ph3").selectedOptions[0]?.text || "Unknown";
        const sigText = document.getElementById("sig3").selectedOptions[0]?.text || "Unknown";
        title += ` (${phenText} / ${sigText})`;
    } else {
        title += ' (All VTEC Events)';
    }
    document.getElementById("table3title").textContent = title;
    // Do what we need to for table 3
    fetch((by === "wfo" ? `${BACKEND_EVENTS}?${new URLSearchParams(params)}` : `${BACKEND_EVENTS_BYSTATE}?${new URLSearchParams(params)}`))
    .then(response => response.json())
    .then(data => {
        const tableData = data.events.map(row => ({
            event: `<a href="${row.uri}" target="_blank">${row.phenomena}.${row.significance}.${row.eventid}</a>`,
            phenomena: row.ph_name,
            significance: row.sig_name,
            phenomena_code: row.phenomena,
            significance_code: row.significance,
            wfo: row.wfo,
            locations: row.locations,
            issued: row.issue,
            expired: row.expire
        }));
        table3.setData(tableData);
        // Update phenomena summary
        createPhenomenaSummary(tableData, 'table3title');
        // Update table toolbar with record count
        updateTableToolbar('table3title', tableData);
    })
    .catch(() => {
        // Handle error silently
    });
}


// Bean counting and filtering functionality for phenomena/significance combinations
function createPhenomenaSummary(tableData, containerId) {
    const titleElement = document.getElementById(containerId);
    if (!titleElement) return;
    
    // Find the card body that contains the title
    const cardBody = titleElement.closest('.card-body');
    if (!cardBody) return;
    
    // Remove existing summary
    const existingSummary = cardBody.querySelector('.phenomena-summary');
    if (existingSummary) {
        existingSummary.remove();
    }
    
    // Count phenomena/significance combinations
    const combinations = {};
    tableData.forEach(row => {
        const key = `${row.phenomena}|${row.significance}`;
        if (!combinations[key]) {
            combinations[key] = {
                phenomena: row.phenomena,
                significance: row.significance,
                phenomena_code: row.phenomena_code || '',
                significance_code: row.significance_code || '',
                count: 0
            };
        }
        combinations[key].count++;
    });
    
    // Sort by count (descending)
    const sortedCombinations = Object.values(combinations).sort((a, b) => b.count - a.count);
    
    if (sortedCombinations.length === 0) return;
    
    // Create summary panel
    const summaryDiv = document.createElement('div');
    summaryDiv.className = 'phenomena-summary mt-3 mb-3';
    summaryDiv.innerHTML = `
        <div class="card border-info">
            <div class="card-header bg-light">
                <h6 class="mb-0">
                    <button class="btn btn-link text-decoration-none p-0 fw-bold" type="button" 
                            data-bs-toggle="collapse" data-bs-target="#${containerId}-summary" 
                            aria-expanded="true" aria-controls="${containerId}-summary">
                        <i class="bi bi-bar-chart-fill me-2" aria-hidden="true"></i>Phenomena Summary (${tableData.length} total events)
                        <i class="bi bi-chevron-up ms-2 summary-chevron" aria-hidden="true"></i>
                    </button>
                </h6>
            </div>
            <div class="collapse show" id="${containerId}-summary">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <small class="text-muted">
                            <i class="bi bi-info-circle me-1" aria-hidden="true"></i>
                            Click any combination to filter the table:
                        </small>
                        <button class="btn btn-sm btn-outline-secondary clear-filter-btn" type="button" style="display: none;" 
                                title="Clear current filter and show all results">
                            <i class="bi bi-x-lg me-1" aria-hidden="true"></i>Clear Filter
                        </button>
                    </div>
                    <div class="phenomena-grid">
                        ${sortedCombinations.map(combo => `
                            <div class="phenomena-item" data-phenomena="${combo.phenomena}" data-significance="${combo.significance}"
                                 title="Click to filter table by ${combo.phenomena} / ${combo.significance} (${combo.count} events)">
                                <div class="phenomena-badge">
                                    <span class="fw-bold">${combo.phenomena}</span> / <span class="fw-bold">${combo.significance}</span>
                                    ${combo.phenomena_code?.length && combo.significance_code?.length
                                        ? `<span class="badge bg-secondary ms-1">${combo.phenomena_code}.${combo.significance_code}</span>`
                                        : ''
                                    }
                                    <span class="badge bg-primary ms-2">${combo.count}</span>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Insert summary before the table-responsive div
    const tableContainer = cardBody.querySelector('.table-responsive');
    if (tableContainer) {
        cardBody.insertBefore(summaryDiv, tableContainer);
    }
    
    // Add event listeners for filtering
    summaryDiv.querySelectorAll('.phenomena-item').forEach(item => {
        item.addEventListener('click', () => {
            const phenomena = item.dataset.phenomena;
            const significance = item.dataset.significance;
            filterTableByPhenomena(containerId, phenomena, significance);
            
            // Update UI state
            summaryDiv.querySelectorAll('.phenomena-item').forEach(i => i.classList.remove('active'));
            item.classList.add('active');
            summaryDiv.querySelector('.clear-filter-btn').style.display = 'inline-block';
        });
    });
    
    // Clear filter button
    summaryDiv.querySelector('.clear-filter-btn').addEventListener('click', () => {
        clearPhenomenaFilter(containerId);
        summaryDiv.querySelectorAll('.phenomena-item').forEach(i => i.classList.remove('active'));
        summaryDiv.querySelector('.clear-filter-btn').style.display = 'none';
    });
    
    // Toggle chevron icon
    const collapseElement = document.getElementById(`${containerId}-summary`);
    collapseElement.addEventListener('show.bs.collapse', () => {
        summaryDiv.querySelector('.summary-chevron').classList.replace('bi-chevron-down', 'bi-chevron-up');
    });
    collapseElement.addEventListener('hide.bs.collapse', () => {
        summaryDiv.querySelector('.summary-chevron').classList.replace('bi-chevron-up', 'bi-chevron-down');
    });
}

function filterTableByPhenomena(containerId, phenomena, significance) {
    const table = (containerId === 'table1title') ? table1 : 
                  (containerId === 'table2title') ? table2 : 
                  (containerId === 'table3title') ? table3 : null;
    if (!table) return;
    
    // Apply filter to Tabulator
    table.setFilter([
        {field: "phenomena", type: "=", value: phenomena},
        {field: "significance", type: "=", value: significance}
    ]);
    
    // Update table title
    const titleElement = document.getElementById(containerId);
    if (titleElement) {
        const originalText = titleElement.textContent.split(' (')[0]; // Remove any existing filter text
        const filteredCount = table.getDataCount("active");
    titleElement.innerHTML = `<i class="bi bi-table me-2" aria-hidden="true"></i>${escapeHTML(originalText)} <small class="text-muted">(filtered: ${phenomena} / ${significance} - ${filteredCount} events)</small>`;
    }
    
    // Update toolbar count
    const filteredCount = table.getDataCount("active");
    const tableData = table.getData(); // Get original data for count
    updateTableToolbar(containerId, tableData, filteredCount);
}

function clearPhenomenaFilter(containerId) {
    const table = (containerId === 'table1title') ? table1 : 
                  (containerId === 'table2title') ? table2 : 
                  (containerId === 'table3title') ? table3 : null;
    if (!table) return;
    
    // Clear filter
    table.clearFilter();
    
    // Reset table title
    const titleElement = document.getElementById(containerId);
    if (titleElement) {
        let originalText = titleElement.textContent.split(' (')[0];
        // Prevent DOM text interpreted as HTML
        originalText = escapeHTML(originalText);
        titleElement.innerHTML = `<i class="bi bi-table me-2" aria-hidden="true"></i>${originalText}`;
    }
    
    // Update toolbar count (no filter)
    const tableData = table.getData();
    updateTableToolbar(containerId, tableData);
}

// Helper function to get container from containerId (complexity reduction)
function getTableContainer(containerId) {
    const titleElement = document.getElementById(containerId);
    return titleElement ? titleElement.parentNode : null;
}

// Helper function to format record count text (complexity reduction)
function formatRecordCountText(totalCount, filteredCount) {
    const displayCount = filteredCount !== null ? filteredCount : totalCount;
    const filterText = filteredCount !== null ? ` (${filteredCount} of ${totalCount} shown)` : '';
    return `${displayCount} record${displayCount !== 1 ? 's' : ''}${filterText}`;
}

// Update table toolbar with current data count
function updateTableToolbar(containerId, tableData, filteredCount = null) {
    const container = getTableContainer(containerId);
    if (!container) return;
    
    const toolbar = container.querySelector('.table-toolbar');
    if (!toolbar) return;
    
    const countSpan = toolbar.querySelector('.table-count');
    if (countSpan) {
        countSpan.textContent = formatRecordCountText(tableData.length, filteredCount);
    }
}

// Helper functions for buildUI complexity reduction
function setupExportButtons() {
    document.querySelectorAll(".iemtool").forEach(btn => {
        btn.addEventListener('click', (event) => {
            event.preventDefault();
            event.stopPropagation();
            let url = BACKEND_SBW_BYPOINT;
            let params = {
                fmt: (btn.dataset.opt === "csv") ? "csv" : "xlsx",
                lat: document.getElementById("lat").value,
                lon: document.getElementById("lon").value,
                buffer: document.querySelector('select[name="buffer"]').value,
                sdate: formatDatePicker(sdate1),
                edate: formatDatePicker(edate1)
            };
            if (btn.dataset.table === "2"){
                url = BACKEND_EVENTS_BYUGC;
                params.ugc = ugcSelect.value;
                params.sdate = formatDatePicker(sdate);
                params.edate = formatDatePicker(edate);
                if (table2IsByPoint) {
                    url = BACKEND_EVENTS_BYPOINT;
                    params.lon = document.getElementById("lon2").value;
                    params.lat = document.getElementById("lat2").value;
                }
            }
            if (btn.dataset.table === "3"){
                const by = document.querySelector("input[name='by3']:checked").value;
                url = (by === "state") ? BACKEND_EVENTS_BYSTATE: BACKEND_EVENTS;
                params = {
                    fmt: (btn.dataset.opt === "csv") ? "csv" : "xlsx",
                    wfo: document.getElementById("wfo3").value,
                    state: stateSelect3.value,
                    year: document.getElementById("year3").value,
                    phenomena: document.getElementById("ph3").value,
                    significance: document.getElementById("sig3").value
                };
            }
            // For CSV, trigger download; for Excel, open in new tab to avoid reload
            const downloadUrl = `${url}?${new URLSearchParams(params).toString()}`;
            if (btn.dataset.opt === "csv") {
                // Create a hidden link and click it to trigger download
                const aa = document.createElement('a');
                aa.href = downloadUrl;
                aa.download = '';
                document.body.appendChild(aa);
                aa.click();
                document.body.removeChild(aa);
            } else {
                // Open Excel export in a new tab to avoid page reload
                window.open(downloadUrl, '_blank');
            }
        });
    });
}

function setupTableConfigurations() {
    // Tables
    table1 = new Tabulator("#table1", {
        layout: "fitColumns",
        placeholder: "Drag marker on map to auto-populate this table",
        height: "400px",
        columns: [
            {
                title: "Event",
                field: "event",
                formatter: "html",
                headerSort: false,
                width: 120,
                download: (value) => {
                    // Extract eventid from the HTML string for export
                    const div = document.createElement('div');
                    div.innerHTML = value;
                    const aa = div.querySelector('a');
                    return aa ? aa.textContent : value;
                }
            },
            {title: "Phenomena", field: "phenomena", headerSort: true, sorter: "string"},
            {title: "Significance", field: "significance", headerSort: true, sorter: "string"},
            {title: "Issued", field: "issued", headerSort: true, sorter: customDateTimeSorter},
            {title: "Expired", field: "expired", headerSort: true, sorter: customDateTimeSorter},
            {title: "Issue Hail Tag", field: "issue_hailtag", headerSort: true, sorter: "string"},
            {title: "Issue Wind Tag", field: "issue_windtag", headerSort: true, sorter: "string"},
            {title: "Issue Tornado Tag", field: "issue_tornadotag", headerSort: true, sorter: "string"},
            {title: "Issue Damage Tag", field: "issue_damagetag", headerSort: true, sorter: "string"}
        ],
        initialSort: [
            {column: "issued", dir: "desc"}
        ]
    });
    
    // Add table toolbar with current view exports
    const table1Title = document.getElementById("table1title");
    if (table1Title && !table1Title.querySelector('.table-toolbar')) {
        const toolbarDiv = document.createElement('div');
        toolbarDiv.className = 'table-toolbar d-flex justify-content-between align-items-center mb-3 p-2 bg-light border rounded';
        toolbarDiv.innerHTML = `${''}
            <div class="table-info">
                <small class="text-muted">
                    <i class="bi bi-table me-1" aria-hidden="true"></i>
                    <span class="table-count">Table data</span>
                </small>
            </div>
            <div class="table-exports">
                <span class="badge bg-info me-2">Export Current View:</span>
                <button type="button" class="btn btn-sm btn-success me-1" onclick="table1.download('xlsx', 'sbw-current-view.xlsx')" title="Export visible table data to Excel">
                    <i class="bi bi-download me-1" aria-hidden="true"></i>Excel
                </button>
                <button type="button" class="btn btn-sm btn-primary" onclick="table1.download('csv', 'sbw-current-view.csv')" title="Export visible table data to CSV">
                    <i class="bi bi-download me-1" aria-hidden="true"></i>CSV
                </button>
            </div>
        `;
        
        // Insert toolbar after the phenomena summary (or after title if no summary)
        const phenomenaSummary = table1Title.parentNode.querySelector('.phenomena-summary');
        const insertAfter = phenomenaSummary || table1Title;
        insertAfter.parentNode.insertBefore(toolbarDiv, insertAfter.nextSibling);
    }
    
    table2 = new Tabulator("#table2", {
        layout: "fitColumns",
        placeholder: "Drag marker on map or select UGC to auto-populate this table",
        height: "400px",
        columns: [
            {
                title: "Event",
                field: "event",
                formatter: "html",
                headerSort: false,
                width: 120,
                download: (value) => {
                    const div = document.createElement('div');
                    div.innerHTML = value;
                    const aa = div.querySelector('a');
                    return aa ? aa.textContent : value;
                }
            },
            {title: "Phenomena", field: "phenomena", headerSort: true, sorter: "string"},
            {title: "Significance", field: "significance", headerSort: true, sorter: "string"},
            {title: "Issued", field: "issued", headerSort: true, sorter: customDateTimeSorter},
            {title: "Expired", field: "expired", headerSort: true, sorter: customDateTimeSorter}
        ],
        initialSort: [
            {column: "issued", dir: "desc"}
        ]
    });
    
    // Add table toolbar with current view exports for table2
    const table2Title = document.getElementById("table2title");
    if (table2Title && !table2Title.querySelector('.table-toolbar')) {
        const toolbarDiv = document.createElement('div');
        toolbarDiv.className = 'table-toolbar d-flex justify-content-between align-items-center mb-3 p-2 bg-light border rounded';
        toolbarDiv.innerHTML = `${''}
            <div class="table-info">
                <small class="text-muted">
                    <i class="bi bi-table me-1" aria-hidden="true"></i>
                    <span class="table-count">Table data</span>
                </small>
            </div>
            <div class="table-exports">
                <span class="badge bg-info me-2">Export Current View:</span>
                <button type="button" class="btn btn-sm btn-success me-1" onclick="table2.download('xlsx', 'events-current-view.xlsx')" title="Export visible table data to Excel">
                    <i class="bi bi-download me-1" aria-hidden="true"></i>Excel
                </button>
                <button type="button" class="btn btn-sm btn-primary" onclick="table2.download('csv', 'events-current-view.csv')" title="Export visible table data to CSV">
                    <i class="bi bi-download me-1" aria-hidden="true"></i>CSV
                </button>
            </div>
        `;
        
        // Insert toolbar after the phenomena summary (or after title if no summary)
        const phenomenaSummary = table2Title.parentNode.querySelector('.phenomena-summary');
        const insertAfter = phenomenaSummary || table2Title;
        insertAfter.parentNode.insertBefore(toolbarDiv, insertAfter.nextSibling);
    }
    
    table3 = new Tabulator("#table3", {
        layout: "fitColumns",
        placeholder: "Select options to auto-populate this table",
        height: "400px",
        columns: [
            {
                title: "Event",
                field: "event",
                formatter: "html",
                headerSort: false,
                width: 120,
                download: (value) => {
                    const div = document.createElement('div');
                    div.innerHTML = value;
                    const aa = div.querySelector('a');
                    return aa ? aa.textContent : value;
                }
            },
            {title: "Phenomena", field: "phenomena", headerSort: true, sorter: "string"},
            {title: "Significance", field: "significance", headerSort: true, sorter: "string"},
            {title: "WFO", field: "wfo", headerSort: true, sorter: "string"},
            {title: "Locations", field: "locations", headerSort: true, sorter: "string"},
            {title: "Issued", field: "issued", headerSort: true, sorter: customDateTimeSorter},
            {title: "Expired", field: "expired", headerSort: true, sorter: customDateTimeSorter}
        ],
        initialSort: [
            {column: "issued", dir: "desc"}
        ]
    });
    
    // Add table toolbar with current view exports for table3
    const table3Title = document.getElementById("table3title");
    if (table3Title && !table3Title.querySelector('.table-toolbar')) {
        const toolbarDiv = document.createElement('div');
        toolbarDiv.className = 'table-toolbar d-flex justify-content-between align-items-center mb-3 p-2 bg-light border rounded';
        toolbarDiv.innerHTML = `${''}
            <div class="table-info">
                <small class="text-muted">
                    <i class="bi bi-table me-1" aria-hidden="true"></i>
                    <span class="table-count">Table data</span>
                </small>
            </div>
            <div class="table-exports">
                <span class="badge bg-info me-2">Export Current View:</span>
                <button type="button" class="btn btn-sm btn-success me-1" onclick="table3.download('xlsx', 'list-current-view.xlsx')" title="Export visible table data to Excel">
                    <i class="bi bi-download me-1" aria-hidden="true"></i>Excel
                </button>
                <button type="button" class="btn btn-sm btn-primary" onclick="table3.download('csv', 'list-current-view.csv')" title="Export visible table data to CSV">
                    <i class="bi bi-download me-1" aria-hidden="true"></i>CSV
                </button>
            </div>
        `;
        
        table3Title.parentNode.insertBefore(toolbarDiv, table3Title.nextSibling);
    }
}

function setupDateInputs() {
    // Native date inputs - applying jQuery removal rule
    sdate = document.querySelector("input[name='sdate']");
    edate = document.querySelector("input[name='edate']");
    sdate1 = document.querySelector("input[name='sdate1']");
    edate1 = document.querySelector("input[name='edate1']");
    
    // Get tomorrow's UTC date
    const tomorrow = new Date();
    tomorrow.setUTCDate(tomorrow.getUTCDate() + 1);
    const tomorrowUTC = tomorrow.toISOString().split('T')[0];
    
    // Set default values
    sdate.value = "1986-01-01";
    edate.value = tomorrowUTC; // Tomorrow's UTC date
    sdate1.value = "2002-01-01";
    edate1.value = tomorrowUTC; // Tomorrow's UTC date
    
    // Set min/max attributes for date validation
    sdate.min = "1986-01-01";
    sdate.max = tomorrowUTC;
    edate.min = "1986-01-01";
    edate.max = tomorrowUTC;
    sdate1.min = "2002-01-01";
    sdate1.max = tomorrowUTC;
    edate1.min = "2002-01-01";
    edate1.max = tomorrowUTC;
    
    // Add event listeners for date changes
    sdate.addEventListener('change', () => {
        updateTable2ByUGC();
    });
    edate.addEventListener('change', () => {
        updateTable2ByUGC();
    });
    sdate1.addEventListener('change', () => {
        updateTable();
    });
    edate1.addEventListener('change', () => {
        updateTable();
    });
}

function setupSelectBoxes() {
    // select boxes - applying jQuery removal rule
    const data = states.map(obj => ({
        id: obj[0],
        text: obj[1]
    }));
    
    // Setup state selects with vanilla JavaScript
    stateSelect3 = document.getElementById("state3");
    stateSelect = document.getElementById("state");
    
    // Populate state selects
    [stateSelect3, stateSelect].forEach(select => {
        // Clear existing options
        select.innerHTML = '<option value="">Select a geography/state</option>';
        data.forEach(item => {
            const option = document.createElement('option');
            option.value = item.id;
            option.textContent = item.text;
            select.appendChild(option);
        });
    });
    
    stateSelect.addEventListener('change', (e) => {
        const state = e.target.value;
        if (!state) return;
        
        // Set clean URL parameters for this mode only
        setModeParams('byugc', { state });
        
        // Load the ugcSelect box
        fetch(`/json/state_ugc.json?${new URLSearchParams({ state })}`)
        .then(response => response.json())
        .then(data2 => {
            ugcSelect.innerHTML = '<option value="">Select County/Zone</option>';
            data2.ugcs.forEach(obj => {
                const extra = (obj.ugc.substring(2, 1) === "Z") ? " (Zone)": "";
                const option = document.createElement('option');
                option.value = obj.ugc;
                option.textContent = `[${obj.ugc}] ${obj.name}${extra}`;
                ugcSelect.appendChild(option);
            });
            // Check if we need to set a specific UGC from URL parameters
            const urlParams = getURLParams();
            const targetUGC = urlParams.get('ugc');
            if (targetUGC){
                ugcSelect.value = targetUGC;
                updateTable2ByUGC();
            }
        })
        .catch(() => {
            // Handle error silently
        });
    });
    
    ugcSelect = document.querySelector("select[name='ugc']");
    ugcSelect.innerHTML = '<option value="">Select County/Zone after Selecting Geography</option>';
    ugcSelect.addEventListener('change', (e) => {
        const ugc = e.target.value;
        if (!ugc) return;
        // Set clean URL parameters for this mode only - include both state and ugc
        setModeParams('byugc', { 
            state: stateSelect.value,
            ugc 
        });
        updateTable2ByUGC();
    });
}

function setupManualButtons() {
    // Manual Point Entry
    document.getElementById("manualpt").addEventListener('click', () => {
        const la = parseFloat(document.getElementById("lat").value);
        const lo = parseFloat(document.getElementById("lon").value);
        if (isNaN(la) || isNaN(lo)){
            return;
        }
        // Update the marker's position
        marker1.setGeometry(new ol.geom.Point(ol.proj.fromLonLat([lo, la])));
        updateMarkerPosition(lo, la);
    });
    document.getElementById("manualugc").addEventListener('click', () => {
        const ugc = ugcSelect.value;
        if (ugc === null){
            return;
        }
        // Set clean URL parameters for this mode only - include both state and ugc
        setModeParams('byugc', { 
            state: stateSelect.value,
            ugc 
        });
        updateTable2ByUGC();
    });
    document.getElementById("manualpt2").addEventListener('click', () => {
        const la = parseFloat(document.getElementById("lat2").value);
        const lo = parseFloat(document.getElementById("lon2").value);
        if (isNaN(la) || isNaN(lo)){
            return;
        }
        marker2.setGeometry(new ol.geom.Point(ol.proj.fromLonLat([lo, la])));
        updateMarkerPosition2(lo, la);
    });
    document.getElementById("button3").addEventListener('click', () => {
        updateTable3();
    });
}

function setupDropdownPopulation() {
    // Populate wfos select with iemdata.wfos data - applying jQuery removal rule
    const wfoSelect = document.querySelector("select[name='wfo']");
    wfoSelect.innerHTML = '<option value="">Select a WFO</option>';
    iemdata.wfos.forEach(obj => {
        const option = document.createElement('option');
        option.value = obj[0];
        option.textContent = `[${obj[0]}] ${obj[1]}`;
        wfoSelect.appendChild(option);
    });
    
    const phSelect = document.querySelector("select[name='ph']");
    phSelect.innerHTML = '<option value="">Select a Phenomena</option>';
    iemdata.vtec_phenomena.forEach(obj => {
        const option = document.createElement('option');
        option.value = obj[0];
        option.textContent = obj[1];
        phSelect.appendChild(option);
    });
    
    const sigSelect = document.querySelector("select[name='sig']");
    sigSelect.innerHTML = '<option value="">Select a Significance</option>';
    iemdata.vtec_significance.forEach(obj => {
        const option = document.createElement('option');
        option.value = obj[0];
        option.textContent = obj[1];
        sigSelect.appendChild(option);
    });
    // populate year3 select with values from 1986 to current year
    const year3 = document.querySelector("select[name='year']");
    const currentYear = new Date().getFullYear();
    for (let i = 1986; i <= currentYear; i++){
        const option = new Option(i, i, false, false);
        if (i === currentYear) {
            option.selected = true; // Select current year by default
        }
        year3.appendChild(option);
    }
    
    // Set up radio button logic for tab 3 (Single vs All VTEC events)
    const singleRadio = document.getElementById('single3');
    const allRadio = document.getElementById('all3');
    const phSelect2 = document.querySelector("select[name='ph']");
    const sigSelect2 = document.querySelector("select[name='sig']");
    
    // Function to update the state of phenomena and significance selects
    function updateVTECSelects() {
        const isSingleSelected = singleRadio.checked;
        
        // Enable/disable the selects based on radio button state
        phSelect2.disabled = !isSingleSelected;
        sigSelect2.disabled = !isSingleSelected;
        
        // Update visual styling
        if (isSingleSelected) {
            phSelect2.parentElement.classList.remove('opacity-50');
            sigSelect2.parentElement.classList.remove('opacity-50');
        } else {
            phSelect2.parentElement.classList.add('opacity-50');
            sigSelect2.parentElement.classList.add('opacity-50');
            // Clear selections when switching to "All"
            phSelect2.value = '';
            sigSelect2.value = '';
        }
    }
    
    // Add event listeners for radio buttons
    singleRadio.addEventListener('change', updateVTECSelects);
    allRadio.addEventListener('change', updateVTECSelects);
    
    // Initialize the state
    updateVTECSelects();
}

function buildUI(){
    setupExportButtons();
    setupTableConfigurations();
    setupDateInputs();
    setupSelectBoxes();
    setupManualButtons();
    setupDropdownPopulation();
};

// Helper functions for processURLParams complexity reduction
function processHashMigration() {
    const hash = window.location.hash;
    if (hash && hash.length > 1) {
        migrateHashToURLParams(hash.substring(1));
        return true; // Will reload with new URL params
    }
    return false;
}

function handleByUGCMode(urlParams) {
    const state = urlParams.get('state');
    const ugc = urlParams.get('ugc');
    const sdateParam = urlParams.get('sdate');
    const edateParam = urlParams.get('edate');
    
    // Set date values if provided
    if (sdateParam) {
        document.querySelector('input[name="sdate"]').value = sdateParam;
    }
    if (edateParam) {
        document.querySelector('input[name="edate"]').value = edateParam;
    }
    
    // If we have a state parameter, use it directly
    if (state) {
        stateSelect.value = state;
        stateSelect.dispatchEvent(new Event('change'));
    } else if (ugc) {
        // Fallback: extract state from UGC code
        const stateFromUGC = ugc.substring(0, 2);
        stateSelect.value = stateFromUGC;
        stateSelect.dispatchEvent(new Event('change'));
    }
}

function handleByPointMode(urlParams) {
    const lat = parseFloat(urlParams.get('lat'));
    const lon = parseFloat(urlParams.get('lon'));
    const buffer = parseFloat(urlParams.get('buffer'));
    const sdate1Param = urlParams.get('sdate1');
    const edate1Param = urlParams.get('edate1');
    
    // Set date values if provided
    if (sdate1Param) {
        document.getElementById('sdate1').value = sdate1Param;
    }
    if (edate1Param) {
        document.getElementById('edate1').value = edate1Param;
    }
    
    if (!isNaN(lat) && !isNaN(lon)) {
        if (!isNaN(buffer)) {
            document.querySelector('select[name="buffer"]').value = buffer;
        }
        // Update the marker position physically and trigger data loading
        if (marker1) {
            marker1.setGeometry(new ol.geom.Point(ol.proj.fromLonLat([lon, lat])));
        }
        updateMarkerPosition(lon, lat);
    }
}

function handleEventsByPointMode(urlParams) {
    // This mode uses the byugc tab but with different functionality
    const lat2 = parseFloat(urlParams.get('lat'));
    const lon2 = parseFloat(urlParams.get('lon'));
    const buffer2 = parseFloat(urlParams.get('buffer'));
    if (!isNaN(lat2) && !isNaN(lon2)) {
        if (!isNaN(buffer2)) {
            document.querySelector('select[name="buffer2"]').value = buffer2;
        }
        updateMarkerPosition2(lon2, lat2);
    }
}

function handleListMode(urlParams) {
    const by = urlParams.get('by');
    const datum = urlParams.get('datum');
    const year = urlParams.get('year');
    const phenomena = urlParams.get('phenomena');
    const significance = urlParams.get('significance');
    
    if (by && datum && year) {
        document.querySelector(`input[name='by3'][value='${by}']`).checked = true;
        if (phenomena && significance) {
            document.querySelector("input[name='single3'][value='single']").checked = true;
            document.getElementById("ph3").value = phenomena;
            document.getElementById("sig3").value = significance;
        } else {
            document.querySelector("input[name='single3'][value='all']").checked = true;
        }
        document.getElementById("year3").value = year;
        
        if (by === "state"){
            stateSelect3.value = datum;
        } else {
            document.getElementById("wfo3").value = datum;
        }
        // Update VTEC select states after setting radio buttons
        const updateEvent = new Event('change');
        document.querySelector("input[name='single3']:checked").dispatchEvent(updateEvent);
        updateTable3();
    }
}

// Process URL parameters on app initialization - now with Bootstrap tabs
function processURLParams(){
    const urlParams = getURLParams();
    let mode = urlParams.get('mode');
    
    // Handle backward compatibility: migrate hash to URL parameters
    if (processHashMigration()) {
        return; // Will reload with new URL params
    }
    
    // Default to first tab if no mode specified
    if (!mode) {
        mode = 'bypoint';
        const params = getURLParams();
        params.set('mode', mode);
        updateURL(params);
    }
    
    // Activate the appropriate Bootstrap tab
    activateTab(mode);
    
    switch (mode) {
        case 'byugc':
            handleByUGCMode(urlParams);
            break;
            
        case 'bypoint':
            handleByPointMode(urlParams);
            break;
            
        case 'eventsbypoint':
            handleEventsByPointMode(urlParams);
            break;
            
        case 'list':
            handleListMode(urlParams);
            break;
            
        default:
            // Unknown mode, use default (bypoint) already set above
            break;
    }
}

// Activate Bootstrap tab based on mode
function activateTab(mode) {
    // Map modes to tab IDs
    let tabId = 'bypoint-tab'; // Default tab
    switch (mode) {
        case 'bypoint':
            tabId = 'bypoint-tab';
            break;
        case 'byugc':
        case 'eventsbypoint':
            tabId = 'byugc-tab';
            break;
        case 'list':
            tabId = 'list-tab';
            break;
        default:
            // Use default tab (bypoint-tab) already set above
            break;
    }
    
    // Activate the tab using Bootstrap 5 API
    const tabElement = document.getElementById(tabId);
    if (tabElement) {
        const tab = new bootstrap.Tab(tabElement);
        tab.show();
    }
}

// Helper functions for hash migration (complexity reduction)
function handleByUGCHashMigration(tokens, params) {
    params.set('mode', 'byugc');
    params.set('ugc', tokens[1]);
}

function handleByPointHashMigration(tokens, params) {
    params.set('mode', 'bypoint');
    params.set('lon', tokens[1]);
    params.set('lat', tokens[2]);
    if (tokens.length >= 4) {
        params.set('buffer', tokens[3]);
    }
}

function handleEventsByPointHashMigration(tokens, params) {
    params.set('mode', 'eventsbypoint');
    params.set('lon', tokens[1]);
    params.set('lat', tokens[2]);
    if (tokens.length >= 4) {
        params.set('buffer', tokens[3]);
    }
}

function handleListHashMigration(tokens, params) {
    params.set('mode', 'list');
    params.set('by', tokens[1]);
    params.set('datum', tokens[2]);
    params.set('year', tokens[3]);
    if (tokens.length >= 6) {
        params.set('phenomena', tokens[4]);
        params.set('significance', tokens[5]);
    }
}

// Migrate old hash URLs to URL parameters for backward compatibility
function migrateHashToURLParams(hash) {
    const tokens = hash.split("/");
    const params = new URLSearchParams();
    
    if (tokens.length >= 2) {
        if (tokens[0] === 'byugc') {
            handleByUGCHashMigration(tokens, params);
        } else if (tokens[0] === 'bypoint' && tokens.length >= 3) {
            handleByPointHashMigration(tokens, params);
        } else if (tokens[0] === 'eventsbypoint' && tokens.length >= 3) {
            handleEventsByPointHashMigration(tokens, params);
        } else if (tokens[0] === 'list' && tokens.length >= 4) {
            handleListHashMigration(tokens, params);
        }
    }
    
    // Replace URL with parameters and remove hash
    const url = new URL(window.location);
    url.search = params.toString();
    url.hash = '';
    window.location.replace(url);
}

function parseLuxonDate(val) {
    if (!val) return null;
    let dt = window.luxon.DateTime.fromISO(val);
    if (!dt.isValid) dt = window.luxon.DateTime.fromFormat(val, "yyyy-MM-dd HH:mm");
    return dt.isValid ? dt : null;
}

// Custom datetime sorter using Luxon for proper date/time sorting
function customDateTimeSorter(a, b) {
    if (!a && !b) return 0;
    if (!a) return 1;
    if (!b) return -1;
    const dateA = parseLuxonDate(a);
    const dateB = parseLuxonDate(b);
    if (!dateA && !dateB) return 0;
    if (!dateA) return 1;
    if (!dateB) return -1;
    return dateA.toMillis() - dateB.toMillis();
}

// Initialize when DOM is ready
function initializeApp() {
    buildUI();
    
    const res1 = olSelectLonLat("map", updateMarkerPosition);
    marker1 = res1.marker;
    const res2 = olSelectLonLat("map2", updateMarkerPosition2);
    marker2 = res2.marker

    // Process URL parameters after markers are initialized
    processURLParams();
    
    // Bootstrap tab event listeners - update URL when tabs change (clean parameters)
    document.getElementById('bypoint-tab').addEventListener('shown.bs.tab', () => {
        setModeParams('bypoint');
    });
    
    document.getElementById('byugc-tab').addEventListener('shown.bs.tab', () => {
        setModeParams('byugc');
    });
    
    document.getElementById('list-tab').addEventListener('shown.bs.tab', () => {
        setModeParams('list');
    });
}

// Use vanilla JS for DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}