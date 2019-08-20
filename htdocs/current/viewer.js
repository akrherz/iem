var map;
var n0q;
var webcamGeoJsonLayer;
var sbwlayer;
var selectControl;
var ts = null;
var aqlive = 0;
var showlogo = 1;
var selectedCameraFeature;
var realtimeMode = true;
var webcamURLS = {};
var webcamTimes = {};
var webcamNames = {};
var ISOFMT = "Y-MM-DD[T]HH:mm:ss[Z]";

function selectMapFeature(){
	selectControl.unselectAll();
	webcamGeoJsonLayer.features.forEach(function(feat){
		if (feat.data.cid == cameraID){
			selectControl.select(feat);
		}
	});
}
function liveShot()
{
	if (aqlive) return;
	aqlive = true;
	ts = new Date();
	$("#webcam_image").attr('src', "/current/live/"+ cameraID +".jpg?ts="+ts.getTime());
	aqlive = false;
}
function setCameraFromForm(cid){
	setCamera(cid);
	var feature = webcamGeoJsonLayer.getSource().getFeatureById(cid);
	if (feature){
    	if (feature != selectedCameraFeature){
    		if (selectedCameraFeature){
    			selectedCameraFeature.setStyle(feature.getStyle());
    		}
    	}
    	cameraStyle2.getImage().setRotation(parseInt(feature.get('angle')) / 180. * 3.14);
    	feature.setStyle(cameraStyle2);
    	selectedCameraFeature = feature;
    	setCamera(feature.get('cid'));
	}
}
function updateHREF(){
	var extra = realtimeMode ? "" : "/" + $('#dtpicker').data('DateTimePicker').date().utc().format(ISOFMT);
	window.location.href = '#'+cameraID + extra;
}

function updateCamera()
{
    var imgurl = webcamURLS[cameraID];
    if (imgurl !== undefined){
    	$("#webcam_image").attr('src', imgurl);
    	$("#webcam_title").html(cameraID.substring(0, 4) +"-TV " +
    		webcamNames[cameraID] +' @ '+
    		moment(webcamTimes[cameraID]).format("h:mm A"));
    	updateHREF();
    }
    
}
function cronMinute(){
	// We are called every minute
	if (!realtimeMode) return;
	refreshRADAR();
	refreshJSON();

}

function getRADARSource(){
	var dt = moment();
	if (!realtimeMode) dt = $('#dtpicker').data('DateTimePicker').date();
	dt.subtract(dt.minutes() % 5, 'minutes');
	var prod = dt.year() < 2011 ? 'N0R': 'N0Q';
	$("#radar_title").html('US Base Reflectivity @ '+ dt.format("h:mm A"));
    return new ol.source.XYZ({
		url: '/cache/tile.py/1.0.0/ridge::USCOMP-'+prod+'-'+dt.utc().format('YMMDDHHmm')+'/{z}/{x}/{y}.png'
	});
}


function refreshRADAR(){
    if (n0q){
        n0q.setSource(getRADARSource());
    }
}
function refreshJSON(){
	var url = "/geojson/webcam.php?network=TV";
	if (!realtimeMode){
		// Append the current timestamp to the URI
		url += "&ts=" + $('#dtpicker').data('DateTimePicker').date().utc().format(ISOFMT);
	}
	var newsource = new ol.source.Vector({
		url: url,
		format: new ol.format.GeoJSON()
	});
	newsource.on('change', function(){
		if (webcamGeoJsonLayer.getSource().getFeatures().length == 0){
			var msg = "No Archived Imagery Found!";
			if ($('#dtpicker').data('DateTimePicker').date().minutes() % 5 != 0){
				msg = "No data, try picking minute divisible by 5!";
			}
			$('#webcam_title').html(msg);
		}
	});
	webcamGeoJsonLayer.setSource(newsource);
	
	var url = "/geojson/sbw.geojson";
	if (!realtimeMode){
		// Append the current timestamp to the URI
		url += "?ts=" + $('#dtpicker').data('DateTimePicker').date().utc().format(ISOFMT);
	}
	sbwlayer.setSource(new ol.source.Vector({
		url: url,
		format: new ol.format.GeoJSON()
	}));
}
function setCamera(cid){
	$("#c"+cid).prop('checked', true);
	cameraID = cid;	
	updateHREF();
	updateCamera();
}
function cb_siteOver(feature){
	if (cameraID != feature.data.cid){
		setCamera( feature.data.cid );  
	}
};
var sbwLookup = {
		 "TO": 'red',
		 "MA": 'purple',
		 "EW": 'green',
		 "SV": 'yellow'
		};

