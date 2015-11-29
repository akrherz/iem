var map;
var vectorLayer;
var renderattr = 'snow';
var datatable;

function makeVectorLayer(dt){
        return new ol.layer.Vector({
                source: new ol.source.Vector({
                        format: new ol.format.GeoJSON(),
                        projection: ol.proj.get('EPSG:3857'),
                    url: '/geojson/snowfall.py?dt='+dt
                }),
                style: function(feature, resolution){
        			console.log([feature.get('station'),
        			                    feature.get('snow')]);
        			datatable.row.add({station: feature.get('station'),
        			                    snow: feature.get('snow')}).draw();
                        if (feature.get(renderattr) != "M"){
                                style = [new ol.style.Style({
                                fill: new ol.style.Fill({
                                  color: 'rgba(255, 255, 255, 0.6)'
                                }),
                                stroke: new ol.style.Stroke({
                                  color: '#319FD3',
                                  width: 1
                                }),
                                text: new ol.style.Text({
                                  font: '14px Calibri,sans-serif',
                                  text: feature.get(renderattr),
                                  fill: new ol.style.Fill({
                                    color: '#fff',
                                    width: 3
                                  })
                                })
                              })];
                        } else {
                                style = [
                                       new ol.style.Style({
                                         image: new ol.style.Circle({
                                           fill: new ol.style.Fill({
                                               color: 'rgba(255,255,255,0.4)'
                                           }),
                                       stroke: new ol.style.Stroke({
                                               color: '#3399CC',
                                                     width: 1.25
                                                   }),
                                       radius: 5
                                     }),
                                     fill: new ol.style.Fill({
                                       color: 'rgba(255,255,255,0.4)'
                                   }),
                                     stroke: new ol.style.Stroke({
                                       color: '#3399CC',
                                     width: 1.25
                                   })
                                   })
                                 ];
                    }
                    return style;
            }
    });
}


$(document).ready(function(){
	datatable = $('#datatable').DataTable({
		columns: [
    { data: 'station' },
    { data: 'snow' }
]});
	var data = {};
	$.ajax({
  type: "POST",
  url: 'lsr_oa.py',
  data: data,
  success: function(mydata){
		var $img = $( '<img/>', {                
		"alt": "test image",
		"class": "img img-responsive",
		"src": 'data:image/png;base64,'+mydata
		}).appendTo($('#icontain'));
	},
  	dataType: 'text'
});


	vectorLayer = makeVectorLayer("2015-11-21");

        map = new ol.Map({
                target: 'map',
                layers: [new ol.layer.Tile({
                        title: "Global Imagery",
                        source: new ol.source.TileWMS({
                                url: 'http://demo.opengeo.org/geoserver/wms',
                                params: {LAYERS: 'nasa:bluemarble', VERSION: '1.1.1'}
                        })
                }),
                new ol.layer.Tile({
                        title: 'State Boundaries',
                        source: new ol.source.XYZ({
                                url : '/c/tile.py/1.0.0/s-900913/{z}/{x}/{y}.png'
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

});