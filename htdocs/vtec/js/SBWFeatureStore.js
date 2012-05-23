Ext.ns("App");

App.sbwStyleMap = new OpenLayers.StyleMap({
    'default': {
        strokeColor: 'black',
        strokeWidth: 3,
        fillOpacity  : 0,
        strokeOpacity: 1
    },
    'select': {
        strokeWidth: 5
    }
});

var sbwLookup = {
		 "AS": {strokeColor: "black"},
		 "BW": {strokeColor: "black"},
		 "BZ": {strokeColor: "black"},
		 "CF": {strokeColor: "black"},
		 "DS": {strokeColor: "black"},
		 "DU": {strokeColor: "black"},
		 "EC": {strokeColor: "black"},
		 "EH": {strokeColor: "black"},
		 "FG": {strokeColor: "black"},
		 "FR": {strokeColor: "black"},
		 "FW": {strokeColor: "black"},
		 "FZ": {strokeColor: "black"},
		 "GL": {strokeColor: "black"},
		 "HT": {strokeColor: "black"},
		 "HU": {strokeColor: "black"},
		 "HW": {strokeColor: "black"},
		 "HY": {strokeColor: "black"},
		 "HZ": {strokeColor: "black"},
		 "IS": {strokeColor: "black"},
		 "LE": {strokeColor: "black"},
		 "LO": {strokeColor: "black"},
		 "LS": {strokeColor: "black"},
		 "LW": {strokeColor: "black"},
		 "MF": {strokeColor: "black"},
		 "MS": {strokeColor: "black"},
		 "RB": {strokeColor: "black"},
		 "RP": {strokeColor: "black"},
		 "SC": {strokeColor: "black"},
		 "SE": {strokeColor: "black"},
		 "SI": {strokeColor: "black"},
		 "SM": {strokeColor: "black"},
		 "SR": {strokeColor: "black"},
		 "SU": {strokeColor: "black"},
		 "SW": {strokeColor: "black"},
		 "TR": {strokeColor: "black"},
		 "TS": {strokeColor: "black"},
		 "UP": {strokeColor: "black"},
		 "WC": {strokeColor: "black"},
		 "WI": {strokeColor: "black"},
		 "WS": {strokeColor: "black"},
		 "WW": {strokeColor: "black"},
		 "ZF": {strokeColor: "black"},
		 "ZR": {strokeColor: "black"},
		 "TO": {strokeColor: 'red'},
		 "MA": {strokeColor: 'purple'},
		 "FF": {strokeColor: 'green'},
		 "EW": {strokeColor: 'green'},
		 "FA": {strokeColor: 'green'},
		 "FL": {strokeColor: 'green'},
		 "FF": {strokeColor: 'green'},
		 "SV": {strokeColor: 'yellow'}
		};
App.sbwStyleMap.addUniqueValueRules('default', 'phenomena', sbwLookup);


App.SBWFeatureStore = new GeoExt.data.FeatureStore({
		layer : new OpenLayers.Layer.Vector("VTEC Product",{
		      styleMap: App.sbwStyleMap,
		      sphericalMercator: true,
				eventListeners : {
					featureselected : function(e){
						feature = e.feature;
						record = App.SBWFeatureStore.getByFeature(feature);
					      html = "Issue: "+ record.data.issue.fromUTC()
							.format('Y-m-d g:i A T')
				          +"<br />Expire: "+ record.data.expire.fromUTC()
							.format('Y-m-d g:i A T') ;
                        popup = new GeoExt.Popup({
                                                map : this.map,
                                                location : e.feature,
                                                feature : e.feature,
                                                title : "Event",
                                                width : 200,
                                                html : html,
                                                collapsible : true
                                        });
                        popup.on({
                                 close : function() {
                                     if (OpenLayers.Util.indexOf(
                                    		 App.SBWFeatureStore.layer.selectedFeatures, 
                                    		 this.feature) > -1) {
                                           this.map.controls[4].unselect(this.feature);
                                                        }
                                                }
                                        });
                        popup.show();

					}
				},
		       visibility: true,
		      maxExtent : new OpenLayers.Bounds(-20037508.34,-20037508.34,
		    		  20037508.34,20037508.34)
		      }),
		fields : [{name: 'wfo'},
		          {name: 'issue', type: 'date', dateFormat: 'Y-m-d H:i'},
		          {name: 'expire', type: 'date', dateFormat: 'Y-m-d H:i'},
		          {name: 'phenomena'},
		          {name: 'significance'},
		          {name: 'eventid', type:'int'},
		          {name: 'link'}],
		proxy : new GeoExt.data.ProtocolProxy({
			protocol : new OpenLayers.Protocol.HTTP({
				url : "../geojson/sbw.php?",
				format : new OpenLayers.Format.GeoJSON({
					externalProjection : new OpenLayers.Projection("EPSG:4326"),
					internalProjection : new OpenLayers.Projection("EPSG:900913")
				})
			})
		}),
		autoLoad : false
	
});
