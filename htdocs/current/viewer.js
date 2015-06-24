var map;
var n0q;
var jsonlayer;
var sbwlayer;
var selectControl;
var ts = null;
var aqlive = 0;
var showlogo = 1;
var radar = 'nexrad-n0q-900913';
var selectedCameraFeature;

function selectMapFeature(){
	selectControl.unselectAll();
	jsonlayer.features.forEach(function(feat){
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
	document.camera.src = "live.php?id="+ cameraID +"&"+ ts.getTime();
	aqlive = false;
}
function setCameraFromForm(cid){
	setCamera(cid);
	var feature = jsonlayer.getSource().getFeatureById(cid);
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
	window.location.href = '#'+cameraID;
}
function refreshCamera()
{
    ts = new Date();
    imgurl = "/data/camera/640x480/"+ cameraID +".jpg?"+ ts.getTime();
    document.camera.src = imgurl;
}
function refreshRADAR(){
    if (n0q){
    	var ts = new Date();
        n0q.setSource(new ol.source.XYZ({
			url: '/cache/tile.py/1.0.0/'+radar+'/{z}/{x}/{y}.png?'+ ts.getTime()
		}));
    }
}
function refreshJSON(){
	    jsonlayer.setSource(new ol.source.Vector({
			url: "/geojson/webcam.php?network=TV",
		format: new ol.format.GeoJSON()
	}));
	    sbwlayer.setSource(new ol.source.Vector({
			url: "/geojson/sbw.geojson",
		format: new ol.format.GeoJSON()
	}));
}
function setCamera(cid){
	//console.log("setCamera() called");
	document.getElementById("c"+cid).checked = true;
	cameraID = cid;	
	updateHREF();
	refreshCamera();
}
function cb_siteOver(feature){
	if (cameraID != feature.data.cid){
		setCamera( feature.data.cid );  
	}
};
var sbwLookup = {
		 "TO": 'red',
		 "MA": 'purple',
		 "FF": 'green',
		 "EW": 'green',
		 "FA": 'green',
		 "FL": 'green',
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
/*
var styleMap = new OpenLayers.StyleMap({
    'default': {
 	   externalGraphic: "/images/yellow_arrow.png",
        graphicHeight: 20,
        rotation: "\${angle}",
        strokeOpacity: 1
    },
    'select': {
       graphicHeight: 30
    }
});
*/

function switchRADAR(){
	for (var i=0; i < document.radar.nexrad.length; i++)
	{
		if (document.radar.nexrad[i].checked)
		{
			radar = document.radar.nexrad[i].value;
			n0q.setSource(new ol.source.XYZ({
				url: '/cache/tile.py/1.0.0/'+radar+'/{z}/{x}/{y}.png'
			}));
		}
	}
}

$().ready(function(){

	sbwlayer = new ol.layer.Vector({
		title: 'Storm Based Warnings',
		source: new ol.source.Vector({
			url: "/geojson/sbw.geojson",
			format: new ol.format.GeoJSON()
		}),
		style: function(feature, resolution){
			sbwStyle[1].getStroke().setColor(sbwLookup[feature.get('phenomena')]);
			return sbwStyle;
		}
	});
	jsonlayer = new ol.layer.Vector({
		title: 'Webcams',
		source: new ol.source.Vector({
			url: "/geojson/webcam.php?network=TV",
			format: new ol.format.GeoJSON()
		}),
		style: function(feature, resolution){
			// OL rotation is in radians!
			if (feature.getId() == cameraID){
				cameraStyle2.getImage().setRotation(parseInt(feature.get('angle')) / 180. * 3.14);
				return [cameraStyle2];				
			}
			cameraStyle.getImage().setRotation(parseInt(feature.get('angle')) / 180. * 3.14);
			return [cameraStyle];
		}
	});
	n0q = new ol.layer.Tile({
		title: 'NEXRAD Base Reflectivity',
		source: new ol.source.XYZ({
			url: '/cache/tile.py/1.0.0/'+radar+'/{z}/{x}/{y}.png'
		})
	});
	map = new ol.Map({
		target: 'map',
		layers: [new ol.layer.Tile({
            title: 'OpenStreetMap',
            visible: true,
            source: new ol.source.OSM()
            }),
            n0q,
            sbwlayer, jsonlayer
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
    	    	cameraStyle2.getImage().setRotation(parseInt(feature.get('angle')) / 180. * 3.14);
    	    	feature.setStyle(cameraStyle2);
    	    	selectedCameraFeature = feature;
    	    	setCamera(feature.get('cid'));
    		}
    	}
    });
    
	var tokens = window.location.href.split('#');
	if (tokens.length == 2){
		setCamera(tokens[1]);
		
	}
 	    
    window.setInterval(refreshRADAR, 150000);
    window.setInterval(refreshCamera, 60000);
    window.setInterval(refreshJSON, 65000);
});


