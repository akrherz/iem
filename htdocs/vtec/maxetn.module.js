// VTEC Max ETN Tabulator implementation
// Applies rules: jQuery removal, ES modules, avoid `this` usage
import { TabulatorFull as Tabulator } from 'https://unpkg.com/tabulator-tables@6.3.1/dist/js/tabulator_esm.min.mjs';

// Global state management
const state = {
    table: null,
    config: null
};

// Tabulator configuration
const tabulatorConfig = {
    layout: "fitColumns",
    pagination: "local",
    paginationSize: 20,
    paginationSizeSelector: [10, 20, 50, 100, true],
    movableColumns: true,
    resizableColumns: true,
    sortMode: "local",
    filterMode: "local",
    responsiveLayout: "hide",
    tooltips: true,
    clipboard: true,
    clipboardCopyHeader: true,
    placeholder: "No VTEC data available for this year",
    htmlOutputConfig: {
        columnHeaders: true,
        columnGroups: false,
        rowGroups: false,
        columnCalcs: false,
        dataTree: false
    },
    downloadConfig: {
        columnHeaders: true,
        columnGroups: false,
        rowGroups: false,
        columnCalcs: false,
        dataTree: false
    }
};

// HTML formatter for cells with links
function htmlFormatter(cell) {
    return cell.getValue();
}

// Initialize column definitions based on the data structure
function generateColumns(data) {
    if (!data || data.length === 0) return [];
    
    const columns = [];
    const firstRow = data[0];
    
    // Create columns based on the first row keys
    Object.keys(firstRow).forEach(key => {
        // Skip raw data fields (used for sorting)
        if (key.endsWith('_raw')) {
            return;
        }
        
        const column = {
            title: formatColumnTitle(key),
            field: key,
            sorter: "string",
            minWidth: getColumnWidth(key)
        };
        
        // Special handling for certain columns
        if (key === 'max_eventid' || key.includes('eventid')) {
            column.hozAlign = "right";
            column.formatter = htmlFormatter; // Allow HTML links
            // Custom sorter to use raw numeric value
            column.sorter = (a, b, aRow, bRow) => {
                const aVal = aRow.getData()[`${key}_raw`] || 0;
                const bVal = bRow.getData()[`${key}_raw`] || 0;
                return aVal - bVal;
            };
            // For CSV downloads, extract the numeric value
            column.accessorDownload = (value) => {
                const match = value.match(/>(\d+)</);
                return match ? parseInt(match[1], 10) : 0;
            };
        } else if (key === 'url') {
            column.visible = false; // Hide URL column as it's used for links
        } else if (key === 'wfo') {
            column.width = 80;
            column.headerFilter = "input";
        } else if (key === 'phenomena' || key === 'significance') {
            column.width = 100;
            column.headerFilter = "input";
        }
        
        columns.push(column);
    });
    
    return columns;
}

// Format column titles for display
function formatColumnTitle(key) {
    const titleMap = {
        'wfo': 'WFO',
        'phenomena': 'Phenomena',
        'significance': 'Significance',
        'max_eventid': 'Max Event ID',
        'url': 'URL'
    };
    
    return titleMap[key] || key.charAt(0).toUpperCase() + key.slice(1);
}

// Get appropriate column width based on content
function getColumnWidth(key) {
    const widthMap = {
        'wfo': 80,
        'phenomena': 120,
        'significance': 120,
        'max_eventid': 130,
        'url': 200
    };
    
    return widthMap[key] || 100;
}

// Process the raw JSON data for Tabulator
function processData(rawData) {
    if (!rawData.table || rawData.table.length === 0) {
        return [];
    }
    
    const columnNames = rawData.columns.map(col => col.name);
    
    return rawData.table.map(row => {
        const processedRow = {};
        
        row.forEach((value, index) => {
            const columnName = columnNames[index];
            
            // Special handling for max_eventid - create link if URL column exists
            if (columnName === 'max_eventid' && columnNames.includes('url')) {
                const urlIndex = columnNames.indexOf('url');
                const url = row[urlIndex];
                processedRow[columnName] = `<a href="${url}" class="btn btn-sm btn-outline-primary">${value}</a>`;
                // Store raw numeric value for sorting
                processedRow[`${columnName}_raw`] = parseInt(value, 10) || 0;
            } else if (columnName !== 'url') { // Skip URL column as it's used for links
                processedRow[columnName] = value;
            }
        });
        
        return processedRow;
    });
}

