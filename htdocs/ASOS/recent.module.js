
let report = 'snowdepth';

/**
 * Fetch recent interesting METAR reports and populate the table.
 * Exposed for potential reuse (e.g. manual refresh button later).
 */
const buildRowHTML = (feat) => [
    '<tr>',
    `<td>${feat.properties.station}</td>`,
    `<td>${feat.properties.network}</td>`,
    `<td>${feat.properties.valid}</td>`,
    `<td>${feat.properties.value}</td>`,
    `<td>${feat.properties.metar}</td>`,
    '</tr>'
].join('');

const updateStatus = (live, message) => { if (live) live.textContent = message; };

export const fetchData = async () => {
    const tableBody = document.querySelector('#datatable tbody');
    if (!tableBody) return;
    const live = document.getElementById('recent-status');

    tableBody.innerHTML = '<tr><th colspan="5">Querying server, one moment</th></tr>';
    updateStatus(live, 'Loading recent METAR reports…');
    try {
        const resp = await fetch(`/geojson/recent_metar.py?q=${encodeURIComponent(report)}`);
        if (!resp.ok) throw new Error(`${resp.status} ${resp.statusText}`);
        const j = await resp.json();
        tableBody.innerHTML = '';
        j.features.forEach((feat) => tableBody.insertAdjacentHTML('beforeend', buildRowHTML(feat)));
        if (j.features.length === 0) {
            tableBody.innerHTML = '<tr><th colspan="5">No results were found, sorry!</th></tr>';
            updateStatus(live, 'No recent METAR reports found for selected type.');
            return;
        }
        updateStatus(live, `${j.features.length} recent METAR report${j.features.length === 1 ? '' : 's'} loaded.`);
    } catch (error) {
        tableBody.innerHTML = `<tr><th colspan="5">Error loading data ${error.message}</th></tr>`;
        updateStatus(live, `Error loading data: ${error.message}`);
    }
};

/** Get current report type. */
export const getReport = () => report;

/**
 * Set current report type, update the URL hash, refresh data.
 * @param {string} value
 */
export const setReport = (value) => {
    report = value;
    // Update ?report= parameter without reloading page.
    const params = new URLSearchParams(window.location.search);
    params.set('report', value);
    const newUrl = `${window.location.pathname}?${params.toString()}`;
    window.history.replaceState({}, '', newUrl);
    fetchData();
};

/** Initialize report selection from current URL hash. */
const initReportFromURL = () => {
    const params = new URLSearchParams(window.location.search);
    const fromParam = params.get('report');
    let candidate = fromParam;
    // Hash shim: allow legacy #value and migrate to ?report=value
    if (!candidate && window.location.hash.length > 1) {
        candidate = window.location.hash.substring(1);
        // Migrate hash -> query param (preserve other params if they appear later)
        const migrateParams = new URLSearchParams(window.location.search);
        migrateParams.set('report', candidate);
        const newUrl = `${window.location.pathname}?${migrateParams.toString()}`;
        window.history.replaceState({}, '', newUrl);
    }
    if (candidate) report = candidate;
    const select = document.getElementById('report');
    if (select instanceof HTMLSelectElement) {
        if ([...select.options].some(opt => opt.value === report)) {
            select.value = report;
        }
    }
};

/** Wire up UI events and perform initial data load. */
export const init = () => {
    const select = document.getElementById('report');
    if (select instanceof HTMLSelectElement) {
        select.addEventListener('change', (e) => {
            const target = e.currentTarget;
            if (target instanceof HTMLSelectElement) setReport(target.value);
        });
    }
    initReportFromURL();
    fetchData();
};

// Auto initialize when DOM is ready.
document.addEventListener('DOMContentLoaded', init);
