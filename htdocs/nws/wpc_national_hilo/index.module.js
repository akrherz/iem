// WPC National High/Low Temperature - Modern ES Module with API calls
import {TabulatorFull as Tabulator} from 'https://unpkg.com/tabulator-tables@6.3.1/dist/js/tabulator_esm.min.mjs';

let table = null;
const API_BASE_URL = '/api/1/nws/wpc_national_hilo.json';

// Validate raw data structure
function validateRawData(rawData) {
    return rawData?.data && Array.isArray(rawData.data) && rawData.data.length > 0;
}

// Create location string from row data
function createLocationString(row) {
    return `(${row.station || 'Unknown'}) ${row.name || 'Unknown'}, ${row.state || 'Unknown'}`;
}

// Initialize date entry if it doesn't exist
function initializeDateEntry(processedData, date) {
    if (!processedData.has(date)) {
        processedData.set(date, {
            date,
            min_temp: '',
            min_locations: [],
            max_temp: '',
            max_locations: []
        });
    }
    return processedData.get(date);
}

// Process a single row of temperature data
function processTemperatureRow(processedData, row) {
    if (!row || !row.date) {
        return; // Skip invalid rows
    }
    
    const date = row.date;
    const entry = initializeDateEntry(processedData, date);
    const locationString = createLocationString(row);
    
    if (row.n_x === 'N') {
        entry.min_temp = row.value || '';
        entry.min_locations.push(locationString);
    } else if (row.n_x === 'X') {
        entry.max_temp = row.value || '';
        entry.max_locations.push(locationString);
    }
}

// Convert processed data to display format
function convertToDisplayFormat(processedData) {
    return Array.from(processedData.values()).map(entry => ({
        date: entry.date,
        min_temp: entry.min_temp,
        min_locations: entry.min_locations.join('<br>'),
        max_temp: entry.max_temp,
        max_locations: entry.max_locations.join('<br>')
    })).sort((a, b) => new Date(b.date) - new Date(a.date)); // Sort by date descending
}

// Process raw API data into tabulator format
function processTableData(rawData) {
    // Check if we have valid data structure
    if (!validateRawData(rawData)) {
        return [];
    }

    const processedData = new Map();
    
    // Group data by date
    rawData.data.forEach(row => processTemperatureRow(processedData, row));
    
    // Convert Map to Array and format for display
    return convertToDisplayFormat(processedData);
}

// Format temperature values with color coding
function formatTemperature(cell, formatterParams) {
    const value = cell.getValue();
    if (!value) return '<span class="text-muted">—</span>';
    
    const tempClass = formatterParams.type === 'max' ? 'temp-high' : 'temp-low';
    return `<span class="${tempClass}">${value}°F</span>`;
}

// Format location lists
function formatLocations(cell) {
    const value = cell.getValue();
    if (!value) return '<span class="text-muted">No data</span>';
    
    return `<div class="location-list">${value}</div>`;
}

// Initialize Tabulator table
function initializeTable() {
    table = new Tabulator('#data-table', {
        layout: "fitColumns",
        placeholder: "No temperature data available for the selected criteria",
        height: "600px",
        columns: [
            {
                title: "Date", 
                field: "date", 
                sorter: "datetime",
                sorterParams: {
                    format: "yyyy-MM-dd",
                    alignEmptyValues: "bottom"
                },
                width: 120,
                headerSort: true
            },
            {
                title: "Min °F", 
                field: "min_temp", 
                formatter: formatTemperature,
                formatterParams: { type: 'min' },
                width: 100,
                headerSort: true,
                cssClass: "text-center"
            },
            {
                title: "Minimum Temperature Location(s)", 
                field: "min_locations", 
                formatter: formatLocations,
                headerSort: false,
                widthGrow: 2
            },
            {
                title: "Max °F", 
                field: "max_temp", 
                formatter: formatTemperature,
                formatterParams: { type: 'max' },
                width: 100,
                headerSort: true,
                cssClass: "text-center"
            },
            {
                title: "Maximum Temperature Location(s)", 
                field: "max_locations", 
                formatter: formatLocations,
                headerSort: false,
                widthGrow: 2
            }
        ],
        initialSort: [
            {column: "date", dir: "desc"}
        ]
    });
    
    return table;
}

// Update result count badge
function updateResultCount(count) {
    const badge = document.getElementById('result-count');
    if (badge) {
        badge.textContent = `${count} records`;
        badge.className = `badge ${count > 0 ? 'bg-success' : 'bg-secondary'} ms-2`;
    }
}

// Update page title
function updatePageTitle(title) {
    const titleElement = document.querySelector('.card-header h5');
    if (titleElement) {
        titleElement.innerHTML = `<i class="bi bi-table me-2"></i>${title} <span id="result-count" class="badge bg-light text-dark ms-2">Loading...</span>`;
    }
}

