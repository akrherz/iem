const getStationField = formEl =>
    formEl.querySelector('#station') ||
    formEl.querySelector("select[name='station']") ||
    formEl.querySelector("input[name='station']");

const updateStatus = (statusEl, message, klass = 'secondary') => {
    statusEl.className = `alert alert-${klass}`;
    statusEl.textContent = message;
};

const buildLink = (url, label) => {
    if (!url) {
        return null;
    }
    const a = document.createElement('a');
    a.href = url;
    a.target = '_blank';
    a.rel = 'noopener noreferrer';
    a.textContent = label;
    return a;
};

const formatLocalValid = value => {
    if (!value) {
        return '';
    }
    const match = value.match(
        /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})/
    );
    if (!match) {
        return value;
    }

    const year = Number(match[1]);
    const month = Number(match[2]);
    const day = Number(match[3]);
    const hour24 = Number(match[4]);
    const minute = Number(match[5]);
    const labels = [
        'Jan',
        'Feb',
        'Mar',
        'Apr',
        'May',
        'Jun',
        'Jul',
        'Aug',
        'Sep',
        'Oct',
        'Nov',
        'Dec'
    ];
    if (
        Number.isNaN(year) ||
        Number.isNaN(month) ||
        Number.isNaN(day) ||
        Number.isNaN(hour24) ||
        Number.isNaN(minute) ||
        month < 1 ||
        month > 12
    ) {
        return value;
    }
    const suffix = hour24 >= 12 ? 'PM' : 'AM';
    const hour12 = hour24 % 12 || 12;
    return `${labels[month - 1]} ${day}, ${hour12}:${String(minute).padStart(2, '0')} ${suffix}`;
};

const buildValueBadge = (value, previousValue) => {
    const badge = document.createElement('span');
    badge.className = 'badge text-bg-secondary';
    if (value === null || value === undefined) {
        return { badge, nextPreviousValue: previousValue };
    }
    const currentValue = Number(value);
    if (Number.isFinite(currentValue) && previousValue !== null) {
        if (currentValue > previousValue) {
            badge.className = 'badge text-bg-danger';
        } else if (currentValue < previousValue) {
            badge.className = 'badge text-bg-primary';
        } else {
            badge.className = 'badge text-bg-success';
        }
    }
    badge.textContent = `${value}`;
    return {
        badge,
        nextPreviousValue: Number.isFinite(currentValue)
            ? currentValue
            : previousValue
    };
};

const renderTable = (target, events) => {
    target.textContent = '';
    if (!events || events.length === 0) {
        const div = document.createElement('div');
        div.className = 'p-3 text-muted';
        div.textContent = 'No events found.';
        target.append(div);
        return;
    }

    const table = document.createElement('table');
    table.className = 'table table-sm table-striped mb-0 cli-audit-table';

    const thead = document.createElement('thead');
    thead.innerHTML =
        '<tr><th>Local Valid</th><th>Source</th><th>Value</th><th>Description</th></tr>';
    table.append(thead);

    const tbody = document.createElement('tbody');
    let previousValue = null;
    for (const event of events) {
        const row = document.createElement('tr');

        const validCell = document.createElement('td');
        validCell.className = 'cli-valid-cell';
        validCell.textContent = formatLocalValid(event.local_valid);
        validCell.title = `local: ${event.local_valid || ''}\nutc: ${event.utc_valid || ''}`;
        row.append(validCell);

        const sourceCell = document.createElement('td');
        sourceCell.className = 'cli-source-cell';
        const sourceText = event.source || '';
        const sourceLink = buildLink(event.link, sourceText);
        if (sourceLink) {
            sourceCell.append(sourceLink);
        } else {
            sourceCell.textContent = sourceText;
        }
        row.append(sourceCell);

        const valueCell = document.createElement('td');
        valueCell.className = 'cli-value-cell';
        const { badge, nextPreviousValue } = buildValueBadge(
            event.value,
            previousValue
        );
        previousValue = nextPreviousValue;
        valueCell.append(badge);
        row.append(valueCell);

        const descCell = document.createElement('td');
        descCell.className = 'cli-desc-cell';
        descCell.textContent = event.description || '';
        descCell.title = event.description || '';
        row.append(descCell);

        tbody.append(row);
    }
    table.append(tbody);
    target.append(table);
};

