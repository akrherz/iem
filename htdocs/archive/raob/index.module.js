
/**
 * Initialize datetime input fields with appropriate defaults and constraints
 */
function initializeDateTimeInputs() {
    // Find all elements that were previously using flatpickr
    const dateInputs = document.querySelectorAll('.fdp');
    
    // Set minimum date to 1947-02-01 (consistent with original flatpickr config)
    const minDateTime = '1947-02-01T00:00';
    
    dateInputs.forEach(input => {
        // Convert to datetime-local input type for native browser support
        input.type = 'datetime-local';
        input.min = minDateTime;
        
        // Set default value if empty
        if (!input.value) {
            // Set default to current date/time for better UX
            const now = new Date();
            const year = now.getFullYear();
            const month = String(now.getMonth() + 1).padStart(2, '0');
            const day = String(now.getDate()).padStart(2, '0');
            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            
            input.value = `${year}-${month}-${day}T${hours}:${minutes}`;
        }
    });
}

/**
 * Initialize the RAOB archive page functionality
 */
function init() {
    initializeDateTimeInputs();
}

// Initialize when DOM is loaded
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
} else {
    init();
}

export { init, initializeDateTimeInputs };