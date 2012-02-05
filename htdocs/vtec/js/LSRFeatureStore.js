Ext.ns("App");

App.lsrStyleMap = new OpenLayers.StyleMap({
			'default' : {
				externalGraphic : '../lsr/icons/other.png',
				fillOpacity : 1,
				pointRadius : 10
			},
			'select' : {
				fillOpacity : 1,
				pointRadius : 15
			}
		});
var lsrLookup = {
		 "0": {externalGraphic: "../lsr/icons/tropicalstorm.gif"},
		 "1": {externalGraphic: "../lsr/icons/flood.png"},
		 "2": {externalGraphic: "../lsr/icons/other.png"},
		 "3": {externalGraphic: "../lsr/icons/other.png"},
		 "4": {externalGraphic: "../lsr/icons/other.png"},
		 "5": {externalGraphic: "../lsr/icons/ice.png"},
		 "6": {externalGraphic: "../lsr/icons/cold.png"},
		 "7": {externalGraphic: "../lsr/icons/cold.png"},
		 "8": {externalGraphic: "../lsr/icons/fire.png"},
		 "9": {externalGraphic: "../lsr/icons/other.png"},
		 "a": {externalGraphic: "../lsr/icons/other.png"},
		 "A": {externalGraphic: "../lsr/icons/wind.png"},
		 "B": {externalGraphic: "../lsr/icons/downburst.png"},
		 "C": {externalGraphic: "../lsr/icons/funnelcloud.png"},
		 "D": {externalGraphic: "../lsr/icons/winddamage.png"},
		 "E": {externalGraphic: "../lsr/icons/flood.png"},
		 "F": {externalGraphic: "../lsr/icons/flood.png"},
		 "G": {externalGraphic: "../lsr/icons/wind.png"},
		 "H": {externalGraphic: "../lsr/icons/hail.png"},
		 "I": {externalGraphic: "../lsr/icons/hot.png"},
		 "J": {externalGraphic: "../lsr/icons/fog.png"},
		 "K": {externalGraphic: "../lsr/icons/lightning.gif"},
		 "L": {externalGraphic: "../lsr/icons/lightning.gif"},
		 "M": {externalGraphic: "../lsr/icons/wind.png"},
		 "N": {externalGraphic: "../lsr/icons/wind.png"},
		 "O": {externalGraphic: "../lsr/icons/wind.png"},
		 "P": {externalGraphic: "../lsr/icons/other.png"},
		 "Q": {externalGraphic: "../lsr/icons/tropicalstorm.gif"},
		 "R": {externalGraphic: "../lsr/icons/heavyrain.png"},
		 "s": {externalGraphic: "../lsr/icons/sleet.png"},
		 "S": {externalGraphic: "../lsr/icons/snow.png"},
		 "T": {externalGraphic: "../lsr/icons/tornado.png"},
		 "U": {externalGraphic: "../lsr/icons/fire.png"},
		 "V": {externalGraphic: "../lsr/icons/avalanche.gif"},
		 "W": {externalGraphic: "../lsr/icons/waterspout.png"},
		 "X": {externalGraphic: "../lsr/icons/funnelcloud.png"},
		 "Z": {externalGraphic: "../lsr/icons/blizzard.png"}
		};
		App.lsrStyleMap.addUniqueValueRules('default', 'type', lsrLookup);
		


App.LSRFeatureStore = new GeoExt.data.FeatureStore({
		layer : new OpenLayers.Layer.Vector("Local Storm Reports", {
					styleMap : App.lsrStyleMap,
					sphericalMercator : true,
					eventListeners : {
						featureselected : function(e){
							feature = e.feature;
							record = App.LSRFeatureStore.getByFeature(feature);
						      html = "Time: "+ record.data.valid.fromUTC()
								.format('Y-m-d g:i A T')
					           +"<br />Event: "+ feature.data.magnitude +" "+ feature.data.typetext
					           +"<br />Source: "+ feature.data.source
					           +"<br />Remark: "+ feature.data.remark ;

	                        popup = new GeoExt.Popup({
	                                                map : this.map,
	                                                location : feature,
	                                                feature : feature,
	                                                title: feature.data.wfo +": "+ feature.data.city,
	                                                width : 200,
	                                                html : html,
	                                                collapsible : true
	                                        });
	                        popup.on({
	                                 close : function() {
	                                     if (OpenLayers.Util.indexOf(
	                                    		 App.LSRFeatureStore.layer.selectedFeatures, 
	                                    		 this.feature) > -1) {
	                                           this.map.controls[4].unselect(this.feature);
	                                                        }
	                                                }
	                                        });
	                        popup.show();

						}
					},
					maxExtent : new OpenLayers.Bounds(-20037508.34,
							-20037508.34, 20037508.34, 20037508.34)
				}),
		fields : [{
					name : 'wfo',
					type : 'string'
				}, {
					name : 'valid',
					type : 'date',
					dateFormat : 'Y-m-d H:i'
				}, {
					name : 'county'
				}, {
					name : 'city'
				}, {
					name : 'st',
					type : 'string'
				}, {
					name : 'typetext',
					type : 'string'
				}, {
					name : 'remark'
				}, {
					name : 'prodlinks'
				}, {
					name : 'wfo'
				}, {
					name : 'source'
				}, {
					name : 'magnitude',
					type : 'float'
				}, {
					name : 'lat',
					type : 'float'
				}, {
					name : 'lon',
					type : 'float'
				}],
		proxy : new GeoExt.data.ProtocolProxy({
			protocol : new OpenLayers.Protocol.HTTP({
				url : "../geojson/lsr.php?inc_ap=yes",
				format : new OpenLayers.Format.GeoJSON({
					externalProjection : new OpenLayers.Projection("EPSG:4326"),
					internalProjection : new OpenLayers.Projection("EPSG:900913")
				})
			})
		}),
		autoLoad : false
	
});
