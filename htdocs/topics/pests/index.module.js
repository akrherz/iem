// Pest Forecasting Maps - ES Module
import { 
    escapeHTML, 
    requireElement, 
    getElement,
    requireInputElement,
    getElementValue,
    setElementValue
} from '/js/iemjs/domUtils.js';

const pestData = {};
pestData.seedcorn_maggot = { 'gddbase': 39, 'gddceil': 84 };
pestData.alfalfa_weevil = { 'gddbase': 48, 'gddceil': 90 };
pestData.soybean_aphid = { 'gddbase': 50, 'gddceil': 90 };
pestData.common_stalk_borer = { 'gddbase': 41, 'gddceil': 90 };
pestData.japanese_beetle = { 'gddbase': 50, 'gddceil': 90 };
pestData.western_bean_cutworm = { 'gddbase': 38, 'gddceil': 75 };
pestData.european_corn_borer = { 'gddbase': 50, 'gddceil': 86 };

/**
 * Hide image loading indicator and show download links
 */
function hideImageLoad() {
    const willloadEl = getElement('willload');
    if (willloadEl) {
        willloadEl.style.display = 'none';
    }
    
    const theImageEl = getElement('theimage');
    const theDataEl = getElement('thedata');
    if (theImageEl && theDataEl) {
        const url = theImageEl.src.replace(".png", "");
        theDataEl.innerHTML = 
            `<p>Download point data: <a href="${url}.txt" class="btn btn-primary">` +
            '<i class="fa fa-table"></i> As CSV</a> &nbsp;' +
            `<a href="${url}.xlsx" class="btn btn-primary">` +
            '<i class="fa fa-table"></i> As Excel</a></p>';
    }
}

/**
 * Rectify start date based on selected pest
 */
function rectify_start_date(pest) {
    let month = (pest === "western_bean_cutworm") ? "03": "01"; // le sigh
    let day = "01";
    if (pest === "european_corn_borer") {
        month = "05";
        day = "20";
    }
    // Get the year from the edate input
    const edate = getElementValue('edate');
    if (edate) {
        const year = parseInt(edate.substring(0, 4), 10);
        setElementValue('sdate', `${year}-${month}-${day}`);
    }
}

/**
 * Update station forecast data using fetch API
 */
async function updateStationForecast() {
    const stationEl = document.querySelector('select[name="station"]');
    const pestEl = document.querySelector('select[name="pest"]');
    
    if (!stationEl) {
        return;
    }
    
    const station = escapeHTML(stationEl.value);
    const pest = escapeHTML(pestEl.value);
    const opts = pestData[pest];
    const sdate = escapeHTML(getElementValue('sdate'));
    const edate = escapeHTML(getElementValue('edate'));
    
    const url = `/json/climodat_dd.py?station=${station}&gddbase=${opts.gddbase}&gddceil=${opts.gddceil}&sdate=${sdate}&edate=${edate}`;
    
    try {
        const response = await fetch(url);
        const data = await response.json();
        
        // Update observed data
        const stationDateEl = requireElement('station_date');
        const stationAccumEl = requireElement('station_accum');
        stationDateEl.textContent = `${data.sdate} to ${data.edate}`;
        stationAccumEl.textContent = data.accum.toFixed(1);

        // Update GFS forecast
        const stationGfsDateEl = requireElement('station_gfs_date');
        const stationGfsAccumEl = requireElement('station_gfs_accum');
        const stationGfsTotalEl = requireElement('station_gfs_total');
        stationGfsDateEl.textContent = `${data.gfs_sdate} to ${data.gfs_edate}`;
        stationGfsAccumEl.textContent = `+${data.gfs_accum.toFixed(1)}`;
        stationGfsTotalEl.textContent = (data.accum + data.gfs_accum).toFixed(1);

        // Update NDFD forecast
        const stationNdfdDateEl = requireElement('station_ndfd_date');
        const stationNdfdAccumEl = requireElement('station_ndfd_accum');
        const stationNdfdTotalEl = requireElement('station_ndfd_total');
        stationNdfdDateEl.textContent = `${data.ndfd_sdate} to ${data.ndfd_edate}`;
        stationNdfdAccumEl.textContent = `+${data.ndfd_accum.toFixed(1)}`;
        stationNdfdTotalEl.textContent = (data.accum + data.ndfd_accum).toFixed(1);
    } catch {
        // Silently handle error - station forecast update failed
    }
}

