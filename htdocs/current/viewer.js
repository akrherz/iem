/* global ol, moment, bootstrap */

/**
 * Format date for datetime-local input (YYYY-MM-DDTHH:MM)
 * @param {Date} date - Date to format
 * @returns {string} Formatted date string
 */
function formatDateTimeLocal(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day}T${hours}:${minutes}`;
}

/**
 * Parse datetime-local input value to Date object
 * @param {string} dateTimeStr - Datetime string from input
 * @returns {Date} Parsed date object
 */
function parseDateTimeLocal(dateTimeStr) {
    return new Date(dateTimeStr);
}


let map = null;
let n0q = null;
let webcamGeoJsonLayer = null;
let idotdashcamGeoJsonLayer = null;
let idotRWISLayer = null;
let sbwlayer = null;
let ts = null;
let aqlive = 0;
let realtimeMode = true;
let currentCameraFeature = null;
let element = null;
let popup = null;
let bootstrapPopover = null;
let cameraID = "ISUC-006";
const ISOFMT = "Y-MM-DD[T]HH:mm:ss[Z]";

const sbwLookup = {
    "TO": 'red',
    "MA": 'purple',
    "EW": 'green',
    "SV": 'yellow',
    "SQ": "#C71585",
    "DS": "#FFE4C4"
};

const sbwStyle = [new ol.style.Style({
    stroke: new ol.style.Stroke({
        color: '#FFF',
        width: 4.5
    })
}), new ol.style.Style({
    stroke: new ol.style.Stroke({
        color: '#319FD3',
        width: 3
    })
})
];

const cameraStyle = new ol.style.Style({
    image: new ol.style.Icon({
        src: '/images/yellow_arrow.png'
    })
});
const trackaplowStyle = new ol.style.Style({
    image: new ol.style.Icon({
        src: '/images/trackaplow.png',
        scale: 0.4
    })
});
const trackaplowStyle2 = new ol.style.Style({
    image: new ol.style.Icon({
        src: '/images/trackaplow_red.png',
        scale: 0.6
    })
});
const rwisStyle = new ol.style.Style({
    image: new ol.style.Icon({
        src: '/images/rwiscam.svg',
        scale: 0.6
    })
});
const cameraStyle2 = new ol.style.Style({
    image: new ol.style.Icon({
        src: '/images/red_arrow.png',
        scale: 1.2
    })
});

/**
 * Replace HTML special characters with their entity equivalents
 * @param string val 
 * @returns string converted string
 */
function escapeHTML(val) {
    return val.replace(/&/g, '&amp;')
              .replace(/</g, '&lt;')
              .replace(/>/g, '&gt;')
              .replace(/"/g, '&quot;')
              .replace(/'/g, '&#039;');
}

function liveShot() {
    if (aqlive) return;
    aqlive = true;
    ts = new Date();
    const webcamImg = document.getElementById("webcam_image");
    if (webcamImg) {
        webcamImg.src = `/current/live/${currentCameraFeature.get("cid")}.jpg?ts=${ts.getTime()}`;
    }
    aqlive = false;
}

// Updates the window location shown for deep linking
function updateHashLink() {
    if (!currentCameraFeature) {
        return;
    }
    let extra = "";
    if (!realtimeMode) {
        const dtpicker = document.getElementById('dtpicker');
        if (dtpicker?.value) {
            const dt = moment(parseDateTimeLocal(dtpicker.value));
            extra = `/${dt.utc().format(ISOFMT)}`;
        }
    }
    window.location.href = `#${currentCameraFeature.get("cid")}${extra}`;
}

function findFeatureByCid(cid) {
    // Find the feature for the given camera id
    let feature = null;
    webcamGeoJsonLayer.getSource().forEachFeature((feat) => {
        if (feat.get('cid') === cid) {
            feature = feat;
        }
    });
    if (feature) {
        return feature;
    }
    idotdashcamGeoJsonLayer.getSource().forEachFeature((feat) => {
        if (feat.get('cid') === cid) {
            feature = feat;
        }
    });
    if (feature) {
        return feature;
    }
    idotRWISLayer.getSource().forEachFeature((feat) => {
        if (feat.get('cid') === cid) {
            feature = feat;
        }
    });
    return feature;
}

function handleRWISClick(img) {
    const rwisMain = document.getElementById("rwismain");
    if (rwisMain && img && img.src) {
        rwisMain.src = img.src;
    }
}

window.hrs = handleRWISClick;

