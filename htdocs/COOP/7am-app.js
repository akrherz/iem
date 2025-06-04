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

function parseHashlink() {
    // Figure out what was set from the hash links
    const tokens = window.location.href.split('#');
    if (tokens.length < 2) return;
    const subtokens = tokens[1].split('/');
    if (subtokens.length > 1) {
        renderattr = escapeHTML(subtokens[1]);
        const renderAttrElement = document.getElementById('renderattr');
        if (renderAttrElement instanceof HTMLSelectElement) {
            renderAttrElement.value = renderattr;
        }
    }
    const dt = parseDateYYMMDD(escapeHTML(subtokens[0]));
    const datepickerElement = document.getElementById('datepicker');
    if (datepickerElement instanceof HTMLInputElement) {
        datepickerElement.value = formatDateISO(dt);
    }
}

function updateURL() {
    const datepickerElement = document.getElementById('datepicker');
    if (!(datepickerElement instanceof HTMLInputElement)) return;

    const selectedDate = new Date(datepickerElement.value);
    const tt = formatDateYYMMDD(selectedDate);
    window.location.href = `#${tt}/${renderattr}`;
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

    const selectedDate = new Date(datepickerElement.value);
    const fullDate = formatDateISO(selectedDate);

    map.removeLayer(cocorahsLayer);
    cocorahsLayer = makeVectorLayer(fullDate, 'IA CoCoRaHS Reports', 'cocorahs');
    map.addLayer(cocorahsLayer);

    map.removeLayer(coopLayer);
    coopLayer = makeVectorLayer(fullDate, 'NWS COOP Reports', 'coop');
    map.addLayer(coopLayer);

    map.removeLayer(azosLayer);
    azosLayer = makeVectorLayer(fullDate, 'ASOS/AWOS Reports', 'azos');
    map.addLayer(azosLayer);

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

    const selectedDate = new Date(datepickerElement.value);
    const dateStr = formatDateISO(selectedDate);
    return `/cache/tile.py/1.0.0/idep0::mrms-12z24h::${dateStr}/{z}/{x}/{y}.png`;
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
        minusDayElement.addEventListener('click', () => {
            const datepicker = document.getElementById('datepicker');
            if (datepicker instanceof HTMLInputElement && datepicker.value) {
                datepicker.value = addDaysToDateString(datepicker.value, -1);
                updateDate();
            }
        });
    }

    const plusDayElement = document.getElementById('plusday');
    if (plusDayElement) {
        plusDayElement.addEventListener('click', () => {
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
    parseHashlink();

    const currentDate = formatDateISO(new Date());
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

            // Style the popup element to look like a popover
            element.style.display = 'block';
            element.style.backgroundColor = 'white';
            element.style.border = '1px solid #ccc';
            element.style.padding = '10px';
            element.style.borderRadius = '5px';
            element.style.boxShadow = '0 2px 10px rgba(0,0,0,0.2)';
            element.style.fontSize = '12px';
            element.style.lineHeight = '1.4';
            element.style.minWidth = '200px';
            element.style.maxWidth = '300px';
            element.style.position = 'relative';

            popoverVisible = true;
        }
    }

    function hidePopover() {
        if (element && popoverVisible) {
            element.style.display = 'none';
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
            const content = [
                `<p><strong><a href="${link}" target="_new">${feature.getId()}</a> ${feature.get('name')}</strong>`,
                `<br />Hour of Ob: ${feature.get('hour')}`,
                `<br />High: ${pretty(feature.get('high'))}`,
                `<br />Low: ${pretty(feature.get('low'))}`,
                `<br />Temp at Ob: ${pretty(feature.get('coop_tmpf'))}`,
                `<br />Precip: ${pretty(feature.get('pday'))}`,
                `<br />Snow: ${pretty(feature.get('snow'))}`,
                `<br />Snow Depth: ${pretty(feature.get('snowd'))}`,
                '</p>',
            ];
            showPopover(content.join(''));
        } else {
            hidePopover();
        }
    });
});
