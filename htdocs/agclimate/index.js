/* global ol */
let map = null;
let gj = null;
let invgj = null;
let dtpicker = null;
let n0q = null;
let varname = 'tmpf';
let currentdt = new Date();
let timeChanged = false;

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

function pad(number) {
    let strnum = String(number);
    if (strnum.length === 1) {
        strnum = `0${strnum}`;
    }
    return strnum;
};

function getN0QSource() {
    // currentdt needs to be rectified to the nearest 5 minute value in the past
    const rectifiedDate = new Date(Math.floor(currentdt.getTime() / (5 * 60 * 1000)) * (5 * 60 * 1000));
    return new ol.source.XYZ({
        url: `https://mesonet.agron.iastate.edu/cache/tile.py/1.0.0/ridge::USCOMP-N0Q-${toIEMString(rectifiedDate)}/{z}/{x}/{y}.png`
    });
}

function toIEMString(val) {
    return `${val.getUTCFullYear()}${pad(val.getUTCMonth() + 1)}${pad(val.getUTCDate())}${pad(val.getUTCHours())}${pad(val.getUTCMinutes())}`;
};

function toISOString(val) {
    return `${val.getUTCFullYear()}-${pad(val.getUTCMonth() + 1)}-${pad(val.getUTCDate())}T${pad(val.getUTCHours())}:${pad(val.getUTCMinutes())}Z`;
};

function logic() {
    timeChanged = true;
    currentdt = new Date(dtpicker.value);
    updateMap();
}

function updateTitle() {
    const selectedOption = document.querySelector('#varpicker option:checked');
    const maptitleDiv = document.getElementById('maptitle');
    
    if (maptitleDiv && selectedOption) {
        // Find the specific text element within the maptitle structure
        const textDiv = maptitleDiv.querySelector('.small');
        if (textDiv) {
            // Format the datetime for display
            const options = { 
                year: 'numeric', 
                month: 'short', 
                day: 'numeric', 
                hour: '2-digit', 
                minute: '2-digit',
                timeZoneName: 'short'
            };
            const formattedDate = currentdt.toLocaleString('en-US', options);
            textDiv.textContent = `The map is displaying ${selectedOption.textContent} valid at ${formattedDate}`;
        }
    }
    updateURL();
}

function updateURL() {
    const url = new URL(window.location);
    url.searchParams.set('var', varname);
    if (timeChanged) {
        url.searchParams.set('dt', toISOString(currentdt));
    } else {
        url.searchParams.delete('dt');
    }
    // Remove hash if present
    url.hash = '';
    window.history.replaceState({}, '', url);
}

function updateMap() {
    if (currentdt && typeof currentdt !== "string") {
        const dt = toISOString(currentdt);
        const uristamp = timeChanged ? `dt=${dt}` : "";
        gj.setSource(new ol.source.Vector({
            url: `/geojson/agclimate.py?${uristamp}`,
            format: new ol.format.GeoJSON()
        })
        );
        invgj.setSource(new ol.source.Vector({
            url: `/geojson/agclimate.py?inversion&${uristamp}`,
            format: new ol.format.GeoJSON()
        })
        );
    }
    n0q.setSource(getN0QSource());
    updateTitle();
}


const mystyle = new ol.style.Style({
    text: new ol.style.Text({
        font: '16px Calibri,sans-serif',
        fill: new ol.style.Fill({
            color: '#000',
            width: 3
        }),
        stroke: new ol.style.Stroke({
            color: '#ff0',
            width: 5
        })
    })
});
const greenArrow = new ol.style.Style({
    image: new ol.style.Icon({
        crossOrigin: 'anonymous',
        scale: 0.04,
        src: '/images/green_arrow_up.svg',
    })
});
const redArrow = new ol.style.Style({
    image: new ol.style.Icon({
        crossOrigin: 'anonymous',
        scale: 0.04,
        src: '/images/red_arrow_down.svg',
    })
});

