/* global ol */
let renderattr = 'pday';
let map = null;
let coopLayer = null;
let azosLayer = null;
let mrmsLayer = null;
let cocorahsLayer = null;
const DATE_MIN = '2009-02-01';
const ATTR_CONFIG = {
    pday: {
        badge: 'Precipitation',
        legendText:
            'MRMS 24-hour precipitation is shown as the background raster for comparison against station reports.',
        media:
            '<img src="/images/mrms_q3_p24h.png" alt="Legend for MRMS 24 hour precipitation" class="img-fluid" loading="lazy" decoding="async">',
    },
    snow: {
        badge: 'Snowfall',
        legendText:
            'Snowfall values come from station reports. No gridded snowfall legend is shown in this comparison view.',
        media:
            '<span class="small text-muted">Compare snowfall totals across COOP, CoCoRaHS, and ASOS/AWOS stations.</span>',
    },
    snowd: {
        badge: 'Snow Depth',
        legendText:
            'Snow depth values come from station reports and are best interpreted as point observations rather than a continuous surface.',
        media:
            '<span class="small text-muted">Use station density and nearby reports to judge representativeness.</span>',
    },
    high: {
        badge: 'High Temperature',
        legendText:
            'High temperature values are station-based daily extremes for the 24-hour period ending near 7 AM local time.',
        media:
            '<span class="small text-muted">The MRMS raster is not used for temperature parameters.</span>',
    },
    low: {
        badge: 'Low Temperature',
        legendText:
            'Low temperature values are station-based daily extremes for the 24-hour period ending near 7 AM local time.',
        media:
            '<span class="small text-muted">Compare station-to-station gradients instead of expecting a continuous field.</span>',
    },
    coop_tmpf: {
        badge: 'Observation Temperature',
        legendText:
            'Observation-time temperature is the reading near the 7 AM report time for each station.',
        media:
            '<span class="small text-muted">This parameter highlights observation-time differences among reporting networks.</span>',
    },
};
let pendingLoads = 0;
let pendingSuccessMessage = 'Map updated.';

/**
 * Replace HTML special characters with their entity equivalents
 * @param string val
 * @returns string converted string
 */
