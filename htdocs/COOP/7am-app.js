/* global ol */
let renderattr = 'pday';
let map = null;
let coopLayer = null;
let azosLayer = null;
let mrmsLayer = null;
let cocorahsLayer = null;

/**
 * Replace HTML special characters with their entity equivalents
 * @param string val
 * @returns string converted string
 */
function escapeHTML(val) {
    return val
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
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
    const year = parseInt(parts[0]);
    const month = parseInt(parts[1]) - 1; // Month is 0-based
    const day = parseInt(parts[2]);
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
    
    if (attrParam) {
        renderattr = escapeHTML(attrParam);
        const renderAttrElement = document.getElementById('renderattr');
        if (renderAttrElement instanceof HTMLSelectElement) {
            renderAttrElement.value = renderattr;
        }
    }
    
    if (dateParam) {
        const dt = parseDateYYMMDD(escapeHTML(dateParam));
        const datepickerElement = document.getElementById('datepicker');
        if (datepickerElement instanceof HTMLInputElement) {
            datepickerElement.value = formatDateISO(dt);
        }
    }
}

/**
 * Update URL with current parameters using URLSearchParams
 */
function updateURL() {
    const datepickerElement = document.getElementById('datepicker');
    if (!(datepickerElement instanceof HTMLInputElement)) return;

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
        renderattr = escapeHTML(renderattrElement.value);
    }
    coopLayer.setStyle(coopLayer.getStyle());
    azosLayer.setStyle(azosLayer.getStyle());
    updateURL();
}

function updateDate() {
    // We have a changed date, hello!
    const datepickerElement = document.getElementById('datepicker');
    if (!(datepickerElement instanceof HTMLInputElement)) return;

    // Use parseDateISO to avoid timezone issues instead of new Date()
    const selectedDate = parseDateISO(datepickerElement.value);
    const fullDate = formatDateISO(selectedDate);

    // Create new sources with updated URLs to force refresh
    // This ensures OpenLayers actually fetches new data
    cocorahsLayer.setSource(new ol.source.Vector({
        format: new ol.format.GeoJSON(),
        projection: ol.proj.get('EPSG:3857'),
        url: `/geojson/7am.py?group=cocorahs&dt=${fullDate}`,
    }));
    
    coopLayer.setSource(new ol.source.Vector({
        format: new ol.format.GeoJSON(),
        projection: ol.proj.get('EPSG:3857'),
        url: `/geojson/7am.py?group=coop&dt=${fullDate}`,
    }));
    
    azosLayer.setSource(new ol.source.Vector({
        format: new ol.format.GeoJSON(),
        projection: ol.proj.get('EPSG:3857'),
        url: `/geojson/7am.py?group=azos&dt=${fullDate}`,
    }));

    mrmsLayer.setSource(
        new ol.source.XYZ({
            url: get_tms_url(),
        })
    );
    updateURL();
}

function pretty(val) {
    if (val === null || val === undefined) return 'M';
    if (val === 0.0001) return 'T';
    return val;
}

function makeVectorLayer(dt, title, group) {
    return new ol.layer.Vector({
        title,
        source: new ol.source.Vector({
            format: new ol.format.GeoJSON(),
            projection: ol.proj.get('EPSG:3857'),
            url: `/geojson/7am.py?group=${group}&dt=${dt}`,
        }),
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
    // Generate the TMS URL given the current settings
    const datepickerElement = document.getElementById('datepicker');
    if (!(datepickerElement instanceof HTMLInputElement)) return '';

    // Use parseDateISO to avoid timezone issues instead of new Date()
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
        datepickerElement.min = '2009-02-01';
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
            if (datepicker instanceof HTMLInputElement && datepicker.value) {
                datepicker.value = addDaysToDateString(datepicker.value, -1);
                updateDate();
            }
        });
    }

    const plusDayElement = document.getElementById('plusday');
    if (plusDayElement) {
        plusDayElement.addEventListener('click', (event) => {
            event.preventDefault(); // Prevent form submission
            const datepicker = document.getElementById('datepicker');
            if (datepicker instanceof HTMLInputElement && datepicker.value) {
                datepicker.value = addDaysToDateString(datepicker.value, 1);
                updateDate();
            }
        });
    }
}
document.addEventListener('DOMContentLoaded', () => {
    buildUI();
    parseURLParams();

    // Get the date from the datepicker after parseURLParams() has run
    // This will be either the URL date or today's date (set by buildUI)
    const datepickerElement = document.getElementById('datepicker');
    const currentDate = datepickerElement instanceof HTMLInputElement && datepickerElement.value 
        ? datepickerElement.value 
        : formatDateISO(new Date());
    
    cocorahsLayer = makeVectorLayer(currentDate, 'IA CoCoRaHS Reports', 'cocorahs');
    coopLayer = makeVectorLayer(currentDate, 'NWS COOP Reports', 'coop');
    azosLayer = makeVectorLayer(currentDate, 'ASOS/AWOS Reports', 'azos');

    mrmsLayer = new ol.layer.Tile({
        title: 'MRMS 12z 24 Hour',
        source: new ol.source.XYZ({
            url: get_tms_url(),
        }),
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
            // Put content directly in the popup element
            element.innerHTML = content;

            // Use CSS classes instead of inline styles
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
            const link = `/sites/site.php?station=${feature.getId()}&network=${feature.get('network')}`;
            const dt = new Date(feature.get('valid'));
            const content = [
                `<p><strong><a href="${link}" target="_new">${feature.getId()}</a> ${feature.get('name')}</strong>`,
                `<br />Hour of Ob: ${feature.get('hour')}`,
                `<br />High: ${pretty(feature.get('high'))}`,
                `<br />Low: ${pretty(feature.get('low'))}`,
                `<br />Temp at Ob: ${pretty(feature.get('coop_tmpf'))}`,
                `<br />Precip: ${pretty(feature.get('pday'))}`,
                `<br />Snow: ${pretty(feature.get('snow'))}`,
                `<br />Snow Depth: ${pretty(feature.get('snowd'))}`,
                `<br />Valid: ${dt}`,
                '</p>',
            ];
            showPopover(content.join(''));
        } else {
            hidePopover();
        }
    });
});
