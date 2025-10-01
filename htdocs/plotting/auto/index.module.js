
import flatpickr from 'https://cdn.jsdelivr.net/npm/flatpickr@4.6.13/+esm';
import tomSelect from 'https://cdn.jsdelivr.net/npm/tom-select@2.4.3/+esm'

/**
 * Format state for colormap select dropdown
 * @param {Object} data - The select option data
 * @returns {string} HTML string for the option
 */
export function formatState(data) {
    return `<div><img src="/pickup/cmaps/${data.value}.png" /> ${data.text}</div>`;
}

/**
 * Handle network change events - submit form with wait indicator
 */
export function onNetworkChange() {
    const waitInput = document.getElementById('_wait');
    if (waitInput) {
        waitInput.value = 'yes';
    }
    const myForm = document.getElementById('myForm');
    if (myForm) {
        myForm.submit();
    }
}

/**
 * Hide the image loading indicator
 */
export function hideImageLoad() {
    const willload = document.getElementById('willload');
    if (willload) {
        willload.style.display = 'none';
    }
}

/**
 * Setup timing progress bar for image loading
 */
export function setupTiming() {
    const willload = document.getElementById("willload");
    if (!willload) return;
    if (!willload.dataset.timingsecs) return;

    const timingSecs = parseInt(willload.dataset.timingsecs, 10);
    let timing = 0;

    const progressBar = setInterval(() => {
        if (
            timing >= timingSecs ||
            document.getElementById('willload').style.display === 'none'
        ) {
            clearInterval(progressBar);
        }
        const width = (timing / timingSecs) * 100;
        const timingBar = document.getElementById('timingbar');
        timingBar.style.width = `${width}%`;
        timingBar.setAttribute('aria-valuenow', width);
        timing = timing + 0.2;
    }, 200);
}

/**
 * Create flatpickr instance for date/time inputs
 * @param {HTMLElement} inputelem - The input element to attach flatpickr to
 * @returns {Object} The flatpickr instance
 */
export function createFP(inputelem) {
    return flatpickr(inputelem, {
        dateFormat: inputelem.dataset.dateformat,
        defaultDate: inputelem.dataset.defaultdate,
        minDate: inputelem.dataset.mindate,
        maxDate: inputelem.dataset.maxdate,
        allowInput: true,
        time_24hr: true,
        enableTime: inputelem.dataset.dateformat.includes('H'),
        onChange: () => {
            if (inputelem.dataset.onc === 'true') {
                onNetworkChange();
            }
        }
    });
}

/**
 * Initialize optional controls
 */
function initOptionalControls() {
    document.querySelectorAll('.optcontrol').forEach(control => {
        control.addEventListener('change', () => {
            const targetEl = document.getElementById(control.name);
            if (targetEl) {
                targetEl.style.display = control.checked ? 'block' : 'none';
            }
        });
    });
}

/**
 * Initialize flatpickr date inputs
 */
function initDateInputs() {
    document.querySelectorAll('.apfp').forEach(createFP);
}

/**
 * Initialize image load handlers
 */
function initImageHandlers() {
    const theImage = document.getElementById('theimage');
    if (theImage) {
        theImage.addEventListener('load', hideImageLoad);
        theImage.addEventListener('error', hideImageLoad);

        // Check if image is already loaded (cached)
        if (theImage.complete) {
            hideImageLoad();
        }
    }
}

/**
 * Initialize colormap select dropdowns
 */
function initColormapSelects() {
    document.querySelectorAll('.cmapselect').forEach(el => {
        window.ts = new tomSelect(el, {
            maxOptions: 1000,
            render: {
                option: formatState,
                item: formatState,
            },
        });
    });
}

/**
 * Main initialization function
 */
function init() {
    setupTiming();
    initOptionalControls();
    initDateInputs();
    initImageHandlers();
    initColormapSelects();
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', init);
