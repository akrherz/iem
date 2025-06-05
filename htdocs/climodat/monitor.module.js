
/**
 * Handle map station selection functionality
 */
function handleMapStationSelection() {
    const addMapStationsBtn = document.getElementById('addmapstations');
    if (addMapStationsBtn) {
        addMapStationsBtn.addEventListener('click', () => {
            const stationsOut = document.getElementById('stations_out');
            if (stationsOut) {
                stationsOut.setAttribute('name', 's[]');
            }
        });
    }
}

/**
 * Convert date format from HTML5 date input (YYYY-MM-DD) to PHP format (MM/DD/YYYY)
 */
function convertDateFormat(dateValue) {
    if (!dateValue) return null;
    
    const dateParts = dateValue.split('-');
    if (dateParts.length !== 3) return null;
    
    const [year, month, day] = dateParts;
    return `${month}/${day}/${year}`;
}

/**
 * Create hidden input element for form submission
 */
function createHiddenInput(name, value) {
    const hiddenInput = document.createElement('input');
    hiddenInput.type = 'hidden';
    hiddenInput.name = name;
    hiddenInput.value = value;
    return hiddenInput;
}

/**
 * Handle date format conversion for form submission
 */
function handleDateFormSubmission() {
    const dateForm = document.querySelector('form[name="dates"]');
    if (!dateForm) return;

    dateForm.addEventListener('submit', () => {
        const sdateInput = document.getElementById('sdate');
        const edateInput = document.getElementById('edate');

        // Handle start date conversion
        if (sdateInput && sdateInput instanceof HTMLInputElement && sdateInput.value) {
            const sdateFormatted = convertDateFormat(sdateInput.value);
            if (sdateFormatted) {
                const hiddenSdate = createHiddenInput('sdate', sdateFormatted);
                dateForm.appendChild(hiddenSdate);
                sdateInput.removeAttribute('name');
            }
        }

        // Handle end date conversion
        if (edateInput && edateInput instanceof HTMLInputElement && edateInput.value) {
            const edateFormatted = convertDateFormat(edateInput.value);
            if (edateFormatted) {
                const hiddenEdate = createHiddenInput('edate', edateFormatted);
                dateForm.appendChild(hiddenEdate);
                edateInput.removeAttribute('name');
            }
        }
    });
}

/**
 * Initialize the monitor page functionality
 */
function init() {
    handleMapStationSelection();
    handleDateFormSubmission();
}

// Initialize when DOM is loaded
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
} else {
    init();
}

export { init, handleMapStationSelection, handleDateFormSubmission, convertDateFormat };
