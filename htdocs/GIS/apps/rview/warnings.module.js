
import { getElement } from '/js/iemjs/domUtils.js';

const CONTROL_PANELS = [
    'layers-control',
    'locations-control',
    'time-control',
    'options-control',
];

function setButtonExpanded(controlName, expanded) {
    const button = document.querySelector(`button[data-control="${controlName}"]`);
    if (button) {
        button.setAttribute('aria-expanded', expanded ? 'true' : 'false');
    }
}

/**
 * Show or hide control panels
 * @param {string} layerName ID of the control panel to toggle
 */
function showControl(layerName) {
    const targetElement = getElement(layerName);
    const oldval = targetElement ? targetElement.style.display : 'none';

    // Hide all control panels
    CONTROL_PANELS.forEach((panelId) => {
        setLayerDisplay(panelId, 'none');
        setButtonExpanded(panelId.replace('-control', ''), false);
    });

    // Show the target panel if it was hidden
    if (oldval === 'none') {
        setLayerDisplay(layerName, 'block');
        setButtonExpanded(layerName.replace('-control', ''), true);
        targetElement?.querySelector('input, select, button, textarea')?.focus();
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
        element.hidden = displayValue === 'none';
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
            button.addEventListener('click', () => {
                const controlType = button.getAttribute('data-control');
                if (controlType) {
                    showControl(`${controlType}-control`);
                }
            });
        });
    }

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            CONTROL_PANELS.forEach((panelId) => {
                setLayerDisplay(panelId, 'none');
                setButtonExpanded(panelId.replace('-control', ''), false);
            });
        }
    });

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
