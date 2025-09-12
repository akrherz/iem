import {TabulatorFull as Tabulator} from 'https://unpkg.com/tabulator-tables@6.3.1/dist/js/tabulator_esm.min.mjs';

// Network configurations
const networks = [
    ['IA_ASOS', 'Iowa ASOS/AWOS'],
    ['AL_ASOS', 'Alabama ASOS/AWOS'],
    ['AK_ASOS', 'Alaska ASOS/AWOS'],
    ['AZ_ASOS', 'Arizona ASOS/AWOS'],
    ['AR_ASOS', 'Arkansas ASOS/AWOS'],
    ['CA_ASOS', 'California ASOS/AWOS'],
    ['CO_ASOS', 'Colorado ASOS/AWOS'],
    ['CT_ASOS', 'Connecticut ASOS/AWOS'],
    ['DE_ASOS', 'Delaware ASOS/AWOS'],
    ['FL_ASOS', 'Florida ASOS/AWOS'],
    ['GA_ASOS', 'Georgia ASOS/AWOS'],
    ['HI_ASOS', 'Hawaii ASOS/AWOS'],
    ['ID_ASOS', 'Idaho ASOS/AWOS'],
    ['IL_ASOS', 'Illinois ASOS/AWOS'],
    ['IN_ASOS', 'Indiana ASOS/AWOS'],
    ['KS_ASOS', 'Kansas ASOS/AWOS'],
    ['KY_ASOS', 'Kentucky ASOS/AWOS'],
    ['LA_ASOS', 'Louisiana ASOS/AWOS'],
    ['MA_ASOS', 'Massachusetts ASOS/AWOS'],
    ['MD_ASOS', 'Maryland ASOS/AWOS'],
    ['ME_ASOS', 'Maine ASOS/AWOS'],
    ['MI_ASOS', 'Michigan ASOS/AWOS'],
    ['MN_ASOS', 'Minnesota ASOS/AWOS'],
    ['MO_ASOS', 'Missouri ASOS/AWOS'],
    ['MS_ASOS', 'Mississippi ASOS/AWOS'],
    ['MT_ASOS', 'Montana ASOS/AWOS'],
    ['NC_ASOS', 'North Carolina ASOS/AWOS'],
    ['NE_ASOS', 'Nebraska ASOS/AWOS'],
    ['NV_ASOS', 'Nevada ASOS/AWOS'],
    ['NH_ASOS', 'New Hampshire ASOS/AWOS'],
    ['NJ_ASOS', 'New Jersey ASOS/AWOS'],
    ['NM_ASOS', 'New Mexico ASOS/AWOS'],
    ['NY_ASOS', 'New York ASOS/AWOS'],
    ['ND_ASOS', 'North Dakota ASOS/AWOS'],
    ['OH_ASOS', 'Ohio ASOS/AWOS'],
    ['OK_ASOS', 'Oklahoma ASOS/AWOS'],
    ['OR_ASOS', 'Oregon ASOS/AWOS'],
    ['PA_ASOS', 'Pennsylvania ASOS/AWOS'],
    ['PR_ASOS', 'Puerto Rico ASOS/AWOS'],
    ['RI_ASOS', 'Rhode Island ASOS/AWOS'],
    ['SC_ASOS', 'South Carolina ASOS/AWOS'],
    ['SD_ASOS', 'South Dakota ASOS/AWOS'],
    ['TN_ASOS', 'Tennessee ASOS/AWOS'],
    ['TX_ASOS', 'Texas ASOS/AWOS'],
    ['UT_ASOS', 'Utah ASOS/AWOS'],
    ['VA_ASOS', 'Virginia ASOS/AWOS'],
    ['VT_ASOS', 'Vermont ASOS/AWOS'],
    ['VI_ASOS', 'Virgin Islands ASOS/AWOS'],
    ['WA_ASOS', 'Washington ASOS/AWOS'],
    ['WI_ASOS', 'Wisconsin ASOS/AWOS'],
    ['WV_ASOS', 'West Virginia ASOS/AWOS'],
    ['WY_ASOS', 'Wyoming ASOS/AWOS']
];

