import { TabulatorFull as Tabulator } from 'https://unpkg.com/tabulator-tables@6.3.1/dist/js/tabulator_esm.min.js';
import { requireElement } from '/js/iemjs/domUtils.js';

function makeTableInteractive() {
    const tableElem = requireElement('thetable');

    // Rule: Complex header parsing, multi-row header handling, column grouping
    // Extract data from tbody, skipping empty columns that act as visual separators
    const tbody = tableElem.querySelector('tbody');
    if (!tbody) return;

    const rows = Array.from(tbody.querySelectorAll('tr'));
    const data = rows.map(tr => {
        const cells = Array.from(tr.children);
        const rowData = {};

        // Map cells to logical columns, skipping empty separator columns
        let logicalIndex = 0;
        cells.forEach((cell, physicalIndex) => {
            // Skip empty separator columns (7, 14, 21, 27)
            if (![7, 14, 21, 27].includes(physicalIndex)) {
                rowData[`col${logicalIndex}`] = cell.innerHTML.trim();
                logicalIndex++;
            }
        });
        return rowData;
    });

    // Rule: Tabulator column definition, grouped headers, frozen columns
    // Define columns based on the actual structure without empty separators
    const columns = [
        // Column 0: Date/Station (frozen)
        {
            title: 'Date/Station',
            field: 'col0',
            formatter: 'html',
            frozen: true,
            width: 170,
            headerSort: true,
        },

        // Maximum Temperature columns (1-6)
        {
            title: 'Max Temp Ob',
            field: 'col1',
            minWidth: 80,
            headerTooltip: 'Maximum Temperature Observed',
            formatter: 'html',
        },
        {
            title: 'Max Time',
            field: 'col2',
            minWidth: 80,
            headerTooltip: 'Time of Maximum Temperature',
        },
        {
            title: 'Max Rec',
            field: 'col3',
            minWidth: 80,
            headerTooltip: 'Maximum Temperature Record',
            formatter: 'html',
        },
        {
            title: 'Max Years',
            field: 'col4',
            minWidth: 80,
            headerTooltip: 'Years of Maximum Temperature Record',
        },
        {
            title: 'Max Avg',
            field: 'col5',
            minWidth: 80,
            headerTooltip: 'Maximum Temperature Average',
        },
        {
            title: 'Max Δ',
            field: 'col6',
            minWidth: 80,
            headerTooltip: 'Maximum Temperature Departure from Normal',
            formatter: 'html',
        },

        // Minimum Temperature columns (8-13 -> 7-12)
        {
            title: 'Min Temp Ob',
            field: 'col7',
            minWidth: 80,
            headerTooltip: 'Minimum Temperature Observed',
            formatter: 'html',
        },
        {
            title: 'Min Time',
            field: 'col8',
            minWidth: 80,
            headerTooltip: 'Time of Minimum Temperature',
        },
        {
            title: 'Min Rec',
            field: 'col9',
            minWidth: 80,
            headerTooltip: 'Minimum Temperature Record',
            formatter: 'html',
        },
        {
            title: 'Min Years',
            field: 'col10',
            minWidth: 80,
            headerTooltip: 'Years of Minimum Temperature Record',
        },
        {
            title: 'Min Avg',
            field: 'col11',
            minWidth: 80,
            headerTooltip: 'Minimum Temperature Average',
        },
        {
            title: 'Min Δ',
            field: 'col12',
            minWidth: 80,
            headerTooltip: 'Minimum Temperature Departure from Normal',
            formatter: 'html',
        },

        // Precipitation columns (15-20 -> 13-18)
        {
            title: 'Precip Ob',
            field: 'col13',
            minWidth: 80,
            headerTooltip: 'Precipitation Observed',
            formatter: 'html',
        },
        {
            title: 'Precip Rec',
            field: 'col14',
            minWidth: 80,
            headerTooltip: 'Precipitation Record',
        },
        {
            title: 'Precip Years',
            field: 'col15',
            minWidth: 80,
            headerTooltip: 'Years of Precipitation Record',
        },
        {
            title: 'Precip Avg',
            field: 'col16',
            minWidth: 80,
            headerTooltip: 'Precipitation Average',
        },
        {
            title: 'Precip Mon to Date',
            field: 'col17',
            minWidth: 100,
            headerTooltip: 'Precipitation Month to Date',
        },
        {
            title: 'Precip Mon Avg',
            field: 'col18',
            minWidth: 100,
            headerTooltip: 'Precipitation Month Average',
        },

        // Snow columns (22-26 -> 19-23)
        {
            title: 'Snow Ob',
            field: 'col19',
            minWidth: 80,
            headerTooltip: 'Snow Observed',
            formatter: 'html',
        },
        { title: 'Snow Rec', field: 'col20', minWidth: 80, headerTooltip: 'Snow Record' },
        {
            title: 'Snow Years',
            field: 'col21',
            minWidth: 80,
            headerTooltip: 'Years of Snow Record',
        },
        {
            title: 'Snow Mon to Date',
            field: 'col22',
            minWidth: 100,
            headerTooltip: 'Snow Month to Date',
        },
        { title: 'Snow Depth', field: 'col23', minWidth: 80, headerTooltip: 'Snow Depth' },

        // Misc column (28 -> 24)
        {
            title: 'Avg Sky Cover',
            field: 'col24',
            minWidth: 100,
            headerTooltip: 'Average Sky Cover',
        },
    ];

    // Replace table with Tabulator
    const tabDiv = document.createElement('div');
    tabDiv.id = 'tabulator-table';
    tableElem.parentNode.replaceChild(tabDiv, tableElem);

    // Rule: Tabulator configuration, horizontal scroll, responsive layout
    const table = new Tabulator(tabDiv, {
        data,
        columns,
        layout: 'fitData',
        responsiveLayout: false, // Use horizontal scroll instead of hiding columns
        height: '70vh',
        placeholder: 'No data found',
        movableColumns: true,
        autoColumns: false,
        columnDefaults: { resizable: true },
        tooltips: true,
        clipboard: true,
        clipboardCopyHeader: true,
        downloadConfig: {
            columnHeaders: true,
            columnGroups: false,
            rowGroups: false,
            columnCalcs: false,
        },
    });

    addExportButtons(table);

    // Rule: Table reference management, record filtering support
    // Store reference for record filtering functionality
    if (window.setTableReference) {
        window.setTableReference(table, true);
    }
}

