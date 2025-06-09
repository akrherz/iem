// mcview.module.js - NEXRAD Mosaic Loop Application
// Provides functionality for switching between real-time and archive modes

/**
 * Switch the mode selector to archive mode when date/time controls are changed
 * This provides intuitive UX by automatically switching modes when users interact with date controls
 */
const switchToArchiveMode = () => {
    const modeSelect = document.querySelector('select[name="mode"]');
    if (modeSelect) {
        modeSelect.value = 'archive';
    }
};

/**
 * Initialize event handlers when DOM is loaded
 * Sets up change listeners for date/time controls to auto-switch to archive mode
 */
const init = () => {
    // Find all date and time related form controls
    const dateTimeControls = document.querySelectorAll(
        'select[name="year"], select[name="month"], select[name="day"], select[name="hour"], select[name="minute"]'
    );
    
    // Add change listeners to automatically switch to archive mode
    dateTimeControls.forEach(control => {
        control.addEventListener('change', switchToArchiveMode);
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
export { switchToArchiveMode, init };