/**
 * Update the pest map image and URL
 */
function updateImage() {
    showProgressBar();
    
    const theImageEl = requireElement('theimage');
    theImageEl.src = "/images/pixel.gif";
    
    const stationEl = document.querySelector('select[name="station"]');
    const pestEl = document.querySelector('select[name="pest"]');
    const networkEl = document.querySelector("select[name='network']");
    
    const station = escapeHTML(stationEl.value);
    const pest = escapeHTML(pestEl.value);

    // Hide all the pinfo containers
    document.querySelectorAll('.pinfo').forEach(el => {
        el.style.display = 'none';
    });

    // Show this pest's pinfo container
    const pestInfoEl = getElement(pest);
    if (pestInfoEl) {
        pestInfoEl.style.display = 'block';
    }
    
    const opts = pestData[pest];
    const sdate = escapeHTML(getElementValue('sdate'));
    const edate = escapeHTML(getElementValue('edate'));
    let state = networkEl ? escapeHTML(networkEl.value) : "IA";
    state = (state !== undefined) ? state.substring(0, 2) : "IA";
    
    const imgurl = `/plotting/auto/plot/97/d:sector::sector:${state}::var:gdd_sum::gddbase:${opts.gddbase}::gddceil:${opts.gddceil}::date1:${sdate}::usdm:no::date2:${edate}::p:contour::cmap:RdYlBu_r::c:yes::_r:43.png`;
    
    theImageEl.src = imgurl;

    // Update the web browser URL
    let url = `/topics/pests/?state=${state}&pest=${pest}&sdate=${sdate}&station=${station}`;
    // is edate_off checked?
    const edateOffEl = requireInputElement('edate_off');
    if (!edateOffEl.checked) {
        url += `&edate=${edate}`;
    }
    window.history.pushState({}, "", url);
    updateStationForecast();
}

/**
 * Show progress bar animation
 */
function showProgressBar() {
    const willloadEl = requireElement('willload');
    willloadEl.style.display = 'block';
    
    let timing = 0;
    const progressBar = setInterval(() => {
        const willloadDisplay = getElement('willload');
        if (timing >= 10 || (willloadDisplay && willloadDisplay.style.display === 'none')) {
            clearInterval(progressBar);
        }
        const width = (timing / 10) * 100.0;
        const timingBarEl = requireElement('timingbar');
        timingBarEl.style.width = `${width}%`;
        timingBarEl.setAttribute('aria-valuenow', width.toString());
        timing = timing + 0.2;
    }, 200);
}

/**
 * Simple date picker functionality (replacing jQuery UI datepicker)
 */
function setupDatePicker(elementId, onChangeCallback) {
    const element = requireInputElement(elementId);
    
    // Set basic date input properties
    element.type = 'date';
    element.min = '1893-01-01';
    element.max = new Date().toISOString().split('T')[0]; // Today's date
    
    // Add change event listener
    element.addEventListener('change', onChangeCallback);
}

/**
 * Setup UI event handlers
 */
function setupUI() {
    const theImageEl = requireElement('theimage');
    theImageEl.addEventListener('load', hideImageLoad);
    theImageEl.addEventListener('error', hideImageLoad);
    
    // The image may be cached and return to the user before this javascript
    // is hit, so we do a check to see if it is indeed loaded now
    if (theImageEl.complete) {
        hideImageLoad();
    }

    // Setup date pickers
    setupDatePicker('edate', updateImage);
    setupDatePicker('sdate', updateImage);

    // Setup station dropdown change handler
    const stationEl = document.querySelector('select[name="station"]');;
    stationEl.addEventListener('change', updateStationForecast);
}

/**
 * Update pest selection and related UI
 */
function updatePest() {
    const pestEl = document.querySelector('select[name="pest"]');;
    const pest = escapeHTML(pestEl.value);
    rectify_start_date(pest);
    updateImage();
}

/**
 * Global function for pest updates (called from PHP-generated onchange)
 */
window.updatePest = updatePest;

/**
 * Initialize the application
 */
function init() {
    updateImage();
    updateStationForecast();
    showProgressBar();
    setupUI();
}

// Initialize when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    // DOM already loaded
    init();
}
