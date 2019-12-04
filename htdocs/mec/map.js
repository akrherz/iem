var map;
var epsg4326 = new OpenLayers.Projection('EPSG:4326');
var epsg3857 = new OpenLayers.Projection('EPSG:3857');

var context = {
        getFillColor: function(feature){
        	var expansion = feature.data.expansion;
        	if (expansion == 1) return '#0000ff';
        	if (expansion == 2) return '#00ff00';
        	if (expansion == 3) return '#ff0000';
        	if (expansion == 4) return '#00ffff';
        	return 'black';
        }
};

var template = OpenLayers.Util.extend({
    strokeColor: "white",
    strokeOpacity: 1,
    strokeWidth: 2,
    fillColor: "${getFillColor}",
    fillOpacity: 0.5,
    pointRadius: 5,
    pointerEvents: "visiblePainted",
    // label with \n linebreaks
    label : "${id}",
    
    fontColor: "black",
    fontSize: "12px",
    fontFamily: "Courier New, monospace",
    fontWeight: "bold",
    labelAlign: "left",
    labelXOffset: "4",
    labelYOffset: "0",
    labelOutlineColor: "white",
    labelOutlineWidth: 3
});
var style = new OpenLayers.Style(template, {context: context});
var styleMap = new OpenLayers.StyleMap(style);



function cb_siteOver(feature){
	  var popup = new OpenLayers.Popup('chicken',
	              feature.geometry.getBounds().getCenterLonLat(),
	              new OpenLayers.Size(200,20),
	          "<strong>Turbine Name</strong>: " + feature.attributes.turbinename 
	          +"<br /><strong>Expansion<strong>: "+ feature.attributes.expansion
	          +"<br /><strong>Graphing ID</strong>: "+ feature.attributes.id,
	              true);
	  feature.popup = popup;
	  feature.popup.autoSize = true;
	  map.addPopup(popup);
	};

	function cb_siteOut(feature){
	    map.removePopup(feature.popup);
	    feature.popup.destroy();
	    feature.popup = null;
	};



function init(){
	  map = new OpenLayers.Map( 'map',{
	        projection: epsg3857,
	        displayProjection: epsg4326,
	        units: 'm',
	        wrapDateLine: false,
	        numZoomLevels: 18,
	        maxResolution: 156543.0339,
	        maxExtent: new OpenLayers.Bounds(-20037508, -20037508,
	                                         20037508, 20037508.34)
	  });
	  var geojson = new OpenLayers.Layer.Vector("Palmeroy Turbines", {
          protocol: new OpenLayers.Protocol.HTTP({
              url: "sites.py",
              format: new OpenLayers.Format.GeoJSON()
          }),
          projection: epsg4326,
          styleMap: styleMap,
          strategies: [new OpenLayers.Strategy.Fixed()]
	  });

	  map.addLayers([new OpenLayers.Layer.Google(
              "Google Hybrid", {type: google.maps.MapTypeId.HYBRID,
                  numZoomLevels: 20,
                  visibility: true,
                  isBaseLayer: true}
	  	),new OpenLayers.Layer.Google(
              "Google Physical", {type: google.maps.MapTypeId.TERRAIN,
                   visibility: false,
                   isBaseLayer: true}
	  	),new OpenLayers.Layer.Google(
              "Google Streets", {type: google.maps.MapTypeId.ROADMAP,
            	  numZoomLevels: 20,
                      visibility: false,
                           isBaseLayer: true}
	  	),new OpenLayers.Layer.Google(
              "Google Satellite", {type: google.maps.MapTypeId.SATELLITE,
                   numZoomLevels: 22,
                   visibility: false,
                   isBaseLayer: true}
	  	), geojson]);
	  var point = new OpenLayers.LonLat(-94.76, 42.59);
	  point.transform(epsg4326, epsg900913);
	  map.setCenter(point, 12);

	  map.addControl( new OpenLayers.Control.LayerSwitcher({id:'ls'}) );
	  map.addControl( new OpenLayers.Control.MousePosition() );

	  var selectControl = new OpenLayers.Control.SelectFeature(geojson, {
	       onSelect: cb_siteOver,
	       onUnselect: cb_siteOut
	   });
	  map.addControl(selectControl);
	  selectControl.activate();

}