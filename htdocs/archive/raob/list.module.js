/* RAOB List - Tabulator + Vanilla JS Implementation */
import {TabulatorFull as Tabulator} from 'https://unpkg.com/tabulator-tables@6.3.1/dist/js/tabulator_esm.min.mjs';
import { requireElement } from '/js/iemjs/domUtils.js';

let station = '_OAX';
let year = new Date().getFullYear();
let table = null;
let sortby = "-";  // Sentinel value for no sort
let asc = "desc";
let filter_year = true;  // Not implemented as too much data for JSON

function rnd(val, precision) {
    return (val === null) ? "" : val.toFixed(precision);
}

// Column definitions for Tabulator
const columns = [
    {title: "ID", field: "station", width: 80, frozen: true},
    {title: "Valid", field: "valid", width: 120, frozen: true},
    {title: "SBCAPE J/kg", field: "sbcape_jkg", width: 110, formatter: (cell) => rnd(cell.getValue(), 0), sorter: "number"},
    {title: "MUCAPE J/kg", field: "mucape_jkg", width: 110, formatter: (cell) => rnd(cell.getValue(), 0), sorter: "number"},
    {title: "SBCIN J/kg", field: "sbcin_jkg", width: 110, formatter: (cell) => rnd(cell.getValue(), 0), sorter: "number"},
    {title: "MUCIN J/kg", field: "mucin_jkg", width: 110, formatter: (cell) => rnd(cell.getValue(), 0), sorter: "number"},
    {title: "PrecipWater mm", field: "pwater_mm", width: 120, formatter: (cell) => rnd(cell.getValue(), 1), sorter: "number"},
    {title: "LCL m", field: "lcl_agl_m", width: 80, formatter: (cell) => rnd(cell.getValue(), 0), sorter: "number"},
    {title: "LFC m", field: "lfc_agl_m", width: 80, formatter: (cell) => rnd(cell.getValue(), 0), sorter: "number"},
    {title: "EL m", field: "el_agl_m", width: 80, formatter: (cell) => rnd(cell.getValue(), 0), sorter: "number"},
    {title: "Total Totals", field: "total_totals", width: 100, formatter: (cell) => rnd(cell.getValue(), 1), sorter: "number"},
    {title: "SWEAT", field: "sweat_index", width: 80, formatter: (cell) => rnd(cell.getValue(), 1), sorter: "number"},
    {title: "SRH 0-3 km m²/s²", field: "srh_sfc_3km_total", width: 130, formatter: (cell) => rnd(cell.getValue(), 0), sorter: "number"},
    {title: "SRH 0-1 km m²/s²", field: "srh_sfc_1km_total", width: 130, formatter: (cell) => rnd(cell.getValue(), 0), sorter: "number"},
    {title: "SHR 0-6 km m/s", field: "shear_sfc_6km_smps", width: 120, formatter: (cell) => rnd(cell.getValue(), 1), sorter: "number"}
];

function initializeTable() {
    table = new Tabulator("#datatable", {
        height: "80vh",
        layout: "fitColumns",
        responsiveLayout: "hide",
        responsiveLayoutCollapseStartOpen: false,
        columnDefaults: {
            tooltip: true,
        },
        columns,
        placeholder: "No data available",
        pagination: "local",
        paginationSize: 50,
        paginationSizeSelector: [25, 50, 100, 200, true],
        movableColumns: true,
        resizableRows: false,
        selectable: false,
        data: [],
        footerElement: '<div class="tabulator-footer"><span class="tabulator-info">Viewing: Table of Sounding Parameters</span></div>'
    });
}

function buildServiceUrl() {
    const ascbool = (asc === "asc") ? "true" : "false";
    let service = `/api/1/raobs_by_year.json?station=${station}&asc=${ascbool}`;

    if (sortby !== "-") {
        service += `&sortby=${sortby}`;
    } else if (filter_year) {
        service += `&year=${year}`;
    }

    return service;
}

function buildCaption() {
    let caption = `RAOB Data for ${station}`;

    if (sortby !== "-") {
        caption = `${caption} sorted by ${sortby} ${asc} (Top 100)`;
    } else if (filter_year) {
        caption = `${caption} for ${year}`;
    }

    return caption;
}

function updateUrlParameters() {
    const url = new URL(window.location);
    url.searchParams.set('station', station);

    if (sortby !== "-") {
        url.searchParams.set('sortby', sortby);
        url.searchParams.set('asc', asc);
        url.searchParams.delete('year');
    } else if (filter_year) {
        url.searchParams.set('year', year);
        url.searchParams.set('asc', asc);
        url.searchParams.delete('sortby');
    }

    window.history.replaceState({}, '', url);
}

function updateFooterCaption(caption, suffix = '') {
    const footerInfo = document.querySelector('.tabulator-info');
    if (footerInfo) {
        footerInfo.textContent = `${caption}${suffix}`;
    }
}

function handleFetchSuccess(data, caption) {
    table.setData(data.data);
    updateFooterCaption(`Viewing: ${caption}`, ` (${data.data.length} records)`);
    
    if (data.data.length === 0) {
        table.setData([]);
    }
}

