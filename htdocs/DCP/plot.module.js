// ES Module for DCP plotting application

import { escapeHTML, requireSelectElement } from '/js/iemjs/domUtils.js';
import { iemdata } from '/js/iemjs/iemdata.js';

// DOM element references
let stateSelect = null;
let stationSelect = null; 
let variableSelect = null;
let dateInput = null;
let dayIntervalInput = null;
let imageDisplay = null;
let messageDiv = null;

/**
 * Initialize the form elements and event handlers
 */
function initializeForm() {
    // Get DOM elements
    stateSelect = requireSelectElement('state-select');
    stationSelect = requireSelectElement('station-select');
    variableSelect = requireSelectElement('variable-select');
    dateInput = document.getElementById('date-input');
    dayIntervalInput = document.getElementById('day-interval');
    imageDisplay = document.getElementById('imagedisplay');
    messageDiv = document.getElementById('msg');

    // Populate state dropdown
    populateStateSelect();

    // Set up event handlers
    stateSelect.addEventListener('change', handleStateChange);
    stationSelect.addEventListener('change', handleStationChange);
    
    // Set up form submission
    const plotButton = document.getElementById('plot-button');
    if (plotButton) {
        plotButton.addEventListener('click', updateImage);
    }

    // Set default values
    if (dateInput) {
        const today = new Date();
        dateInput.value = formatDateForInput(today);
        dateInput.setAttribute('min', '2002-01-01');
        dateInput.setAttribute('max', formatDateForInput(today));
    }

    if (dayIntervalInput) {
        dayIntervalInput.value = '5';
        dayIntervalInput.min = '1';
        dayIntervalInput.max = '31';
    }

    // Check URL for initial values (supports both legacy hash and modern URLParams)
    parseURLHash();
    parseURLParams();
}

/**
 * Populate the state dropdown with options
 */
function populateStateSelect() {
    // Clear existing options except the first placeholder
    stateSelect.innerHTML = '<option value="">Select State...</option>';
    
    iemdata.states.forEach(([abbr, name]) => {
        const option = document.createElement('option');
        option.value = abbr;
        option.textContent = `[${abbr}] ${name}`;
        stateSelect.appendChild(option);
    });
}

/**
 * Handle state selection change
 */
async function handleStateChange() {
    const selectedState = stateSelect.value;
    
    // Clear dependent dropdowns
    clearSelect(stationSelect, 'Select Station...');
    clearSelect(variableSelect, 'Select Variable...');
    clearMessage();

    if (!selectedState) return;

    try {
        const response = await fetch(`/json/network.json?network=${selectedState}_DCP`);
        if (!response.ok) throw new Error('Network response was not ok');
        
        const data = await response.json();
        populateStationSelect(data.stations || []);
    } catch (error) {
        showMessage(`Error loading stations: ${error.message}`);
    }
}

/**
 * Populate station dropdown
 */
function populateStationSelect(stations) {
    clearSelect(stationSelect, 'Select Station...');
    
    stations.forEach(station => {
        const option = document.createElement('option');
        option.value = station.id;
        option.textContent = `[${station.id}] ${station.name}`;
        stationSelect.appendChild(option);
    });
}

/**
 * Handle station selection change
 */
async function handleStationChange() {
    const selectedStation = stationSelect.value;
    
    // Clear variable dropdown
    clearSelect(variableSelect, 'Select Variable...');
    clearMessage();

    if (!selectedStation) return;

    try {
        const response = await fetch(`/json/dcp_vars.json?station=${selectedStation}`);
        if (!response.ok) throw new Error('Network response was not ok');
        
        const data = await response.json();
        populateVariableSelect(data.vars || []);
        
        if (data.vars && data.vars.length === 0) {
            showMessage('Sorry, did not find any variables for this site!');
        }
    } catch (error) {
        showMessage(`Error loading variables: ${error.message}`);
    }
}

/**
 * Populate variable dropdown
 */
function populateVariableSelect(variables) {
    clearSelect(variableSelect, 'Select Variable...');
    
    variables.forEach(variable => {
        const option = document.createElement('option');
        option.value = variable.id;
        option.textContent = `[${variable.id}]`;
        variableSelect.appendChild(option);
    });
}

/**
 * Clear a select element and add placeholder option
 */
function clearSelect(selectElement, placeholderText) {
    selectElement.innerHTML = `<option value="">${escapeHTML(placeholderText)}</option>`;
}

/**
 * Show message to user
 */
function showMessage(message) {
    if (messageDiv) {
        messageDiv.textContent = message;
    }
}

/**
 * Clear message
 */
function clearMessage() {
    if (messageDiv) {
        messageDiv.textContent = '';
    }
}

/**
 * Format date for HTML date input (YYYY-MM-DD)
 */
