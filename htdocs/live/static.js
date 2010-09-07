function osm_getTileURL(bounds) {
     var res = this.map.getResolution();
     var x = Math.round((bounds.left - this.maxExtent.left) / (res * this.tileSize.w));
     var y = Math.round((this.maxExtent.top - bounds.top) / (res * this.tileSize.h));
     var z = this.map.getZoom();
     var limit = Math.pow(2, z);
 	
     if (y < 0 || y >= limit) {
         return OpenLayers.Util.getImagesLocation() + "404.png";
    } else {
        x = ((x % limit) + limit) % limit;
        return this.url + z + "/" + x + "/" + y + "." + this.type;
    }
}

Ext.onReady(function(){

/*
 * Webcams JSON data source 
 */
cameraLayer =  new OpenLayers.Layer.Vector("IEM WebCams",{
     sphericalMercator: true,
     maxExtent : new OpenLayers.Bounds(-20037508.34,-20037508.34,20037508.34,20037508.34),
     eventListeners: {
      'visibilitychanged': function(){
         //updateURL();
      },
      'featureselected': function(feature){
         popup = new GeoExt.Popup({
            title: feature.feature.data.name + ' Webcam',
            feature: feature.feature,
            width:200,
            html: "<p>Hello There <br /><img src=\""+ feature.feature.data.url +"\" />",
            maximizable: true,
            collapsible: true
        });
        // unselect feature when the popup
        // is closed
        popup.show();
      }
     }
});


cameraStore = new GeoExt.data.FeatureStore({
      layer     : cameraLayer,
      fields    : [
         {name: 'cid', type: 'string'},
         {name: 'name'},
         {name: 'county'},
         {name: 'url'}
      ],
      proxy: new GeoExt.data.ProtocolProxy({
            protocol : new OpenLayers.Protocol.HTTP({
              url      : "../geojson/webcam.php",
              format   : new OpenLayers.Format.GeoJSON({
                   externalProjection: new OpenLayers.Projection("EPSG:4326"),
                   internalProjection: new OpenLayers.Projection("EPSG:900913")
               })
             })
      }),
      autoLoad  : true
});


/* Live NEXRAD TMS */
var nexrad = new OpenLayers.Layer.TMS("NEXRAD Composite",
   "http://mesonet.agron.iastate.edu/cache/tile.py/1.0.0/nexrad-n0r-900913/", 
  {
   sphericalMercator: true,
   isBaseLayer      : false,
   getURL           : osm_getTileURL,
   type             :'png'} );


/* Google Physical Layer */
var gphy = new OpenLayers.Layer.Google("Google Physical",{
   type             : G_PHYSICAL_MAP,
   sphericalMercator: true,
   maxExtent        : new OpenLayers.Bounds(-20037508.34,-20037508.34,
                        20037508.34,20037508.34)
});

options = {
    projection    : new OpenLayers.Projection("EPSG:900913"),
    units         : "m",
    numZoomLevels : 18,
    maxResolution : 156543.0339,
    maxExtent     : new OpenLayers.Bounds(-20037508, -20037508,
                                             20037508, 20037508.34)
}


mapObj = new OpenLayers.Map(options);
ls = new OpenLayers.Control.LayerSwitcher();
mapObj.addControl(ls);

var selectCtrl = new OpenLayers.Control.SelectFeature(cameraLayer);
mapObj.addControl(selectCtrl);
selectCtrl.activate();


new Ext.Viewport({
  layout: 'border',
  items:  [{
    region: 'center',
    xtype: 'gx_mappanel',
    map:  mapObj,
    layers: [gphy, nexrad, cameraLayer],
   sphericalMercator: true,
    extent   : new OpenLayers.Bounds(-10757882, 4920650,-10034345, 5388572),
    split    : true
  }]

});


});
