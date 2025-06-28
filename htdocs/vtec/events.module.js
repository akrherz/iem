import { TabulatorFull as Tabulator } from 'https://unpkg.com/tabulator-tables@6.3.1/dist/js/tabulator_esm.min.js';
import { vtec_phenomena_dict, vtec_significance_dict } from '/js/iemjs/iemdata.js';
import { requireElement } from '/js/iemjs/domUtils.js';

function updateEventCount(count) {
    const countElement = requireElement('#event-count');
    countElement.textContent = `${count} Events`;
}

function updateApiUrlDisplay(apiUrl) {
    const apiUrlElement = requireElement('#api-url');
    const copyBtn = apiUrlElement.nextElementSibling;
    apiUrlElement.value = apiUrl;
    if (copyBtn) {
        copyBtn.setAttribute('onclick', `navigator.clipboard.writeText('${apiUrl}')`);
    }
}

function showLoading(show) {
    const loadingElement = requireElement('#loading-indicator');
    loadingElement.style.display = show ? 'block' : 'none';
}

function showError(show) {
    const errorElement = requireElement('#error-message');
    errorElement.style.display = show ? 'block' : 'none';
}

function showDownloadButtons(show) {
    const buttonsElement = requireElement('#download-buttons');
    buttonsElement.style.display = show ? 'flex' : 'none';
}

function getInputValue(selector, defaultValue) {
    return document.querySelector(selector)?.value || defaultValue;
}

function getCheckboxValue(selector) {
    return document.querySelector(selector)?.checked || false;
}

function getRadioValue(selector, defaultValue) {
    return document.querySelector(selector)?.value || defaultValue;
}

function getFormValues() {
    return {
        whichValue: getRadioValue('input[name="which"]:checked', 'wfo'),
        wfo: getInputValue('select[name="wfo"]', 'DMX'),
        state: getInputValue('select[name="state"]', 'IA'),
        year: getInputValue('select[name="year"]', new Date().getFullYear()),
        phenomena: getInputValue('select[name="p"]', ''),
        significance: getInputValue('select[name="s"]', ''),
        ponChecked: getCheckboxValue('input[name="pon"]'),
        sonChecked: getCheckboxValue('input[name="son"]'),
    };
}

function buildBaseApiUrl(whichValue, wfo, state, year) {
    return whichValue === 'wfo'
        ? `/json/vtec_events.py?wfo=${wfo}&year=${year}`
        : `/json/vtec_events_bystate.py?state=${state}&year=${year}`;
}

function addFiltersToUrl(apiUrl, ponChecked, phenomena, sonChecked, significance) {
    let url = apiUrl;
    if (ponChecked && phenomena) {
        url += `&phenomena=${phenomena}`;
    }
    if (sonChecked && significance) {
        url += `&significance=${significance}`;
    }
    return url;
}

function getConfig() {
    const formValues = getFormValues();
    const baseUrl = buildBaseApiUrl(formValues.whichValue, formValues.wfo, formValues.state, formValues.year);
    const apiUrl = addFiltersToUrl(baseUrl, formValues.ponChecked, formValues.phenomena, formValues.sonChecked, formValues.significance);

    return {
        apiUrl,
        ...formValues,
    };
}

function toggleFormVisibility() {
    const whichValue = document.querySelector('input[name="which"]:checked')?.value;
    const wfoContainer = document.getElementById('wfo-select-container');
    const stateContainer = document.getElementById('state-select-container');

    if (whichValue === 'wfo') {
        wfoContainer.style.display = 'block';
        stateContainer.style.display = 'none';
    } else if (whichValue === 'state') {
        wfoContainer.style.display = 'none';
        stateContainer.style.display = 'block';
    }
}

class VTECEvents {
    constructor() {
        this.table = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadEvents();
    }

    setupEventListeners() {
        // Form visibility based on which option is selected
        const whichRadios = document.querySelectorAll('input[name="which"]');
        whichRadios.forEach(radio => {
            radio.addEventListener('change', () => toggleFormVisibility());
        });

        // Initial visibility setup
        toggleFormVisibility();

        // CSV Download
        const downloadCsvBtn = document.getElementById('download-csv');
        if (downloadCsvBtn) {
            downloadCsvBtn.addEventListener('click', () => this.downloadCSV());
        }

        // Copy to clipboard
        const copyBtn = document.getElementById('copy-clipboard');
        if (copyBtn) {
            copyBtn.addEventListener('click', () => this.copyToClipboard());
        }

        // Listen for form submissions to reload data
        const form = document.getElementById('vtec-form');
        if (form) {
            form.addEventListener('submit', e => {
                e.preventDefault();
                this.loadEvents();
            });
        }
    }