function formatDateForInput(date) {
    return date.toISOString().split('T')[0];
}

/**
 * Add days to a date
 */
function addDays(date, days) {
    const result = new Date(date);
    result.setDate(result.getDate() + days);
    return result;
}

/**
 * Update the plot image and URL
 */
function updateImage() {
    const state = stateSelect.value;
    const station = stationSelect.value;
    const variable = variableSelect.value;
    const startDate = dateInput?.value;
    const dayInterval = parseInt(dayIntervalInput?.value || '5', 10);

    // Validate required fields
    if (!state || !station || !variable || !startDate) {
        showMessage('Please fill in all required fields.');
        return;
    }

    try {
        const startDateObj = new Date(startDate);
        const endDateObj = addDays(startDateObj, dayInterval);
        const endDate = formatDateForInput(endDateObj);

        // Build the image URL
        const params = new URLSearchParams({
            station,
            sday: startDate,
            eday: endDate,
            var: variable
        });
        
        const imageUrl = `plot.php?${params.toString()}`;
        
        if (imageDisplay) {
            imageDisplay.src = imageUrl;
        }

        // Update browser URL
        updateURL(state, station, variable, startDate, dayInterval);
        
        clearMessage();
    } catch (error) {
        showMessage(`Error creating plot: ${error.message}`);
    }
}

/**
 * Update the URL with current form values using URLSearchParams
 */
function updateURL(state, station, variable, startDate, dayInterval) {
    const url = new URL(window.location);
    url.searchParams.set('state', state);
    url.searchParams.set('station', station);
    url.searchParams.set('variable', variable);
    url.searchParams.set('startDate', startDate);
    url.searchParams.set('dayInterval', dayInterval);
    
    // Update URL without reloading the page
    window.history.replaceState({}, '', url);
}

/**
 * Parse URL search parameters and set form values
 */
function parseURLParams() {
    const urlParams = new URLSearchParams(window.location.search);
    
    const state = urlParams.get('state');
    const station = urlParams.get('station');
    const variable = urlParams.get('variable');
    const startDate = urlParams.get('startDate');
    const dayInterval = urlParams.get('dayInterval');

    // Only proceed if we have the minimum required parameters
    if (!state || !station || !variable || !startDate) return;

    // Validate date format (YYYY-MM-DD)
    const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
    if (!dateRegex.test(startDate)) {
        showMessage('Invalid date format in URL. Please use YYYY-MM-DD format.');
        return;
    }

    // Validate dayInterval is a reasonable number
    const interval = parseInt(dayInterval, 10);
    if (dayInterval && (isNaN(interval) || interval < 1 || interval > 31)) {
        showMessage('Invalid day interval in URL. Must be between 1 and 31 days.');
        return;
    }

    setFormValues(state, station, variable, startDate, dayInterval || '5');
}

/**
 * Parse URL hash and migrate to URLParams (for backward compatibility)
 * Legacy URLs used format: #IA.AEEI4.HGIZ.2024-12-01.7
 * New URLs use format: ?state=IA&station=AEEI4&variable=HGIZ&startDate=2024-12-01&dayInterval=7
 */
function parseURLHash() {
    const hash = window.location.hash.substring(1); // Remove #
    if (!hash) return;

    const tokens = hash.split('.');
    if (tokens.length !== 5) return;

    const [state, station, variable, startDate, dayInterval] = tokens;

    // Migrate hash to URLParams and clear the hash
    const url = new URL(window.location);
    url.searchParams.set('state', state);
    url.searchParams.set('station', station);
    url.searchParams.set('variable', variable);
    url.searchParams.set('startDate', startDate);
    url.searchParams.set('dayInterval', dayInterval);
    url.hash = ''; // Clear the hash
    
    // Update URL and set form values
    window.history.replaceState({}, '', url);
    setFormValues(state, station, variable, startDate, dayInterval);
}

/**
 * Set form values and trigger appropriate updates
 */
function setFormValues(state, station, variable, startDate, dayInterval) {
    if (state && stateSelect) {
        stateSelect.value = state;
        handleStateChange().then(() => {
            if (station && stationSelect) {
                // Wait a bit for stations to load, then set station
                setTimeout(() => {
                    stationSelect.value = station;
                    handleStationChange().then(() => {
                        if (variable && variableSelect) {
                            // Wait for variables to load, then set variable
                            setTimeout(() => {
                                variableSelect.value = variable;
                                if (dateInput && startDate) dateInput.value = startDate;
                                if (dayIntervalInput && dayInterval) dayIntervalInput.value = dayInterval;
                                updateImage();
                            }, 100);
                        }
                    });
                }, 100);
            }
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeForm);

// Export functions for potential external use
export { initializeForm, updateImage };
