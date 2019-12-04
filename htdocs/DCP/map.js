var physical_code = "EP";
var duration = "D";
var days = 2;
var vectorLayer;
var map;
var element;
var fontSize = 14;

function updateURL(){
	window.location.href = "#" + physical_code + "." + duration + "." + days;
}

function updateMap(){
	physical_code = $('#pe').val();
	duration = $('#duration').val();
	days = $('#days').val();
	map.removeLayer(vectorLayer);
	vectorLayer = makeVectorLayer();
	map.addLayer(vectorLayer);
	updateURL();
}

var vectorStyleFunction = function(feature, resolution){
	var style;
	if (feature.get("value") != "M"){
  		style = [new ol.style.Style({
  	        fill: new ol.style.Fill({
  	          color: 'rgba(255, 255, 255, 0.6)'
  	        }),
  	        text: new ol.style.Text({
  	          font: fontSize+'px Calibri,sans-serif',
  	          text: feature.get("value").toString(),
  	          fill: new ol.style.Fill({
  	            color: '#FFFFFF',
  	            width: 1
  	          }),
  	          stroke: new ol.style.Stroke({
  	        	  color: '#000000',
    	          width: 3
    	      })
  	        })
  	      })];
	} else {
		style = [new ol.style.Style({
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


function makeVectorLayer(){
	var vs = new ol.source.Vector({
		format: new ol.format.GeoJSON(),
			projection: ol.proj.get('EPSG:3857'),
			url: '/api/1/shef_currents.geojson?duration='+duration +'&pe=' + physical_code +"&days=" + days
		});
	vs.on('change', function(){
		if (vs.getFeatures().length == 0){
			alert("No Data Found!");
		}
	 });
	return new ol.layer.Vector({
		source: vs,
	  style: vectorStyleFunction
	});
}

$(document).ready(function(){

	vectorLayer = makeVectorLayer();
	var key = 'AsgbmE8m-iBbkypiCOE23M0qElHUfEQtaTvPdDPdM0p7s0N7pJcgrjo70FXjX6bY';
	map = new ol.Map({
		target: 'map',
		layers: [new ol.layer.Tile({
			title: 'Global Imagery',
	        source: new ol.source.BingMaps({key: key, imagerySet: 'Aerial'})
	      }),
		new ol.layer.Tile({
			title: 'State Boundaries',
			source: new ol.source.XYZ({
				url : '/c/tile.py/1.0.0/usstates/{z}/{x}/{y}.png'
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
			var content = "<p><strong>ID:</strong> "+ feature.get('station')
			+"<br /><strong>Value:</strong> " + feature.get('value')
			+"<br /><strong>UTC Valid:</strong> " + feature.get('utc_valid')
			+"</p>";
			$('#popover-content').html(content);
			$(element).popover('show');

		} else {
			$(element).popover('hide');
		}

	});

	// Figure out if we have anything specified from the window.location
	var tokens = window.location.href.split("#");
	if (tokens.length == 2){
		// #YYYYmmdd/variable
		tokens = tokens[1].split(".");
		if (tokens.length == 3){
			physical_code = tokens[0];
			duration = tokens[1];
			days = tokens[2];
		}
	}
	$('select[id=pe] option[value='+physical_code+']').attr("selected", "selected");
	$('select[id=duration] option[value='+duration+']').attr("selected", "selected");
	$("#days").val(days);
	updateMap();

	// Font size buttons
	$('#fplus').click(function(){
		fontSize += 2;
		vectorLayer.setStyle(vectorStyleFunction);
	});
	$('#fminus').click(function(){
		fontSize -= 2;
		vectorLayer.setStyle(vectorStyleFunction);
	});
	
});