    async loadEvents() {
        try {
            this.showLoading(true);

            const config = getConfig();
            updateApiUrlDisplay(config.apiUrl);

            const response = await fetch(config.apiUrl);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.renderTable(data.events || []);
            updateEventCount(data.events?.length || 0);
            showDownloadButtons(true);
        } catch {
            // Error loading events, show error message
            showError(true);
        } finally {
            showLoading(false);
        }
    }

    renderTable(events) {
        const tableContainer = document.getElementById('vtec-table');

        if (events.length === 0) {
            tableContainer.innerHTML =
                '<div class="alert alert-warning"><i class="bi bi-info-circle"></i> No events found for the selected criteria.</div>';
            tableContainer.style.display = 'block';
            return;
        }

        // Transform data for Tabulator
        const tableData = events.map(event => {
            let hmlUrl = '';
            if (event.hvtec_nwsli && event.hvtec_nwsli !== '00000') {
                const ts = new Date(event.issue);
                const dateStr = `${ts.getFullYear()}/${String(ts.getMonth() + 1).padStart(2, '0')}/${String(ts.getDate()).padStart(2, '0')} 0000`;
                hmlUrl = `/plotting/auto/?_wait=no&q=160&station=${event.hvtec_nwsli}&dt=${dateStr}`;
            }

            return {
                wfo: event.wfo,
                eventid: event.eventid,
                eventid_link: event.uri,
                phenomena: event.phenomena,
                significance: event.significance,
                phenomena_desc: vtec_phenomena_dict[event.phenomena] || event.phenomena,
                significance_desc: vtec_significance_dict[event.significance] || event.significance,
                issue: event.issue,
                expire: event.expire,
                hvtec_nwsli: event.hvtec_nwsli,
                hml_url: hmlUrl,
            };
        });

        // Clear previous table if exists
        if (this.table) {
            this.table.destroy();
        }

        // Create Tabulator table
        this.table = new Tabulator(tableContainer, {
            data: tableData,
            layout: 'fitColumns',
            responsiveLayout: 'collapse',
            pagination: 'local',
            paginationSize: 50,
            paginationSizeSelector: [25, 50, 100, 200],
            movableColumns: true,
            resizableColumns: true,
            tooltips: true,
            columns: [
                {
                    title: 'WFO',
                    field: 'wfo',
                    width: 80,
                    sorter: 'string',
                    headerFilter: 'input',
                },
                {
                    title: 'Event ID',
                    field: 'eventid',
                    width: 100,
                    sorter: 'number',
                    formatter: cell => {
                        const data = cell.getRow().getData();
                        return `<a href="${data.eventid_link}" target="_blank">${data.eventid}</a>`;
                    },
                },
                {
                    title: 'Phenomena',
                    field: 'phenomena',
                    width: 120,
                    sorter: 'string',
                    headerFilter: 'input',
                },
                {
                    title: 'Significance',
                    field: 'significance',
                    width: 120,
                    sorter: 'string',
                    headerFilter: 'input',
                },
                {
                    title: 'Description',
                    field: 'phenomena_desc',
                    minWidth: 200,
                    sorter: 'string',
                    formatter: cell => {
                        const data = cell.getRow().getData();
                        return `${data.phenomena_desc} ${data.significance_desc}`;
                    },
                    headerFilter: 'input',
                },
                {
                    title: 'Issue Time',
                    field: 'issue',
                    width: 180,
                    sorter: 'datetime',
                    sorterParams: {
                        format: 'YYYY-MM-DD HH:mm',
                    },
                },
                {
                    title: 'Expire Time',
                    field: 'expire',
                    width: 180,
                    sorter: 'datetime',
                    sorterParams: {
                        format: 'YYYY-MM-DD HH:mm',
                    },
                },
                {
                    title: 'HVTEC NWSLI',
                    field: 'hvtec_nwsli',
                    width: 130,
                    sorter: 'string',
                    formatter: cell => {
                        const data = cell.getRow().getData();
                        if (data.hml_url && data.hvtec_nwsli && data.hvtec_nwsli !== '00000') {
                            return `<a href="${data.hml_url}" target="_blank">${data.hvtec_nwsli}</a>`;
                        }
                        return data.hvtec_nwsli || '';
                    },
                },
            ],
        });

        tableContainer.style.display = 'block';
    }

    downloadCSV() {
        if (this.table) {
            this.table.download('csv', 'vtec_events.csv');
        }
    }

    copyToClipboard() {
        if (this.table) {
            this.table.copyToClipboard('table');
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new VTECEvents();
});
