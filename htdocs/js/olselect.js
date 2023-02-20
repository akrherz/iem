let map = null;
let vectorLayer = null;
let element = null;
let popup = null;
let network = null;
var ol = window.ol || {}; // skipcq: JS-0239

$(document).ready(() => {
    network = $("#map").data("network");
    if (network === null){
        return;
    }

    vectorLayer = new ol.layer.Vector({
        source: new ol.source.Vector({
            url: `/api/1/network/${network}.geojson`,
            format: new ol.format.GeoJSON()
        }),
        style: (feature, _resolution) => {
            const color = feature.get("online") ? '#00ff00' : '#ffff00';
            const zindex = feature.get("online") ? 100 : 99;
            return [
                new ol.style.Style({
                    zIndex: zindex,
                    image: new ol.style.Circle({
                        fill: new ol.style.Fill({
                            color
                        }),
                        stroke: new ol.style.Stroke({
                            color: '#000000',
                            width: 2.25
                        }),
                        radius: 7
                    })
                })
            ];
        }
    });
    vectorLayer.getSource().on('change', (_e) => {
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
        layers: [new ol.layer.Tile({
            title: 'OpenStreetMap',
            visible: true,
            source: new ol.source.OSM()
        }),
        new ol.layer.Tile({
            title: "Global Imagery",
            visible: false,
            source: new ol.source.TileWMS({
                url: 'http://maps.opengeo.org/geowebcache/service/wms',
                params: { LAYERS: 'bluemarble', VERSION: '1.1.1' }
            })
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

    jQuery('<div/>', {
        id: 'mappopup',
        style: 'width: 200px;'
    }).appendTo('#map');
    element = document.getElementById('mappopup');
    popup = new ol.Overlay({
        element,
        positioning: 'bottom-center',
        stopEvent: false
    });
    map.addOverlay(popup);

    // display popup on click
    map.on('click', (evt) => {
        const feature = map.forEachFeatureAtPixel(evt.pixel,
            (feature2, _layer) => {
                return feature2;
            });
        $(element).popover('destroy');
        if (feature) {
            const geometry = feature.getGeometry();
            const coord = geometry.getCoordinates();
            popup.setPosition(coord);
            $(element).popover({
                'placement': 'top',
                'animation': false,
                'html': true,
                'content': `<p>${feature.get('name')} [${feature.get('id')}]<br /><strong>Online:</strong> ${feature.get('online')}</p>`
            });
            $(element).popover('show');
            // Set the select form to proper value
            $('select[name="station"]').select2().val(feature.get('id')).trigger('change');
        }
    });

});
