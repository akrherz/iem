
// Modernized for Tabulator.js, Bootstrap 5, and vanilla JS
// Rule(s): Tabulator migration, jQuery removal, Bootstrap5 UI, code modernization


import { TabulatorFull as Tabulator } from "https://unpkg.com/tabulator-tables@6.3.1/dist/js/tabulator_esm.min.mjs";

window.addEventListener("DOMContentLoaded", () => {
    const btn = document.getElementById("makefancy");
    if (!btn) return;
    btn.addEventListener("click", () => {
        const tableElem = document.getElementById("thetable");
        if (!tableElem) return;
        // Manually extract columns and data from HTML table
        const columns = [];
        const data = [];
        const thead = tableElem.querySelector('thead');
        const tbody = tableElem.querySelector('tbody');
        if (!thead || !tbody) return;
        // Use the last row of thead for column titles
        const headerRows = thead.querySelectorAll('tr');
        const lastHeaderRow = headerRows[headerRows.length - 1];
        const ths = lastHeaderRow.querySelectorAll('th');
        ths.forEach((th, i) => {
            columns.push({
                title: th.textContent.trim(),
                field: `col${i}`,
                headerSort: false,
                ...(i === 0 ? { formatter: "html" } : {})
            });
        });
        // Extract data rows
        const trs = tbody.querySelectorAll('tr');
        trs.forEach(tr => {
            const tds = tr.querySelectorAll('td');
            const row = {};
            tds.forEach((td, i) => {
                // Preserve HTML for first column (date/station link)
                row[`col${i}`] = (i === 0) ? td.innerHTML.trim() : td.textContent.trim();
            });
            data.push(row);
        });
        // Create a new div to host Tabulator
        const tabDiv = document.createElement("div");
        tabDiv.id = "thetable-tabulator";
        tableElem.parentNode.replaceChild(tabDiv, tableElem);
        // Initialize Tabulator on the new div
        const tab = new Tabulator(tabDiv, {
            data,
            columns,
            layout: "fitDataStretch",
            responsiveLayout: true,
            movableColumns: true,
            height: "600px",
            headerSort: false,
            pagination: false,
            downloadConfig: {
                columnGroups: false,
                rowGroups: false,
            },
            columnDefaults: {
                headerHozAlign: "center",
                vertAlign: "middle"
            }
        });
        // Add export buttons
        if (!document.getElementById("tab-export-btns")) {
            const exportDiv = document.createElement('div');
            exportDiv.id = 'tab-export-btns';
            exportDiv.className = 'my-2';
            exportDiv.innerHTML =
                '<button class="btn btn-sm btn-outline-primary me-2" id="tab-csv">Export CSV</button>' +
                '<button class="btn btn-sm btn-outline-secondary me-2" id="tab-xlsx">Export XLSX</button>' +
                '<button class="btn btn-sm btn-outline-success" id="tab-json">Export JSON</button>';
            tabDiv.parentNode.insertBefore(exportDiv, tabDiv);
            document.getElementById('tab-csv').onclick = () => tab.download('csv', 'cf6table.csv');
            document.getElementById('tab-xlsx').onclick = () => tab.download('xlsx', 'cf6table.xlsx');
            document.getElementById('tab-json').onclick = () => tab.download('json', 'cf6table.json');
        }
        btn.disabled = true;
        btn.textContent = "Table is Interactive";
    });
});
