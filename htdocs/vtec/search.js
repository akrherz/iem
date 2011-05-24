Ext.BLANK_IMAGE_URL = '../ext/resources/images/default/s.gif';
function post_to_url(path, params, method) {
     method = method || "post";
     var form = document.createElement("form");
     form.setAttribute("method", method);
     form.setAttribute("action", path);
     for(var i=0; i<params.length; i++) {
         var hiddenField = document.createElement("input");
         hiddenField.setAttribute("type", "hidden");
         hiddenField.setAttribute("name", params[i].name);
         hiddenField.setAttribute("value", params[i].value);
         form.appendChild(hiddenField);
     }
     document.body.appendChild(form);
     form.submit();
}

Ext.override(Date, {
			toUTC : function() {
				// Convert the date to the UTC date
				return this.add(Date.MINUTE, this.getTimezoneOffset());
			},

			fromUTC : function() {
				// Convert the date from the UTC date
				return this.add(Date.MINUTE, -this.getTimezoneOffset());
			}
		});

Ext.override(Ext.form.ComboBox, {
			doQuery : function(q, forceAll) {
				if (q === undefined || q === null) {
					q = '';
				}
				var qe = {
					query : q,
					forceAll : forceAll,
					combo : this,
					cancel : false
				};
				if (this.fireEvent('beforequery', qe) === false || qe.cancel) {
					return false;
				}
				q = qe.query;
				forceAll = qe.forceAll;
				if (forceAll === true || (q.length >= this.minChars)) {
					if (this.lastQuery !== q) {
						this.lastQuery = q;
						if (this.mode == 'local') {
							this.selectedIndex = -1;
							if (forceAll) {
								this.store.clearFilter();
							} else {
								this.store.filter(this.displayField, q, true);
							}
							this.onLoad();
						} else {
							this.store.baseParams[this.queryParam] = q;
							this.store.load({
										params : this.getParams(q)
									});
							this.expand();
						}
					} else {
						this.selectedIndex = -1;
						this.onLoad();
					}
				}
			}
		});

states = [["AL", "Alabama"], ["AK", "Alaska"], ["AZ", "Arizona"],
		["AR", "Arkansas"], ["CA", "California"], ["CO", "Colorado"],
		["CT", "Connecticut"], ["DE", "Delaware"], ["FL", "Florida"],
		["GA", "Georgia"], ["HI", "Hawaii"], ["ID", "Idaho"],
		["IL", "Illinois"], ["IN", "Indiana"], ["IA", "Iowa"],
		["KS", "Kansas"], ["KY", "Kentucky"], ["LA", "Louisiana"],
		["ME", "Maine"], ["MD", "Maryland"], ["MA", "Massachusetts"],
		["MI", "Michigan"], ["MN", "Minnesota"], ["MS", "Mississippi"],
		["MO", "Missouri"], ["MT", "Montana"], ["NE", "Nebraska"],
		["NV", "Nevada"], ["NH", "New Hampshire"], ["NJ", "New Jersey"],
		["NM", "New Mexico"], ["NY", "New York"], ["NC", "North Carolina"],
		["ND", "North Dakota"], ["OH", "Ohio"], ["OK", "Oklahoma"],
		["OR", "Oregon"], ["PA", "Pennsylvania"], ["RI", "Rhode Island"],
		["SC", "South Carolina"], ["SD", "South Dakota"], ["TN", "Tennessee"],
		["TX", "Texas"], ["UT", "Utah"], ["VT", "Vermont"], ["VA", "Virginia"],
		["WA", "Washington"], ["WV", "West Virginia"], ["WI", "Wisconsin"],
		["WY", "Wyoming"],
		["AM", "Atlantic Ocean AM"],
		["AN", "Atlantic Ocean AN"],
		["AS", "AS"],
		["DC", "Distict of Columbia"],
		["GM", "Gulf of Mexico"],
		["GU", "Guam"],
		["LC", "Lake St. Clair"],
		["LE", "Lake Erie"],
		["LH", "Lake Huron"],
		["LM", "Lake Michigan"],
		["LO", "Lake Ontario"],
		["LS", "Lake Superior"],
		["PH", "Hawaii PH Zones"],
		["PK", "Alaska PK Zones"],
		["PM", "Zones PM"],
		["PR", "Puerto Rico"],
		["PS", "Zones PS"],
		["PZ", "Pacific Ocean PZ"],
		["SL", "St. Lawrence River"]
		];

