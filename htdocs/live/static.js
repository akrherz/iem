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


new Ext.Viewport({
  layout: 'border',
  items:  [{
    region: 'center',
    xtype: 'gx_mappanel',
    map:  mapObj,
    layers: [gphy, nexrad],
   sphericalMercator: true,
    extent   : new OpenLayers.Bounds(-10757882, 4920650,-10034345, 5388572),
    split    : true
  }]

});


});
