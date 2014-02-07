var map, gj, dtpicker, n0q;
var currentdt = new Date(defaultdt);

function pad(number) {
    var r = String(number);
    if ( r.length === 1 ) {
      r = '0' + r;
    }
    return r;
  }


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

function updateMap(){
	gj.protocol.params.varname = $('#varpicker').val();
	if (currentdt && typeof currentdt != "string"){
		gj.protocol.params.dt = currentdt.toISOString();
	}
	gj.refresh();
	if (n0q.getVisibility()){
		n0q.redraw();
		n0q.setVisibility(false);
		n0q.setVisibility(true);		
	}
}
function get_my_url (bounds) {
    var res = this.map.getResolution();
    var x = Math.round((bounds.left - this.maxExtent.left)
                    / (res * this.tileSize.w));
    var y = Math.round((this.maxExtent.top - bounds.top)
                    / (res * this.tileSize.h));
    var z = this.map.getZoom();

    var path = z + "/" + x + "/" + y + "." + this.type ;
            /* Need no cache buster now that our service IDs are unique
             * + "?"+ parseInt(Math.random() * 9999);
             */
    var url = this.url;
    if (url instanceof Array) {
            url = this.selectUrl(path, url);
    }
    return url + this.service + "/ridge::" + this.radar + "-" + this.radarProduct + "-"
    +  currentdt.toIEMString() + "/" + path;
}


function init(){
	  // Build Map Object
	  map = new OpenLayers.Map( 'map',{
	        projection: new OpenLayers.Projection('EPSG:900913'),
	        displayProjection: new OpenLayers.Projection('EPSG:4326'),
	        units: 'm',
	        wrapDateLine: false,
	        numZoomLevels: 18,
	        maxResolution: 156543.0339,
	        maxExtent: new OpenLayers.Bounds(-20037508, -20037508,
	                                         20037508, 20037508.34)
	  });
	  // Traditional Google Map Layer
	  var googleLayer = new OpenLayers.Layer.Google(
	                'Google Streets',
	                 {'sphericalMercator': true}
	            );

      n0q = new OpenLayers.Layer.TMS(
              'NEXRAD Base Reflectivity',
              'http://mesonet1.agron.iastate.edu/cache/tile.py/', {
                  layername : 'bogus',
                  service : '1.0.0',
                  type : 'png',
                  visibility : true,
                  opacity : 1,
                  getURL : get_my_url,
                  radarProduct : 'N0Q',
                  radar : 'USCOMP',
                  isBaseLayer : false
          }
      );

	  
	  var styleMap = new OpenLayers.StyleMap({
	       'default': {
               strokeColor: "#00FF00",
               strokeOpacity: 1,
               strokeWidth: 3,
               fillColor: "#FF5500",
               fillOpacity: 0.5,
               pointRadius: 6,
               pointerEvents: "visiblePainted",
               // label with \n linebreaks
               label : "${value}",
               fontColor: "black",
               fontSize: "12px",
               fontFamily: "Courier New, monospace",
               fontWeight: "bold",
               labelOutlineColor: "white",
               labelOutlineWidth: 3
	       }
	   });

	  gj = new OpenLayers.Layer.Vector("Data", {
		  protocol: new OpenLayers.Protocol.HTTP({
			  params: {dt: currentdt.toISOString(), 
				  		varname: $('#varpicker').val()},
	          url: "/geojson/agclimate.py",
	          format: new OpenLayers.Format.GeoJSON()
	      }),
	      projection: new OpenLayers.Projection('EPSG:4326'),
	      styleMap: styleMap,
	      strategies: [new OpenLayers.Strategy.Fixed()]
	  });
	  map.addLayers([googleLayer,gj,n0q]);
	   
	  var proj = new OpenLayers.Projection('EPSG:4326');
	   var proj2 = new OpenLayers.Projection('EPSG:900913');
	   var point = new OpenLayers.LonLat(-93.8, 42.2);
	   point.transform(proj, proj2);

	   map.setCenter(point, 7);


	   map.addControl( new OpenLayers.Control.LayerSwitcher({id:'ls'}) );
	   map.addControl( new OpenLayers.Control.MousePosition() );

	   dtpicker = $('#datetimepicker');
	   dtpicker.datetimepicker({
		   showMinute: false,
		   showSecond: false,
		   onSelect: logic,
		   minDate: new Date(2013, 1, 1, 0, 0),
		   timeFormat: 'hh:mm tt'
	   });
	   dtpicker.datetimepicker('setDate', defaultdt);
	   updateMap();
}

$('#plusonehour').click(function(){
	currentdt = new Date(currentdt.valueOf() + 3600000);
	dtpicker.datetimepicker('setDate', currentdt);
	updateMap();
});

$('#minusonehour').click(function(){
	currentdt = new Date(currentdt - 3600000);
	dtpicker.datetimepicker('setDate', currentdt);
	updateMap();
});

$('#varpicker').change(function(){
	updateMap();
});