Ext.onReady(function() {

	Ext.namespace("iemdata");
	var pDict = new Ext.data.SimpleStore({
				idIndex : 0,
				fields : ['abbr', 'name'],
				data : iemdata.vtec_phenomena_dict
			});
	var sDict = new Ext.data.SimpleStore({
				idIndex : 0,
				fields : ['abbr', 'name'],
				data : iemdata.vtec_sig_dict
			});
	var eventStore = new Ext.data.Store({
				autoLoad : false,
				proxy : new Ext.data.HttpProxy({
							url : 'events.php'
						}),
				baseParams : {
					'ugc' : 'IAC001'
				},
				reader : new Ext.data.JsonReader({
							root : 'events',
							id : 'id'
						}, [{
									name : 'id',
									mapping : 'id'
								}, {
									name : 'eventid',
									type : 'float'
								}, {name: 'wfo'},
								{
									name : 'phenomena'
								}, {
			name : 'pstring',
			convert : function(val, record){
				rec = pDict.getById(record.phenomena);
				if (rec) {
					return rec.data.name;
				} else {
					return record.phenomena;
				}
			}
		},{
			name : 'sig_string',
			convert : function(val, record){
				rec = sDict.getById(record.significance);
				if (rec) {
					return rec.data.name;
				} else {
					return record.phenomena;
				}
			}
		},{
									name : 'significance'
								}, {
									name : 'expire',
									type : 'date',
									dateFormat : 'Y-m-d H:i'
								}, {
									name : 'issue',
									type : 'date',
									dateFormat : 'Y-m-d H:i'
								}])
			});

	var ugcStore = new Ext.data.Store({
				autoLoad : false,
				proxy : new Ext.data.HttpProxy({
							url : '../json/state_ugc.php'
						}),
				baseParams : {
					'state' : 'IA'
				},
				reader : new Ext.data.JsonReader({
							root : 'ugcs',
							id : 'ugc'
						}, [{
									name : 'ugc',
									mapping : 'ugc'
							}, {name : 'name',
								mapping : 'name'
							},
								{
								name : 'nicename',
								convert : function(val, record){
									
									var e = record.ugc.substr(2,1) == "Z" ? " (Zone) " : "";
									var s = String.format("[{0}] {1} {2}", record.ugc, 
										record.name, e);
							
									return s;
								}
								}])
			});

	var ugcCB = new Ext.form.ComboBox({
				store : ugcStore,
				displayField : 'nicename',
				valueField : 'ugc',
				width : 300,
				mode : 'local',
				triggerAction : 'all',
				fieldLabel : 'County/Zone',
				emptyText : 'Then Select County/Zone...',
				typeAhead : false,
//				itemSelector : 'div.search-item',
				hideTrigger : false,
				listeners : {
					select : function(cb, record, idx) {
						eventStore.load({
									add : false,
									params : {
										ugc : record.data.ugc
									}
								});
						gp.setTitle("VTEC Events for: " + record.data.nicename);
						return false;
					}
				}
			});

	var stateCB = new Ext.form.ComboBox({
		hiddenName : 'state',
		store : new Ext.data.SimpleStore({
					fields : ['abbr', 'name'],
					data : states
				}),
		valueField : 'abbr',
		width : 180,
		fieldLabel : 'Step 1: Select State',
		displayField : 'name',
		typeAhead : true,
		tpl : '<tpl for="."><div class="x-combo-list-item">[{abbr}] {name}</div></tpl>',
		mode : 'local',
		triggerAction : 'all',
		emptyText : 'Select/or type here...',
		selectOnFocus : true,
		lazyRender : true,
		id : 'stateselector',
		listeners : {
			select : function(cb, record, idx) {
				ugcStore.load({
							add : false,
							params : {
								state : record.data.abbr
							}
						});
				return false;
			}
		}
	});

	var form = new Ext.form.FormPanel({
				applyTo : 'myform',
				labelAlign : 'top',
				width : 320,
				style : 'padding-left: 5px;',
				title : 'Select County/Zone to search for...',
				items : [stateCB, ugcCB]

			});

	var gp = new Ext.grid.GridPanel({
				height : 500,
				width : 650,
				title : 'Events Listing',
				loadMask : {
					msg : 'Loading Data...'
				},
				store : eventStore,
				tbar : [{
	                                        id : 'grid-excel-button',
	                                        icon : '../lsr/icons/excel.png',
	                                        text : 'Export to Excel...',
	                                        handler : function() {
	                                                var xd = gp.getExcelXml(true);
	                                                if (Ext.isIE6 || Ext.isIE7 || Ext.isIE8 || Ext.isSafari
	                                                                || Ext.isSafari2 || Ext.isSafari3) {
	                                                        var dataURL = 'exportexcel.php';
	                                                        params = [{
	                                                                                name : 'ex',
	                                                                                value : xd
	                                                                        }];
	                                                        post_to_url(dataURL, params, 'post');
	                                                } else {
	                                                        document.location = 'data:application/vnd.ms-excel;base64,'
	                                                                        + Base64.encode(xd);
	                                                }
	                                        }
                                }],
				columns : [{
							'header' : 'Event ID',
							dataIndex : 'eventid',
							width : 50,
							renderer : function(value, metaData, record){
								var url = String.format("/vtec/#{0}-O-NEW-K{1}-{2}-{3}-{4}", record.data.issue.format('Y'),
									record.data.wfo, record.data.phenomena, record.data.significance,
									String.leftPad(record.data.eventid,4,'0'));
								return "<a href='"+url+"' target='_blank'>"+ value +"</a>";
							}
						}, {
							'header' : 'Phenomena',
							sortable : true,
							dataIndex : 'pstring',
							width : 150
						}, {
							'header' : 'Significance',
							sortable : true,
							dataIndex : 'sig_string'
						}, {
	header : 'VTEC Phenomena',
	hidden : true,
	dataIndex : 'phenomena'
},{
	header : 'VTEC Significance',
	hidden : true,
	dataIndex : 'significance'
},{
							'header' : 'Issued',
							sortable : true,
							dataIndex : 'issue',
							width : 150,
							renderer : function(value) {
								return value.fromUTC().format('M d, Y g:i A');
							}
						}, {
							'header' : 'Expired',
							sortable : true,
							dataIndex : 'expire',
							width : 150,
							renderer : function(value) {
								return value.fromUTC().format('M d, Y g:i A');
							}
						}]
			});
	gp.render('mytable');
	gp.doLayout();

});
