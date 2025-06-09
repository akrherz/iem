// watchwarn.module.js - NWS Watch, Warning, Advisory Download Interface
// Provides form submission functionality for different data formats

/**
 * Submit form with specified action URL and reset accept field
 * Used for KML and Shapefile downloads that require different endpoints
 */
const submitFormWithAction = (form, url) => {
    form.action = url;
    // Reset accept field to default 'shapefile' value for shapefile/KML requests
    const acceptField = document.getElementById('accept');
    if (acceptField) {
        acceptField.value = 'shapefile';
    }
    form.submit();
};

/**
 * Set the accept format and submit form
 * Updates the hidden accept field before form submission for CSV/Excel downloads
 */
const setAcceptAndSubmit = (form, acceptValue) => {
    const acceptField = document.getElementById('accept');
    if (acceptField) {
        acceptField.value = acceptValue;
    }
    form.submit();
};

/**
 * Initialize location group radio button functionality
 * Shows/hides appropriate select boxes based on radio button selection
 */
const initializeLocationGroups = () => {
    const locationRadios = document.querySelectorAll('input[name="location_group"]');
    const locationContainers = document.querySelectorAll('.location_group');

    // Function to update visibility based on selected radio
    const updateLocationVisibility = () => {
        const selectedValue = document.querySelector('input[name="location_group"]:checked')?.value;
        
        locationContainers.forEach(container => {
            const containerId = container.id;
            const shouldShow = containerId.endsWith(`-${selectedValue}`);
            
            // Show/hide with smooth transition
            container.style.display = shouldShow ? 'block' : 'none';
            container.style.opacity = shouldShow ? '1' : '0.5';
        });
    };

    // Add change listeners to radio buttons
    locationRadios.forEach(radio => {
        radio.addEventListener('change', updateLocationVisibility);
    });

    // Initialize visibility on page load
    updateLocationVisibility();
};

/**
 * Initialize event handlers when DOM is loaded
 * Sets up click handlers for form submission buttons and location group toggles
 */
const init = () => {
    // Find the main form
    const form = document.querySelector('form[action="/cgi-bin/request/gis/watchwarn.py"]');
    if (!form) return;

    // Handle Shapefile download button
    const shapefileBtn = form.querySelector('input[value="Request Shapefile"]');
    if (shapefileBtn) {
        shapefileBtn.addEventListener('click', (event) => {
            event.preventDefault();
            submitFormWithAction(form, '/cgi-bin/request/gis/watchwarn.py');
        });
    }

    // Handle CSV download button
    const csvBtn = form.querySelector('input[value="Request CSV"]');
    if (csvBtn) {
        csvBtn.addEventListener('click', (event) => {
            event.preventDefault();
            setAcceptAndSubmit(form, 'csv');
        });
    }

    // Handle Excel download button
    const excelBtn = form.querySelector('input[value="Request Excel"]');
    if (excelBtn) {
        excelBtn.addEventListener('click', (event) => {
            event.preventDefault();
            setAcceptAndSubmit(form, 'excel');
        });
    }

    // Handle KML download button
    const kmlBtn = form.querySelector('input[value*="Request KML"]');
    if (kmlBtn) {
        kmlBtn.addEventListener('click', (event) => {
            event.preventDefault();
            submitFormWithAction(form, '/kml/sbw_interval.php');
        });
    }

    // Initialize location group functionality
    initializeLocationGroups();
};



// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    // DOM already loaded
    init();
}

// Export functions for potential external use or testing
export { submitFormWithAction, setAcceptAndSubmit, init };