/* global moment, ol, $ */
let olmap = null;
let elayer = null;
const tornadoFeatures = [];
const flashFloodFeatures = [];

const sbwStyle = [new ol.style.Style({
    stroke: new ol.style.Stroke({
        color: '#FFF',
        width: 4.5
    })
}), new ol.style.Style({
    stroke: new ol.style.Stroke({
        color: '#319FD3',
        width: 3
    }),
    fill: new ol.style.Fill({
        color: '#319FD330'
    })
})
];
const sbwLookup = {
    "TO": '#FF0000',
    "FF": '#00FF00'
};

function toggleFeatures(type, show) {
    const source = elayer.getSource();
    if (type === "TO") {
        tornadoFeatures.forEach((feature) => {
            if (show) {
                source.addFeature(feature);
            } else {
                source.removeFeature(feature);
            }
        });
    } else if (type === "FF") {
        flashFloodFeatures.forEach((feature) => {
            if (show) {
                source.addFeature(feature);
            } else {
                source.removeFeature(feature);
            }
        });
    }
}

function load_data() {
    $.ajax({
        url: "/api/1/nws/emergencies.geojson",
        method: "GET",
        dataType: "json",
        success: (geodata) => {
            const format = new ol.format.GeoJSON({
                featureProjection: "EPSG:3857"
            });
            const vectorSource = new ol.source.Vector({
                features: format.readFeatures(geodata)
            });
            elayer.setSource(vectorSource);

            vectorSource.getFeatures().forEach((feature) => {
                const prop = feature.getProperties();
                if (prop.phenomena === "TO") {
                    tornadoFeatures.push(feature);
                } else if (prop.phenomena === "FF") {
                    flashFloodFeatures.push(feature);
                }
            });

            $.each(geodata.features, (_idx, feat) => {
                const prop = feat.properties;
                const lbl = (prop.phenomena === "TO") ? "Tornado" : "Flash Flood";
                $('#thetable tbody').append(
                    `<tr><td>${prop.year}</td><td>${prop.wfo}</td><td>${prop.states}</td><td><a href="${prop.uri}">${prop.eventid}</a></td><td>${lbl} Warning</td><td>${prop.utc_issue}</td><td>${prop.utc_expire}</td></tr>`);
            });

        }
    })
}
function featureHTML(features, lalo) {
    const html = [];
    
    // Only add title if there's more than one feature
    if (features.length > 1) {
        html.push(
            '<div class="panel panel-default">',
            '<div class="panel-heading">',
            `<h3 class="panel-title">Emergencies List @${lalo[0].toFixed(3)}E ${lalo[1].toFixed(3)}N</h3>`,
            '</div>'
        );
    } else {
        html.push(
            '<div class="panel panel-default">'
        );
    }
    
    html.push('<div class="panel-body"><ul>');
    
    $.each(features, (_i, feature) => {
        const utcTime = moment.utc(feature.get('utc_issue'));
        const localTime = moment(utcTime).local();
        const dtUTC = utcTime.format('HHmm [UTC]');
        const dtLocal = localTime.format('MMM Do, YYYY h:mm A');
        const lbl = (feature.get("phenomena") === "TO") ? "Tornado" : "Flash Flood";
        html.push(
            `<li><strong>${dtLocal} [${dtUTC}]</strong><br />` +
            `${feature.get('wfo')}: <a href="${feature.get('uri')}">${lbl} Warning #${feature.get('eventid')}</a></li>`
        );
    });
    html.push('</ul></div></div>');
    return html.join('\n');
}
function init_map() {
    elayer = new ol.layer.Vector({
        title: 'Emergencies',
        style: (feature) => {
            sbwStyle[1].getStroke().setColor(sbwLookup[feature.get('phenomena')]);
            sbwStyle[1].getFill().setColor(`${sbwLookup[feature.get('phenomena')]}30`);
            return sbwStyle;
        },
        source: new ol.source.Vector({
            format: new ol.format.GeoJSON()
        })
    });
    olmap = new ol.Map({
        target: 'map',
        view: new ol.View({
            enableRotation: false,
            center: ol.proj.transform([-94.5, 37.1], 'EPSG:4326', 'EPSG:3857'),
            zoom: 4
        }),
        layers: [
            new ol.layer.Tile({
                title: 'OpenStreetMap',
                visible: true,
                source: new ol.source.OSM()
            }),
            elayer
        ]
    });

    // Handle map clicks with vanilla JS
    olmap.on('click', (evt) => {
        const features = [];
        olmap.forEachFeatureAtPixel(evt.pixel, (feature) => {
            features.push(feature);
        });
        
        if (features.length > 0) {
            const coordinates = features[0].getGeometry().getFirstCoordinate();
            const lalo = ol.proj.transform(coordinates, 'EPSG:3857', 'EPSG:4326');
            const content = featureHTML(features, lalo);
            
            // Use vanilla JS popup
            createPopup(content, coordinates);
            
            // Prevent event propagation to document
            evt.stopPropagation();
        }
    });
}

let popups = [];

