/* global moment, ol, Tabulator */
let olmap = null;
let elayer = null;
let emergenciesTable = null;
const tornadoFeatures = [];
const flashFloodFeatures = [];
const tableData = [];

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
    // Use fetch instead of jQuery Ajax
    fetch("/api/1/nws/emergencies.geojson")
        .then(response => response.json())
        .then(geodata => {
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

            // Populate table data array for Tabulator
            tableData.length = 0; // Clear existing data
            geodata.features.forEach(feat => {
                const prop = feat.properties;
                const lbl = (prop.phenomena === "TO") ? "Tornado" : "Flash Flood";
                tableData.push({
                    year: prop.year,
                    wfo: prop.wfo,
                    states: prop.states,
                    eventid: prop.eventid,
                    uri: prop.uri,
                    event: `${lbl} Warning`,
                    issue: prop.utc_issue,
                    expire: prop.utc_expire
                });
            });

            // If table is initialized, update its data
            if (emergenciesTable) {
                emergenciesTable.setData(tableData);
            }
        })
        .catch(() => {
            // Handle errors
            document.getElementById('thetable').innerHTML = '<div class="alert alert-danger">Error loading data</div>';
        });
}
function featureHTML(features, lalo) {
    const html = [];
    
    // Only add title if there's more than one feature
    if (features.length > 1) {
        html.push(
            '<div class="card">',
            '<div class="card-header">',
            `<h3 class="card-title">Emergencies List @${lalo[0].toFixed(3)}E ${lalo[1].toFixed(3)}N</h3>`,
            '</div>'
        );
    } else {
        html.push(
            '<div class="card">'
        );
    }
    
    html.push('<div class="card-body"><ul>');
    
    features.forEach(feature => {
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
    let pos1 = 0;
    let pos2 = 0;
    let pos3 = 0;
    let pos4 = 0;
    
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
    let start = document.getElementById('startdate').value;
    let end = document.getElementById('enddate').value;
    if (start) start = moment.utc(start, 'YYYY-MM-DD');
    if (end) end = moment.utc(end, 'YYYY-MM-DD').endOf('day');

    // Update the filter title
    const filterTitle = document.getElementById('filter-title');
    if (start && end) {
        const formattedStart = moment.utc(start).format('MMMM D, YYYY');
        const formattedEnd = moment.utc(end).format('MMMM D, YYYY');
        filterTitle.textContent = `Emergencies from ${formattedStart} to ${formattedEnd}`;
    } else if (start) {
        const formattedStart = moment.utc(start).format('MMMM D, YYYY');
        filterTitle.textContent = `Emergencies since ${formattedStart}`;
    } else if (end) {
        const formattedEnd = moment.utc(end).format('MMMM D, YYYY');
        filterTitle.textContent = `Emergencies until ${formattedEnd}`;
    } else {
        filterTitle.textContent = '';
    }

    const source = elayer.getSource();
    source.clear();
    
    // Helper functions for applyDateFilter complexity reduction
    function isFeatureValidForDateRange(feature, startDate, endDate) {
        const issue = moment.utc(feature.get('utc_issue'));
        if (startDate?.isBefore && issue.isBefore(startDate)) return false;
        return !(endDate?.isAfter && issue.isAfter(endDate));
    }
    
    function isToggleCheckedForType(type) {
        if (type === "TO") {
            const tornadoToggle = document.getElementById('toggleTornado');
            return tornadoToggle?.checked;
        } else if (type === "FF") {
            const flashFloodToggle = document.getElementById('toggleFlashFlood');
            return flashFloodToggle?.checked;
        }
        return false;
    }
    
    const addFeatureIfValid = function(feature, type) {
        if (isFeatureValidForDateRange(feature, start, end) && isToggleCheckedForType(type)) {
            source.addFeature(feature);
        }
    };
    
    tornadoFeatures.forEach(f => addFeatureIfValid(f, "TO"));
    flashFloodFeatures.forEach(f => addFeatureIfValid(f, "FF"));
}

function initTable() {
    emergenciesTable = new Tabulator("#emergencies-table", {
        data: tableData,
        layout: "fitColumns",
        responsiveLayout: "collapse",
        pagination: "local",
        paginationSize: 25,
        paginationSizeSelector: [10, 25, 50, 100],
        movableColumns: true,
        resizableColumns: true,
        tooltips: true,
        columns: [
            {
                title: "Year",
                field: "year",
                width: 80,
                sorter: "number",
                headerFilter: "input"
            },
            {
                title: "WFO",
                field: "wfo",
                width: 80,
                sorter: "string",
                headerFilter: "input"
            },
            {
                title: "State(s)",
                field: "states",
                width: 120,
                sorter: "string",
                headerFilter: "input"
            },
            {
                title: "Event ID",
                field: "eventid",
                width: 120,
                sorter: "number",
                formatter(cell) {
                    const data = cell.getRow().getData();
                    return `<a href="${data.uri}" target="_blank">${data.eventid}</a>`;
                }
            },
            {
                title: "Event",
                field: "event",
                minWidth: 150,
                sorter: "string",
                headerFilter: "input"
            },
            {
                title: "Issue",
                field: "issue",
                width: 180,
                sorter: "datetime",
                sorterParams: {
                    format: "YYYY-MM-DD HH:mm"
                }
            },
            {
                title: "Expire",
                field: "expire",
                width: 180,
                sorter: "datetime",
                sorterParams: {
                    format: "YYYY-MM-DD HH:mm"
                }
            }
        ]
    });
}

function init_ui() {
    // Initialize table immediately and show it
    initTable();
    
    // Hide the placeholder since table will be visible
    const placeholder = document.querySelector('.table-placeholder');
    if (placeholder) {
        placeholder.style.display = 'none';
    }
    
    // Hide the "Make Fancy" button since table is already interactive
    const makeFancyBtn = document.getElementById('makefancy');
    if (makeFancyBtn) {
        makeFancyBtn.style.display = 'none';
    }

    // Set default values for date inputs
    const defaultStartDate = '1999-05-01';
    const tomorrow = moment().add(1, 'days').format('YYYY-MM-DD');
    document.getElementById('startdate').value = defaultStartDate;
    document.getElementById('enddate').value = tomorrow;

    const controls = '<div>' +
        '<label><input type="checkbox" id="toggleTornado" checked /> Show <span style="color: #FF0000; font-weight: bold;">■</span> Tornado Emergencies</label>' +
        '<br /><label><input type="checkbox" id="toggleFlashFlood" checked /> Show <span style="color: #00FF00; font-weight: bold;">■</span> Flash Flood Emergencies</label>' +
        '</div>';
    document.getElementById('map').insertAdjacentHTML('beforebegin', controls);

    document.getElementById('toggleTornado').addEventListener('change', (e) => {
        toggleFeatures("TO", e.target.checked);
    });

    document.getElementById('toggleFlashFlood').addEventListener('change', (e) => {
        toggleFeatures("FF", e.target.checked);
    });

    document.getElementById('applyFilter').addEventListener('click', applyDateFilter);
}

document.addEventListener('DOMContentLoaded', () => {
    init_map();
    init_ui();
    load_data();
    // Apply the default date filter on initial load
    applyDateFilter();
});