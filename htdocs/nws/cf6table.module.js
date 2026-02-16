
// Modernized for Tabulator.js, Bootstrap 5, and vanilla JS
// Rule(s): Tabulator migration, jQuery removal, Bootstrap5 UI, code modernization


import { TabulatorFull as Tabulator } from "https://unpkg.com/tabulator-tables@6.3.1/dist/js/tabulator_esm.min.mjs";

window.addEventListener("DOMContentLoaded", () => {
    const btn = document.getElementById("makefancy");
    if (!btn) return;
    btn.addEventListener("click", () => {
        const tableElem = document.getElementById("thetable");
        if (!tableElem) return;
        // Extract columns from thead
        const thead = tableElem.querySelector('thead');
        const headerCells = thead.querySelectorAll('tr th');
        const columns = Array.from(headerCells).map((th, i) => {
            const col = { title: th.textContent.trim(), field: `col${i}` };
            // Only the first column (icon + date/station) is HTML
            if (i === 0) {
                col.headerSort = false;
                col.formatter = 'html';
                col.frozen = true;
            }
            return col;
        });
        // Extract data rows
        const tbody = tableElem.querySelector('tbody');
        if (!tbody) return;
        const trs = tbody.querySelectorAll('tr');
        const data = [];
        trs.forEach(tr => {
            const tds = tr.querySelectorAll('td');
            const row = {};
            for (let i = 0; i < columns.length; i++) {
                const td = tds[i];
                if (td) {
                    row[`col${i}`] = (i === 0) ? td.innerHTML.trim() : td.textContent.trim();
                } else {
                    row[`col${i}`] = "";
                }
            }
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
            movableColumns: true,
            height: "600px",
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
