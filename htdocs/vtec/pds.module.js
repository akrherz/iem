// Tabulator-based PDS (Particularly Dangerous Situation) Watch/Warning Listing
// Replaces jQuery DataTables implementation with modern Tabulator
import {TabulatorFull as Tabulator} from 'https://unpkg.com/tabulator-tables@6.3.1/dist/js/tabulator_esm.min.mjs';

// Application state
let pdsTable = null;
let originalData = [];
let statusEl = null;

// Common Tabulator configuration for PDS table
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
    placeholder: "No PDS events available",
    initialSort: [
        {column: "year", dir: "desc"},
        {column: "issue", dir: "desc"}
    ]
};

// Column definitions for PDS data
function getPDSColumns() {
    return [
        {
            title: "Year", 
            field: "year", 
            width: 80, 
            sorter: "number",
            headerFilter: "number",
            headerFilterPlaceholder: "Filter year..."
        },
        {
            title: "WFO", 
            field: "wfo", 
            width: 80, 
            sorter: "string",
            headerFilter: "input",
            headerFilterPlaceholder: "Filter WFO..."
        },
        {
            title: "State(s)", 
            field: "states", 
            width: 100, 
            sorter: "string",
            headerFilter: "input",
            headerFilterPlaceholder: "Filter states..."
        },
        {
            title: "Event ID", 
            field: "eventid", 
            width: 100, 
            sorter: "string",
            formatter: "link",
            formatterParams: {
                urlField: "uri",
                target: "_blank"
            },
            headerFilter: "input",
            headerFilterPlaceholder: "Filter event ID..."
        },
        {
            title: "PH", 
            field: "phenomena", 
            width: 60, 
            sorter: "string",
            headerFilter: "input",
            headerFilterPlaceholder: "PH..."
        },
        {
            title: "SIG", 
            field: "significance", 
            width: 60, 
            sorter: "string",
            headerFilter: "input",
            headerFilterPlaceholder: "SIG..."
        },
        {
            title: "Event", 
            field: "event", 
            minWidth: 200, 
            sorter: "string",
            headerFilter: "input",
            headerFilterPlaceholder: "Filter event type..."
        },
        {
            title: "Issue Time", 
            field: "issue", 
            width: 180, 
            sorter: "string",
            headerFilter: "input",
            headerFilterPlaceholder: "Filter issue time..."
        },
        {
            title: "Expire Time", 
            field: "expire", 
            width: 180, 
            sorter: "string",
            headerFilter: "input",
            headerFilterPlaceholder: "Filter expire time..."
        }
    ];
}

// Load and process PDS data from the existing table
function loadTableData() {
    const tableElement = document.querySelector('#original-table table');
    if (!tableElement) {
        return [];
    }

    const rows = tableElement.querySelectorAll('tbody tr');
    const data = [];

    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 9) {
            // Extract event ID and URI from the link
            const linkElement = cells[3].querySelector('a');
            const eventid = linkElement ? linkElement.textContent.trim() : cells[3].textContent.trim();
            const uri = linkElement ? linkElement.href : '';

            data.push({
                year: parseInt(cells[0].textContent.trim()),
                wfo: cells[1].textContent.trim(),
                states: cells[2].textContent.trim(),
                eventid,
                uri,
                phenomena: cells[4].textContent.trim(),
                significance: cells[5].textContent.trim(),
                event: cells[6].textContent.trim(),
                issue: cells[7].textContent.trim(),
                expire: cells[8].textContent.trim()
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
    pdsTable = new Tabulator("#pds-tabulator-table", {
        ...commonConfig,
        columns: getPDSColumns(),
        data: originalData
    });

    // Show the new table and controls
    const container = document.getElementById('tabulator-container');
    container.classList.remove('d-none');
    const controls = document.getElementById('table-controls');
    controls.classList.remove('d-none');
    controls.removeAttribute('aria-hidden');
    if (statusEl) statusEl.textContent = 'Interactive table loaded. Use column headers to sort and filter inputs to refine results.';
    
    // Hide the original table and button
    const original = document.getElementById('original-table');
    original.style.display = 'none';
    const btn = document.getElementById('makefancy');
    btn.style.display = 'none';
    btn.setAttribute('aria-expanded', 'true');
}

// Setup table control event handlers
function setupControls() {
    // Download CSV button
    document.getElementById('download-csv').addEventListener('click', () => {
        if (pdsTable) {
            pdsTable.download("csv", "pds-events.csv");
        }
    });

    // Download JSON button
    document.getElementById('download-json').addEventListener('click', () => {
        if (pdsTable) {
            pdsTable.download("json", "pds-events.json");
        }
    });

    // Copy to clipboard button
    document.getElementById('copy-clipboard').addEventListener('click', () => {
        if (pdsTable) {
            pdsTable.copyToClipboard("active");
        }
    });

    // Clear all filters button
    document.getElementById('clear-filters').addEventListener('click', () => {
        if (pdsTable) {
            pdsTable.clearHeaderFilter();
        }
    });
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    statusEl = document.getElementById('pds-status');
    // Setup the "Make Table Interactive" button
    const makeFancyButton = document.getElementById('makefancy');
    if (makeFancyButton) {
        makeFancyButton.addEventListener('click', () => {
            if (statusEl) statusEl.textContent = 'Initializing interactive table…';
            initializeTable();
        });
    }

    // Setup table controls
    setupControls();
});
