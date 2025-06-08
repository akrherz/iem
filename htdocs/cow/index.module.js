// COW (Cowley's Verification Application) - ES Module
// Provides checkbox selection functionality for LSR types and warning types

/**
 * Select all LSR (Local Storm Report) type checkboxes
 * Enables all available LSR report types for verification analysis
 */
const selectAllLSRTypes = () => {
    const lsrTypeIds = ["T", "D", "H", "G", "FF2", "MA2", "DS2", "SQ2"];
    lsrTypeIds.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.checked = true;
        }
    });
};

/**
 * Select all warning type checkboxes
 * Enables all available warning types for verification analysis
 */
const selectAllWarningTypes = () => {
    const warningTypeIds = ["TO", "SV", "MA", "FF", "DS", "SQ"];
    warningTypeIds.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.checked = true;
        }
    });
};

/**
 * Initialize event handlers when DOM is loaded
 * Sets up click handlers for select all buttons
 */
const init = () => {
    // Find all "Select All" buttons and determine their context
    const buttons = document.querySelectorAll('button');
    
    buttons.forEach(button => {
        if (button.textContent.trim() === 'Select All') {
            // Find the closest table row to determine context
            const row = button.closest('tr');
            if (row) {
                const header = row.querySelector('th');
                if (header) {
                    const headerText = header.textContent;
                    
                    if (headerText.includes('Warning Type')) {
                        button.addEventListener('click', (event) => {
                            event.preventDefault();
                            selectAllWarningTypes();
                        });
                    } else if (headerText.includes('LSR Type')) {
                        button.addEventListener('click', (event) => {
                            event.preventDefault();
                            selectAllLSRTypes();
                        });
                    }
                }
            }
        }
    });
};

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    // DOM already loaded
    init();
}

// Export functions for potential external use or testing
export { selectAllLSRTypes, selectAllWarningTypes, init };