function createPopup(content, coordinates) {
    // Create popup container
    const popup = document.createElement('div');
    popup.className = 'feature-popup';
    popup.innerHTML = content;
    
    // Add to document first so we can get its dimensions
    document.body.appendChild(popup);
    
    // Position the popup after it's in the DOM so we have dimensions
    const mapEl = document.getElementById('map');
    const mapRect = mapEl.getBoundingClientRect();
    const point = olmap.getPixelFromCoordinate(coordinates);
    
    if (point) {
        // Apply window scroll offset for fixed positioning
        const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        popup.style.position = 'absolute';
        popup.style.left = `${(mapRect.left + point[0] - (popup.offsetWidth / 2) + scrollLeft)}px`;
        popup.style.top = `${(mapRect.top + point[1] - popup.offsetHeight - 15 + scrollTop)}px`;
    } else {
        // Fallback positioning if point calculation fails
        popup.style.position = 'fixed';
        popup.style.left = '50%';
        popup.style.top = '50%';
        popup.style.transform = 'translate(-50%, -50%)';
    }
    
    // Add close button
    const closeBtn = document.createElement('button');
    closeBtn.innerHTML = '×';
    closeBtn.className = 'popup-close-btn';
    closeBtn.onclick = function(e) {
        e.stopPropagation();
        document.body.removeChild(popup);
        // Remove this popup from our array
        popups = popups.filter(p => p !== popup);
    };
    popup.appendChild(closeBtn);
    
    // Make popup draggable
    makeDraggable(popup);
    
    // Track this popup in our array
    popups.push(popup);
    
    return popup;
}

// Draggable functionality
function makeDraggable(element) {
    let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
    
    element.onmousedown = dragMouseDown;
    
    function dragMouseDown(e) {
        e = e || window.event;
        e.preventDefault();
        
        // Don't start drag if clicking on a button, link, or close button
        if (e.target.tagName === 'BUTTON' || e.target.tagName === 'A' || 
            e.target.className === 'popup-close-btn') {
            return;
        }
        
        // Get the mouse cursor position at startup
        pos3 = e.clientX;
        pos4 = e.clientY;
        
        // Bring this popup to the front
        element.style.zIndex = 1001;
        popups.forEach(p => {
            if (p !== element) p.style.zIndex = 1000;
        });
        
        document.onmouseup = closeDragElement;
        document.onmousemove = elementDrag;
    }
    
    function elementDrag(e) {
        e = e || window.event;
        e.preventDefault();
        
        // Calculate the new cursor position
        pos1 = pos3 - e.clientX;
        pos2 = pos4 - e.clientY;
        pos3 = e.clientX;
        pos4 = e.clientY;
        
        // Set the element's new position
        element.style.top = `${element.offsetTop - pos2}px`;
        element.style.left = `${element.offsetLeft - pos1}px`;
    }
    
    function closeDragElement() {
        // Stop moving when mouse button is released
        document.onmouseup = null;
        document.onmousemove = null;
    }
}

function applyDateFilter() {
    let start = $('#startdate').val();
    let end = $('#enddate').val();
    if (start) start = moment.utc(start, 'YYYY-MM-DD');
    if (end) end = moment.utc(end, 'YYYY-MM-DD').endOf('day');

    // Update the filter title
    if (start && end) {
        const formattedStart = moment.utc(start).format('MMMM D, YYYY');
        const formattedEnd = moment.utc(end).format('MMMM D, YYYY');
        $('#filter-title').text(`Emergencies from ${formattedStart} to ${formattedEnd}`);
    } else if (start) {
        const formattedStart = moment.utc(start).format('MMMM D, YYYY');
        $('#filter-title').text(`Emergencies since ${formattedStart}`);
    } else if (end) {
        const formattedEnd = moment.utc(end).format('MMMM D, YYYY');
        $('#filter-title').text(`Emergencies until ${formattedEnd}`);
    } else {
        $('#filter-title').text('');
    }

    const source = elayer.getSource();
    source.clear();
    const addFeatureIfValid = function(feature, type) {
        const issue = moment.utc(feature.get('utc_issue'));
        let valid = true;
        if (start && issue.isBefore(start)) valid = false;
        if (end && issue.isAfter(end)) valid = false;
        if (valid) {
            if ((type === "TO" && $('#toggleTornado').is(':checked')) ||
                (type === "FF" && $('#toggleFlashFlood').is(':checked'))) {
                source.addFeature(feature);
            }
        }
    };
    tornadoFeatures.forEach(f => addFeatureIfValid(f, "TO"));
    flashFloodFeatures.forEach(f => addFeatureIfValid(f, "FF"));
}

function init_ui() {
    $('#makefancy').click(() => {
        $("#thetable table").DataTable();
    });

    // Set default values for date inputs
    const defaultStartDate = '1999-05-01';
    const tomorrow = moment().add(1, 'days').format('YYYY-MM-DD');
    $('#startdate').val(defaultStartDate);
    $('#enddate').val(tomorrow);

    const controls = `
        <div>
            <label><input type="checkbox" id="toggleTornado" checked /> Show <span style="color: #FF0000; font-weight: bold;">■</span> Tornado Emergencies</label>
            <br /><label><input type="checkbox" id="toggleFlashFlood" checked /> Show <span style="color: #00FF00; font-weight: bold;">■</span> Flash Flood Emergencies</label>
        </div>`;
    $('#map').before(controls);

    $('#toggleTornado').change((e) => {
        toggleFeatures("TO", e.target.checked);
    });

    $('#toggleFlashFlood').change((e) => {
        toggleFeatures("FF", e.target.checked);
    });

    $('#applyFilter').click(applyDateFilter);
}

$(document).ready(() => {
    init_map();
    init_ui();
    load_data();
    // Apply the default date filter on initial load
    applyDateFilter();
});