function doRWISView() {
    // Do the magic that is the multi-view RWIS data...
    const singleImageView = document.getElementById("singleimageview");
    const rwisView = document.getElementById("rwisview");
    const rwisList = document.getElementById("rwislist");
    const rwisMain = document.getElementById("rwismain");
    if (singleImageView) singleImageView.style.display = "none";
    if (rwisView) rwisView.style.display = "block";
    if (rwisList) rwisList.innerHTML = "";
    let i = 0;
    let hit = false;
    while (i < 10) {
        const url = currentCameraFeature.get(`imgurl${i}`);
        if (url !== null && url !== undefined) {
            if (!hit) {
                if (rwisMain) rwisMain.src = url;
                hit = true;
                i += 1;
                continue;
            }
            if (rwisList) {
                const div = document.createElement("div");
                div.className = "col-md-2";
                const img = document.createElement("img");
                img.src = url;
                img.className = "img img-fluid";
                img.onclick = function() { handleRWISClick(this); };
                div.appendChild(img);
                rwisList.appendChild(div);
            }
        }
        i += 1;
    }
}

// main workflow for updating the webcam image shown to the user
function updateCamera() {
    if (!currentCameraFeature) {
        currentCameraFeature = findFeatureByCid(cameraID);
        if (!currentCameraFeature) {
            return;
        }
    }
    const cid = currentCameraFeature.get("cid");
    if (cid.startsWith("IDOT-")) {
        doRWISView();
        updateHashLink();
        return;
    }
    showSingleImageView();
}

function showSingleImageView() {
    setSingleImageViewVisibility();
    const url = getSingleImageUrl();
    if (url !== undefined) {
        setWebcamImageAndTitle(url);
        updateHashLink();
    }
}

function setSingleImageViewVisibility() {
    const singleImageView = document.getElementById("singleimageview");
    const rwisView = document.getElementById("rwisview");
    const liveShotBtn = document.getElementById("liveshot");
    if (singleImageView) singleImageView.style.display = "block";
    if (rwisView) rwisView.style.display = "none";
    if (liveShotBtn) liveShotBtn.style.display = "block";
    const url = getCameraImageUrl();
    if (url === undefined && liveShotBtn) liveShotBtn.style.display = "none";
}

function getSingleImageUrl() {
    let url = getCameraImageUrl();
    if (url === undefined) {
        url = getFallbackCameraImageUrl();
    }
    return url;
}

function setWebcamImageAndTitle(url) {
    const valid = currentCameraFeature.get("valid") ?? currentCameraFeature.get("utc_valid");
    const name = currentCameraFeature.get("name") ?? "Iowa DOT Dash Cam";
    const webcamImg = document.getElementById("webcam_image");
    const webcamTitle = document.getElementById("webcam_title");
    if (webcamImg) webcamImg.src = url;
    if (webcamTitle) webcamTitle.innerHTML =
        `[${currentCameraFeature.get("cid")}] ${name} @ ${moment(valid).format("D MMM YYYY h:mm A")}`;
}

function getCameraImageUrl() {
    return currentCameraFeature.get("url");
}

function getFallbackCameraImageUrl() {
    return currentCameraFeature.get("imgurl") ?? currentCameraFeature.get("imgurl0");
}
function cronMinute() {
    // We are called every minute
    if (!realtimeMode) return;
    refreshRADAR();
    refreshJSON();
}

function getRADARSource() {
    let dt = moment();
    if (!realtimeMode) {
        const dtpicker = document.getElementById('dtpicker');
        if (dtpicker?.value) {
            dt = moment(parseDateTimeLocal(dtpicker.value));
        }
    }
    dt.subtract(dt.minutes() % 5, 'minutes');
    const prod = dt.year() < 2011 ? 'N0R' : 'N0Q';
    const radarTitle = document.getElementById("radar_title");
    if (radarTitle) radarTitle.innerHTML = `US Base Reflectivity @ ${dt.format("h:mm A")}`;
    return new ol.source.XYZ({
        url: `https://mesonet.agron.iastate.edu/cache/tile.py/1.0.0/ridge::USCOMP-${prod}-${dt.utc().format('YMMDDHHmm')}/{z}/{x}/{y}.png`
    });
}

function refreshRADAR() {
    if (n0q) {
        n0q.setSource(getRADARSource());
    }
}
function refreshJSON() {
    setWebcamGeoJsonLayer();
    setDashcamGeoJsonLayer();
    setRWISGeoJsonLayer();
    setSBWLayer();
}

function setWebcamGeoJsonLayer() {
    let url = "/geojson/webcam.geojson?network=TV";
    if (!realtimeMode) {
        const dtpicker = document.getElementById('dtpicker');
        if (dtpicker?.value) {
            const dt = moment(parseDateTimeLocal(dtpicker.value));
            url += `&valid=${dt.utc().format(ISOFMT)}`;
        }
    }
    setLayerSource(webcamGeoJsonLayer, url);
}

function setDashcamGeoJsonLayer() {
    let url = "/api/1/idot_dashcam.geojson";
    if (!realtimeMode) {
        const dtpicker = document.getElementById('dtpicker');
        if (dtpicker?.value) {
            const dt = moment(parseDateTimeLocal(dtpicker.value));
            url += `?valid=${dt.utc().format(ISOFMT)}`;
        }
    }
    setLayerSource(idotdashcamGeoJsonLayer, url);
}

