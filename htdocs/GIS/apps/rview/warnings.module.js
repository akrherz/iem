/**
 * Warnings Application - Vanilla JavaScript ES Module
 * Migrated from jQuery to vanilla JavaScript
 */

import { getElement } from '/js/iemjs/domUtils.js';

/**
 * Show or hide control panels
 * @param {string} layerName ID of the control panel to toggle
 */
function showControl(layerName) {
    const targetElement = getElement(layerName);
    const oldval = targetElement ? targetElement.style.display : 'none';
    
    // Hide all control panels
    setLayerDisplay("layers-control", 'none');
    setLayerDisplay("locations-control", 'none');
    setLayerDisplay("time-control", 'none');
    setLayerDisplay("options-control", 'none');
    
    // Show the target panel if it was hidden
    if (oldval === 'none') {
        setLayerDisplay(layerName, 'block');
    }
}

/**
 * Set display style for a layer element
 * @param {string} layerName ID of the element to modify
 * @param {string} displayValue CSS display value to set
 */
function setLayerDisplay(layerName, displayValue) {
    const element = getElement(layerName);
    if (element) {
        element.style.display = displayValue;
    }
}

/**
 * Initialize the application
 */
function init() {
    // Set up event listeners for control buttons
    const dataWindow = getElement('datawindow');
    if (dataWindow) {
        const buttons = dataWindow.querySelectorAll('button[data-control]');
        buttons.forEach(button => {
            button.addEventListener('click', (event) => {
                const controlType = event.target.getAttribute('data-control');
                if (controlType) {
                    showControl(`${controlType}-control`);
                }
            });
        });
    }

    // Set up auto-refresh for non-archive mode
    const urlParams = new URLSearchParams(window.location.search);
    if (!urlParams.has('archive')) {
        // Auto-refresh every 5 minutes if not in archive mode
        setTimeout(() => {
            const form = document.forms.myform;
            if (form) {
                form.submit();
            }
        }, 300000);
    }
}

// Initialize when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