// Application state
let precipTable = null;
let autoRefreshInterval = null;
let currentNetwork = '';

// Common Tabulator configuration
const commonConfig = {
    layout: "fitDataStretch",
    pagination: "local",
    paginationSize: 50,
    paginationSizeSelector: [25, 50, 100, true],
    movableColumns: true,
    resizableColumns: true,
    sortMode: "local",
    filterMode: "local",
    responsiveLayout: false, // Disable responsive hiding - use horizontal scroll instead
    tooltips: true,
    clipboard: true,
    clipboardCopyHeader: true,
    height: "70vh",
    placeholder: "No precipitation data available"
};

// Format precipitation values (handle trace amounts)
function formatPrecipitation(cell) {
    const value = cell.getValue();
    if (value > 0 && value < 0.009) return "T";
    if (value === 0 || value === null || value === undefined) return "0.00";
    return parseFloat(value).toFixed(2);
}

// Time offset mapping for each precipitation field
const timeOffsets = {
    'pmidnight': 0,
    'p1': 1,
    'p3': 3,
    'p6': 6,
    'p12': 12,
    'p24': 24,
    'p48': 48,
    'p72': 72,
    'p168': 168,
    'p720': 720,
    'p2160': 2160,
    'p8760': 8760
};

// Column definitions for precipitation data
function getPrecipitationColumns() {
    return [
        {title: "Station ID", field: "id", frozen: true, width: 80, sorter: "string"},
        {title: "Station Name", field: "name", frozen: true, minWidth: 200, sorter: "string"},
        {title: "Midnight", field: "pmidnight", width: 120, sorter: "number", formatter: formatPrecipitation, 
         headerTooltip: "Precipitation since midnight Central Time"},
        {title: "1 Hour", field: "p1", width: 120, sorter: "number", formatter: formatPrecipitation,
         headerTooltip: "Precipitation in the past 1 hour"},
        {title: "3 Hours", field: "p3", width: 120, sorter: "number", formatter: formatPrecipitation,
         headerTooltip: "Precipitation in the past 3 hours"},
        {title: "6 Hours", field: "p6", width: 120, sorter: "number", formatter: formatPrecipitation,
         headerTooltip: "Precipitation in the past 6 hours"},
        {title: "12 Hours", field: "p12", width: 120, sorter: "number", formatter: formatPrecipitation,
         headerTooltip: "Precipitation in the past 12 hours"},
        {title: "1 Day", field: "p24", width: 120, sorter: "number", formatter: formatPrecipitation,
         headerTooltip: "Precipitation in the past 24 hours"},
        {title: "2 Days", field: "p48", width: 120, sorter: "number", formatter: formatPrecipitation,
         headerTooltip: "Precipitation in the past 48 hours"},
        {title: "3 Days", field: "p72", width: 120, sorter: "number", formatter: formatPrecipitation,
         headerTooltip: "Precipitation in the past 72 hours"},
        {title: "1 Week", field: "p168", width: 120, sorter: "number", formatter: formatPrecipitation,
         headerTooltip: "Precipitation in the past week (168 hours)"},
        {title: "30 Days", field: "p720", width: 120, sorter: "number", formatter: formatPrecipitation,
         headerTooltip: "Precipitation in the past 30 days (720 hours)"},
        {title: "90 Days", field: "p2160", width: 120, sorter: "number", formatter: formatPrecipitation,
         headerTooltip: "Precipitation in the past 90 days (2160 hours)"},
        {title: "1 Year", field: "p8760", width: 120, sorter: "number", formatter: formatPrecipitation,
         headerTooltip: "Precipitation in the past year (8760 hours)"}
    ];
}

// Update URL parameters
function updateURL(network) {
    const url = new URL(window.location);
    url.searchParams.set('network', network);
    window.history.pushState({}, '', url);
}

// Update status message
function updateStatus(message, type = 'info') {
    const statusEl = document.getElementById('status-message');
    const alertEl = statusEl.parentElement;
    
    // Remove existing alert classes
    alertEl.className = alertEl.className.replace(/alert-\w+/g, '');
    alertEl.classList.add(`alert-${type}`);
    
    statusEl.textContent = message;
}

