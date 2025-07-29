/* global ol */
let map = null;
let vectorLayer = null;
let element = null;
let popup = null;
let network = null;

document.addEventListener('DOMContentLoaded', () => {
    const mapElement = document.getElementById('map');
    if (!mapElement) {
        return;
    }
    network = mapElement.dataset.network;
    if (network === null){
        return;
    }

    vectorLayer = new ol.layer.Vector({
        source: new ol.source.Vector({
            url: `/api/1/network/${network}.geojson`,
            format: new ol.format.GeoJSON()
        }),
        style: (feature) => {
            const isOnline = feature.get("online");
            const color = isOnline ? '#198754' : '#ffc107'; // Bootstrap success and warning colors
            const strokeColor = isOnline ? '#146c43' : '#ffca2c';
            const zindex = isOnline ? 100 : 99;
            return [
                new ol.style.Style({
                    zIndex: zindex,
                    image: new ol.style.Circle({
                        fill: new ol.style.Fill({
                            color
                        }),
                        stroke: new ol.style.Stroke({
                            color: strokeColor,
                            width: 2.5
                        }),
                        radius: 8
                    })
                })
            ];
        }
    });
    vectorLayer.getSource().on('change', () => {
        if (vectorLayer.getSource().getState() === 'ready') {
            map.getView().fit(
                vectorLayer.getSource().getExtent(),
                {
                    size: map.getSize(),
                    padding: [50, 50, 50, 50]
                }
            );
        }
    });

    map = new ol.Map({
        target: 'map',
        layers: [
            new ol.layer.Tile({
                source: new ol.source.XYZ({
                    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                    attributions: 'Tiles © Esri — Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
                })
            }),
            new ol.layer.Tile({
                source: new ol.source.XYZ({
                    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}',
                    attributions: 'Tiles © Esri'
                }),
                opacity: 0.8,
                zIndex: 1000
            }),
            new ol.layer.Tile({
                source: new ol.source.XYZ({
                    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Transportation/MapServer/tile/{z}/{y}/{x}',
                    attributions: 'Tiles © Esri'
                }),
                opacity: 0.7,
                zIndex: 1001
            }),
            vectorLayer
        ],
        view: new ol.View({
            projection: 'EPSG:3857',
            center: [-10575351, 5160979],
            zoom: 3
        })
    });

    const layerSwitcher = new ol.control.LayerSwitcher();
    map.addControl(layerSwitcher);

    // Create popup element
    element = document.createElement('div');
    element.id = 'mappopup';
    element.style.width = '400px';
    document.getElementById('map').appendChild(element);
    popup = new ol.Overlay({
        element,
        positioning: 'bottom-center',
        stopEvent: false
    });
    map.addOverlay(popup);

    // display popup on click
    map.on('click', (evt) => {
        const feature = map.forEachFeatureAtPixel(evt.pixel,
            (feature2) => {
                return feature2;
            });
        
        // Hide any existing tooltip
        hideTooltip();
        
        if (feature) {
            const geometry = feature.getGeometry();
            const coord = geometry.getCoordinates();
            popup.setPosition(coord);

            // Show custom tooltip
            showTooltip(feature);

            // Set the select form to proper value (Tom Select aware)
            const stationSelect = document.querySelector('select[name="station"]');
            if (stationSelect?.tomselect) {
                // Use Tom Select API to update value and UI
                stationSelect.tomselect.setValue(feature.get('id'), true);
            } else if (stationSelect) {
                // Fallback for plain select
                stationSelect.value = feature.get('id');
                const changeEvent = new Event('change', { bubbles: true });
                stationSelect.dispatchEvent(changeEvent);
            }
        }
    });

});

// Custom tooltip functions with Bootstrap 5 styling
function showTooltip(feature) {
    const tooltip = document.createElement('div');
    tooltip.id = 'custom-tooltip';
    tooltip.className = 'tooltip bs-tooltip-top show';
    tooltip.setAttribute('role', 'tooltip');
    
    const tooltipArrow = document.createElement('div');
    tooltipArrow.className = 'tooltip-arrow';
    
    const tooltipInner = document.createElement('div');
    tooltipInner.className = 'tooltip-inner';
    tooltipInner.innerHTML = `
        <div class="text-start">
            <strong>${feature.get('name')}</strong><br>
            <small class="text-light">Station ID: ${feature.get('id')}</small><br>
            <span class="badge ${feature.get('online') ? 'bg-success' : 'bg-warning text-dark'} mt-1">
                ${feature.get('online') ? 'Online' : 'Offline'}
            </span>
        </div>
    `;
    
    tooltip.appendChild(tooltipArrow);
    tooltip.appendChild(tooltipInner);
    
    // Enhanced styling for better visibility
    tooltip.style.cssText = `${''}
        position: absolute;
        z-index: 1070;
        max-width: 250px;
        font-size: 0.875rem;
        word-wrap: break-word;
        opacity: 1;
        left: 50%;
        bottom: 100%;
        transform: translateX(-50%);
        margin-bottom: 8px;
        pointer-events: none;
    `;
    
    element.appendChild(tooltip);
}

function hideTooltip() {
    const existingTooltip = element.querySelector('#custom-tooltip');
    if (existingTooltip) {
        existingTooltip.remove();
    }
}
