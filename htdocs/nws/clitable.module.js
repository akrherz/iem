import { TabulatorFull as Tabulator } from 'https://unpkg.com/tabulator-tables@6.3.1/dist/js/tabulator_esm.min.js';

function makeTableInteractive() {
    const tableElem = document.getElementById('thetable');
    if (!tableElem) return;
    // Extract headers
    const headers = Array.from(tableElem.querySelectorAll('thead th')).map(th => th.innerText.trim());
    // Extract rows
    const rows = Array.from(tableElem.querySelectorAll('tbody tr')).map(tr => {
        return Array.from(tr.children).map(td => td.innerHTML.trim());
    });
    // Build Tabulator columns
    // Rule: Tabulator.js rendering, HTML column handling, fixed column
    // The first column is Date/Station and contains HTML links, so use the html formatter for col0 and freeze it
    const columns = headers.map((title, i) => {
        if (i === 0) {
            return { title, field: `col${i}`, formatter: 'html', frozen: true };
        }
        return { title, field: `col${i}` };
    });
    // Build Tabulator data
    const data = rows.map(row => {
        const obj = {};
        row.forEach((cell, i) => { obj[`col${i}`] = cell; });
        return obj;
    });
    // Replace table with Tabulator
    const tabDiv = document.createElement('div');
    tabDiv.id = 'tabulator-table';
    tableElem.parentNode.replaceChild(tabDiv, tableElem);
    // Rule: Tabulator.js rendering, fixed column, horizontal scroll
    // Use 'fitData' layout, set width for first column, and minWidth for others
    // This is the most reliable for frozen columns and horizontal scroll in Tabulator
    columns.forEach((col, i) => {
        if (i === 0) {
            col.width = 170;
        } else {
            col.minWidth = 120;
        }
    });
    // Do NOT set a fixed width on tabDiv. Let Tabulator manage all scrolling and frozen columns natively.
    const table = new Tabulator(tabDiv, {
        data,
        columns,
        layout: 'fitData',
        responsiveLayout: 'hide',
        height: '70vh',
        placeholder: 'No data found',
        movableColumns: true,
        autoColumns: false,
        columnDefaults: { resizable: true },
    });
    addExportButtons(table);
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
    document.getElementById('clitable-csv').onclick = () => table.download('csv', 'climate_table.csv');
    document.getElementById('clitable-xlsx').onclick = () => table.download('xlsx', 'climate_table.xlsx', { sheetName: 'Climate' });
}

window.addEventListener('DOMContentLoaded', () => {
    const makeFancyBtn = document.getElementById('makefancy');
    if (makeFancyBtn) {
        makeFancyBtn.addEventListener('click', makeTableInteractive);
    }
    // Optionally, auto-activate Tabulator if desired
    // makeTableInteractive();
    const makeRecordsBtn = document.getElementById('makerecords');
    if (makeRecordsBtn) {
        makeRecordsBtn.addEventListener('click', (event) => {
            const btn = event.currentTarget;
            const val = btn.getAttribute('data-toggle');
            const tableRows = document.querySelectorAll('#thetable [data-record="0"]');
            if (val === '0') {
                tableRows.forEach(row => { row.style.display = 'none'; });
                document.getElementById('makerecordslabel').textContent = 'Show All Rows';
                btn.setAttribute('data-toggle', '1');
            } else {
                document.getElementById('makerecordslabel').textContent = 'Show Rows with Records';
                btn.setAttribute('data-toggle', '0');
                document.querySelectorAll('#thetable tr').forEach(row => { row.style.display = ''; });
            }
        });
    }
});
