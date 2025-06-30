// ES Module for NWS Six Hour Snowfall Reports
import { TabulatorFull as Tabulator } from 'https://unpkg.com/tabulator-tables@6.2.5/dist/js/tabulator_esm.min.js';

let _snowfallTable = null;

/**
 * Initialize the Tabulator table with snowfall data
 */
function initializeTable() {
    // Get existing table data from the DOM
    const tableData = [];
    const rows = document.querySelectorAll('#thetable tbody tr');
    
    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 8) {
            // Extract station link info
            const stationLink = cells[0].querySelector('a');
            const href = stationLink ? stationLink.href : '';
            const stationText = cells[0].textContent.trim();
            
            tableData.push({
                station: stationText,
                stationLink: href,
                name: cells[1].textContent.trim(),
                state: cells[2].textContent.trim(),
                wfo: cells[3].textContent.trim(),
                hour12: cells[4].textContent.trim(),
                hour18: cells[5].textContent.trim(),
                hour0: cells[6].textContent.trim(),
                hour6: cells[7].textContent.trim()
            });
        }
    });

    // Initialize Tabulator table
    _snowfallTable = new Tabulator("#snowfall-tabulator", {
        data: tableData,
        layout: "fitColumns",
        height: "70vh",
        pagination: "local",
        paginationSize: 50,
        paginationSizeSelector: [25, 50, 100, 200],
        movableColumns: true,
        resizableColumns: true,
        tooltips: true,
        placeholder: "No snowfall data available for the selected criteria",
        downloadConfig: {
            columnHeaders: true,
            columnGroups: false,
            rowGroups: false,
            columnCalcs: false,
            dataTree: false
        },
        columns: [
            {
                title: "Station/Network", 
                field: "station", 
                width: 150,
                formatter: (cell) => {
                    const data = cell.getRow().getData();
                    return data.stationLink ? 
                        `<a href="${data.stationLink}" target="_blank">${data.station}</a>` : 
                        data.station;
                },
                download: true
            },
            {title: "Name", field: "name", widthGrow: 2, download: true},
            {title: "State", field: "state", width: 80, download: true},
            {title: "WFO", field: "wfo", width: 80, download: true},
            {
                title: "12 UTC<br/>(6 AM CST)", 
                field: "hour12", 
                width: 120,
                hozAlign: "center",
                formatter: (cell) => {
                    const value = cell.getValue();
                    return value === 'T' ? '<span class="badge bg-info">T</span>' : value;
                },
                download: true
            },
            {
                title: "18 UTC<br/>(12 PM CST)", 
                field: "hour18", 
                width: 120,
                hozAlign: "center",
                formatter: (cell) => {
                    const value = cell.getValue();
                    return value === 'T' ? '<span class="badge bg-info">T</span>' : value;
                },
                download: true
            },
            {
                title: "0 UTC<br/>(6 PM CST)", 
                field: "hour0", 
                width: 120,
                hozAlign: "center",
                formatter: (cell) => {
                    const value = cell.getValue();
                    return value === 'T' ? '<span class="badge bg-info">T</span>' : value;
                },
                download: true
            },
            {
                title: "6 UTC<br/>(12 AM CST)", 
                field: "hour6", 
                width: 120,
                hozAlign: "center",
                formatter: (cell) => {
                    const value = cell.getValue();
                    return value === 'T' ? '<span class="badge bg-info">T</span>' : value;
                },
                download: true
            }
        ]
    });

    // Add download buttons
    const downloadContainer = document.createElement('div');
    downloadContainer.className = 'mb-3';
    downloadContainer.innerHTML = '<div class="btn-group" role="group" aria-label="Download options">' +
        '<button id="download-csv" class="btn btn-outline-success btn-sm">' +
        '<i class="fas fa-file-csv"></i> Download CSV</button>' +
        '<button id="download-xlsx" class="btn btn-outline-primary btn-sm">' +
        '<i class="fas fa-file-excel"></i> Download Excel</button>' +
        '<button id="download-json" class="btn btn-outline-info btn-sm">' +
        '<i class="fas fa-file-code"></i> Download JSON</button>' +
        '</div>';
    
    document.getElementById('tabulator-container').insertBefore(downloadContainer, document.getElementById('snowfall-tabulator'));

    // Add download event listeners
    document.getElementById('download-csv').addEventListener('click', () => {
        _snowfallTable.download("csv", "snowfall_6hour.csv");
    });

    document.getElementById('download-xlsx').addEventListener('click', () => {
        _snowfallTable.download("xlsx", "snowfall_6hour.xlsx", {sheetName: "Snowfall Data"});
    });

    document.getElementById('download-json').addEventListener('click', () => {
        _snowfallTable.download("json", "snowfall_6hour.json");
    });

    // Hide the original table and show the Tabulator container
    document.getElementById('thetable').style.display = 'none';
    document.getElementById('tabulator-container').style.display = 'block';
}

/**
 * Initialize the application
 */
function init() {
    // Replace the "Make Table Interactive" button functionality
    const makeFancyBtn = document.getElementById('makefancy');
    if (makeFancyBtn) {
        makeFancyBtn.addEventListener('click', () => {
            initializeTable();
            makeFancyBtn.style.display = 'none';
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', init);