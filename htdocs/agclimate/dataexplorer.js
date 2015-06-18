var map, gj, dtpicker, n0q;
var varname = 'tmpf';
var currentdt = new Date(defaultdt);

function pad(number) {
    var r = String(number);
    if ( r.length === 1 ) {
    	r = '0' + r;
    }
    return r;
};


Date.prototype.toIEMString = function() {
	return this.getUTCFullYear()
    + pad( this.getUTCMonth() + 1 )
    + pad( this.getUTCDate() )
    + pad( this.getUTCHours() )
    + '00';
};

if ( !Date.prototype.toISOString ) {
	  ( function() {

	    
	    Date.prototype.toISOString = function() {
	      return this.getUTCFullYear()
	        + '-' + pad( this.getUTCMonth() + 1 )
	        + '-' + pad( this.getUTCDate() )
	        + 'T' + pad( this.getUTCHours() )
	        + ':' + pad( this.getUTCMinutes() )
	        + ':' + pad( this.getUTCSeconds() )
	        + '.' + String( (this.getUTCMilliseconds()/1000).toFixed(3) ).slice( 2, 5 )
	        + 'Z';
	    };

	  }() );
	}

function logic( dstring ){
	currentdt = dtpicker.datetimepicker('getDate'); // toISOString()
	updateMap();
}
function updateTitle(){
	$('#maptitle').text("The map is displaying "
			+ $('#varpicker :selected').text() + " valid at "+ currentdt);
	window.location.href = '#'+ varname +'/'+ currentdt.toISOString();
}

function updateMap(){
	if (currentdt && typeof currentdt != "string"){
		var dt = currentdt.toISOString();
		gj.setSource(new ol.source.Vector({
						url: "/geojson/agclimate.py?dt="+dt,
						format: new ol.format.GeoJSON()
						})
		);
	}
	n0q.setSource(new ol.source.XYZ({
	    url: '/cache/tile.py/1.0.0/ridge::USCOMP-N0Q-'+currentdt.toIEMString()+'/{z}/{x}/{y}.png'
					})
	);
	updateTitle();
}


var mystyle = new ol.style.Style({
	text: new ol.style.Text({
        font: '16px Calibri,sans-serif',
        fill: new ol.style.Fill({
        	color: '#000',
        	width: 3
        }),
        stroke: new ol.style.Stroke({
        	color: '#ff0',
        	width: 5
        })
	})
});

$().ready(function(){
	gj = new ol.layer.Vector({
		title: 'ISUSM Data',
		source: new ol.source.Vector({
			url: "/geojson/agclimate.py",
			format: new ol.format.GeoJSON()
		}),
		style: function(feature, resolution){
			mystyle.getText().setText(feature.get(varname));
			return [mystyle];
		}
	});
	n0q = new ol.layer.Tile({
	    title: 'NEXRAD Base Reflectivity',
	    source: new ol.source.XYZ({
	            url: '/cache/tile.py/1.0.0/ridge::USCOMP-N0Q-'+currentdt.toIEMString()+'/{z}/{x}/{y}.png'
	        })
	});
	map = new ol.Map({
		target: 'map',
		layers: [new ol.layer.Tile({
            title: 'OpenStreetMap',
            visible: true,
            source: new ol.source.OSM()
        	}), n0q, gj],
		view: new ol.View({
            projection: 'EPSG:3857',
            center: ol.proj.transform([-93.5, 42.1], 'EPSG:4326', 'EPSG:3857'),
            zoom: 7
		})
	});

    var layerSwitcher = new ol.control.LayerSwitcher();
    map.addControl(layerSwitcher);



	dtpicker = $('#datetimepicker');
	dtpicker.datetimepicker({
		showMinute: false,
		showSecond: false,
		onSelect: logic,
		minDateTime: (new Date(2013, 1, 1, 0, 0)),
		maxDateTime: (new Date()),
		timeFormat: 'h:mm TT'
	});
	   
	   try{
		   var tokens = window.location.href.split('#');
		   if (tokens.length == 2){
			   var tokens2 = tokens[1].split("/");
			   varname = tokens2[0];
			   $('#varpicker').val(varname);
			   if (tokens2.length == 2){
				   currentdt = (new Date(Date.parse(tokens2[1])));
			   }
			   gj.redraw();
		   }
	   } catch(err) {
		   varname = 'tmpf';
		   currentdt = new Date(defaultdt);
	   }
		   
	   setDate();
	   updateMap();
});

function setDate(){
	   dtpicker.datepicker( "disable" )
	   	.datetimepicker('setDate', currentdt)
	   	.datepicker( "enable" );
}

$('#plusonehour').click(function(e){
	$(this).removeClass('focus');	
	currentdt = new Date(currentdt.valueOf() + 3600000);
	   setDate();
	updateMap();
});

$('#minusonehour').click(function(e){
	$(this).removeClass('focus');
	currentdt = new Date(currentdt.valueOf() - 3600000);
	setDate();
	updateMap();
});

$('#minusoneday').click(function(e){
	$(this).removeClass('focus');
	currentdt = new Date(currentdt.valueOf() - (24 * 3600000));
	setDate();
	updateMap();
});

$('#plusoneday').click(function(e){
	$(this).removeClass('focus');
	currentdt = new Date(currentdt.valueOf() + (24 * 3600000));
	setDate();
	updateMap();
});

$('#varpicker').change(function(){
	varname = $('#varpicker').val();
	gj.setStyle(gj.getStyle());
	updateTitle();
});
