import { TabulatorFull as Tabulator } from 'https://unpkg.com/tabulator-tables@6.3.1/dist/js/tabulator_esm.min.js';

// Helper: get URL parameters as object (safe, no prototype pollution)
function getUrlParams() {
    const params = Object.create(null); // no prototype
    for (const [key, value] of new URLSearchParams(window.location.search)) {
        if (Object.prototype.hasOwnProperty.call(params, key)) continue; // skip if already set
        params[key] = value;
    }
    return params;
}

// Fetch UGC data from API
async function fetchUgcs(params) {
    const apiParams = {};
    if (params.just_firewx) apiParams.just_firewx = params.just_firewx;
    if (params.w === 'wfo' && params.station) apiParams.wfo = params.station;
    if (params.w === 'state' && params.state) apiParams.state = params.state;
    const url = `/api/1/nws/ugcs.json?${new URLSearchParams(apiParams).toString()}`;
    const resp = await fetch(url);
    if (!resp.ok) throw new Error('Failed to fetch UGC data');
    return (await resp.json()).data;
}

function formatSearchCell(cell) {
    const state = cell.getValue().slice(0, 2); // Extract state from UGC
    return `<a href="/vtec/search.php?mode=byugc&state=${state}&ugc=${cell.getValue()}">Link</a>`;
}

// Render Tabulator table
function renderTable(data) {
    const table = new Tabulator('#ugcs-table', {
        data,
        layout: 'fitDataTable',
        responsiveLayout: 'hide',
        height: '70vh',
        columns: [
            { title: 'UGC', field: 'ugc', headerSort: true },
            { title: 'Warning Search', field: 'ugc', formatter: formatSearchCell, headerSort: false },
            { title: 'Name', field: 'name', headerSort: true },
            { title: 'WFO', field: 'wfo', headerSort: true },
        ],
        placeholder: 'No UGCs found for the selected criteria',
    });
    addExportButtons(table);
}

// Add export buttons (CSV, Excel)
function addExportButtons(table) {
    let container = document.getElementById('ugcs-export-buttons');
    if (!container) {
        container = document.createElement('div');
        container.id = 'ugcs-export-buttons';
        container.className = 'mb-2 d-flex gap-2';
        container.innerHTML =
            '<button id="ugcs-csv" class="btn btn-outline-success btn-sm"><i class="bi bi-download"></i> Download CSV</button>' +
            '<button id="ugcs-xlsx" class="btn btn-outline-primary btn-sm"><i class="bi bi-download"></i> Download Excel</button>';
        const tableDiv = document.getElementById('ugcs-table');
        tableDiv.parentNode.insertBefore(container, tableDiv);
    }
    document.getElementById('ugcs-csv').onclick = () => table.download('csv', 'ugcs.csv');
    document.getElementById('ugcs-xlsx').onclick = () => table.download('xlsx', 'ugcs.xlsx', { sheetName: 'UGCs' });
}

// On DOM ready
window.addEventListener('DOMContentLoaded', async () => {
    // Form: update URL on submit (so PHP reloads page with correct params)
    const form = document.querySelector('form[name="changeme"]');
    if (form) {
        form.addEventListener('submit', () => {
            // Let normal submit happen (PHP will reload page)
        });
    }
    // Only render table if placeholder exists
    const tableDiv = document.getElementById('ugcs-table');
    if (!tableDiv) return;
    // Fetch and render data
    try {
        const params = getUrlParams();
        const data = await fetchUgcs(params);
        renderTable(data);
    } catch (err) {
        tableDiv.innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
    }
});
