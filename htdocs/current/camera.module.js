/**
 * Switch the archived checkbox to checked state
 */
export function switchToArchiveMode() {
    const isArchivedElement = document.getElementById('isarchived');
    if (isArchivedElement instanceof HTMLInputElement) {
        isArchivedElement.checked = true;
    }
}

/**
 * Set up event listeners for camera form controls
 */
function setupEventListeners() {
    // Get all the form controls that should trigger archive mode
    const formControls = [
        document.querySelector('select[name="year"]'),
        document.querySelector('select[name="month"]'),
        document.querySelector('select[name="day"]'),
        document.querySelector('select[name="hour"]'),
        document.querySelector('select[name="minute"]')
    ];

    // Add change event listeners to all form controls
    formControls.forEach(control => {
        if (control) {
            control.addEventListener('change', switchToArchiveMode);
        }
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', setupEventListeners);