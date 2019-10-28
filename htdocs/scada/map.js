var map;
var turbineLayer;
var fanLayer;
var config = {
	bladeLength: 39.0,
	fanAngleDeg: 5.0,
	fanDownstreamLength: 1000.,
	windDirectionDeg: 180.
};
var colors = ['#ffffa6', '#9cf26d', '#76cc94', '#6399ba', '#5558a1', '#c34dee'];
var levels = [0, 1, 2, 3, 4, 5];

var fanStyle = new ol.style.Style({
    fill: new ol.style.Fill({
      color: 'rgba(255, 255, 255, 0)'
    }),
    text: new ol.style.Text({
            font: '14px Calibri,sans-serif',
            stroke: new ol.style.Stroke({
        color: '#fff',
        width: 8
      }),
            fill: new ol.style.Fill({
        color: '#000',
        width: 3
      })
    }),
    stroke: new ol.style.Stroke({
      color: '#000000', //'#319FD3',
      width: 0.5
    })
  });
var turbineStyle = new ol.style.Style({
    image: new ol.style.Circle({
        radius: 4,
        stroke: new ol.style.Stroke({
        	color: '#000000',
        	width: 0.5
        }),
        fill: new ol.style.Fill({
            color: colors[0]
        })
    })
  });

function north2cart(deg){
	var val = 0 - deg + 90;
	if (val < 0){ val += 360.;};
	return val;
}

function rotatePoints(center, points, windDeg) {
	// rotate my points around some center point
	var res = [];
	var angle = deg2rad(north2cart(windDeg));
	for (var i=0; i<points.length; i++) {
		var p = points[i];
	    // translate to center
	    var p2 = [p[0] - center[0], p[1] - center[1]];
	    // rotate using matrix rotation
	    var p3 = [
	    	Math.cos(angle)*p2[0] - Math.sin(angle)*p2[1],
	    	Math.sin(angle)*p2[0] + Math.cos(angle)*p2[1]];
	    // translate back to center
	    var p4 = [ p3[0]+center[0], p3[1]+center[1]];
	    // done with that point
	    res.push(p4);
	};
	return res;
}

function deg2rad(deg){
	return deg / 180. * Math.PI;
}

function createFans(){
	//console.log("createFans() called...");
	// Use our turbine locations from the geojson layer
	fanLayer.getSource().clear();
	$(turbineLayer.getSource().getFeatures()).each(function(i, feat){
		var coords = feat.getGeometry().getCoordinates();
		var x = coords[0];
		var y = coords[1];
		// Compute first 
		var q = config.bladeLength / Math.atan(deg2rad(config.fanAngleDeg));
		var R = q + config.fanDownstreamLength;
		var opp = R * Math.sin(deg2rad(config.fanAngleDeg));
		var points = [
			[x + q, y],
			[x - R + q, y - opp],
			[x - R + q, y + opp],
			[x + q, y]];
		points = rotatePoints(coords, points, config.windDirectionDeg);
		var polyFeature = new ol.Feature({
			wakes: -1,
			geometry: new ol.geom.Polygon([points])
		});
		fanLayer.getSource().addFeature(polyFeature);
	});
	// For each turbine, see how many fans cover it
	$(turbineLayer.getSource().getFeatures()).each(function(i, feat){
		var coord = feat.getGeometry().getCoordinates();
		var fans = fanLayer.getSource().getFeaturesAtCoordinate(coord);
		feat.set('wakes', fans.length - 1, true);
		$(fans).each(function(i, fan){
			fan.set('wakes', fan.get('wakes') + 1, true);
		});
	});
	//Re-render fans
	fanLayer.changed();
	turbineLayer.changed();
	// Update counts
	var counts = [0, 0, 0, 0, 0, 0];
	$(turbineLayer.getSource().getFeatures()).each(function(i, feat){
		var cnt = feat.get('wakes');
		if (cnt > 5) cnt = 5;
		counts[cnt] += 1;
	});
	for (var i=0; i<counts.length; i++){
		$("#t"+i).html(counts[i]);
	}
	counts = [0, 0, 0, 0, 0, 0];
	$(fanLayer.getSource().getFeatures()).each(function(i, feat){
		var cnt = feat.get('wakes');
		if (cnt > 5) cnt = 5;
		counts[cnt] += 1;
	});
	for (i=0; i<counts.length; i++){
		$("#w"+i).html(counts[i]);
	}
}

function init(){
	var geosource = new ol.source.Vector({
		url: 'sites.py',
		format: new ol.format.GeoJSON()
	});
	geosource.on('change', function(){
		createFans();
	});
	turbineLayer = new ol.layer.Vector({
		title: 'Turbines',
		source: geosource,
	    style: function(feature, resolution){
	    	var c = 'rgba(255, 255, 255, 0)'; //hallow
	    	for (var i=(levels.length-2); i>=0; i--){
	    		if (feature.get('wakes') >= levels[i]){
	    			c = colors[i];
	    			break;
	    		}
	    	}
	    	var ts = new ol.style.Style({
	    	    image: new ol.style.Circle({
	    	        radius: 4,
	    	        stroke: new ol.style.Stroke({
	    	        	color: '#000000',
	    	        	width: 0.5
	    	        }),
	    	        fill: new ol.style.Fill({
	    	            color: c
	    	        })
	    	    })
	    	  });
	    	//turbineStyle.getImage().getFill().setColor(c);
	    	return [ts];
	    }
	});
	fanLayer = new ol.layer.Vector({
		title: 'Fans',
		source: new ol.source.Vector({
			features: []
	    }),
	    style: function(feature, resolution){
	    	var c = 'rgba(255, 255, 255, 0)'; //hallow
	    	for (var i=(levels.length-2); i>=0; i--){
	    		if (feature.get('wakes') >= levels[i]){
	    			c = colors[i];
	    			break;
	    		}
	    	}
	    	fanStyle.getFill().setColor(c);
	    	return [fanStyle];
	    }
	});
	
	map = new ol.Map({
        target: 'map',
        layers: [new ol.layer.Tile({
        	title: 'OpenStreetMap',
        	visible: true,
        	source: new ol.source.OSM()
        	}),
        	fanLayer, turbineLayer
        ],
        view: new ol.View({
        	projection: 'EPSG:3857',
            center: ol.proj.transform([-93.39, 42.25], 'EPSG:4326', 'EPSG:3857'),
            zoom: 12
        })
    });
    var layerSwitcher = new ol.control.LayerSwitcher();
    map.addControl(layerSwitcher);

}
function UIinit(){
	var handle = $( "#dirslider-handle" );
    $( "#dirslider" ).slider({
    	min: 0,
    	max: 360,
    	value: 180,
    	create: function() {
    		handle.text( $( this ).slider( "value" ) );
    	},
    	slide: function( event, ui ) {
    		handle.text( ui.value );
    		config.windDirectionDeg = ui.value;
    		createFans();
    	}
    });
	var handle2 = $( "#angleslider-handle" );
    $( "#angleslider" ).slider({
    	min: 0,
    	max: 90,
    	value: 5,
    	create: function() {
    		handle2.text( $( this ).slider( "value" ) );
    	},
    	slide: function( event, ui ) {
    		handle2.text( ui.value );
    		config.fanAngleDeg = ui.value;
    		createFans();
    	}
    });
    $("#bladeLength").keyup(function(){
    	config.bladeLength = parseInt($(this).val());
    	createFans();
    });
    $("#downstreamLength").keyup(function(){
    	config.fanDownstreamLength = parseInt($(this).val());
    	createFans();
    });
}

$(document).ready(function(){
	init();
	UIinit();
});
