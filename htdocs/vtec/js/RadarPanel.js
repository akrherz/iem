/*
 * RADAR Panel for use in various apps
 */
Ext.ns("App");

App.get_my_url = function(bounds) {
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
	+ ((this.radarTime == null) ? '0' : this.radarTime.format("YmdHi")) + "/" + path;

};

var baseESRILayer = new OpenLayers.Layer.ArcGISCache("ESRI Topo",
		"https://services.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer", {
    layerInfo: {
    	 "currentVersion": 10.2,
    	 "serviceDescription": "This map is designed to be used as a basemap by GIS professionals and as a reference map by anyone. The map includes administrative boundaries, cities, water features, physiographic features, parks, landmarks, highways, roads, railways, and airports overlaid on land cover and shaded relief imagery for added context. The map provides coverage for the world down to a scale of ~1:72k. Coverage is provided down to ~1:4k for the following areas: Australia and New Zealand; India; Europe; Canada; Mexico; the continental United States and Hawaii; South America and Central America; Africa; and most of the Middle East. Coverage down to ~1:1k and ~1:2k is available in select urban areas. This basemap was compiled from a variety of best available sources from several data providers, including the U.S. Geological Survey (USGS), U.S. Environmental Protection Agency (EPA), U.S. National Park Service (NPS), Food and Agriculture Organization of the United Nations (FAO), Department of Natural Resources Canada (NRCAN), GeoBase, Agriculture and Agri-Food Canada, DeLorme, HERE, Esri, OpenStreetMap contributors, and the GIS User Community. For more information on this map, including the terms of use, visit us <a href=\"http://goto.arcgisonline.com/maps/World_Topo_Map \" target=\"_new\" >online<\/a>.",
    	 "mapName": "Layers",
    	 "description": "This map is designed to be used as a basemap by GIS professionals and as a reference map by anyone. The map includes administrative boundaries, cities, water features, physiographic features, parks, landmarks, highways, roads, railways, and airports overlaid on land cover and shaded relief imagery for added context. The map provides coverage for the world down to a scale of ~1:72k. Coverage is provided down to ~1:4k for the following areas: Australia and New Zealand; India; Europe; Canada; Mexico; the continental United States and Hawaii; South America and Central America; Africa; and most of the Middle East. Coverage down to ~1:1k and ~1:2k is available in select urban areas. This basemap was compiled from a variety of best available sources from several data providers, including the U.S. Geological Survey (USGS), U.S. Environmental Protection Agency (EPA), U.S. National Park Service (NPS), Food and Agriculture Organization of the United Nations (FAO), Department of Natural Resources Canada (NRCAN), GeoBase, Agriculture and Agri-Food Canada, DeLorme, HERE, Esri, OpenStreetMap contributors, and the GIS User Community. For more information on this map, including our terms of use, visit us online at http://goto.arcgisonline.com/maps/World_Topo_Map",
    	 "copyrightText": "Sources: Esri, HERE, DeLorme, TomTom, Intermap, increment P Corp., GEBCO, USGS, FAO, NPS, NRCAN, GeoBase, IGN, Kadaster NL, Ordnance Survey, Esri Japan, METI, Esri China (Hong Kong), swisstopo, MapmyIndia, © OpenStreetMap contributors, and the GIS User Community",
    	 "supportsDynamicLayers": false,
    	 "layers": [
    	  {
    	   "id": 0,
    	   "name": "Citations",
    	   "parentLayerId": -1,
    	   "defaultVisibility": false,
    	   "subLayerIds": null,
    	   "minScale": 0,
    	   "maxScale": 0
    	  }
    	 ],
    	 "tables": [],
    	 "spatialReference": {
    	  "wkid": 102100,
    	  "latestWkid": 3857
    	 },
    	 "singleFusedMapCache": true,
    	 "tileInfo": {
    	  "rows": 256,
    	  "cols": 256,
    	  "dpi": 96,
    	  "format": "JPEG",
    	  "compressionQuality": 90,
    	  "origin": {
    	   "x": -2.0037508342787E7,
    	   "y": 2.0037508342787E7
    	  },
    	  "spatialReference": {
    	   "wkid": 102100,
    	   "latestWkid": 3857
    	  },
    	  "lods": [
    	   {
    	    "level": 0,
    	    "resolution": 156543.03392800014,
    	    "scale": 5.91657527591555E8
    	   },
    	   {
    	    "level": 1,
    	    "resolution": 78271.51696399994,
    	    "scale": 2.95828763795777E8
    	   },
    	   {
    	    "level": 2,
    	    "resolution": 39135.75848200009,
    	    "scale": 1.47914381897889E8
    	   },
    	   {
    	    "level": 3,
    	    "resolution": 19567.87924099992,
    	    "scale": 7.3957190948944E7
    	   },
    	   {
    	    "level": 4,
    	    "resolution": 9783.93962049996,
    	    "scale": 3.6978595474472E7
    	   },
    	   {
    	    "level": 5,
    	    "resolution": 4891.96981024998,
    	    "scale": 1.8489297737236E7
    	   },
    	   {
    	    "level": 6,
    	    "resolution": 2445.98490512499,
    	    "scale": 9244648.868618
    	   },
    	   {
    	    "level": 7,
    	    "resolution": 1222.992452562495,
    	    "scale": 4622324.434309
    	   },
    	   {
    	    "level": 8,
    	    "resolution": 611.4962262813797,
    	    "scale": 2311162.217155
    	   },
    	   {
    	    "level": 9,
    	    "resolution": 305.74811314055756,
    	    "scale": 1155581.108577
    	   },
    	   {
    	    "level": 10,
    	    "resolution": 152.87405657041106,
    	    "scale": 577790.554289
    	   },
    	   {
    	    "level": 11,
    	    "resolution": 76.43702828507324,
    	    "scale": 288895.277144
    	   },
    	   {
    	    "level": 12,
    	    "resolution": 38.21851414253662,
    	    "scale": 144447.638572
    	   },
    	   {
    	    "level": 13,
    	    "resolution": 19.10925707126831,
    	    "scale": 72223.819286
    	   },
    	   {
    	    "level": 14,
    	    "resolution": 9.554628535634155,
    	    "scale": 36111.909643
    	   },
    	   {
    	    "level": 15,
    	    "resolution": 4.77731426794937,
    	    "scale": 18055.954822
    	   },
    	   {
    	    "level": 16,
    	    "resolution": 2.388657133974685,
    	    "scale": 9027.977411
    	   },
    	   {
    	    "level": 17,
    	    "resolution": 1.1943285668550503,
    	    "scale": 4513.988705
    	   },
    	   {
    	    "level": 18,
    	    "resolution": 0.5971642835598172,
    	    "scale": 2256.994353
    	   },
    	   {
    	    "level": 19,
    	    "resolution": 0.29858214164761665,
    	    "scale": 1128.497176
    	   }
    	  ]
    	 },
    	 "initialExtent": {
    	  "xmin": -1.9003965069419548E7,
    	  "ymin": -236074.10024122056,
    	  "xmax": 1.9003965069419548E7,
    	  "ymax": 1.458937939490844E7,
    	  "spatialReference": {
    	   "cs": "pcs",
    	   "wkid": 102100
    	  }
    	 },
    	 "fullExtent": {
    	  "xmin": -2.0037507067161843E7,
    	  "ymin": -1.9971868880408604E7,
    	  "xmax": 2.0037507067161843E7,
    	  "ymax": 1.997186888040863E7,
    	  "spatialReference": {
    	   "cs": "pcs",
    	   "wkid": 102100
    	  }
    	 },
    	 "minScale": 5.91657527591555E8,
    	 "maxScale": 1128.497176,
    	 "units": "esriMeters",
    	 "supportedImageFormatTypes": "PNG32,PNG24,PNG,JPG,DIB,TIFF,EMF,PS,PDF,GIF,SVG,SVGZ,BMP",
    	 "documentInfo": {
    	  "Title": "World Topographic Map",
    	  "Author": "Esri",
    	  "Comments": "",
    	  "Subject": "topographic, topography, administrative boundaries, cities, water features, physiographic features, parks, landmarks, highways, roads, railways, airports, land cover, shaded relief imagery",
    	  "Category": "imageryBaseMapsEarthCover (Imagery, basemaps, and land cover)",
    	  "AntialiasingMode": "None",
    	  "TextAntialiasingMode": "Force",
    	  "Keywords": "World,Global,Europe,North America,South America,Southern Africa,Australia,New Zealand,India"
    	 },
    	 "capabilities": "Map,Query,Data",
    	 "supportedQueryFormats": "JSON, AMF",
    	 "exportTilesAllowed": false,
    	 "maxRecordCount": 1000,
    	 "maxImageHeight": 4096,
    	 "maxImageWidth": 4096,
    	 "supportedExtensions": "KmlServer"
    	}
});

