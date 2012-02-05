Ext.ns("App");

App.sbwIStyleMap = new OpenLayers.StyleMap({
    'default': {
        strokeColor: 'black',
        strokeWidth: 6,
        fillOpacity  : 0,
        strokeOpacity: 1
    },
    'select': {
        strokeWidth: 5
    }
});

App.SBWIntersectionFeatureStore = new GeoExt.data.FeatureStore({
		layer : new OpenLayers.Layer.Vector("County Intersection",{
		      styleMap: App.sbwIStyleMap,
		      sphericalMercator: true,
		       visibility: false,
		      maxExtent : new OpenLayers.Bounds(-20037508.34,-20037508.34,
		    		  20037508.34,20037508.34)
		      }),
		fields : [{name: 'sz'}],
		proxy : new GeoExt.data.ProtocolProxy({
			protocol : new OpenLayers.Protocol.HTTP({
				url : "../geojson/sbw_county_intersect.php?",
				format : new OpenLayers.Format.GeoJSON({
					externalProjection : new OpenLayers.Projection("EPSG:4326"),
					internalProjection : new OpenLayers.Projection("EPSG:900913")
				})
			})
		}),
		autoLoad : false
	
});