function setupMap() {
    gj = new ol.layer.Vector({
        title: 'ISUSM Data',
        source: new ol.source.Vector({
            url: "/geojson/agclimate.py",
            format: new ol.format.GeoJSON()
        }),
        style(feature) {
            mystyle.getText().setText(feature.get(varname).toString());
            return [mystyle];
        }
    });
    invgj = new ol.layer.Vector({
        title: 'ISUSM Inversion Data',
        source: new ol.source.Vector({
            url: "/geojson/agclimate.py?inversion",
            format: new ol.format.GeoJSON()
        }),
        style(feature) {
            // Update the img src to the appropriate arrow
            const arrowEl = document.getElementById(`${feature.getId()}_arrow`);
            if (arrowEl) {
                arrowEl.src = feature.get("is_inversion") ? "/images/red_arrow_down.svg" : "/images/green_arrow_up.svg";
            }
            const temp15El = document.getElementById(`${feature.getId()}_15`);
            if (temp15El) temp15El.textContent = feature.get('tmpf_15');
            const temp5El = document.getElementById(`${feature.getId()}_5`);
            if (temp5El) temp5El.textContent = feature.get('tmpf_5');
            const temp10El = document.getElementById(`${feature.getId()}_10`);
            if (temp10El) temp10El.textContent = feature.get('tmpf_10');
            return [feature.get("is_inversion") ? redArrow : greenArrow];
        }
    });
    n0q = new ol.layer.Tile({
        title: 'NEXRAD Base Reflectivity',
        source: getN0QSource()
    });
    map = new ol.Map({
        target: 'map',
        layers: [new ol.layer.Tile({
            title: 'OpenStreetMap',
            visible: true,
            source: new ol.source.OSM()
        }), n0q, invgj, gj],
        view: new ol.View({
            projection: 'EPSG:3857',
            center: ol.proj.transform([-93.5, 42.1], 'EPSG:4326', 'EPSG:3857'),
            zoom: 7
        })
    });

    // Popup showing the position the user clicked
    const popup = new ol.Overlay({
        element: document.getElementById('popup')
    });
    map.addOverlay(popup);
    // Support clicking on the map to get more details on the station
    map.on('click', (evt) => {
        const element = popup.getElement();
        // Clear any existing content
        element.innerHTML = '';
        element.style.display = 'none';
        
        const pixel = map.getEventPixel(evt.originalEvent);
        const feature = map.forEachFeatureAtPixel(pixel, (feature2) => {
            return feature2;
        });
        if (feature) {
            popup.setPosition(evt.coordinate);
            let content = [
                `<p>Site ID: <code>${feature.getId()}</code>`,
                `Name: ${feature.get('name')}`,
                `Air Temp: ${feature.get('tmpf')}`,
                '</p>'
            ].join('<br/>');
            if (feature.get("tmpf_15")) {
                content = [
                    `<p>Site ID: <code>${feature.getId()}</code>`,
                    `Name: ${feature.get('name')}`,
                    `Inversion: ${feature.get("is_inversion") ? "Likely" : "Unlikely"}`,
                    `Air Temp @1.5ft: ${feature.get('tmpf_15')}`,
                    `Air Temp @5ft: ${feature.get('tmpf_5')}`,
                    `Air Temp @10ft: ${feature.get('tmpf_10')}`,
                    '</p>'
                ].join('<br/>');
            }
            element.innerHTML = content;
            element.style.display = 'block';
        }
    });

    const layerSwitcher = new ol.control.LayerSwitcher();
    map.addControl(layerSwitcher);

    dtpicker = document.getElementById('datetimepicker');
    dtpicker.addEventListener('change', logic);
    
    // Set min and max dates for the datetime picker
    const minDate = new Date(2013, 1, 1, 0, 0);
    const maxDate = new Date();
    dtpicker.min = minDate.toISOString().slice(0, 16);
    dtpicker.max = maxDate.toISOString().slice(0, 16);

    try {
        // First check for hash parameters (legacy) and migrate to URL params
        const hashTokens = window.location.href.split('#');
        if (hashTokens.length === 2) {
            const hashParts = hashTokens[1].split("/");
            varname = escapeHTML(hashParts[0]);
            document.getElementById('varpicker').value = varname;
            if (hashParts.length === 2) {
                currentdt = (new Date(Date.parse(escapeHTML(hashParts[1]))));
                timeChanged = true;
            }
            gj.setStyle(gj.getStyle());
            // Migrate to URL params and remove hash
            updateURL();
            return;
        }
        
        // Check for URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.has('var')) {
            varname = escapeHTML(urlParams.get('var'));
            document.getElementById('varpicker').value = varname;
            if (urlParams.has('dt')) {
                currentdt = new Date(Date.parse(escapeHTML(urlParams.get('dt'))));
                timeChanged = true;
            }
            gj.setStyle(gj.getStyle());
        }
    } catch {
        varname = 'tmpf';
        currentdt = new Date(document.getElementById("defaultdt").dataset.dt);
    }

    setDate();
    updateMap();
};

function setDate() {
    if (currentdt && dtpicker) {
        // Convert to local datetime string for the input
        const year = currentdt.getFullYear();
        const month = String(currentdt.getMonth() + 1).padStart(2, '0');
        const day = String(currentdt.getDate()).padStart(2, '0');
        const hours = String(currentdt.getHours()).padStart(2, '0');
        const minutes = String(currentdt.getMinutes()).padStart(2, '0');
        
        dtpicker.value = `${year}-${month}-${day}T${hours}:${minutes}`;
    }
}

function setupUI() {
    const dtButtons = document.querySelectorAll(".dt");
    dtButtons.forEach(button => {
        button.addEventListener('click', (event) => {
            timeChanged = true;
            event.target.classList.remove('focus');
            const delta = parseInt(event.target.dataset.delta);
            currentdt = new Date(currentdt.valueOf() + delta);
            setDate();
            updateMap();
        });
    });

    const varpicker = document.getElementById('varpicker');
    varpicker.addEventListener('change', () => {
        varname = escapeHTML(varpicker.value);
        gj.setStyle(gj.getStyle());
        updateTitle(); // Update the title when variable changes
    });
};

document.addEventListener('DOMContentLoaded', () => {
    currentdt = new Date(document.getElementById("defaultdt").dataset.dt);
    setupMap();
    setupUI();
});
