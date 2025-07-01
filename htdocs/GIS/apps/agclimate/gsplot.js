/** global ol */
let map = null;
let dataLayer = null;
let popup = null;
let datavar = null;

function roundValue(value, varType) {
    const round = {"precip": 2, "gdd": 0, "sgdd": 0, "et": 2, "srad": 0};
    const roundDigits = round[varType] || 0;
    return parseFloat(value).toFixed(roundDigits);
}

function generateASCIITable(features) {
    const mapDiv = document.getElementById('map');
    if (!mapDiv) return '';
    
    const varname = mapDiv.dataset.var;
    if (!varname || !datavar) return '';
    const vardisplay = mapDiv.dataset.vardisplay;
    const period = mapDiv.dataset.period;
    const year = mapDiv.dataset.year;
    
    let output = `# ${year} ${vardisplay} (${period})\n`;
    output += "#-----------------------snip------------------\n";
    output += `ID   ,StationName                             ,City           ,Latitude  ,Longitude ,${varname.padEnd(10)},climate_${varname}\n`;
    
    const climovar = `climo_${datavar}`;
    
    features.forEach(feature => {
        const props = feature.getProperties();
        if (props[datavar] === null || props[datavar] === undefined) {
            return; // Skip missing data
        }
        
        let climo = "M";
        if (props[climovar] !== null && props[climovar] !== undefined) {
            climo = roundValue(props[climovar], datavar);
        }
        
        // Format each field with proper width and alignment
        const station = props.station.toString().padEnd(5);
        const name = props.name.substring(0, 40).padEnd(40);
        const city = props.city.substring(0, 15).padEnd(15);
        const lat = props.lat.toFixed(4).padStart(10);
        const lon = props.lon.toFixed(4).padStart(10);
        const value = roundValue(props[datavar], datavar).toString().padStart(10);
        const climoStr = climo.toString().padStart(10);
        
        output += `${station},${name},${city},${lat},${lon},${value},${climoStr}\n`;
    });
    
    return output;
}

function createPopupContent(feature) {
    const props = feature.getProperties();
    const mapDiv = document.getElementById('map');
    if (!mapDiv) return '';
    
    if (!datavar) {
        return '';
    }
    const vardisplay = mapDiv.dataset.vardisplay;
    
    let value = props[datavar];
    if (value === null || value === undefined) {
        value = "M";
    } else {
        value = roundValue(value, datavar);
    }
    
    return `
        <div class="popup-content">
            <h4>${props.name}</h4>
            <p><strong>Station ID:</strong> ${props.station}</p>
            <p><strong>City:</strong> ${props.city}</p>
            <p><strong>Location:</strong> ${props.lat.toFixed(4)}, ${props.lon.toFixed(4)}</p>
            <hr>
            <p><strong>${vardisplay}:</strong> ${value}</p>
        </div>
    `;
}