function handleFetchError(error) {
    updateFooterCaption(`Error loading data ${error.message}`);
}

async function fetchData() {
    const service = buildServiceUrl();
    const caption = buildCaption();
    
    updateUrlParameters();
    updateFooterCaption(`Loading: ${caption}...`);
    
    try {
        const response = await fetch(service);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        handleFetchSuccess(data, caption);
    } catch (error) {
        handleFetchError(error);
    }
}

function setupEventListeners() {
    // Station select change
    const stationSelect = document.querySelector("select[name='station']");
    if (stationSelect) {
        stationSelect.addEventListener('change', (e) => {
            station = e.target.value;
            fetchData();
        });
    }
    
    // Year select change
    const yearSelect = document.querySelector("select[name='year']");
    if (yearSelect) {
        yearSelect.addEventListener('change', (e) => {
            const sortbySelect = document.querySelector("select[name='sortby']");
            if (sortbySelect) {
                sortbySelect.value = "-";
            }
            sortby = "-";
            year = e.target.value;
            fetchData();
        });
    }
    
    // Sort by select change
    const sortbySelect = document.querySelector("select[name='sortby']");
    if (sortbySelect) {
        sortbySelect.addEventListener('change', (e) => {
            sortby = e.target.value;
            if (sortby !== "-") {
                fetchData();
            }
        });
    }
    
    // Ascending/Descending select change
    const ascSelect = document.querySelector("select[name='asc']");
    if (ascSelect) {
        ascSelect.addEventListener('change', (e) => {
            asc = e.target.value;
            fetchData();
        });
    }
    
    // Download button
    const downloadBtn = requireElement('download');
    downloadBtn.addEventListener('click', () => {
        const service = `/api/1/raobs_by_year.txt?station=${encodeURIComponent(station)}`;
        window.location.href = service;
    });
}

function setStationFromToken(token) {
    station = token;
    const stationSelect = document.querySelector("select[name='station']");
    if (stationSelect) {
        stationSelect.value = station;
    }
}

function setYearFromToken(token) {
    year = token;
    const yearSelect = document.querySelector("select[name='year']");
    if (yearSelect) {
        yearSelect.value = year;
    }
}

function setSortbyFromToken(token) {
    sortby = token;
    const sortbySelect = document.querySelector("select[name='sortby']");
    if (sortbySelect) {
        sortbySelect.value = sortby;
    }
    filter_year = false;
}

function setAscFromToken(token) {
    asc = token;
    const ascSelect = document.querySelector("select[name='asc']");
    if (ascSelect) {
        ascSelect.value = asc;
    }
}

function handleSecondToken(token) {
    const yearRegex = /^\d{4}$/;
    if (yearRegex.test(token)) {
        setYearFromToken(token);
    } else {
        setSortbyFromToken(token);
    }
}

function parseLegacyHashFormat(hash) {
    const tokens = hash.split(":");
    if (tokens.length === 0) return false;
    
    // Set station
    setStationFromToken(tokens[0]);
    filter_year = true;
    
    // Handle second token (year or sortby)
    if (tokens.length > 1) {
        handleSecondToken(tokens[1]);
    }
    
    // Handle third token (asc)
    if (tokens.length > 2) {
        setAscFromToken(tokens[2]);
    }
    
    return true;
}

function convertLegacyHashToUrlParams() {
    const url = new URL(window.location);
    url.hash = '';
    url.searchParams.set('station', station);
    
    if (sortby !== "-") {
        url.searchParams.set('sortby', sortby);
        url.searchParams.set('asc', asc);
    } else if (filter_year) {
        url.searchParams.set('year', year);
        url.searchParams.set('asc', asc);
    }
    
    window.history.replaceState({}, '', url);
}

function parseStationParam(urlParams) {
    if (urlParams.has('station')) {
        setStationFromToken(urlParams.get('station'));
    }
}

function parseYearParam(urlParams) {
    if (urlParams.has('year')) {
        setYearFromToken(urlParams.get('year'));
        filter_year = true;
    }
}

function parseSortbyParam(urlParams) {
    if (urlParams.has('sortby')) {
        setSortbyFromToken(urlParams.get('sortby'));
    }
}

function parseAscParam(urlParams) {
    if (urlParams.has('asc')) {
        setAscFromToken(urlParams.get('asc'));
    }
}

function parseModernUrlParameters(urlParams) {
    parseStationParam(urlParams);
    parseYearParam(urlParams);
    parseSortbyParam(urlParams);
    parseAscParam(urlParams);
}

function parseUrlParameters() {
    const urlParams = new URLSearchParams(window.location.search);
    const hash = window.location.hash.substring(1); // Remove #
    
    // Check for legacy hash format first for backwards compatibility
    if (hash && !urlParams.has('station')) {
        if (parseLegacyHashFormat(hash)) {
            convertLegacyHashToUrlParams();
            return;
        }
    }
    
    // Parse modern URL parameters
    parseModernUrlParameters(urlParams);
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    initializeTable();
    setupEventListeners();
    parseUrlParameters();
    fetchData();
});
