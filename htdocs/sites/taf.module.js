import { requireElement } from '/js/iemjs/domUtils.js';

/**
 * Loads and displays Terminal Aerodrome Forecast (TAF) data
 * @param {HTMLElement} element - The target element to populate
 * @param {string} station3 - 3-character station identifier
 */
const loadTafData = async (element, station3) => {
    if (!station3) {
        element.innerHTML = '<div class="alert alert-warning">No station identifier provided for TAF data.</div>';
        return;
    }
    
    try {
        const response = await fetch(`/cgi-bin/afos/retrieve.py?pil=TAF${station3}&fmt=html`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        const data = await response.text();
        element.innerHTML = data || '<div class="alert alert-info">No TAF data available for this station.</div>';
    } catch (error) {
        element.innerHTML = `<div class="alert alert-danger"><strong>Error:</strong> Unable to load TAF data. ${error.message}</div>`;
    }
};

/**
 * Loads and displays Area Forecast Discussion (AFD) aviation data
 * @param {HTMLElement} element - The target element to populate
 * @param {string} wfo - Weather Forecast Office identifier
 */
const loadAfdData = async (element, wfo) => {
    if (!wfo) {
        element.innerHTML = '<div class="alert alert-warning">No Weather Forecast Office identifier provided for AFD data.</div>';
        return;
    }
    
    try {
        const response = await fetch(`/cgi-bin/afos/retrieve.py?pil=AFD${wfo}&fmt=html&aviation_afd=1`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        const data = await response.text();
        element.innerHTML = data || '<div class="alert alert-info">No AFD aviation data available for this office.</div>';
    } catch (error) {
        element.innerHTML = `<div class="alert alert-danger"><strong>Error:</strong> Unable to load AFD data. ${error.message}</div>`;
    }
};

/**
 * Loads and displays recent METAR observations
 * @param {HTMLElement} element - The target element to populate
 * @param {string} station4 - 4-character station identifier
 */
const loadMetarData = async (element, station4) => {
    if (!station4) {
        element.innerHTML = '<div class="alert alert-warning">No station identifier provided for METAR data.</div>';
        return;
    }
    
    try {
        const response = await fetch(
            `/cgi-bin/request/asos.py?station=${station4}&hours=4&nometa=1&data=metar&report_type=3,4`
        );
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        const data = await response.text();
        const processedData = data.trim();
        if (processedData) {
            element.innerHTML = `<pre class="bg-light p-3 rounded border">${processedData}</pre>`;
        } else {
            element.innerHTML = '<div class="alert alert-info">No recent METAR data available for this station.</div>';
        }
    } catch (error) {
        element.innerHTML = `<div class="alert alert-danger"><strong>Error:</strong> Unable to load METAR data. ${error.message}</div>`;
    }
};

/**
 * Initialize aviation weather data loading when DOM is ready
 */
document.addEventListener('DOMContentLoaded', () => {
    // Load TAF data for the raw text section
    const rawtext = requireElement('rawtext');
    const station3 = rawtext.dataset.station3;
    loadTafData(rawtext, station3);

    // Load AFD aviation data
    const afd = requireElement('afd');
    const wfo = afd.dataset.wfo;
    loadAfdData(afd, wfo);

    // Load recent METAR observations
    const metars = requireElement('metars');
    const station4 = metars.dataset.station4;
    loadMetarData(metars, station4);
});

// Export functions for testing purposes
export { loadTafData, loadAfdData, loadMetarData };
