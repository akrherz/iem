<?
include("../../config/settings.inc.php");
$network = isset($_GET['network']) ? $_GET['network'] : 'IA_ASOS';
header("Content-type: text/plain");
?>
var map, selectedFeature, selectControl;

function cb_siteOver(feature){
  selectedFeature = feature;
  document.olselect.station.value = feature.attributes.sid;
  document.getElementById("sname").innerHTML = feature.attributes.sname;
  popup = new OpenLayers.Popup('chicken', 
              feature.geometry.getBounds().getCenterLonLat(),
              new OpenLayers.Size(200,20),
          "<div style='font-size:1em'>" + feature.attributes.sname +"</div>",
              true);
  feature.popup = popup;
  map.addPopup(popup);
};

function cb_siteOut(feature){ 
    map.removePopup(feature.popup);
  document.getElementById("sname").innerHTML = "No Site Selected";
    feature.popup.destroy();
    feature.popup = null;
};


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
   var styleMap = new OpenLayers.StyleMap({
       'default': {
           fillColor: 'black',
           strokeColor: 'yellow',
           strokeWidth: 2,
           pointRadius: 5,
           strokeOpacity: 1
       },
       'select': {
          fillOpacity: 1,
          strokeColor: 'white',
          fillColor: 'red'
       }
   });

  var geojson = new OpenLayers.Layer.GML("The Network", 
    "<?php echo $rooturl; ?>/geojson/network.php?network=<?php echo $network; ?>",
            {
                projection: new OpenLayers.Projection('EPSG:4326'),
                format: OpenLayers.Format.GeoJSON, 
                styleMap: styleMap
             });
  //geojson.setVisibility(false);
  map.addLayers([googleLayer,geojson]);
   
  // Provide hover capabilities over road_condition layer
  selectControl = new OpenLayers.Control.SelectFeature(geojson, {
       onSelect: cb_siteOver, 
       onUnselect: cb_siteOut
   });
   map.addControl(selectControl);
   selectControl.activate();

   geojson.events.register('loadend', geojson, function() {
     var e = geojson.getDataExtent();
     map.setCenter( e.getCenterLonLat(), geojson.getZoomForExtent(e,false));
   });

   var proj = new OpenLayers.Projection('EPSG:4326');
   var proj2 = new OpenLayers.Projection('EPSG:900913');
   var point = new OpenLayers.LonLat(-93.8, 42.2);
   point.transform(proj, proj2);

   map.setCenter(point, 7);


   map.addControl( new OpenLayers.Control.LayerSwitcher({id:'ls'}) );
   map.addControl( new OpenLayers.Control.MousePosition() );
}
