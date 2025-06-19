// Tabulator-based interactive tables for NWS Warning Tags
// Replaces ExtJS implementation with modern Tabulator
import {TabulatorFull as Tabulator} from 'https://unpkg.com/tabulator-tables@6.3.1/dist/js/tabulator_esm.min.mjs';

// Common Tabulator configuration
const commonConfig = {
    layout: "fitColumns",
    pagination: "local",
    paginationSize: 25,
    paginationSizeSelector: [10, 25, 50, 100, true],
    movableColumns: true,
    resizableColumns: true,
    sortMode: "local",
    filterMode: "local",
    responsiveLayout: "hide",
    tooltips: true,
    clipboard: true,
    clipboardCopyHeader: true,
    htmlOutputConfig: {
        columnHeaders: true,
        columnGroups: false,
        rowGroups: false,
        columnCalcs: false,
        dataTree: false
    },
    downloadConfig: {
        columnHeaders: true,
        columnGroups: false,
        rowGroups: false,
        columnCalcs: false,
        dataTree: false
    }
};

// Custom formatter for HTML content
function htmlFormatter(cell) {
    return cell.getValue();
}

// Extract data from HTML table
function extractTableData(table) {
    const data = [];
    const headers = [];
    
    // Get headers
    const headerCells = table.querySelectorAll('thead th');
    headerCells.forEach(cell => {
        headers.push(cell.textContent.trim());
    });
    
    // Get data rows
    const rows = table.querySelectorAll('tbody tr');
    rows.forEach(row => {
        const rowData = {};
        const cells = row.querySelectorAll('td');
        cells.forEach((cell, index) => {
            if (index < headers.length) {
                rowData[headers[index]] = cell.innerHTML; // Use innerHTML to preserve links and formatting
            }
        });
        data.push(rowData);
    });
    
    return data;
}

function setupTableButton(buttonId, tableId, columns) {
    const button = document.getElementById(buttonId);
    if (!button) return;

    button.addEventListener('click', () => {
        button.disabled = true;
        button.innerHTML = '<i class="bi bi-hourglass-split"></i> Creating Interactive Table...';
        
        // Extract data from the existing HTML table
        const htmlTable = document.getElementById(tableId);
        const data = extractTableData(htmlTable);
        
        // Hide the original table
        htmlTable.style.display = 'none';
        
        // Create a new container for Tabulator
        const tabulatorContainer = document.createElement('div');
        tabulatorContainer.id = `${tableId}-tabulator`;
        htmlTable.parentNode.insertBefore(tabulatorContainer, htmlTable.nextSibling);
        
        // Create Tabulator instance with the extracted data
        const table = new Tabulator(`#${tableId}-tabulator`, {
            ...commonConfig,
            data,
            columns,
            autoColumns: false,
            initialSort: [
                {column: "Eventid", dir: "desc"}
            ]
        });

        // Add download buttons after table creation
        table.on("tableBuilt", () => {
            addDownloadButtons(buttonId, table);
            button.style.display = 'none'; // Hide the original button
        });
    }, { once: true }); // Only allow one click
}

function addDownloadButtons(originalButtonId, table) {
    const originalButton = document.getElementById(originalButtonId);
    const buttonContainer = document.createElement('div');
    buttonContainer.className = 'mb-2';
    buttonContainer.innerHTML = `
        <div class="btn-group" role="group">
            <button type="button" class="btn btn-success btn-sm download-csv">
                <i class="bi bi-file-earmark-spreadsheet"></i> Download CSV
            </button>
            <button type="button" class="btn btn-secondary btn-sm copy-clipboard">
                <i class="bi bi-clipboard"></i> Copy to Clipboard
            </button>
        </div>
    `;
    
    originalButton.parentNode.insertBefore(buttonContainer, originalButton);
    
    // Add event listeners for download buttons
    buttonContainer.querySelector('.download-csv').addEventListener('click', () => {
        table.download("csv", "warning-tags.csv");
    });
    
    buttonContainer.querySelector('.copy-clipboard').addEventListener('click', () => {
        table.copyToClipboard("active");
    });
}