// Load data from the JSON API
async function loadData() {
    // Ensure we have current config
    if (!state.config) {
        state.config = getConfigFromForm();
    }
    
    const loadingIndicator = document.getElementById('loading-indicator');
    const errorMessage = document.getElementById('error-message');
    const tableContainer = document.getElementById('vtec-table');
    
    try {
        loadingIndicator.style.display = 'block';
        errorMessage.style.display = 'none';
        tableContainer.style.display = 'none';
        
        const response = await fetch(`/json/vtec_max_etn.py?year=${state.config.year}`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const rawData = await response.json();
        const processedData = processData(rawData);
        const columns = generateColumns(processedData);
        
        // Destroy existing table if it exists
        if (state.table) {
            state.table.destroy();
            state.table = null;
        }
        
        // Initialize Tabulator
        state.table = new Tabulator("#vtec-table", {
            ...tabulatorConfig,
            data: processedData,
            columns,
            initialSort: [
                { column: "wfo", dir: "asc" },
                { column: "phenomena", dir: "asc" },
                { column: "significance", dir: "asc" }
            ]
        });
        
        // Show table when built
        state.table.on("tableBuilt", () => {
            loadingIndicator.style.display = 'none';
            tableContainer.style.display = 'block';
            setupDownloadButtons();
        });
        
        // Handle empty data
        if (processedData.length === 0) {
            loadingIndicator.style.display = 'none';
            tableContainer.style.display = 'block';
        }
        
    } catch (error) {
        // Log error for debugging but show user-friendly message
        loadingIndicator.style.display = 'none';
        errorMessage.style.display = 'block';
        errorMessage.innerHTML = `
            <i class="bi bi-exclamation-triangle"></i> 
            Error loading data: ${error.message}. Please try again or contact support.
        `;
    }
}

// Setup download functionality
function setupDownloadButtons() {
    const downloadButtons = document.getElementById('download-buttons');
    const csvButton = document.getElementById('download-csv');
    const clipboardButton = document.getElementById('copy-clipboard');
    
    if (downloadButtons && csvButton && clipboardButton) {
        downloadButtons.style.display = 'block';
        
        csvButton.addEventListener('click', () => {
            const filename = `vtec-max-etn-${state.config.year}.csv`;
            state.table.download("csv", filename);
        });
        
        clipboardButton.addEventListener('click', () => {
            state.table.copyToClipboard("active");
            
            // Visual feedback
            const originalText = clipboardButton.innerHTML;
            clipboardButton.innerHTML = '<i class="bi bi-check"></i> Copied!';
            clipboardButton.classList.add('btn-success');
            clipboardButton.classList.remove('btn-secondary');
            
            setTimeout(() => {
                clipboardButton.innerHTML = originalText;
                clipboardButton.classList.remove('btn-success');
                clipboardButton.classList.add('btn-secondary');
            }, 2000);
        });
    }
}

// Initialize the application
function init() {
    // Get configuration from form elements
    state.config = getConfigFromForm();
    
    if (!state.config) {
        // Configuration missing - show error in UI instead of console
        const errorMessage = document.getElementById('error-message');
        if (errorMessage) {
            errorMessage.style.display = 'block';
            errorMessage.innerHTML = '<i class="bi bi-exclamation-triangle"></i> Configuration error. Please refresh the page.';
        }
        return;
    }

    // Set up form change handler for live updates
    setupFormHandler();

    // Load data when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', loadData);
    } else {
        loadData();
    }
}

// Get configuration from form elements
function getConfigFromForm() {
    const yearSelect = document.querySelector('select[name="year"]');
    if (!yearSelect) {
        return null;
    }
    
    return {
        year: parseInt(yearSelect.value, 10) || new Date().getFullYear()
    };
}

// Set up form handler for dynamic updates
function setupFormHandler() {
    const yearSelect = document.querySelector('select[name="year"]');
    const form = yearSelect?.closest('form');
    
    if (yearSelect) {
        yearSelect.addEventListener('change', () => {
            // Update configuration
            state.config.year = parseInt(yearSelect.value, 10);
            
            // Update page elements
            updatePageElements();
            
            // Reload data with new year 
            loadData();
        });
    }
    
    // Prevent form submission since we handle changes dynamically
    if (form) {
        form.addEventListener('submit', (event) => {
            event.preventDefault();
            // Trigger change event to reload data
            if (yearSelect) {
                yearSelect.dispatchEvent(new Event('change'));
            }
        });
    }
}

// Update page elements when year changes
function updatePageElements() {
    // Update the card title
    const cardTitle = document.querySelector('.card-title:not(.mb-0)');
    if (cardTitle?.textContent.includes('Max VTEC ETN Listing')) {
        cardTitle.textContent = `Max VTEC ETN Listing for ${state.config.year}`;
    }
    
    // Update the API URL display
    const apiUrlInput = document.querySelector('.input-group .form-control');
    if (apiUrlInput) {
        const newUrl = `/json/vtec_max_etn.py?year=${state.config.year}`;
        apiUrlInput.value = newUrl;
        
        // Update the copy button onclick
        const copyButton = apiUrlInput.nextElementSibling;
        if (copyButton) {
            copyButton.setAttribute('onclick', `navigator.clipboard.writeText('${newUrl}')`);
        }
    }
}

// Start the application
init();