function initMap() {
    const mapDiv = document.getElementById('map');
    if (!mapDiv) return;
    const wsuri = mapDiv.dataset.wsuri;
    datavar = mapDiv.dataset.datavar;
    if (!wsuri || !datavar) return;

    // Create data layer
    dataLayer = new ol.layer.Vector({
        title: 'ISU Soil Moisture Station Data',
        source: new ol.source.Vector({
            url: wsuri,
            format: new ol.format.GeoJSON(),
            projection: 'EPSG:4326'
        }),
        style: (feature) => {
            const props = feature.getProperties();
            const value = props[datavar];
            
            if (value === null || value === undefined) {
                // Missing data - gray circle
                return new ol.style.Style({
                    image: new ol.style.Circle({
                        radius: 8,
                        fill: new ol.style.Fill({color: '#cccccc'}),
                        stroke: new ol.style.Stroke({color: '#000000', width: 1})
                    })
                });
            }
            
            // Display value as text on the map
            const displayValue = roundValue(value, datavar);
            
            return new ol.style.Style({
                image: new ol.style.Circle({
                    radius: 18,
                    fill: new ol.style.Fill({color: 'rgba(255, 255, 255, 0.9)'}),
                    stroke: new ol.style.Stroke({color: '#0066cc', width: 2})
                }),
                text: new ol.style.Text({
                    text: displayValue.toString(),
                    font: 'bold 13px Arial',
                    fill: new ol.style.Fill({color: '#0066cc'}),
                    stroke: new ol.style.Stroke({color: '#ffffff', width: 3})
                })
            });
        }
    });

    // Base layers
    const osmLayer = new ol.layer.Tile({
        title: 'OpenStreetMap',
        type: 'base',
        visible: true,
        source: new ol.source.OSM()
    });
    
    const stateLayer = new ol.layer.Tile({
        title: 'State Boundaries',
        source: new ol.source.XYZ({
            url: '/c/tile.py/1.0.0/usstates/{z}/{x}/{y}.png'
        })
    });

    const countyLayer = new ol.layer.Tile({
        title: 'County Boundaries',
        visible: false,
        source: new ol.source.XYZ({
            url: '/c/tile.py/1.0.0/uscounties/{z}/{x}/{y}.png'
        })
    });

    // Create map
    map = new ol.Map({
        target: 'map',
        layers: [osmLayer, stateLayer, countyLayer, dataLayer],
        view: new ol.View({
            projection: 'EPSG:3857',
            center: ol.proj.transform([-93.5, 42.1], 'EPSG:4326', 'EPSG:3857'),
            zoom: 7
        })
    });

    // Add layer switcher
    const layerSwitcher = new ol.control.LayerSwitcher();
    map.addControl(layerSwitcher);

    // Create popup overlay
    const popupElement = document.createElement('div');
    popupElement.className = 'ol-popup';
    popupElement.style.cssText = `${''}
        background: white;
        border: 2px solid #000;
        border-radius: 5px;
        padding: 10px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.2);
        max-width: 300px;
    `;
    
    popup = new ol.Overlay({
        element: popupElement,
        positioning: 'bottom-center',
        stopEvent: false,
        offset: [0, -15]
    });
    map.addOverlay(popup);

    // Handle map clicks
    map.on('click', (evt) => {
        const feature = map.forEachFeatureAtPixel(evt.pixel, (feature2) => {
            return feature2;
        });
        
        if (feature) {
            const coordinates = feature.getGeometry().getCoordinates();
            popup.setPosition(coordinates);
            popupElement.innerHTML = createPopupContent(feature);
        } else {
            popup.setPosition();
        }
    });

    // Handle data loading
    dataLayer.getSource().on('change', () => {
        const state = dataLayer.getSource().getState();
        const tableElement = document.getElementById('datatable');
        if (!tableElement) return;
        
        if (state === 'loading') {
            tableElement.textContent = 'Loading station data...';
        } else if (state === 'ready') {
            const features = dataLayer.getSource().getFeatures();
            if (features.length > 0) {
                // Generate and populate ASCII table
                const tableContent = generateASCIITable(features);
                tableElement.textContent = tableContent;
                
                // Fit map to data extent with padding
                map.getView().fit(dataLayer.getSource().getExtent(), {
                    size: map.getSize(),
                    padding: [50, 50, 50, 50],
                    maxZoom: 10
                });
                
            } else {
                tableElement.textContent = 'No data available for the selected period.';
            }
        } else if (state === 'error') {
            tableElement.textContent = 'Error loading data. Please try refreshing the page or selecting a different time period.';
        }
    });

    // Handle cursor changes on hover
    map.on('pointermove', (evt) => {
        const pixel = map.getEventPixel(evt.originalEvent);
        const hit = map.hasFeatureAtPixel(pixel);
        const target = map.getTarget();
        if (target?.style) {
            target.style.cursor = hit ? 'pointer' : '';
        }
    });
}

window.addEventListener('DOMContentLoaded', () => {
    // Initialize the map
    initMap();

    // Handle CSV download (vanilla JS)
    const saveBtn = document.getElementById('save');
    if (saveBtn) {
        saveBtn.addEventListener('click', () => {
            const datatable = document.getElementById('datatable');
            if (!datatable) return;
            const content = datatable.textContent.split(/\n/).slice(2).join("\n");
            const link = document.createElement('a');
            link.setAttribute('download', 'isusm.csv');
            link.setAttribute('href', `data:text/plain;charset=utf-8,${encodeURIComponent(content)}`);
            link.click();
        });
    }
});