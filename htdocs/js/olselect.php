<?php
/*
 * Emit some javascript that drives our selector widget, this code is
 * 'called' from all sorts of apps, so be careful!
 */
require_once "../../config/settings.inc.php";
require_once "../../include/forms.php";
$network = isset($_GET['network']) ? xssafe($_GET['network']) : 'IA_ASOS';
$multi = isset($_GET["multi"]);
header("Content-type: application/javascript");
$uri = sprintf("/api/1/network/%s.geojson", $network);

echo <<<EOF
var map;
var vectorLayer;
var element;
var popup;

function selectAllStations(){
  $("#olstation").find('option').attr('selected','selected');
}

$(document).ready(function(){

    vectorLayer = new ol.layer.Vector({
        source: new ol.source.Vector({
            url: '{$uri}',
            format: new ol.format.GeoJSON()
        }),
        style: function(feature, resolution){
            var color = feature.get("online") ? '#00ff00' : '#ffff00';
            var zindex = feature.get("online") ? 100 : 99;
            return [
                new ol.style.Style({
                    zIndex: zindex,
                    image: new ol.style.Circle({
                        fill: new ol.style.Fill({
                            color: color
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
    vectorLayer.getSource().on('change', function(e){
        if (vectorLayer.getSource().getState() == 'ready'){
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
                        params: {LAYERS: 'bluemarble', VERSION: '1.1.1'}
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

    var layerSwitcher = new ol.control.LayerSwitcher();
    map.addControl(layerSwitcher);

    jQuery('<div/>', {
        id: 'mappopup',
        style: 'width: 200px;'
    }).appendTo('#map');
    element = document.getElementById('mappopup');
    popup = new ol.Overlay({
        element: element,
        positioning: 'bottom-center',
        stopEvent: false
    });
    map.addOverlay(popup);
    
    // display popup on click
    map.on('click', function(evt) {
        var feature = map.forEachFeatureAtPixel(evt.pixel,
             function(feature, layer) {
                 return feature;
             });
        $(element).popover('destroy');
        if (feature) {
            var geometry = feature.getGeometry();
            var coord = geometry.getCoordinates();
            popup.setPosition(coord);
            $(element).popover({
                'placement': 'top',
                'animation': false,
                'html': true,
                'content': '<p>'+
                    feature.get('name') +
                    '<br /><strong>Online:</strong> ' + feature.get('online') +
                    '</p>'
              });
            $(element).popover('show');
            // Set the select form to proper value
               $('select[name="station"]').select2().val(feature.get('id')).trigger('change');
          } 
   });

});
EOF;
