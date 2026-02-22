import {TabulatorFull as Tabulator} from 'https://unpkg.com/tabulator-tables@6.3.1/dist/js/tabulator_esm.min.mjs';

// Network configurations
const networks = [
    ['AL_ASOS', 'Alabama ASOS/AWOS'],
    ['AL_DCP', 'Alabama DCP/HADS'],
    ['AK_ASOS', 'Alaska ASOS/AWOS'],
    ['AK_DCP', 'Alaska DCP/HADS'],
    ['AZ_ASOS', 'Arizona ASOS/AWOS'],
    ['AZ_DCP', 'Arizona DCP/HADS'],
    ['AR_ASOS', 'Arkansas ASOS/AWOS'],
    ['AR_DCP', 'Arkansas DCP/HADS'],
    ['CA_ASOS', 'California ASOS/AWOS'],
    ['CA_DCP', 'California DCP/HADS'],
    ['CO_ASOS', 'Colorado ASOS/AWOS'],
    ['CO_DCP', 'Colorado DCP/HADS'],
    ['CT_ASOS', 'Connecticut ASOS/AWOS'],
    ['CT_DCP', 'Connecticut DCP/HADS'],
    ['DE_ASOS', 'Delaware ASOS/AWOS'],
    ['DE_DCP', 'Delaware DCP/HADS'],
    ['FL_ASOS', 'Florida ASOS/AWOS'],
    ['FL_DCP', 'Florida DCP/HADS'],
    ['GA_ASOS', 'Georgia ASOS/AWOS'],
    ['GA_DCP', 'Georgia DCP/HADS'],
    ['HI_ASOS', 'Hawaii ASOS/AWOS'],
    ['HI_DCP', 'Hawaii DCP/HADS'],
    ['ID_ASOS', 'Idaho ASOS/AWOS'],
    ['ID_DCP', 'Idaho DCP/HADS'],
    ['IL_ASOS', 'Illinois ASOS/AWOS'],
    ['IL_DCP', 'Illinois DCP/HADS'],
    ['IN_ASOS', 'Indiana ASOS/AWOS'],
    ['IN_DCP', 'Indiana DCP/HADS'],
    ['IA_ASOS', 'Iowa ASOS/AWOS'],
    ['IA_DCP', 'Iowa DCP/HADS'],
    ['KS_ASOS', 'Kansas ASOS/AWOS'],
    ['KS_DCP', 'Kansas DCP/HADS'],
    ['KY_ASOS', 'Kentucky ASOS/AWOS'],
    ['KY_DCP', 'Kentucky DCP/HADS'],
    ['LA_ASOS', 'Louisiana ASOS/AWOS'],
    ['LA_DCP', 'Louisiana DCP/HADS'],
    ['MA_ASOS', 'Massachusetts ASOS/AWOS'],
    ['MA_DCP', 'Massachusetts DCP/HADS'],
    ['MD_ASOS', 'Maryland ASOS/AWOS'],
    ['MD_DCP', 'Maryland DCP/HADS'],
    ['ME_ASOS', 'Maine ASOS/AWOS'],
    ['ME_DCP', 'Maine DCP/HADS'],
    ['MI_ASOS', 'Michigan ASOS/AWOS'],
    ['MI_DCP', 'Michigan DCP/HADS'],
    ['MN_ASOS', 'Minnesota ASOS/AWOS'],
    ['MN_DCP', 'Minnesota DCP/HADS'],
    ['MO_ASOS', 'Missouri ASOS/AWOS'],
    ['MO_DCP', 'Missouri DCP/HADS'],
    ['MS_ASOS', 'Mississippi ASOS/AWOS'],
    ['MS_DCP', 'Mississippi DCP/HADS'],
    ['MT_ASOS', 'Montana ASOS/AWOS'],
    ['MT_DCP', 'Montana DCP/HADS'],
    ['NC_ASOS', 'North Carolina ASOS/AWOS'],
    ['NC_DCP', 'North Carolina DCP/HADS'],
    ['NE_ASOS', 'Nebraska ASOS/AWOS'],
    ['NE_DCP', 'Nebraska DCP/HADS'],
    ['NV_ASOS', 'Nevada ASOS/AWOS'],
    ['NV_DCP', 'Nevada DCP/HADS'],
    ['NH_ASOS', 'New Hampshire ASOS/AWOS'],
    ['NH_DCP', 'New Hampshire DCP/HADS'],
    ['NJ_ASOS', 'New Jersey ASOS/AWOS'],
    ['NJ_DCP', 'New Jersey DCP/HADS'],
    ['NM_ASOS', 'New Mexico ASOS/AWOS'],
    ['NM_DCP', 'New Mexico DCP/HADS'],
    ['NY_ASOS', 'New York ASOS/AWOS'],
    ['NY_DCP', 'New York DCP/HADS'],
    ['ND_ASOS', 'North Dakota ASOS/AWOS'],
    ['ND_DCP', 'North Dakota DCP/HADS'],
    ['OH_ASOS', 'Ohio ASOS/AWOS'],
    ['OH_DCP', 'Ohio DCP/HADS'],
    ['OK_ASOS', 'Oklahoma ASOS/AWOS'],
    ['OK_DCP', 'Oklahoma DCP/HADS'],
    ['OR_ASOS', 'Oregon ASOS/AWOS'],
    ['OR_DCP', 'Oregon DCP/HADS'],
    ['PA_ASOS', 'Pennsylvania ASOS/AWOS'],
    ['PA_DCP', 'Pennsylvania DCP/HADS'],
    ['PR_ASOS', 'Puerto Rico ASOS/AWOS'],
    ['PR_DCP', 'Puerto Rico DCP/HADS'],
    ['RI_ASOS', 'Rhode Island ASOS/AWOS'],
    ['RI_DCP', 'Rhode Island DCP/HADS'],
    ['SC_ASOS', 'South Carolina ASOS/AWOS'],
    ['SC_DCP', 'South Carolina DCP/HADS'],
    ['SD_ASOS', 'South Dakota ASOS/AWOS'],
    ['SD_DCP', 'South Dakota DCP/HADS'],
    ['TN_ASOS', 'Tennessee ASOS/AWOS'],
    ['TN_DCP', 'Tennessee DCP/HADS'],
    ['TX_ASOS', 'Texas ASOS/AWOS'],
    ['TX_DCP', 'Texas DCP/HADS'],
    ['UT_ASOS', 'Utah ASOS/AWOS'],
    ['UT_DCP', 'Utah DCP/HADS'],
    ['VA_ASOS', 'Virginia ASOS/AWOS'],
    ['VA_DCP', 'Virginia DCP/HADS'],
    ['VT_ASOS', 'Vermont ASOS/AWOS'],
    ['VT_DCP', 'Vermont DCP/HADS'],
    ['VI_ASOS', 'Virgin Islands ASOS/AWOS'],
    ['VI_DCP', 'Virgin Islands DCP/HADS'],
    ['WA_ASOS', 'Washington ASOS/AWOS'],
    ['WA_DCP', 'Washington DCP/HADS'],
    ['WI_ASOS', 'Wisconsin ASOS/AWOS'],
    ['WI_DCP', 'Wisconsin DCP/HADS'],
    ['WV_ASOS', 'West Virginia ASOS/AWOS'],
    ['WV_DCP', 'West Virginia DCP/HADS'],
    ['WY_ASOS', 'Wyoming ASOS/AWOS'],
    ['WY_DCP', 'Wyoming DCP/HADS']
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
