// SPC Watches Tabulator implementation - Bootstrap 5 compatible
import { TabulatorFull as Tabulator } from 'https://unpkg.com/tabulator-tables@6.3.1/dist/js/tabulator_esm.min.js';

document.addEventListener('DOMContentLoaded', () => {
    const tableElement = document.getElementById('watchesTable');

    if (tableElement) {
        // Small delay to ensure DOM is fully rendered
        setTimeout(() => {
            // Get existing table headers
            const headers = Array.from(tableElement.querySelectorAll('thead th')).map(th => th.textContent.trim());
            
            const table = new Tabulator(tableElement, {
                height: "70vh",
                layout: "fitColumns",
                virtualDomBuffer: 50,
                headerFilter: true,
                downloadConfig: {
                    columnHeaders: true,
                    columnGroups: false,
                    rowGroups: false,
                    columnCalcs: false,
                },
                initialSort: [
                    {column: "col_3", dir: "desc"}, // Sort by Issued date (newest first)
                ],
                columns: headers.map((header, index) => {
                    const baseConfig = {
                        title: header,
                        field: `col_${index}`,
                        formatter: index === 1 ? "html" : undefined, // Watch Num column has HTML links and badges
                        headerFilterLiveFilter: false, // Reduce API calls while typing
                    };
                    
                    // Special handling for States column (index 2)
                    if (index === 2) {
                        baseConfig.headerFilter = "input";
                        baseConfig.headerFilterFunc = (headerValue, rowValue) => {
                            if (!headerValue) return true;
                            // Convert both to uppercase for case-insensitive search
                            const searchTerm = headerValue.toUpperCase();
                            const states = rowValue.toUpperCase();
                            
                            // Check if search term matches any state in the CSV list
                            return states.split(',').some(state => 
                                state.trim().includes(searchTerm)
                            );
                        };
                        baseConfig.headerFilterPlaceholder = "e.g. IA, NE";
                    }
                    
                    // Date/time columns - better filtering
                    if (index === 3 || index === 4) { // Issued, Expired columns
                        baseConfig.headerFilterPlaceholder = "YYYY-MM-DD";
                    }
                    
                    // Numeric columns - number filtering
                    if (index >= 5 && index <= 8) { // Tornado, Hail prob, Max hail, Wind columns
                        baseConfig.headerFilterFunc = ">=";
                        baseConfig.headerFilterPlaceholder = "min value";
                    }
                    
                    return baseConfig;
                }),
                // Add data loading indicators
                dataLoaded: () => {
                    // Data loaded successfully - could add UI feedback here if needed
                },
                renderComplete: () => {
                    // Add tooltips to PDS badges
                    document.querySelectorAll('.badge.bg-danger').forEach(badge => {
                        badge.title = "Particularly Dangerous Situation - Enhanced risk warning";
                    });
                },
            });
            
            // Make table available globally for debugging and export functionality
            window.watchesTable = table;
            
            // Add export functionality
            // Create export buttons
            const exportButtonsContainer = document.createElement('div');
            exportButtonsContainer.className = 'export-buttons mb-3 text-end';
            exportButtonsContainer.innerHTML = 
                '<div class="btn-group" role="group" aria-label="Export options">' +
                    '<button id="download-csv" class="btn btn-outline-success btn-sm">' +
                        '<i class="bi bi-file-earmark-spreadsheet me-1"></i>Download CSV' +
                    '</button>' +
                    '<button id="download-xlsx" class="btn btn-outline-primary btn-sm">' +
                        '<i class="bi bi-file-earmark-excel me-1"></i>Download Excel' +
                    '</button>' +
                '</div>';
            
            // Insert export buttons before the table
            tableElement.parentNode.insertBefore(exportButtonsContainer, tableElement);
            
            // Add event listeners for export buttons
            document.getElementById('download-csv').addEventListener('click', () => {
                const year = new URLSearchParams(window.location.search).get('year') || new Date().getFullYear();
                window.watchesTable.download("csv", `spc_watches_${year}.csv`);
            });
            
            document.getElementById('download-xlsx').addEventListener('click', () => {
                const year = new URLSearchParams(window.location.search).get('year') || new Date().getFullYear();
                window.watchesTable.download("xlsx", `spc_watches_${year}.xlsx`, {sheetName: `SPC Watches ${year}`});
            });
        }, 100);
    }
});