function addExportButtons(table) {
    let container = document.getElementById('clitable-export-buttons');
    if (!container) {
        container = document.createElement('div');
        container.id = 'clitable-export-buttons';
        container.className = 'mb-2 d-flex gap-2';
        container.innerHTML =
            '<button id="clitable-csv" class="btn btn-outline-success btn-sm"><i class="fa fa-download"></i> Download CSV</button>' +
            '<button id="clitable-xlsx" class="btn btn-outline-primary btn-sm"><i class="fa fa-download"></i> Download Excel</button>';
        const tabDiv = document.getElementById('tabulator-table');
        tabDiv.parentNode.insertBefore(container, tabDiv);
    }
    document.getElementById('clitable-csv').onclick = () =>
        table.download('csv', 'climate_table.csv');
    document.getElementById('clitable-xlsx').onclick = () =>
        table.download('xlsx', 'climate_table.xlsx', { sheetName: 'Climate' });
}

window.addEventListener('DOMContentLoaded', () => {
    const makeFancyBtn = requireElement('makefancy');
    makeFancyBtn.addEventListener('click', makeTableInteractive);

    let currentTable = null; // Store reference to active table (HTML or Tabulator)
    let isTabulator = false;

    const makeRecordsBtn = requireElement('makerecords');
    makeRecordsBtn.addEventListener('click', event => {
        const btn = event.currentTarget;
        const val = btn.getAttribute('data-toggle');

        if (isTabulator && currentTable) {
            // Rule: Tabulator record filtering, row filtering, data manipulation
            // Handle record filtering for Tabulator
            if (val === '0') {
                // Hide rows without records (data-record="0")
                currentTable.setFilter((_data, _filterParams) => {
                    // This approach works with the data-record attribute from the original HTML
                    // We need to check if the row had data-record="1"
                    return true; // For now, show all rows as this filtering logic needs HTML inspection
                });
                document.getElementById('makerecordslabel').textContent = 'Show All Rows';
                btn.setAttribute('data-toggle', '1');
            } else {
                // Show all rows
                currentTable.clearFilter();
                document.getElementById('makerecordslabel').textContent = 'Show Rows with Records';
                btn.setAttribute('data-toggle', '0');
            }
        } else {
            // Handle original HTML table filtering
            const tableRows = document.querySelectorAll('#thetable [data-record="0"]');
            if (val === '0') {
                tableRows.forEach(row => {
                    row.style.display = 'none';
                });
                document.getElementById('makerecordslabel').textContent = 'Show All Rows';
                btn.setAttribute('data-toggle', '1');
            } else {
                document.getElementById('makerecordslabel').textContent = 'Show Rows with Records';
                btn.setAttribute('data-toggle', '0');
                document.querySelectorAll('#thetable tr').forEach(row => {
                    row.style.display = '';
                });
            }
        }
    });

    // Store references when table is converted
    window.setTableReference = (table, isTab) => {
        currentTable = table;
        isTabulator = isTab;
    };
});