// Column definitions for Severe Thunderstorm Warnings
function getSVRColumns() {
    return [
        {title: "Event ID", field: "Eventid", sorter: "string", minWidth: 100, formatter: htmlFormatter},
        {title: "Product", field: "Product", sorter: "string", minWidth: 80, formatter: htmlFormatter},
        {title: "WFO", field: "WFO", sorter: "string", width: 80},
        {title: "Start (UTC)", field: "Start (UTC)", sorter: "string", minWidth: 120},
        {title: "End", field: "End", sorter: "string", minWidth: 80},
        {title: "Counties/Parishes", field: "Counties/Parishes", sorter: "string", minWidth: 200},
        {title: "Wind Tag", field: "Wind Tag", sorter: "number", width: 100, hozAlign: "right"},
        {title: "Hail Tag", field: "Hail Tag", sorter: "number", width: 100, hozAlign: "right"},
        {title: "Tornado Tag", field: "Tornado Tag", sorter: "string", width: 120},
        {title: "Damage Tag", field: "Damage Tag", sorter: "string", width: 120},
        {title: "Storm Speed (kts)", field: "Storm Speed (kts)", sorter: "number", width: 130, hozAlign: "right"}
    ];
}

// Column definitions for Tornado Warnings  
function getTORColumns() {
    return getSVRColumns(); // Same structure as SVR
}

// Column definitions for Flash Flood Warnings
function getFFWColumns() {
    return [
        {title: "Event ID", field: "Eventid", sorter: "string", minWidth: 100, formatter: htmlFormatter},
        {title: "Product", field: "Product", sorter: "string", minWidth: 80, formatter: htmlFormatter},
        {title: "WFO", field: "WFO", sorter: "string", width: 80},
        {title: "Start (UTC)", field: "Start (UTC)", sorter: "string", minWidth: 120},
        {title: "End", field: "End", sorter: "string", minWidth: 80},
        {title: "Counties/Parishes", field: "Counties/Parishes", sorter: "string", minWidth: 200},
        {title: "Flash Flood Tag", field: "Flash Flood Tag", sorter: "string", width: 130},
        {title: "Damage Tag", field: "Damage Tag", sorter: "string", width: 120},
        {title: "Heavy Rain Tag", field: "Heavy Rain Tag", sorter: "string", width: 130},
        {title: "Dam Tag", field: "Dam Tag", sorter: "string", width: 100},
        {title: "Leeve Tag", field: "Leeve Tag", sorter: "string", width: 100}
    ];
}

// Column definitions for Marine Warnings
function getSMWColumns() {
    return [
        {title: "Event ID", field: "Eventid", sorter: "string", minWidth: 100, formatter: htmlFormatter},
        {title: "Product", field: "Product", sorter: "string", minWidth: 80, formatter: htmlFormatter},
        {title: "WFO", field: "WFO", sorter: "string", width: 80},
        {title: "Start (UTC)", field: "Start (UTC)", sorter: "string", minWidth: 120},
        {title: "End", field: "End", sorter: "string", minWidth: 80},
        {title: "Counties/Parishes", field: "Counties/Parishes", sorter: "string", minWidth: 200},
        {title: "Wind Tag", field: "Wind Tag", sorter: "number", width: 100, hozAlign: "right"},
        {title: "Hail Tag", field: "Hail Tag", sorter: "number", width: 100, hozAlign: "right"},
        {title: "Waterspout Tag", field: "Waterspout Tag", sorter: "string", width: 130},
        {title: "Storm Speed (kts)", field: "Storm Speed (kts)", sorter: "number", width: 130, hozAlign: "right"}
    ];
}

// Initialize the application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Setup button handlers for each warning type
    setupTableButton('create-grid-svr', 'svr-table', getSVRColumns());
    setupTableButton('create-grid-tor', 'tor-table', getTORColumns()); 
    setupTableButton('create-grid-ffw', 'ffw-table', getFFWColumns());
    setupTableButton('create-grid-smw', 'smw-table', getSMWColumns());
});