function setRWISGeoJsonLayer() {
    let url = "/api/1/idot_rwiscam.geojson";
    if (!realtimeMode) {
        const dtpicker = document.getElementById('dtpicker');
        if (dtpicker?.value) {
            const dt = moment(parseDateTimeLocal(dtpicker.value));
            url += `?valid=${dt.utc().format(ISOFMT)}`;
        }
    }
    setLayerSource(idotRWISLayer, url);
}

function setSBWLayer() {
    let url = "/geojson/sbw.geojson";
    if (!realtimeMode) {
        const dtpicker = document.getElementById('dtpicker');
        if (dtpicker?.value) {
            const dt = moment(parseDateTimeLocal(dtpicker.value));
            url += `?ts=${dt.utc().format(ISOFMT)}`;
        }
    }
    sbwlayer.setSource(new ol.source.Vector({
        url,
        format: new ol.format.GeoJSON()
    }));
}

function setLayerSource(layer, url) {
    const newsource = new ol.source.Vector({
        url,
        format: new ol.format.GeoJSON()
    });
    newsource.on('change', () => {
        updateCamera();
    });
    layer.setSource(newsource);
}

function parseURI() {
    const tokens = window.location.href.split('#');
    if (tokens.length === 2) {
        const tokens2 = tokens[1].split("/");
        if (tokens2.length === 1) {
            cameraID = escapeHTML(tokens[1]);
        } else {
            cameraID = escapeHTML(tokens2[0]);
            const toggleBtns = document.querySelectorAll('#toggle_event_mode button');
            if (toggleBtns[1]) toggleBtns[1].click();
            const dtpicker = document.getElementById('dtpicker');
            if (dtpicker) {
                const momentDate = moment(escapeHTML(tokens2[1]));
                dtpicker.value = formatDateTimeLocal(momentDate.toDate());
            }
        }
    }
}

function buildUI() {

    const liveShotBtn = document.getElementById("liveshot");
    if (liveShotBtn) {
        liveShotBtn.addEventListener('click', () => {
            liveShot();
        });
    }

    // Time increment and decrement buttons
    document.querySelectorAll("button.timecontrol").forEach(button => {
        button.addEventListener('click', (evt) => {
            const offset = parseInt(evt.target.dataset.offset);
            const dtpicker = document.getElementById('dtpicker');
            if (dtpicker?.value) {
                const currentDate = parseDateTimeLocal(dtpicker.value);
                const newDate = new Date(currentDate.getTime() + (offset * 60000)); // offset in minutes
                dtpicker.value = formatDateTimeLocal(newDate);
                // Trigger change event manually
                dtpicker.dispatchEvent(new Event('change'));
            }
            // unblur the button
            evt.target.blur();
        });
    });

    // Thanks to http://jsfiddle.net/hmgyu371/
    document.querySelectorAll('#toggle_event_mode button').forEach((button, idx, btns) => {
        button.addEventListener('click', function () {
            if (this.classList.contains('locked_active') || this.classList.contains('unlocked_inactive')) {
                // Enable Archive
                realtimeMode = false;
                document.getElementById('dtdiv').style.display = '';
                refreshJSON();
            } else {
                // Enable Realtime
                realtimeMode = true;
                document.getElementById('dtdiv').style.display = 'none';
                cronMinute();
            }
            // Toggle classes
            const btn0 = btns[0];
            const btn1 = btns[1];
            btn0.classList.toggle('locked_inactive');
            btn0.classList.toggle('locked_active');
            btn0.classList.toggle('btn-secondary');
            btn0.classList.toggle('btn-info');
            btn1.classList.toggle('unlocked_inactive');
            btn1.classList.toggle('unlocked_active');
            btn1.classList.toggle('btn-info');
            btn1.classList.toggle('btn-secondary');
        });
    });

    // Initialize native datetime picker
    const dtpicker = document.getElementById('dtpicker');
    if (dtpicker) {
        // Set default value to current date/time
        dtpicker.value = formatDateTimeLocal(new Date());
        
        // Add change event listener
        dtpicker.addEventListener('change', () => {
            if (!realtimeMode) {
                refreshJSON();
                refreshRADAR();
            }
        });
    }
}

/**
 * Popup the SBW information
 * @param feature {ol.Feature}
 */