function escapeHTML(val) {
    if (val === null || val === undefined) {
        return '';
    }
    return val
        .toString()
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function getAttrConfig(attr) {
    return ATTR_CONFIG[attr] || ATTR_CONFIG.pday;
}

function clampDateString(dateStr) {
    const maxDate = formatDateISO(new Date());
    if (dateStr < DATE_MIN) {
        return DATE_MIN;
    }
    if (dateStr > maxDate) {
        return maxDate;
    }
    return dateStr;
}

function showStatus(message, type = 'secondary') {
    const status = document.getElementById('status');
    if (!(status instanceof HTMLElement)) {
        return;
    }
    if (!message) {
        status.textContent = '';
        status.className = 'alert alert-secondary py-2 px-3 small mb-3 d-none';
        return;
    }
    status.textContent = message;
    status.className = `alert alert-${type} py-2 px-3 small mb-3`;
}

function setMapLoadingState(isLoading) {
    const mapElement = document.getElementById('map');
    if (!(mapElement instanceof HTMLElement)) {
        return;
    }
    mapElement.classList.toggle('map-loading', isLoading);
}

function startLoading(message, successMessage) {
    pendingLoads += 1;
    pendingSuccessMessage = successMessage;
    setMapLoadingState(true);
    showStatus(message, 'secondary');
}

function finishLoading() {
    pendingLoads = Math.max(0, pendingLoads - 1);
    if (pendingLoads === 0) {
        setMapLoadingState(false);
        showStatus(pendingSuccessMessage, 'success');
    }
}

function failLoading(message) {
    pendingLoads = 0;
    setMapLoadingState(false);
    showStatus(message, 'danger');
}

function updateLegend() {
    const legendBadge = document.getElementById('legend-badge');
    const legendText = document.getElementById('legend-text');
    const legendMedia = document.getElementById('legend-media');
    const config = getAttrConfig(renderattr);
    if (legendBadge) {
        legendBadge.textContent = config.badge;
    }
    if (legendText) {
        legendText.textContent = config.legendText;
    }
    if (legendMedia) {
        legendMedia.innerHTML = config.media;
    }
}

function registerSourceEvents(source, label) {
    if (!source || typeof source.on !== 'function') {
        return;
    }
    const isVectorSource = typeof source.getFormat === 'function';
    const startEvent = isVectorSource ? 'featuresloadstart' : 'tileloadstart';
    const endEvent = isVectorSource ? 'featuresloadend' : 'tileloadend';
    const errorEvent = isVectorSource ? 'featuresloaderror' : 'tileloaderror';

    source.on(startEvent, () => {
        startLoading(`Loading ${label}...`, 'Map data updated.');
    });
    source.on(endEvent, () => {
        finishLoading();
    });
    source.on(errorEvent, () => {
        failLoading(`${label} failed to load.`);
    });
}

function buildVectorSource(dt, group, label) {
    const source = new ol.source.Vector({
        format: new ol.format.GeoJSON(),
        projection: ol.proj.get('EPSG:3857'),
        url: `/geojson/7am.py?group=${group}&dt=${dt}`,
    });
    registerSourceEvents(source, label);
    return source;
}

function buildMrmsSource() {
    const source = new ol.source.XYZ({
        url: get_tms_url(),
    });
    registerSourceEvents(source, 'MRMS background');
    return source;
}

function formatValidTime(valid) {
    if (!valid) {
        return 'Unknown';
    }
    const timestamp = new Date(valid);
    if (Number.isNaN(timestamp.getTime())) {
        return escapeHTML(valid);
    }
    return timestamp.toLocaleString();
}

function buildPopupContent(feature) {
    const link = `/sites/site.php?station=${feature.getId()}&network=${feature.get('network')}`;
    return [
        '<div class="popup-card">',
        '<button type="button" class="btn-close popup-close" aria-label="Close station details"></button>',
        `<div class="small text-uppercase text-muted mb-1">${escapeHTML(feature.get('network'))}</div>`,
        `<h3 class="h6 mb-3"><a href="${link}" target="_blank" rel="noopener">${escapeHTML(feature.getId())}</a> ${escapeHTML(feature.get('name'))}</h3>`,
        '<dl class="popup-metrics">',
        `<dt>Hour of Ob</dt><dd>${pretty(feature.get('hour'))}</dd>`,
        `<dt>High</dt><dd>${pretty(feature.get('high'))}</dd>`,
        `<dt>Low</dt><dd>${pretty(feature.get('low'))}</dd>`,
        `<dt>Temp at Ob</dt><dd>${pretty(feature.get('coop_tmpf'))}</dd>`,
        `<dt>Precip</dt><dd>${pretty(feature.get('pday'))}</dd>`,
        `<dt>Snow</dt><dd>${pretty(feature.get('snow'))}</dd>`,
        `<dt>Snow Depth</dt><dd>${pretty(feature.get('snowd'))}</dd>`,
        `<dt>Valid</dt><dd>${formatValidTime(feature.get('valid'))}</dd>`,
        '</dl>',
        '</div>',
    ].join('');
}

/**
 * Format date as YYMMDD string
 * @param {Date} date
 * @returns {string}
 */
function formatDateYYMMDD(date) {
    const year = date.getFullYear().toString().substring(2);
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const day = date.getDate().toString().padStart(2, '0');
    return year + month + day;
}

/**
 * Format date as YYYY-MM-DD string
 * @param {Date} date
 * @returns {string}
 */
function formatDateISO(date) {
    const year = date.getFullYear();
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const day = date.getDate().toString().padStart(2, '0');
    return `${year}-${month}-${day}`;
}

/**
 * Parse YYMMDD string to Date object
 * @param {string} dateStr
 * @returns {Date}
 */
function parseDateYYMMDD(dateStr) {
    const year = parseInt(`20${dateStr.substring(0, 2)}`, 10);
    const month = parseInt(dateStr.substring(2, 4), 10) - 1;
    const day = parseInt(dateStr.substring(4, 6), 10);
    return new Date(year, month, day);
}

/**
 * Parse YYYY-MM-DD string to Date object without timezone issues
 * @param {string} dateStr
 * @returns {Date}
 */
function parseDateISO(dateStr) {
    const parts = dateStr.split('-');
    const year = parseInt(parts[0], 10);
    const month = parseInt(parts[1], 10) - 1;
    const day = parseInt(parts[2], 10);
    return new Date(year, month, day);
}

/**
 * Add days to a date string without timezone issues
 * @param {string} dateStr - YYYY-MM-DD format
 * @param {number} days - Number of days to add (can be negative)
 * @returns {string} - New date in YYYY-MM-DD format
 */
function addDaysToDateString(dateStr, days) {
    const date = parseDateISO(dateStr);
    date.setDate(date.getDate() + days);
    return formatDateISO(date);
}

/**
 * Migrate legacy hash URLs to URLSearchParams
 * This maintains backward compatibility with old bookmarked URLs
 * Legacy format: #240610/pday
 * New format: ?date=240610&attr=pday
 */
function migrateLegacyHashURLs() {
    const hash = window.location.hash;
    if (hash && hash.length > 1) {
        const hashContent = hash.substring(1); // Remove the # character
        const subtokens = hashContent.split('/');

        if (subtokens.length >= 1) {
            const url = new URL(window.location);

            // Clear the hash and set as URL parameters
            url.hash = '';
            url.searchParams.set('date', subtokens[0]);

            if (subtokens.length > 1) {
                url.searchParams.set('attr', subtokens[1]);
            }

            // Replace the URL without adding to history
            window.history.replaceState({}, '', url);

            return {
                date: subtokens[0],
                attr: subtokens.length > 1 ? subtokens[1] : null
            };
        }
    }
    return null;
}

/**
 * Parse URL parameters to set initial state
 * Handles both URLSearchParams and legacy hash URLs (with migration)
 */
function parseURLParams() {
    // First, check for legacy hash URLs and migrate them
    const migrated = migrateLegacyHashURLs();

    // Get current URL parameters (either from migration or existing params)
    const params = new URLSearchParams(window.location.search);
    const dateParam = params.get('date') || (migrated?.date);
    const attrParam = params.get('attr') || (migrated?.attr);

    if (Object.hasOwn(ATTR_CONFIG, attrParam ?? '')) {
        renderattr = attrParam;
        const renderAttrElement = document.getElementById('renderattr');
        if (renderAttrElement instanceof HTMLSelectElement) {
            renderAttrElement.value = renderattr;
        }
    }

    if (/^\d{6}$/.test(dateParam ?? '')) {
        const dt = parseDateYYMMDD(dateParam);
        const datepickerElement = document.getElementById('datepicker');
        if (datepickerElement instanceof HTMLInputElement) {
            datepickerElement.value = clampDateString(formatDateISO(dt));
        }
    }
}

/**
 * Update URL with current parameters using URLSearchParams
 */
function updateURL() {
    const datepickerElement = document.getElementById('datepicker');
    if (!(datepickerElement instanceof HTMLInputElement)) {return;}

    // Use parseDateISO to avoid timezone issues instead of new Date()
    const selectedDate = parseDateISO(datepickerElement.value);
    const tt = formatDateYYMMDD(selectedDate);

    const url = new URL(window.location);
    url.searchParams.set('date', tt);
    url.searchParams.set('attr', renderattr);

    // Clear any legacy hash
    url.hash = '';

    // Update URL without page reload
    window.history.replaceState({}, '', url);
}

function updateMap() {
    const renderattrElement = document.getElementById('renderattr');
    if (renderattrElement instanceof HTMLSelectElement) {
        renderattr = Object.hasOwn(ATTR_CONFIG, renderattrElement.value) ? renderattrElement.value : 'pday';
    }
    coopLayer.setStyle(coopLayer.getStyle());
    azosLayer.setStyle(azosLayer.getStyle());
    cocorahsLayer.setStyle(cocorahsLayer.getStyle());
    updateLegend();
    updateURL();
    const label = renderattrElement?.selectedOptions?.[0]?.text || renderattr;
    showStatus(`Parameter updated: ${label}`, 'success');
}

function updateDate() {
    const datepickerElement = document.getElementById('datepicker');
    if (!(datepickerElement instanceof HTMLInputElement)) {return;}

    datepickerElement.value = clampDateString(datepickerElement.value);
    const fullDate = formatDateISO(parseDateISO(datepickerElement.value));

    cocorahsLayer.setSource(buildVectorSource(fullDate, 'cocorahs', 'CoCoRaHS reports'));
    coopLayer.setSource(buildVectorSource(fullDate, 'coop', 'COOP reports'));
    azosLayer.setSource(buildVectorSource(fullDate, 'azos', 'ASOS/AWOS reports'));
    mrmsLayer.setSource(buildMrmsSource());
    updateURL();
    showStatus(`Loading map data for ${fullDate}...`, 'secondary');
    const plusDayElement = document.getElementById('plusday');
    const minusDayElement = document.getElementById('minusday');
    if (plusDayElement instanceof HTMLButtonElement) {
        plusDayElement.disabled = datepickerElement.value >= formatDateISO(new Date());
    }
    if (minusDayElement instanceof HTMLButtonElement) {
        minusDayElement.disabled = datepickerElement.value <= DATE_MIN;
    }
}

function pretty(val) {
    if (val === null || val === undefined) {return 'M';}
    if (val === 0.0001) {return 'T';}
    return val;
}

function makeVectorLayer(dt, title, group) {
    return new ol.layer.Vector({
        title,
        source: buildVectorSource(dt, group, title),
        style(feature) {
            let txt = feature.get(renderattr) === 0.0001 ? 'T' : feature.get(renderattr);
            txt = txt === null || txt === undefined ? '.' : txt;
            return [
                new ol.style.Style({
                    text: new ol.style.Text({
                        font: '14px Calibri,sans-serif',
                        text: txt.toString(),
                        stroke: new ol.style.Stroke({
                            color: '#fff',
                            width: 3,
                        }),
                        fill: new ol.style.Fill({
                            color: 'black',
                        }),
                    }),
                }),
            ];
        },
    });
}
function get_tms_url() {
    const datepickerElement = document.getElementById('datepicker');
    if (!(datepickerElement instanceof HTMLInputElement)) {return '';}

    const selectedDate = parseDateISO(datepickerElement.value);
    const dateStr = formatDateISO(selectedDate);
    return `https://mesonet.agron.iastate.edu/cache/tile.py/1.0.0/idep0::mrms-12z24h::${dateStr}/{z}/{x}/{y}.png`;
}

function buildUI() {
    const renderAttrElement = document.getElementById('renderattr');
    if (renderAttrElement) {
        renderAttrElement.addEventListener('change', () => {
            updateMap();
        });
    }

    // Set up date input with HTML5 date type
    const datepickerElement = document.getElementById('datepicker');
    if (datepickerElement instanceof HTMLInputElement) {
        datepickerElement.type = 'date';
        datepickerElement.min = DATE_MIN;
        datepickerElement.max = formatDateISO(new Date());
        datepickerElement.value = formatDateISO(new Date());
        datepickerElement.addEventListener('change', () => {
            updateDate();
        });
    }

    const minusDayElement = document.getElementById('minusday');
    if (minusDayElement) {
        minusDayElement.addEventListener('click', (event) => {
            event.preventDefault(); // Prevent form submission
            const datepicker = document.getElementById('datepicker');
            if (datepicker instanceof HTMLInputElement) {
                if (datepicker.value) {
                    datepicker.value = clampDateString(
                        addDaysToDateString(datepicker.value, -1)
                    );
                    updateDate();
                }
            }
        });
    }

    const plusDayElement = document.getElementById('plusday');
    if (plusDayElement) {
        plusDayElement.addEventListener('click', (event) => {
            event.preventDefault(); // Prevent form submission
            const datepicker = document.getElementById('datepicker');
            if (datepicker instanceof HTMLInputElement) {
                if (datepicker.value) {
                    datepicker.value = clampDateString(
                        addDaysToDateString(datepicker.value, 1)
                    );
                    updateDate();
                }
            }
        });
    }
}
document.addEventListener('DOMContentLoaded', () => {
    buildUI();
    parseURLParams();
    updateLegend();

    const datepickerElement = document.getElementById('datepicker');
    let currentDate = formatDateISO(new Date());
    if (datepickerElement instanceof HTMLInputElement) {
        if (datepickerElement.value) {
            currentDate = datepickerElement.value;
        }
    }

    cocorahsLayer = makeVectorLayer(currentDate, 'IA CoCoRaHS Reports', 'cocorahs');
    coopLayer = makeVectorLayer(currentDate, 'NWS COOP Reports', 'coop');
    azosLayer = makeVectorLayer(currentDate, 'ASOS/AWOS Reports', 'azos');

    mrmsLayer = new ol.layer.Tile({
        title: 'MRMS 12z 24 Hour',
        source: buildMrmsSource(),
    });

    map = new ol.Map({
        target: 'map',
        layers: [
            mrmsLayer,
            new ol.layer.Tile({
                title: 'County Boundaries',
                source: new ol.source.XYZ({
                    url: '/c/tile.py/1.0.0/uscounties/{z}/{x}/{y}.png',
                }),
            }),
            new ol.layer.Tile({
                title: 'State Boundaries',
                source: new ol.source.XYZ({
                    url: '/c/tile.py/1.0.0/usstates/{z}/{x}/{y}.png',
                }),
            }),
            new ol.layer.Tile({
                title: 'NWS CWA Boundaries',
                source: new ol.source.XYZ({
                    url: '/c/tile.py/1.0.0/wfo/{z}/{x}/{y}.png',
                }),
            }),
            cocorahsLayer,
            coopLayer,
            azosLayer,
        ],
        view: new ol.View({
            projection: 'EPSG:3857',
            center: [-10505351, 5160979],
            zoom: 7,
        }),
    });

    const layerSwitcher = new ol.control.LayerSwitcher();
    map.addControl(layerSwitcher);

    const element = document.getElementById('popup');

    const popup = new ol.Overlay({
        element,
        positioning: 'bottom-center',
        stopEvent: false,
    });
    map.addOverlay(popup);

    // Simple popover implementation to replace Bootstrap popover
    let popoverVisible = false;

    function showPopover(content) {
        if (element) {
            element.innerHTML = content;
            element.classList.add('popup-visible');
            popoverVisible = true;
        }
    }

    function hidePopover() {
        if (element && popoverVisible) {
            element.classList.remove('popup-visible');
            element.innerHTML = '';
            popoverVisible = false;
        }
    }

    // display popup on click
    map.on('click', evt => {
        const feature = map.forEachFeatureAtPixel(evt.pixel, feature2 => {
            return feature2;
        });
        if (feature) {
            const geometry = feature.getGeometry();
            const coord = geometry.getCoordinates();
            popup.setPosition(coord);
            showPopover(buildPopupContent(feature));
        } else {
            hidePopover();
        }
    });

    if (element) {
        element.addEventListener('click', evt => {
            const target = evt.target;
            if (target instanceof HTMLElement && target.closest?.('.popup-close')) {
                hidePopover();
            }
        });
    }

    document.addEventListener('keydown', evt => {
        if (evt.key === 'Escape') {
            hidePopover();
        }
    });

    updateDate();
});
