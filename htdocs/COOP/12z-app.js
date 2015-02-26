var renderattr = "pday";
var map, coopLayer, azosLayer;

function updateURL(){
    var t = $.datepicker.formatDate("yymmdd",
            $("#datepicker").datepicker('getDate'));
    window.location.href = "#"+t+"/"+renderattr;
}

function updateMap(){
	updateURL();
}

function makeVectorLayer(dt, title, group){
	return new ol.layer.Vector({
		title : title,
		rendercolor: color,
		source: new ol.source.GeoJSON({
			projection: ol.proj.get('EPSG:3857'),
			url: '/geojson/12z.py?group='+group+'&dt='+dt
		}),
		style: function(feature, resolution){
			txt = (feature.get(renderattr) == 0.001) ? "T" : feature.get(renderattr);
			return [new ol.style.Style({
				text: new ol.style.Text({
					font: '14px Calibri,sans-serif',
					text: txt,
					stroke: new ol.style.Stroke({
						color: '#fff',
						width: 3
					}),
					fill: new ol.style.Fill({
						color: 'black'
					})
				})
			})];
		}
	});
}
function get_tms_url(){
    // Generate the TMS URL given the current settings
    return '/cache/tile.py/1.0.0/idep0::mrms-12z24h::'+$.datepicker.formatDate("yy-mm-dd", new Date())+'/{z}/{x}/{y}.png';
}

$(document).ready(function(){

	$( "#datepicker" ).datepicker({
        dateFormat:"DD, d MM, yy",
        minDate: new Date(2009, 1, 1),
        maxDate: new Date()
	});
	$("#datepicker").datepicker('setDate', new Date());
	$("#datepicker").change(function(){
        updateDate();
	});

	coopLayer = makeVectorLayer($.datepicker.formatDate("yy-mm-dd",new Date()),
			'NWS COOP Reports', 'coop');
	azosLayer = makeVectorLayer($.datepicker.formatDate("yy-mm-dd",new Date()),
			'ASOS/AWOS Reports', 'azos');

    map = new ol.Map({
        target: 'map',
        layers: [new ol.layer.Tile({
        		title : 'MRMS 12z 24 Hour',
        		source: new ol.source.XYZ({
        			url: get_tms_url()
        		})
        	}), new ol.layer.Tile({
                title: 'State Boundaries',
                source: new ol.source.XYZ({
                        url : '/c/tile.py/1.0.0/s-900913/{z}/{x}/{y}.png'
                })
        }), coopLayer, azosLayer
        ],
        view: new ol.View({
                projection: 'EPSG:3857',
                center: [-10505351, 5160979],
                zoom: 7
        })
    });

	var layerSwitcher = new ol.control.LayerSwitcher();
	map.addControl(layerSwitcher);

    element = document.getElementById('popup');

    var popup = new ol.Overlay({
            element: element,
            positioning: 'bottom-center',
            stopEvent: false
    });
    map.addOverlay(popup);

    $(element).popover({
            'placement': 'top',
            'html': true,
            content: function() { return $('#popover-content').html(); }
    });

	
    // display popup on click
    map.on('click', function(evt) {
            var feature = map.forEachFeatureAtPixel(evt.pixel,
                            function(feature, layer) {
                    return feature;
            });
            if (feature) {
                    var geometry = feature.getGeometry();
                    var coord = geometry.getCoordinates();
                    popup.setPosition(coord);
                    var content = "<p><strong>"
                    + feature.getId() +" "+ feature.get('name') +"</strong>"
                    +"<br />Precip: "+ feature.get('pday')
                    +"<br />Snow: "+ feature.get('snow')
                    +"<br />Snow Depth: "+ feature.get('snwowd')
                    +"</p>";
                    $('#popover-content').html(content);
                    $(element).popover('show');
            } else {
                    $(element).popover('hide');
            }
    });


	
});