function popupSBW(feature) {
    const content = `<strong>You clicked:</strong> ${feature.get('wfo')} `
    + `<a target="_new" href="${feature.get('href')}">`
    + `${feature.get('ps')} ${feature.get('eventid')}</a>`
    + '<button type="button" class="btn-close btn-close-white ms-2" aria-label="Close" onclick="closeSBWPopover()"></button>';
    const geometry = feature.getGeometry();
    const coord = geometry.getFirstCoordinate();
    popup.setPosition(coord);
    
    // Update popover content
    const popoverContent = document.getElementById('popover-content');
    popoverContent.innerHTML = content;
    
    // Show Bootstrap 5 popover
    if (bootstrapPopover) {
        bootstrapPopover.dispose();
    }
    bootstrapPopover = new bootstrap.Popover(element, {
        content: popoverContent.innerHTML,
        html: true,
        placement: 'top'
    });
    bootstrapPopover.show();
}

/**
 * Close the SBW popover
 */
// eslint-disable-next-line no-unused-vars
function closeSBWPopover() {
    if (bootstrapPopover) {
        bootstrapPopover.hide();
    }
}

document.addEventListener('DOMContentLoaded', () => {
    buildUI();

    sbwlayer = new ol.layer.Vector({
        title: 'Storm Based Warnings',
        source: new ol.source.Vector({
            url: "/geojson/sbw.geojson",
            format: new ol.format.GeoJSON()
        }),
        style: (feature) => {
            let color = sbwLookup[feature.get('phenomena')];
            if (color === undefined) {
                color = '#000000';
            }
            sbwStyle[1].getStroke().setColor(color);
            return sbwStyle;
        }
    });
    idotdashcamGeoJsonLayer = new ol.layer.Vector({
        title: 'Iowa DOT Truck Dashcams (2014-)',
        style: (feature) => {
            if (currentCameraFeature &&
                currentCameraFeature.get("cid") === feature.get("cid")) {
                currentCameraFeature = feature;
                return [trackaplowStyle2];
            }
            return [trackaplowStyle];
        }
    });
    idotRWISLayer = new ol.layer.Vector({
        title: 'Iowa DOT RWIS Webcams (2010-)',
        style(feature) {
            if (currentCameraFeature &&
                currentCameraFeature.get("cid") === feature.get("cid")) {
                currentCameraFeature = feature;
                return [rwisStyle];
            }
            return [rwisStyle];
        }
    });
    webcamGeoJsonLayer = new ol.layer.Vector({
        title: 'Webcams (2003-)',
        style: (feature) => {
            if (currentCameraFeature &&
                currentCameraFeature.get("cid") === feature.get("cid")) {
                currentCameraFeature = feature;
                // OL rotation is in radians!
                cameraStyle2.getImage().setRotation(
                    parseInt(feature.get('angle')) / 180.0 * 3.14, 10);
                return [cameraStyle2];
            }
            cameraStyle.getImage().setRotation(
                parseInt(feature.get('angle')) / 180.0 * 3.14, 10);
            return [cameraStyle];
        }
    });
    n0q = new ol.layer.Tile({
        title: 'NEXRAD Base Reflectivity',
        source: getRADARSource()
    });

    map = new ol.Map({
        target: 'map',
        layers: [new ol.layer.Tile({
            title: 'OpenStreetMap',
            visible: true,
            source: new ol.source.OSM()
        }),
            n0q,
            sbwlayer,
            idotdashcamGeoJsonLayer,
            idotRWISLayer,
            webcamGeoJsonLayer
        ],
        view: new ol.View({
            projection: 'EPSG:3857',
            center: ol.proj.transform([-93.5, 42.1], 'EPSG:4326', 'EPSG:3857'),
            zoom: 6
        })
    });
    map.addControl(new ol.control.LayerSwitcher());

    element = document.getElementById('popup');

    popup = new ol.Overlay({
        element,
        positioning: 'bottom-center',
        stopEvent: false
    });
    map.addOverlay(popup);

    // Initialize Bootstrap 5 popover (will be created dynamically when needed)
    // Note: Popover will be created in popupSBW function

    map.on('click', (evt) => {
        const feature = map.forEachFeatureAtPixel(evt.pixel, (ft) => ft);
        if (!feature) {
            // Hide existing popover when clicking on empty map area
            if (bootstrapPopover) {
                bootstrapPopover.hide();
            }
            return;
        }
        if (feature.get("cid") === undefined){
            popupSBW(feature);
            return;
        }
        
        // Hide existing popover when clicking on camera features
        if (bootstrapPopover) {
            bootstrapPopover.hide();
        }

        // Remove styling
        if (currentCameraFeature) {
            currentCameraFeature.setStyle(feature.getStyle());
        }
        // Update
        currentCameraFeature = feature;
        // Set new styling
        if (feature.get("angle") !== undefined) {
            cameraStyle2.getImage().setRotation(
                parseInt(feature.get('angle')) / 180.0 * 3.14, 10);
            feature.setStyle(cameraStyle2);
        }
        updateCamera();
    });

    parseURI();
    refreshJSON();
    updateCamera();

    window.setInterval(cronMinute, 60000);
});