var sbwStyle = [new ol.style.Style({
    stroke: new ol.style.Stroke({
      color: '#FFF',
      width: 4.5
    })
  }), new ol.style.Style({
	    stroke: new ol.style.Stroke({
	        color: '#319FD3',
	        width: 3
	      })
	    })
  ];

var cameraStyle = new ol.style.Style({
	image: new ol.style.Icon({
		src: '/images/yellow_arrow.png'
	})
});
var cameraStyle2 = new ol.style.Style({
	image: new ol.style.Icon({
		src: '/images/red_arrow.png',
		scale: 1.2
	})
});

function parseURI(){
	var tokens = window.location.href.split('#');
	if (tokens.length == 2){
		var tokens2 = tokens[1].split("/");
		if (tokens2.length == 1){
			setCamera(tokens[1]);
		} else {
			setCamera(tokens2[0]);
			$('#toggle_event_mode button').eq(1).click();
			$('#dtpicker').data('DateTimePicker').date(moment(tokens2[1]));
		}
	}
}


$().ready(function(){

	// Thanks to http://jsfiddle.net/hmgyu371/
	$('#toggle_event_mode button').click(function(){
		if($(this).hasClass('locked_active') || $(this).hasClass('unlocked_inactive')){
			// Enable Archive
			realtimeMode = false;
			$('#dtdiv').show();
			refreshJSON();
		} else{
			// Enable Realtime
			realtimeMode = true;
			$('#dtdiv').hide();
			cronMinute();
		}
	
		$('#toggle_event_mode button').eq(0).toggleClass('locked_inactive locked_active btn-default btn-info');
		$('#toggle_event_mode button').eq(1).toggleClass('unlocked_inactive unlocked_active btn-info btn-default');
	});
	
	$('#dtpicker').datetimepicker({
		defaultDate: new Date(),
		icons: {
            time: "fa fa-clock-o",
            date: "fa fa-calendar"
		}
	});
	$('#dtpicker').on('dp.change', function(){
		if (!realtimeMode) {
			refreshJSON();
			refreshRADAR();
		}
	});
	
	sbwlayer = new ol.layer.Vector({
		title: 'Storm Based Warnings',
		source: new ol.source.Vector({
			url: "/geojson/sbw.geojson",
			format: new ol.format.GeoJSON()
		}),
		style: function(feature, resolution){
			color = sbwLookup[feature.get('phenomena')];
			if (color === undefined) return;
			sbwStyle[1].getStroke().setColor(color);
			return sbwStyle;
		}
	});
	webcamGeoJsonLayer = new ol.layer.Vector({
		title: 'Webcams',
		source: new ol.source.Vector({
			url: "/geojson/webcam.php?network=TV",
			format: new ol.format.GeoJSON()
		}),
		style: function(feature, resolution){
			webcamURLS[feature.getId()] = feature.get('url');
			webcamNames[feature.getId()] = feature.get('name');
			webcamTimes[feature.getId()] = feature.get('valid');
			// OL rotation is in radians!
			if (feature.getId() == cameraID){
				cameraStyle2.getImage().setRotation(
					parseInt(feature.get('angle')) / 180. * 3.14);
				updateCamera();
				return [cameraStyle2];				
			}
			cameraStyle.getImage().setRotation(
				parseInt(feature.get('angle')) / 180. * 3.14);
			return [cameraStyle];
		}
	});
	n0q = new ol.layer.Tile({
		title: 'NEXRAD Base Reflectivity',
		source: getRADARSource()
	});
	map = new ol.Map({
		target: 'map',
		layers: [new ol.layer.Tile({
            title: 'OpenStreetMap',
            visible: true,
            source: new ol.source.OSM()
            }),
            n0q,
            sbwlayer, webcamGeoJsonLayer
		],
		view: new ol.View({
			projection: 'EPSG:3857',
			center: ol.proj.transform([-93.5, 42.1], 'EPSG:4326', 'EPSG:3857'),
			zoom: 6
		})
	});
    var layerSwitcher = new ol.control.LayerSwitcher();
    map.addControl(layerSwitcher);

    map.on('click', function(evt){
    	var feature = map.forEachFeatureAtPixel(evt.pixel,
    			function(feature, layer){
    				return feature;
    			}
    	);
    	if (feature){
    		if (feature.get('cid')){
    	    	if (feature != selectedCameraFeature){
    	    		if (selectedCameraFeature){
    	    			selectedCameraFeature.setStyle(feature.getStyle());
    	    		}
    	    	}
    	    	cameraStyle2.getImage().setRotation(
    	    		parseInt(feature.get('angle')) / 180. * 3.14);
    	    	feature.setStyle(cameraStyle2);
    	    	selectedCameraFeature = feature;
    	    	setCamera(feature.get('cid'));
    		}
    	}
    });
    
    parseURI();
 	    
    window.setInterval(cronMinute, 60000);
});