// Format time offset for display
function formatTimeOffset(hours) {
    if (hours < 24) return `${hours} Hour`;
    return `${hours / 24} Day`;
}

// Format date for display
function formatDisplayDate(date) {
    return new Intl.DateTimeFormat('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: 'numeric',
        hour12: true,
        timeZone: 'America/Chicago'
    }).format(date);
}

// Format date for column headers (shorter format)
function formatColumnDate(date) {
    return new Intl.DateTimeFormat('en-US', {
        month: 'numeric',
        day: 'numeric',
        hour: 'numeric',
        hour12: true,
        timeZone: 'America/Chicago'
    }).format(date);
}

// Update column headers with dynamic time ranges
function updateColumnHeaders(selectedDateTime) {
    if (!precipTable) return;
    
    const columns = precipTable.getColumnDefinitions();
    const updatedColumns = columns.map(col => {
        // Skip columns that don't have precipitation data
        if (!(col.field in timeOffsets)) return col;
        
        const tOffset = timeOffsets[col.field];
        let startDateTime = null;
        let endDateTime = null;
        
        if (tOffset === 0) {
            // Midnight column: from midnight to selected time
            startDateTime = new Date(selectedDateTime);
            startDateTime.setHours(0, 0, 0, 0);
            endDateTime = new Date(selectedDateTime);
        } else {
            // Other columns: from (selected time - offset) to selected time
            startDateTime = new Date(selectedDateTime.getTime() - (tOffset * 60 * 60 * 1000));
            endDateTime = new Date(selectedDateTime);
        }
        
        const startStr = formatColumnDate(startDateTime);
        const endStr = formatColumnDate(endDateTime);
        
        // Create multi-line header
        let headerText = '';
        if (tOffset === 0) {
            headerText = `Midnight<br/>${startStr}<br/>${endStr}`;
        } else {
            headerText = `${formatTimeOffset(tOffset)}<br/>${startStr}<br/>${endStr}`;
        }
        
        return {
            ...col,
            title: headerText,
            titleFormatter: "html" // Allow HTML in headers
        };
    });
    
    precipTable.setColumns(updatedColumns);
}