const updateUrl = (station, date) => {
    const params = new URLSearchParams({ station, date });
    window.history.replaceState({}, '', `?${params.toString()}`);
};

const getTodayDateString = () => {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
};

const updateServiceMeta = (metaEl, serviceUrl, generatedAt = null) => {
    if (!metaEl) {
        return;
    }
    metaEl.textContent = '';

    const generated = document.createElement('span');
    generated.textContent = generatedAt
        ? `Generated at: ${generatedAt}. `
        : 'Generated at: unavailable. ';
    metaEl.append(generated);

    const cache = document.createElement('span');
    cache.textContent = 'Backend JSON service caching: 3 minutes. Endpoint: ';
    metaEl.append(cache);

    const endpoint = document.createElement('a');
    endpoint.href = serviceUrl;
    endpoint.textContent = serviceUrl;
    endpoint.target = '_blank';
    endpoint.rel = 'noopener noreferrer';
    metaEl.append(endpoint);
};

const loadAudit = async (station, date, statusEl, highEl, lowEl, metaEl) => {
    const params = new URLSearchParams({ station, date });
    const serviceUrl = `/json/cli_audit.py?${params.toString()}`;
    updateStatus(statusEl, 'Loading audit data...', 'secondary');
    updateServiceMeta(metaEl, serviceUrl);
    highEl.textContent = '';
    lowEl.textContent = '';

    try {
        const response = await fetch(serviceUrl);
        if (!response.ok) {
            throw new Error(`Service returned ${response.status}`);
        }
        const data = await response.json();
        renderTable(highEl, data.high?.events || []);
        renderTable(lowEl, data.low?.events || []);
        updateServiceMeta(metaEl, serviceUrl, data.generated_at);
        updateStatus(
            statusEl,
            `Loaded ${station} for ${date}. High events: ${data.high?.events?.length || 0}, Low events: ${data.low?.events?.length || 0}.`,
            'success'
        );
    } catch (err) {
        updateStatus(statusEl, `Failed to load audit data: ${err.message}`, 'danger');
    }
};

const initFromUrl = (stationEl, dateEl, statusEl, highEl, lowEl, metaEl) => {
    const params = new URLSearchParams(window.location.search);
    const station = (params.get('station') || 'KDSM').toUpperCase();
    const date = params.get('date') || getTodayDateString();
    stationEl.value = station;
    dateEl.value = date;
    updateUrl(station, date);
    loadAudit(station, date, statusEl, highEl, lowEl, metaEl);
};

const init = () => {
    const formEl = document.getElementById('query-form');
    const dateEl = document.getElementById('date');
    const statusEl = document.getElementById('status');
    const metaEl = document.getElementById('service-meta');
    const highEl = document.getElementById('high-events');
    const lowEl = document.getElementById('low-events');
    if (!formEl || !dateEl || !statusEl || !highEl || !lowEl) {
        return;
    }

    const stationEl = getStationField(formEl);
    if (!stationEl) {
        updateStatus(statusEl, 'Station field not found on page.', 'danger');
        return;
    }

    const syncParams = () => {
        const station = stationEl.value.trim().toUpperCase();
        const date = dateEl.value || getTodayDateString();
        stationEl.value = station;
        dateEl.value = date;
        updateUrl(station, date);
        loadAudit(station, date, statusEl, highEl, lowEl, metaEl);
    };

    stationEl.addEventListener('change', syncParams);
    dateEl.addEventListener('change', syncParams);

    formEl.addEventListener('submit', evt => {
        evt.preventDefault();
        const station = stationEl.value.trim().toUpperCase();
        const date = dateEl.value;
        stationEl.value = station;
        updateUrl(station, date);
        loadAudit(station, date, statusEl, highEl, lowEl, metaEl);
    });

    initFromUrl(stationEl, dateEl, statusEl, highEl, lowEl, metaEl);
};

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