App.RadarPanel = Ext.extend(GeoExt.MapPanel, {
	p4326 : new OpenLayers.Projection("EPSG:4326"),
	p900913 : new OpenLayers.Projection("EPSG:900913"),
	vtec : null,
	vteckml : null,
	countykml : null,
	selectControl : null,
	initComponent : function() {
		var config = {
			tbar : { // configured using the anchor layout
				xtype : 'container',
				layout : 'anchor',

				defaults : {
					height : 27,
					anchor : '100%'
				},

				items : [new Ext.Toolbar({
					items : [{
								xtype : 'tbtext',
								text : 'Opacity'
							}, {
								xtype : 'gx_opacityslider',
								name : 'opacity',
								width : 70,
								value : 80	
							}, '-', {
								xtype : 'tbtext',
								text : 'RADAR Info:'
							}, {
								xtype : 'tbtext',
								name : 'status',
								text : '---'
							}, '-', {
								xtype : 'button',
								name : 'legend',
								text : 'Show Legend',
								enableToggle : true,
								toggleHandler : function(btn, state){
									if (!Ext.getCmp("legendWindow")){
										return;
									}
									if (state){
										Ext.getCmp("legendWindow").show();
									} else {
										Ext.getCmp("legendWindow").hide();
									}
								}
							}]
				}), new Ext.Toolbar({
							items : [{
								xtype : 'combo',
								name : 'radar',
								disabled : true,
								editable : false,
								forceSelection : true,
								store : new Ext.data.JsonStore({
											autoDestroy : true,
											autoLoad : false,
											proxy : new Ext.data.HttpProxy({
														url : '/json/radar',
														method : 'GET'
													}),
											root : 'radars',
											fields : [{
														name : 'id'
													}, {
														name : 'name'
													}, {
														name : 'full',
														convert : function(v,
																record) {
															return '['
																	+ record.id
																	+ '] '
																	+ record.name;
														}
													}]
										}),
								valueField : 'id',
								width : 220,
								displayField : 'full',
								typeAhead : true,
								mode : 'local',
								triggerAction : 'all',
								emptyText : 'Select RADAR...',
								selectOnFocus : true,
								lazyRender : true
							}, '-', {
								xtype : 'combo',
								name : 'product',
								disabled : true,
								editable : false,
								forceSelection : true,
								store : new Ext.data.JsonStore({
											autoDestroy : true,
											autoLoad : false,
											proxy : new Ext.data.HttpProxy({
														url : '/json/radar',
														method : 'GET'
													}),
											root : 'products',
											fields : [{
														name : 'id'
													}, {
														name : 'name'
													}, {
														name : 'full',
														convert : function(v,
																record) {
															return '['
																	+ record.id
																	+ '] '
																	+ record.name;
														}
													}]
										}),
								valueField : 'id',
								width : 220,
								displayField : 'full',
								typeAhead : true,
								mode : 'local',
								triggerAction : 'all',
								emptyText : 'Select Product...',
								selectOnFocus : true,
								lazyRender : true
							}, '-', {
								xtype : 'tbtext',
								text : 'Time:'
							}, {
								xtype : 'slider',
								name : 'tslider',
								disabled : true,
								plugins : [new Ext.slider.Tip({
											getText : function(thumb) {
												if (thumb.slider.maxValue == 1) {
													return 'No Times Available';
												}
												return thumb.slider.store
														.getAt(thumb.value - 1)
														.get('ts')
														.fromUTC()
														.format('Y-m-d g:i A T');
											}
										})],
								store : new Ext.data.JsonStore({
											autoDestroy : true,
											autoLoad : false,
											proxy : new Ext.data.HttpProxy({
														url : '../json/radar',
														method : 'GET'
													}),
											root : 'scans',
											fields : [{
														name : 'ts',
														type : 'date',
														dateFormat : 'Y-m-d\\TH:i\\Z'
													}]
										}),
								width : 120,
								minValue : 1,
								maxValue : 1,
								increment : 1
							}]
						})]
			},
			map : {
				allOverlays : false,
				projection : new OpenLayers.Projection("EPSG:900913"),
				units : "m",
				numZoomLevels : 18,
				maxResolution : 156543.0339,
				controls : [new OpenLayers.Control.Navigation(),
						new OpenLayers.Control.PanZoom(),
						new OpenLayers.Control.ArgParser()],

				maxExtent : new OpenLayers.Bounds(-20037508, -20037508,
						20037508, 20037508.34)
			},
			controls : [new OpenLayers.Control.Navigation(),
                        new OpenLayers.Control.PanZoom(),
                        new OpenLayers.Control.ArgParser()],
            layers :  [baseESRILayer,
                       new OpenLayers.Layer.TMS('RADAR',
            		   'http://mesonet1.agron.iastate.edu/cache/tile.py/', {
            	   layername : 'cwsu-900913',
            	   service : '1.0.0',
            	   type : 'png',
            	   visibility : true,
            	   isBaseLayer: false,
            	   opacity : 1,
            	   getURL : App.get_my_url,
            	   radarProduct : 'N0Q',
            	   radar : 'DMX',
            	   radarTime : null
               }),  new OpenLayers.Layer.WMS("Counties", "http://mesonet.agron.iastate.edu/c/c.py/",
            		    {layers      : 'c-900913',
            	     format      : 'image/png',
            	     transparent : 'true'},{
            	     opacity     : 1.0,
            	     singleTile  : false,
            	     isBaseLayer : false,
            	     visibility  : false,
            	     buffer      : 0
            	}),
               App.SBWFeatureStore.layer,
               App.LSRFeatureStore.layer,
               App.SBWIntersectionFeatureStore.layer],
			extent : new OpenLayers.Bounds(-14427682, 1423562, -7197350,
					8673462)
		};
		Ext.apply(this, Ext.apply(this.initialConfig, config));

		App.RadarPanel.superclass.initComponent.call(this);
		this.doLayout();
		this.hookUpListeners();
		ls = new OpenLayers.Control.LayerSwitcher();
		this.map.addControl( ls );
		ls.maximizeControl();

	},
	setVTEC : function(vtecObj) {
		// console.log("Setting VTEC");
		this.vtec = vtecObj;
		if (!this.map) {
			// console.log("Uh oh, googlepanel is not up yet");
			return;
		}

		var point = new OpenLayers.LonLat((this.vtec.x1 + this.vtec.x0) / 2,
				(this.vtec.y1 + this.vtec.y0) / 2);
		this.setCenterPoint(point, 9);

		App.LSRFeatureStore.reload({
			add    : false,
		    params : {
		         'sts': vtecObj.issue.format('YmdHi'),
		         'ets': vtecObj.expire.format('YmdHi'),
		         'phenomena': vtecObj.phenomena,
		         'significance': vtecObj.significance,
		         'eventid': vtecObj.eventid,
		         'year': vtecObj.year,
		         'wfo': vtecObj.wfo
		    }
		});
		
		App.SBWFeatureStore.reload({
			add    : false,
		    params : {
		         'sts': vtecObj.issue.format('YmdHi'),
		         'ets': vtecObj.expire.format('YmdHi'),
		         'phenomena': vtecObj.phenomena,
		         'significance': vtecObj.significance,
		         'eventid': vtecObj.eventid,
		         'year': vtecObj.year,
		         'wfo': vtecObj.wfo
		    }
		});

		App.SBWIntersectionFeatureStore.reload({
			add    : false,
		    params : {
		         'sts': vtecObj.issue.format('YmdHi'),
		         'ets': vtecObj.expire.format('YmdHi'),
		         'phenomena': vtecObj.phenomena,
		         'significance': vtecObj.significance,
		         'eventid': vtecObj.eventid,
		         'year': vtecObj.year,
		         'wfo': vtecObj.wfo
		    }
		});
		
		this.countykml = "http://mesonet.agron.iastate.edu/kml/sbw_county_intersect.php?"
				+ Ext.urlEncode(this.vtec);
		this.lsrkml = "http://mesonet.agron.iastate.edu/kml/sbw_lsrs.php?"
				+ Ext.urlEncode(this.vtec);
		this.vteckml = "http://mesonet.agron.iastate.edu/kml/vtec.php?"
			+ Ext.urlEncode(this.vtec);
		this.placefile = "http://mesonet.agron.iastate.edu/request/grx/vtec.php?"
			+ Ext.urlEncode(this.vtec);
		
		this.updateURL();
	},
	setRadar : function(newValue) {
		//console.log("setRadar:"+ newValue);
		this.getRadarLayer().radar = newValue;
		this.getToolbar("radar").setValue(newValue);
		this.loadProducts();
	},
	setProduct : function(newValue) {
		this.getRadarLayer().radarProduct = newValue;
		this.getToolbar("product").setValue(newValue);
		this.loadTimes();
		lw = Ext.getCmp("legendWindow");
		if (!lw){
			lw = new Ext.Window({
				id: 'legendWindow', 
				closeAction : 'hide',
				title : 'N0R',
				closable : false,
				html : '<img src="../GIS/legends/N0R.gif" />'
			});
			lw.show();
			lw.hide();
		}
		if (lw !== 'undefined'){
			lw.setTitle(newValue);
			lw.update('<img src="../GIS/legends/'+newValue+'.gif" />');
		}
	},
	setTime : function(newValue) {
		if (newValue != null) {
			this.getRadarLayer().radarTime = newValue;
		}
		var rl = this.getRadarLayer();
		this.getFooterbar('status').update(rl.radar + " "
				+ rl.radarProduct + " "
				+ rl.radarTime.fromUTC().format("d M Y g:i A T"));
		rl.setName("RADAR: "+ rl.radar +" "+ rl.radarProduct );
		rl.setVisibility(true);
		rl.redraw();
		this.updateURL();
	},
	updateURL : function(){
		// Update the local URL
		//console.log("updateURL called");
		window.location.href = '#'+ this.vtec.year +"-O-NEW-K"+ 
			this.vtec.wfo +"-"+ this.vtec.phenomena +"-"+ 
			this.vtec.significance +"-"+ 
			String.leftPad(this.vtec.eventid,4,'0') +"/"+ 
			this.getRadarLayer().radar +"-"+ 
			this.getRadarLayer().radarProduct +"-"+
			((this.getRadarLayer().radarTime == null) ? '0' : 
				this.getRadarLayer().radarTime.format("YmdHi"));
	},
	hookUpListeners : function() {
		/* ----------- RADAR ------------- */
		this.getToolbar("radar").on("select", function(cb, record) {
					//console.log("RADAR Changed to: "+ record.get('id'));
					this.setRadar(record.get('id'));

				}, this);
		this.getToolbar("radar").store.on("load", function(store, records,
						options) {
					if (store.getCount() == 0) {
						Ext.MessageBox.show({
							title : 'No Data Found',
							width : 300,
							msg : 'Sorry, no RADARs were available '
								+'for this time.',
							buttons : Ext.MessageBox.OK
						});
						this.getToolbar("radar").disable();
						this.getToolbar("product").disable();
						this.getToolbar("tslider").disable();
						return;
					}
					this.getToolbar("radar").enable();
					/* Initially defined from the URL */
					if (App.initRadar){
						//console.log("App.radar set"+ App.initRadar);
						this.setRadar(App.initRadar);
						delete App.initRadar;
						return;
					}
					this.setRadar(records[0].get('id'));
				}, this);

		/* ------------ Product --------------- */
		this.getToolbar("product").on("select", function(cb, record) {
					// console.log("Product Changed to: "+ record.get("id"));
					this.setProduct(record.get("id"));
				}, this);
		this.getToolbar("product").store.on("load", function(store, records,
						options) {
					// console.log("Products Load!");
					if (store.getCount() == 0) {
						Ext.MessageBox.show({
									title : 'No Data Found',
									width : 300,
									msg : 'Sorry, no RADAR products were found '
										+'for this time. Please try another '
										+'RADAR source.',
									buttons : Ext.MessageBox.OK
								});
						this.getToolbar("product").disable();
						this.getToolbar("tslider").disable();
						return;
					}
					this.getToolbar("product").enable();
					/* Initially defined from the URL */
					if (App.initRadarProduct){
						this.getToolbar("product").setValue(App.initRadarProduct);
						this.setProduct(App.initRadarProduct);
						delete App.initRadarProduct;
						return;
					}
					/* Default to first entry, which is the closest */
					if (store.find("id", "N0Q") > -1){
						this.getToolbar("product").setValue("N0Q");
						this.setProduct("N0Q");
						return;
					}
					if (store.find("id", "N0R") > -1){
						this.getToolbar("product").setValue("N0R");
						this.setProduct("N0R");
						return;
					}
					/* Default to first entry, which is the closest */
					this.setProduct(records[0].get('id'));
				}, this);
		
		/* ------------ Time Slider ------------ */
		this.getToolbar("tslider").on("changecomplete",
				function(slider, newValue) {
					this.setTime(slider.store.getAt(newValue - 1).get("ts"));
				}, this);
		this.getToolbar("tslider").store.on("load", function(store, records,
						options) {
					// console.log("Times Loaded!");
					if (store.getCount() == 0) {
						Ext.MessageBox.show({
							title : 'No Data Found',
							width : 300,
							msg : 'Sorry, no RADAR scans were found '
								+'for this time. Please try another '
								+'RADAR source or product.',
							buttons : Ext.MessageBox.OK
						});
						this.getToolbar("tslider").disable();
						return;
					}
					this.getToolbar("tslider").enable();
					this.getToolbar("tslider").maxValue = store.getCount();
					/* Initially defined from the URL */
					if (App.initRadarTime){
						var idx = store.find('ts', App.initRadarTime);
						if (idx > -1){
							this.getToolbar("tslider").setValue(idx+1);
							this.setTime(App.initRadarTime);
						}
						delete App.initRadarTime;
						return;
					}
					this.getToolbar("tslider").setValue(1);
					/* Default to first entry, which is the closest */
					this.setTime(records[0].get('ts'));
					this.getRadarLayer().setVisibility(true);
				}, this);

		/* ------------ Opacity Slider ------------ */
		this.getFooterbar("opacity").setLayer( this.getRadarLayer() );
	},
	loadProducts : function() {
		/* Hide RADAR! */
		this.getRadarLayer().setVisibility(false);
		/* Empty out the products */
		this.getToolbar("product").store.removeAll();
		/* Reload the data store for products */
		this.getToolbar("product").store.load({
					params : {
						operation : 'products',
						radar : this.getToolbar("radar").getValue(),
						start : this.vtec.radarstart.format('Y-m-d\\TH:i\\Z')
					}
				});
	},
	loadTimes : function() {
		//console.log("loadTimes called");
		this.getToolbar("tslider").store.load({
					params : {
						operation : 'list',
						product : this.getToolbar("product").getValue(),
						radar : this.getToolbar("radar").getValue(),
						start : this.vtec.radarstart.format('Y-m-d\\TH:i\\Z'),
						end : this.vtec.radarend.format('Y-m-d\\TH:i\\Z')
					}
				});
	},
	getToolbar : function(name) {
		return this.toolbars[0].find("name", name)[0];
	},
	getFooterbar : function(name) {
		return this.toolbars[0].find("name", name)[0];
	},
	setCenterPoint : function(pt) {
		this.getToolbar("radar").store.load({
					params : {
						start : this.vtec.radarstart.format('Y-m-d\\TH:i\\Z'),
						operation : 'available',
						lat : pt.lat,
						lon : pt.lon
					}
				});
		this.map.setCenter(pt.transform(this.p4326, this.p900913), 8);
		/* Wait till the very last instant to initialize this, shrug */
		if (this.selectControl == null){
			this.selectControl = new OpenLayers.Control.SelectFeature([App.SBWFeatureStore.layer,
			               	                                  App.LSRFeatureStore.layer]);
			this.map.addControl( this.selectControl );
			this.selectControl.activate();
		}
	},
	getRadarLayer : function() {
		// TODO: This is a hack bug!
		return this.layers.getAt(4).data.layer;
	},
	afterRender : function() {
		//console.log("afterRender called");
		App.RadarPanel.superclass.afterRender.call(this);

	}
});
Ext.reg('radarpanel', App.RadarPanel);