// Load precipitation data
async function loadPrecipitationData(network, datetime) {
    if (!network || !datetime) {
        updateStatus('Please select both network and date/time', 'warning');
        return;
    }

    try {
        updateStatus('Loading precipitation data...', 'info');
        
        // Convert local datetime to UTC and format for API (YmdHi format)
        // The datetime parameter is in local timezone, we need to convert to UTC
        // Always set minutes to 0 for the API call
        const utcYear = datetime.getUTCFullYear();
        const utcMonth = String(datetime.getUTCMonth() + 1).padStart(2, '0');
        const utcDay = String(datetime.getUTCDate()).padStart(2, '0');
        const utcHour = String(datetime.getUTCHours()).padStart(2, '0');
        const utcMinute = '00'; // Always use 00 minutes
        const timestamp = `${utcYear}${utcMonth}${utcDay}${utcHour}${utcMinute}`;
        
        const response = await fetch(`obhour-json.php?network=${network}&ts=${timestamp}`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (!data.precip || !Array.isArray(data.precip)) {
            throw new Error('Invalid data format received');
        }

        // Update table with new data
        precipTable.setData(data.precip);
        
        // Update dynamic column headers
        updateColumnHeaders(datetime);
        
        // Update table title and subtitle
        const displayDate = formatDisplayDate(datetime);
        document.getElementById('table-title').textContent = 'Accumulated Precipitation by Interval';
        document.getElementById('table-subtitle').textContent = `Valid at ${displayDate}`;
        
        // Show download buttons
        document.getElementById('download-buttons').classList.remove('d-none');
        
        updateStatus(`Loaded ${data.precip.length} stations for ${displayDate}`, 'success');
        
        // Store current state
        currentNetwork = network;
        
    } catch (error) {
        updateStatus(`Error loading data: ${error.message}`, 'danger');
    }
}

// Initialize form controls
function initializeControls() {
    // Populate network selector
    const networkSelect = document.getElementById('network-select');
    networks.forEach(([value, label]) => {
        const option = document.createElement('option');
        option.value = value;
        option.textContent = label;
        networkSelect.appendChild(option);
    });
    
    // Set default network from URL or use Iowa
    const urlParams = new URLSearchParams(window.location.search);
    const defaultNetwork = urlParams.get('network') || 'IA_ASOS';
    networkSelect.value = defaultNetwork;
    
    // Initialize date to today in local timezone
    const now = new Date();
    const dateSelect = document.getElementById('date-select');
    const localDateString = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
    dateSelect.value = localDateString;
    dateSelect.max = localDateString;
    dateSelect.min = '2008-01-01';
    
    // Populate time selector (24 hours)
    const timeSelect = document.getElementById('time-select');
    for (let hour = 0; hour < 24; hour++) {
        const option = document.createElement('option');
        const displayHour = hour === 0 ? 12 : (hour > 12 ? hour - 12 : hour);
        const ampm = hour < 12 ? 'AM' : 'PM';
        option.value = hour;
        option.textContent = `${displayHour} ${ampm}`;
        timeSelect.appendChild(option);
    }
    
    // Set current hour
    timeSelect.value = now.getHours();
}

// Setup event handlers
function setupEventHandlers() {
    // Form submission
    document.getElementById('precipitation-form').addEventListener('submit', (e) => {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const network = formData.get('network');
        const dateStr = formData.get('date');
        const timeStr = formData.get('time');
        
        if (!network || !dateStr || timeStr === null) {
            updateStatus('Please fill in all required fields', 'warning');
            return;
        }
        
        // Create datetime object using explicit date components to avoid timezone issues
        const dateParts = dateStr.split('-');
        const year = parseInt(dateParts[0]);
        const month = parseInt(dateParts[1]) - 1; // JavaScript months are 0-based
        const day = parseInt(dateParts[2]);
        const datetime = new Date(year, month, day, parseInt(timeStr), 0, 0, 0);
        
        updateURL(network);
        loadPrecipitationData(network, datetime);
    });
    
    // Auto refresh toggle
    document.getElementById('auto-refresh').addEventListener('change', (e) => {
        if (e.target.checked) {
            startAutoRefresh();
        } else {
            stopAutoRefresh();
        }
    });
    
    // Download buttons (when table is loaded)
    document.getElementById('download-csv').addEventListener('click', () => {
        if (precipTable) {
            precipTable.download("csv", "precipitation-data.csv");
        }
    });
    
    document.getElementById('copy-clipboard').addEventListener('click', () => {
        if (precipTable) {
            precipTable.copyToClipboard("active");
        }
    });
}

// Auto refresh functionality
function startAutoRefresh() {
    stopAutoRefresh(); // Clear any existing interval
    
    autoRefreshInterval = setInterval(() => {
        // Update to current time in local timezone
        const now = new Date();
        // Set minutes and seconds to 0 for consistency
        now.setMinutes(0, 0, 0);
        
        const localDateString = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
        document.getElementById('date-select').value = localDateString;
        document.getElementById('time-select').value = now.getHours();
        
        // Reload data if we have a current network
        if (currentNetwork) {
            loadPrecipitationData(currentNetwork, now);
        }
    }, 20 * 60 * 1000); // 20 minutes
    
    updateStatus('Auto-refresh enabled (every 20 minutes)', 'info');
}

function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
    }
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    // Initialize Tabulator table
    precipTable = new Tabulator("#precipitation-table", {
        ...commonConfig,
        columns: getPrecipitationColumns(),
        initialSort: [
            {column: "name", dir: "asc"}
        ]
    });
    
    // Initialize form controls and event handlers
    initializeControls();
    setupEventHandlers();
    
    // Load initial data if network is specified in URL
    const urlParams = new URLSearchParams(window.location.search);
    const initialNetwork = urlParams.get('network');
    if (initialNetwork) {
        // Auto-load with current time, minutes set to 0
        const now = new Date();
        now.setMinutes(0, 0, 0);
        loadPrecipitationData(initialNetwork, now);
    }
});