// Show loading state
function setLoadingState(isLoading) {
    const loadingIndicator = document.getElementById('loading-indicator');
    const submitButton = document.querySelector('#filter-form button[type="submit"]');
    
    if (loadingIndicator) {
        if (isLoading) {
            loadingIndicator.classList.remove('d-none');
        } else {
            loadingIndicator.classList.add('d-none');
        }
    }
    
    if (submitButton) {
        submitButton.disabled = isLoading;
        if (isLoading) {
            submitButton.innerHTML = '<i class="bi bi-arrow-clockwise me-2 spinner-border spinner-border-sm"></i>Loading...';
        } else {
            submitButton.innerHTML = '<i class="bi bi-arrow-clockwise me-2"></i>Update Table';
        }
    }
}

// Fetch data from API
async function fetchTableData(params) {
    setLoadingState(true);
    
    try {
        const url = new URL(API_BASE_URL, window.location.origin);
        
        // Add parameters to URL
        Object.keys(params).forEach(key => {
            if (params[key]) {
                url.searchParams.append(key, params[key]);
            }
        });
        
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data;
        
    } catch {
        updateResultCount(0);
        const badge = document.getElementById('result-count');
        if (badge) {
            badge.textContent = 'Error loading data';
            badge.className = 'badge bg-danger ms-2';
        }
        return { data: [] };
    } finally {
        setLoadingState(false);
    }
}

// Load and display data
async function loadTableData(params) {
    const rawData = await fetchTableData(params);
    const tableData = processTableData(rawData);
    
    // Load data into table
    table.setData(tableData);
    
    // Update result count
    updateResultCount(tableData.length);
    
    return tableData;
}

// Get form parameters
function getFormParams() {
    const form = document.getElementById('filter-form');
    const formData = new FormData(form);
    const params = {};
    
    const opt = formData.get('opt');
    if (opt === '1') {
        // By state
        const state = formData.get('state');
        if (state) {
            params.state = state;
        }
    } else {
        // By year
        const year = formData.get('year');
        if (year) {
            params.year = year;
        }
    }
    
    return params;
}

// Update page title based on current filter
function updateTitleFromParams(params) {
    let title = "WPC National High/Low Temperature Data";
    
    if (params.state) {
        title = `Entries for state: ${params.state}`;
    } else if (params.year) {
        title = `Entries for year: ${params.year}`;
    }
    
    updatePageTitle(title);
}

// Handle form submission
async function handleFormSubmit(event) {
    event.preventDefault();
    
    const params = getFormParams();
    updateTitleFromParams(params);
    
    // Update URL parameters
    const url = new URL(window.location);
    url.search = ''; // Clear existing params
    Object.keys(params).forEach(key => {
        if (params[key]) {
            url.searchParams.set(key, params[key]);
        }
    });
    
    // Add the opt parameter
    const opt = new FormData(document.getElementById('filter-form')).get('opt');
    url.searchParams.set('opt', opt);
    
    window.history.pushState({}, '', url);
    
    await loadTableData(params);
}

// Set up export functionality  
function setupExportButtons() {
    const excelBtn = document.getElementById('export-excel');
    const csvBtn = document.getElementById('export-csv');
    
    if (excelBtn) {
        excelBtn.addEventListener('click', () => {
            table.download("xlsx", "wpc_national_hilo.xlsx", {sheetName: "Temperature Data"});
        });
    }
    
    if (csvBtn) {
        csvBtn.addEventListener('click', () => {
            table.download("csv", "wpc_national_hilo.csv");
        });
    }
}

// Initialize the application
async function initializeApp() {
    // Initialize table
    initializeTable();
    
    // Setup form handler
    const form = document.getElementById('filter-form');
    if (form) {
        form.addEventListener('submit', handleFormSubmit);
    }
    
    // Setup export buttons
    setupExportButtons();
    
    // Load initial data
    const initialParamsScript = document.getElementById('initial-params');
    const titleScript = document.getElementById('page-title');
    
    if (initialParamsScript && titleScript) {
        try {
            const initialParams = JSON.parse(initialParamsScript.textContent);
            const initialTitle = JSON.parse(titleScript.textContent);
            
            updatePageTitle(initialTitle);
            await loadTableData(initialParams);
        } catch {
            // If parsing fails, load with current form values
            const params = getFormParams();
            updateTitleFromParams(params);
            await loadTableData(params);
        }
    } else {
        // Fallback: load with current form values
        const params = getFormParams();
        updateTitleFromParams(params);
        await loadTableData(params);
    }
}

// Initialize when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}