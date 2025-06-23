// Tabulator-based Monthly Precipitation Report
// Replaces ExtJS TableGrid implementation with modern Tabulator
import {TabulatorFull as Tabulator} from 'https://unpkg.com/tabulator-tables@6.3.1/dist/js/tabulator_esm.min.mjs';

// Application state
let precipTable = null;
let originalData = [];

// Common Tabulator configuration
const commonConfig = {
    layout: "fitDataStretch",
    pagination: "local",
    paginationSize: 25,
    paginationSizeSelector: [10, 25, 50, 100, true],
    movableColumns: true,
    resizableColumns: true,
    sortMode: "local",
    filterMode: "local",
    responsiveLayout: false, // Use horizontal scroll instead of hiding columns
    tooltips: true,
    clipboard: true,
    clipboardCopyHeader: true,
    height: "70vh",
    placeholder: "No precipitation data available",
    initialSort: [
        {column: "name", dir: "asc"}
    ]
};

// Format precipitation values (handle missing data)
function formatPrecipitation(cell) {
    const value = cell.getValue();
    if (value === null || value === undefined || value === "M") return "M";
    if (typeof value === 'string' && value.trim() === '') return "M";
    const numValue = parseFloat(value);
    if (isNaN(numValue)) return "M";
    return numValue.toFixed(2);
}

// Column definitions for monthly precipitation data
function getPrecipitationColumns() {
    return [
        {
            title: "Station ID", 
            field: "id", 
            frozen: true, 
            width: 100, 
            sorter: "string",
            formatter: "link",
            formatterParams: {
                urlPrefix: '/sites/site.php?station=',
                urlSuffix: () => `&network=${getNetworkFromURL()}`,
                target: "_blank"
            },
            headerFilter: "input",
            headerFilterPlaceholder: "Filter ID..."
        },
        {
            title: "Station Name", 
            field: "name", 
            frozen: true, 
            minWidth: 200, 
            sorter: "string",
            headerFilter: "input",
            headerFilterPlaceholder: "Filter name..."
        },
        {title: "Jan", field: "jan", width: 80, sorter: "number", formatter: formatPrecipitation, headerTooltip: "January precipitation (inches)"},
        {title: "Feb", field: "feb", width: 80, sorter: "number", formatter: formatPrecipitation, headerTooltip: "February precipitation (inches)"},
        {title: "Mar", field: "mar", width: 80, sorter: "number", formatter: formatPrecipitation, headerTooltip: "March precipitation (inches)"},
        {title: "Apr", field: "apr", width: 80, sorter: "number", formatter: formatPrecipitation, headerTooltip: "April precipitation (inches)"},
        {title: "May", field: "may", width: 80, sorter: "number", formatter: formatPrecipitation, headerTooltip: "May precipitation (inches)"},
        {title: "Jun", field: "jun", width: 80, sorter: "number", formatter: formatPrecipitation, headerTooltip: "June precipitation (inches)"},
        {title: "Jul", field: "jul", width: 80, sorter: "number", formatter: formatPrecipitation, headerTooltip: "July precipitation (inches)"},
        {title: "Aug", field: "aug", width: 80, sorter: "number", formatter: formatPrecipitation, headerTooltip: "August precipitation (inches)"},
        {title: "Sep", field: "sep", width: 80, sorter: "number", formatter: formatPrecipitation, headerTooltip: "September precipitation (inches)"},
        {title: "Oct", field: "oct", width: 80, sorter: "number", formatter: formatPrecipitation, headerTooltip: "October precipitation (inches)"},
        {title: "Nov", field: "nov", width: 80, sorter: "number", formatter: formatPrecipitation, headerTooltip: "November precipitation (inches)"},
        {title: "Dec", field: "dec", width: 80, sorter: "number", formatter: formatPrecipitation, headerTooltip: "December precipitation (inches)"},
        {
            title: "MJJA", 
            field: "mjja", 
            width: 90, 
            sorter: "number", 
            formatter: formatPrecipitation,
            headerTooltip: "May-June-July-August total (growing season)",
            cssClass: "highlight-summer"
        },
        {
            title: "Annual", 
            field: "annual", 
            width: 90, 
            sorter: "number", 
            formatter: formatPrecipitation,
            headerTooltip: "Annual total precipitation",
            cssClass: "highlight-annual"
        }
    ];
}

// Get network parameter from URL
function getNetworkFromURL() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('network') || 'IA_ASOS';
}

// Load and process precipitation data from the existing table
function loadTableData() {
    const tableElement = document.querySelector('#original-table');
    if (!tableElement) {
        return [];
    }

    const rows = tableElement.querySelectorAll('tbody tr');
    const data = [];

    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 16) {
            // Extract station ID from the link
            const linkElement = cells[0].querySelector('a');
            const stationId = linkElement ? linkElement.textContent.trim() : cells[0].textContent.trim();

            data.push({
                id: stationId,
                name: cells[1].textContent.trim(),
                jan: cells[2].textContent.trim(),
                feb: cells[3].textContent.trim(),
                mar: cells[4].textContent.trim(),
                apr: cells[5].textContent.trim(),
                may: cells[6].textContent.trim(),
                jun: cells[7].textContent.trim(),
                jul: cells[8].textContent.trim(),
                aug: cells[9].textContent.trim(),
                sep: cells[10].textContent.trim(),
                oct: cells[11].textContent.trim(),
                nov: cells[12].textContent.trim(),
                dec: cells[13].textContent.trim(),
                mjja: cells[14].textContent.trim(),
                annual: cells[15].textContent.trim()
            });
        }
    });

    return data;
}

// Initialize the Tabulator table
function initializeTable() {
    // Load data from existing table
    originalData = loadTableData();
    
    if (originalData.length === 0) {
        return;
    }

    // Create Tabulator table
    precipTable = new Tabulator("#precipitation-tabulator-table", {
        ...commonConfig,
        columns: getPrecipitationColumns(),
        data: originalData
    });

    // Show the new table and controls
    document.getElementById('tabulator-container').classList.remove('d-none');
    document.getElementById('table-controls').classList.remove('d-none');
    
    // Hide the original table and button
    document.getElementById('original-table').style.display = 'none';
    document.getElementById('create-grid').style.display = 'none';
}

// Setup table control event handlers
function setupControls() {
    // Download CSV button
    document.getElementById('download-csv').addEventListener('click', () => {
        if (precipTable) {
            const year = new URLSearchParams(window.location.search).get('year') || new Date().getFullYear();
            const network = getNetworkFromURL();
            precipTable.download("csv", `${network}_${year}_precipitation.csv`);
        }
    });

    // Download JSON button
    document.getElementById('download-json').addEventListener('click', () => {
        if (precipTable) {
            const year = new URLSearchParams(window.location.search).get('year') || new Date().getFullYear();
            const network = getNetworkFromURL();
            precipTable.download("json", `${network}_${year}_precipitation.json`);
        }
    });

    // Copy to clipboard button
    document.getElementById('copy-clipboard').addEventListener('click', () => {
        if (precipTable) {
            precipTable.copyToClipboard("active");
        }
    });

    // Clear all filters button
    document.getElementById('clear-filters').addEventListener('click', () => {
        if (precipTable) {
            precipTable.clearHeaderFilter();
        }
    });
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    // Setup the "Interactive Grid" button
    const createGridButton = document.getElementById('create-grid');
    if (createGridButton) {
        createGridButton.addEventListener('click', () => {
            initializeTable();
        });
    }

    // Setup table controls
    setupControls();
});