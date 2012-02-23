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
														url : '../json/radar',
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
														url : '../json/radar',
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
			layers : new GeoExt.data.LayerStore({
						layers : [new OpenLayers.Layer.Google(
								"Google Streets", // the default
								{
									numZoomLevels : 20,
									sphericalMercator : true,
									maxZoomLevel : 15,
									maxExtent : new OpenLayers.Bounds(
											-20037508.34, -20037508.34,
											20037508.34, 20037508.34)
								}),new OpenLayers.Layer.TMS('RADAR',
						'http://mesonet1.agron.iastate.edu/cache/tile.py/', {
									layername : 'cwsu-900913',
									service : '1.0.0',
									type : 'png',
									visibility : false,
									opacity : 1,
									getURL : App.get_my_url,
									radarProduct : 'N0Q',
									radar : 'DMX',
									radarTime : null,
									isBaseLayer : false
								}), App.SBWFeatureStore.layer,
								App.LSRFeatureStore.layer,
								App.SBWIntersectionFeatureStore.layer]
					}),
			extent : new OpenLayers.Bounds(-14427682, 1423562, -7197350,
					8673462)
		};
		Ext.apply(this, Ext.apply(this.initialConfig, config));

		App.RadarPanel.superclass.initComponent.call(this);
		this.doLayout();
		this.hookUpListeners();
		this.layerSwitcher = new OpenLayers.Control.LayerSwitcher();
		this.map.addControl( this.layerSwitcher );
		this.layerSwitcher.maximizeControl();

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
					// console.log("RADAR Loaded...");
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
						start : this.vtec.issue.format('Y-m-d\\TH:i\\Z')
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
						start : this.vtec.issue.format('Y-m-d\\TH:i\\Z'),
						end : this.vtec.expire.format('Y-m-d\\TH:i\\Z')
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
						start : this.vtec.issue.format('Y-m-d\\TH:i\\Z'),
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
		return this.layers.getAt(1).data.layer;
	},
	afterRender : function() {
		//console.log("afterRender called");
		App.RadarPanel.superclass.afterRender.call(this);

	}
});
Ext.reg('radarpanel', App.RadarPanel);
