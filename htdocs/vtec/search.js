Ext.BLANK_IMAGE_URL = '/vendor/ext/resources/images/default/s.gif';

function utcdate(v, record){
	return (Ext.Date.parseDate(v, 'c')).toUTC();
}

var warnStore;
var eventStore;
var ugcStore;
var warntable;
var eventTable;
var mapwidget1;
var mapwidget2;
var sdate;
var edate;
var defaultUGC;
var stateCombobox;
var ugcCombobox;
var BACKEND_EVENTS_BYPOINT = '/json/vtec_events_bypoint.py';
var BACKEND_EVENTS_BYUGC = '/json/vtec_events_byugc.py';
var BACKEND_SBW_BYPOINT = '/json/sbw_by_point.py';

Ext.override(Date, {
    toUTC : function() {
                        // Convert the date to the UTC date
        return Ext.Date.add(this, Ext.Date.MINUTE, this.getTimezoneOffset());
    },

    fromUTC : function() {
                        // Convert the date from the UTC date
        return Ext.Date.add(this, Ext.Date.MINUTE, -this.getTimezoneOffset());
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

Ext.define('SBW', {
    extend: 'Ext.data.Model',
    fields: [
        {name: 'id', type: 'string'},
        {name: 'eventid',  type: 'float'},
        {name: 'wfo', type: 'string'},
        {name: 'phenomena', type: 'string'},
        {name: 'ph_name', type: 'string'},
        {name: 'sig_name', type: 'string'},
        {name: 'significance', type: 'string'},
        {name: 'issue', type: 'date', dateFormat: 'c'},
        {name: 'utc_issue', type: 'date', mapping: 'issue', convert: utcdate},
        {name: 'expire', type: 'date', dateFormat: 'c'},
        {name: 'utc_expire', type: 'date', mapping: 'expire', convert: utcdate}
    ]
});

function alinkUGC(){
	window.location.href = Ext.String.format("#byugc/{0}/{1}/{2}/{3}", 
		stateCombobox.getValue(), 
		ugcCombobox.getValue(),
			Ext.Date.format(Ext.getCmp('sdate').getValue(),'Ymd'),
			Ext.Date.format(Ext.getCmp('edate').getValue(),'Ymd')
			);
}

function setupUI() {
	eventStore = new Ext.data.Store({
		autoLoad : false,
		model : 'SBW',
		proxy : {
			type : 'ajax',
			url : BACKEND_EVENTS_BYUGC,
	        reader: {
	            type: 'json',
	            rootProperty: 'events'
	        }
		}
	});

	Ext.define('UGC', {
	    extend: 'Ext.data.Model',
	    fields: [
	        {name: 'ugc', type: 'string'},
	        {name: 'name',  type: 'string'},
	        {name: 'nicename', type:'string', convert: function(val, record){
				var e = record.data.ugc.substr(2,1) == "Z" ? " (Zone) " : "";
				var s = Ext.String.format("[{0}] {1} {2}", record.data.ugc, 
						record.data.name, e);

				return s;
	        }}
	    ]
	});

	
	ugcStore = new Ext.data.Store({
		autoLoad : false,
        model : 'UGC',
        listeners: {
            load: function(){
                var record = ugcStore.findRecord("ugc", defaultUGC);
                defaultUGC = "";
                if (record){
                    ugcCombobox.select(record);
                    ugcCombobox.fireEvent("select", ugcCombobox, record);
                }
                return false;
            }
        },
		proxy : {
			type: 'ajax',
			url : '/json/state_ugc.php',
	        reader: {
	            type: 'json',
	            rootProperty: 'ugcs'
	        }
		}
	});

	ugcCombobox = new Ext.form.ComboBox({
		store : ugcStore,
		displayField : 'nicename',
		valueField : 'ugc',
		queryMode : 'local',
		matchFieldWidth : false,
		triggerAction : 'all',
		fieldLabel : 'County/Zone',
		emptyText : 'Select State First',
		typeAhead : false,
//		itemSelector : 'div.search-item',
		hideTrigger : false,
		listeners : {
			select : function(cb, record, idx) {
                eventStore.getProxy().setUrl(BACKEND_EVENTS_BYUGC);
				eventStore.load({
					add : false,
					params : {
						ugc : record.data.ugc,
						sdate : Ext.Date.format(
								Ext.getCmp('sdate').getValue(),
						'Y/m/d'),
						edate : Ext.Date.format(
								Ext.getCmp('edate').getValue(),
						'Y/m/d')
					}
				});
				eventTable.ugc = record.data.ugc;
				eventTable.setTitle("VTEC Events for: " + record.data.nicename);
				alinkUGC();
				return false;
			}
		}
	});

	Ext.define('States', {
	    extend: 'Ext.data.Model',
	    fields: [
	        {name: 'abbr', type: 'string'},
	        {name: 'name',  type: 'string'}
	    ]
	});
	
	stateCombobox = new Ext.form.ComboBox({
		hiddenName : 'state',
		store : new Ext.data.SimpleStore({
            model : 'States',
			data : states
		}),
		valueField : 'abbr',
		fieldLabel : 'Select State',
		typeAhead : true,
	    tpl: Ext.create('Ext.XTemplate',
	        '<tpl for=".">',
	            '<div class="x-boundlist-item">{abbr} - {name}</div>',
	        '</tpl>'
	    ),
	    displayTpl: Ext.create('Ext.XTemplate',
	        '<tpl for=".">',
	            '{abbr} - {name}',
	        '</tpl>'
	    ),
	    queryMode : 'local',
		triggerAction : 'all',
		emptyText : 'Select/or type here...',
		selectOnFocus : true,
		listeners : {
			select : function(cb, record, idx) {
                eventStore.getProxy().setUrl(BACKEND_EVENTS_BYUGC);
				ugcStore.load({
					add : false,
					params : {
						state: record.data.abbr
					}
				});
				return false;
			}
		}
	});

	/* Date Selectors */
	sdate = new Ext.form.DateField({
		fieldLabel : 'Start UTC Date',
		id : 'sdate',
		format : 'd M Y',
		minValue : new Date('1/1/1986'),
		maxValue : Ext.Date.add(new Date(), Date.DAY, 1),
		value : new Date('1/1/1986')
	});
	edate = new Ext.form.DateField({
		fieldLabel : 'End UTC Date',
		id : 'edate',
		format : 'd M Y',
		minValue : new Date('1/1/1986'),
		maxValue : Ext.Date.add(new Date(), Date.DAY, 1),
		value : Ext.Date.add(new Date(), Date.DAY, 1)
	});
	
	
	new Ext.form.Panel({
		renderTo : 'myform',
		layout : 'anchor',
		title : 'Select County/Zone to search for...',
		items : [stateCombobox, ugcCombobox, sdate, edate],
		buttons : [{
			id : 'eventbutton',
			text : 'Load Grid with Settings Above',
			handler : function(){

				eventStore.getProxy().setUrl(BACKEND_EVENTS_BYUGC);

				eventStore.load({
					add : false,
					params : {
						ugc : ugcCombobox.getValue(),
						sdate : Ext.Date.format(
								Ext.getCmp('sdate').getValue(),
						'Y/m/d'),
						edate : Ext.Date.format(
								Ext.getCmp('edate').getValue(),
						'Y/m/d')
					}
				});
				alinkUGC();
			}
		}]
	});
	eventTable = Ext.create('Ext.grid.GridPanel', {
			ugc : '',
				height : 500,
				title : 'Events Listing',
				loadMask : {
					msg : 'Loading Data...'
				},
				store : eventStore,
				tbar : [{
					id : 'grid-excel-button',
					icon : '/lsr/icons/excel.png',
					text : 'Export to Excel...',
					handler : function(b, e) {
                        var url = eventStore.getProxy().getUrl();
                        // Send both sets of vals to whatever backend is active
                        url = url + "?fmt=xlsx&ugc=" + ugcCombobox.getValue()
                            + "&lat=" + $("#lat2").val()
                            + "&lon=" + $("#lon2").val()
                            + "&sdate=" + Ext.Date.format(
                                Ext.getCmp('sdate').getValue(), 'Y/m/d')
                            + "&edate=" + Ext.Date.format(
                                Ext.getCmp('edate').getValue(), 'Y/m/d');
                        window.location = url;
					}
				},{
					id : 'grid-csv-button',
					text : 'Export to CSV...',
					handler : function(b, e) {
                        var url = eventStore.getProxy().getUrl();
                        // Send both sets of vals to whatever backend is active
                        url = url + "?fmt=csv&ugc=" + ugcCombobox.getValue()
                            + "&lat=" + $("#lat2").val()
                            + "&lon=" + $("#lon2").val()
                            + "&sdate=" + Ext.Date.format(
                                Ext.getCmp('sdate').getValue(), 'Y/m/d')
                            + "&edate=" + Ext.Date.format(
                                Ext.getCmp('edate').getValue(), 'Y/m/d');
                        window.location = url;
					}
				}],
				columns : [{
							'header' : 'Event ID',
							dataIndex : 'eventid',
							width : 50,
							renderer : function(value, metaData, record){
								var url = Ext.String.format("/vtec/#{0}-O-NEW-K{1}-{2}-{3}-{4}", 
										Ext.Date.format(record.data.issue, 'Y'),
									record.data.wfo, record.data.phenomena, record.data.significance,
									Ext.String.leftPad(record.data.eventid,4,'0'));
								return "<a href='"+url+"' target='_blank'>"+ value +"</a>";
							}
						}, {
							'header' : 'Phenomena',
							sortable : true,
							dataIndex : 'ph_name',
							width : 150
						}, {
							'header' : 'Significance',
							sortable : true,
							dataIndex : 'sig_name'
						}, {
							'header' : 'Issued',
							sortable : true,
							dataIndex : 'issue',
							width : 150,
							renderer : function(value) {
								return Ext.Date.format(value,
										'M d, Y g:i A');
							}
						}, {
							'header' : 'Expired',
							sortable : true,
							dataIndex : 'expire',
							width : 150,
							renderer : function(value) {
								return Ext.Date.format(value,
										'M d, Y g:i A');
							}
						}]
			});
	eventTable.render('mytable');
	eventTable.doLayout();
	
	warnStore = new Ext.data.Store({
		autoLoad : false,
		model : 'SBW',
		proxy : {
			type: 'ajax',
			url : BACKEND_SBW_BYPOINT,
	        reader: {
	            type: 'json',
	            rootProperty: 'sbws'
	        }
		}
	});

	
	warntable = Ext.create('Ext.grid.GridPanel', {
		height : 500,
		title : 'Drag marker on map to load data...',
		loadMask : {
			msg : 'Loading Data...'
		},
		store : warnStore,
		tbar : [{
			id : 'grid-excel-button22',
			icon : '/lsr/icons/excel.png',
			text : 'Export to Excel...',
			handler : function(b, e) {
                var url = warnStore.getProxy().getUrl();
                url = url + "?fmt=xlsx&lon=" + $("#lon").val()
                    + "&lat=" + $("#lat").val()
                    + "&sdate=" + Ext.Date.format(
                        Ext.getCmp('sdate').getValue(), 'Y/m/d')
                    + "&edate=" + Ext.Date.format(
                        Ext.getCmp('edate').getValue(), 'Y/m/d');
                window.location = url;
			}
		},{
			id : 'grid-csv-button22',
			text : 'Export to CSV...',
			handler : function(b, e) {
                var url = warnStore.getProxy().getUrl();
                url = url + "?fmt=csv&lon=" + $("#lon").val()
                    + "&lat=" + $("#lat").val()
                    + "&sdate=" + Ext.Date.format(
                        Ext.getCmp('sdate').getValue(), 'Y/m/d')
                    + "&edate=" + Ext.Date.format(
                        Ext.getCmp('edate').getValue(), 'Y/m/d');
                window.location = url;
			}
		}],
		columns : [{
			'header' : 'Event ID',
			dataIndex : 'eventid',
			width : 50,
			renderer : function(value, metaData, record){
				var url = Ext.String.format("/vtec/#{0}-O-NEW-K{1}-{2}-{3}-{4}", 
						Ext.Date.format(record.data.issue, 'Y'),
						record.data.wfo, record.data.phenomena, record.data.significance,
						Ext.String.leftPad(record.data.eventid,4,'0'));
				return "<a href='"+url+"' target='_blank'>"+ value +"</a>";
			}
		}, {
			'header' : 'Phenomena',
			sortable : true,
			dataIndex : 'ph_name',
			width : 150
		}, {
			'header' : 'Significance',
			sortable : true,
			dataIndex : 'sig_name'
		}, {
			'header' : 'Issued',
			sortable : true,
			dataIndex : 'issue',
			width : 150,
			renderer : function(value) {
				return Ext.Date.format(value,
						'M d, Y g:i A');
			}
		}, {
			'header' : 'Expired',
			sortable : true,
			dataIndex : 'expire',
			width : 150,
			renderer : function(value) {
				return Ext.Date.format(value,
						'M d, Y g:i A');
			}
		}, {
			'header' : 'Issue Hail Tag',
			sortable : true,
			dataIndex : 'issue_hailtag'
		}, {
			'header' : 'Issue Wind Tag',
			sortable : true,
			dataIndex : 'issue_windtag'
		}, {
			'header' : 'Issue Tornadp Tag',
			sortable : true,
			dataIndex : 'issue_tornadotag'
		}, {
			'header' : 'Issue Tornado Damage Tag',
			sortable : true,
			dataIndex : 'issue_tornadodamagetag'
		}]
	});
	warntable.render('warntable');
	warntable.doLayout();

	// Do the anchor tag linking, please
	var tokens = window.location.href.split("#");
	if (tokens.length == 2){
		var tokens2 = tokens[1].split("/");
		if (tokens2.length == 5){
			if (tokens2[0] == 'byugc'){
                // scroll page
                var aTag = $("a[name='byugc']");
                $('html,body').animate({scrollTop: aTag.offset().top},'slow');
				sdate = tokens2[3].substr(0,4) +"/"+
						tokens2[3].substr(4,2) +"/"+
						tokens2[3].substr(6,2) ;
				Ext.getCmp("sdate").setValue(new Date(sdate));
				edate = tokens2[4].substr(0,4) +"/"+
						tokens2[4].substr(4,2) +"/"+
						tokens2[4].substr(6,2) ;
				Ext.getCmp("edate").setValue(new Date(edate));
                var record = stateCombobox.getStore().findRecord(
                    "abbr", tokens2[1]);
                if (record){
                    stateCombobox.select(record);
                    stateCombobox.fireEvent('select', stateCombobox, record);    
                }
				defaultUGC = tokens2[2];
				eventStore.load({
					add : false,
					params : {
						ugc : tokens2[2],
						sdate : Ext.Date.format(
								Ext.getCmp('sdate').getValue(),
						'Y/m/d'),
						edate : Ext.Date.format(
								Ext.getCmp('edate').getValue(),
						'Y/m/d')
					}
				});
				eventTable.setTitle("Event Listing for UGC "+ tokens2[2]);
			}
		}

	}

	$("#manualpt").click(function(){
		var la = $("#lat").val();
		var lo = $("#lon").val();
		var latlng = new google.maps.LatLng(parseFloat(la), parseFloat(lo))
		mapwidget1.marker.setPosition(latlng);
		updateMarkerPosition(lo, la);
	});
	$("#manualpt2").click(function(){
		var la = $("#lat2").val();
		var lo = $("#lon2").val();
		var latlng = new google.maps.LatLng(parseFloat(la), parseFloat(lo))
		mapwidget2.marker.setPosition(latlng);
		updateMarkerPosition2(lo, la);
	});
};


function updateMarkerPosition(lon, lat) {
    var latLng = new google.maps.LatLng(parseFloat(lat), parseFloat(lon))
    // callback on when the map marker is moved
	warnStore.load({add: false, params: {
		lon: latLng.lng(),
		lat: latLng.lat()
	}});
	$("#lat").val(latLng.lat().toFixed(4));
	$("#lon").val(latLng.lng().toFixed(4));
	warntable.setTitle( Ext.String.format("SBW Events for Lat: {0} Lon: {1}", 
		latLng.lat().toFixed(4), latLng.lng().toFixed(4) ));
	window.location.href = Ext.String.format("#bypoint/{0}/{1}", 
			latLng.lng().toFixed(4), latLng.lat().toFixed(4)  );
	if (mapwidget1){
        mapwidget1.map.setCenter(latLng);
    }
}

function updateMarkerPosition2(lon, lat) {
    var latLng = new google.maps.LatLng(parseFloat(lat), parseFloat(lon))
	// callback on when the map marker is moved
	eventStore.getProxy().setUrl(BACKEND_EVENTS_BYPOINT);
	eventStore.load({add: false, params: {
		sdate: Ext.Date.format(Ext.getCmp('sdate').getValue(), 'Y/m/d'),
		edate: Ext.Date.format(Ext.getCmp('edate').getValue(), 'Y/m/d'),
		lon: latLng.lng(),
		lat: latLng.lat()
	}});
	$("#lat2").val(latLng.lat().toFixed(4));
	$("#lon2").val(latLng.lng().toFixed(4));
	eventTable.setTitle( Ext.String.format("Events for Lat: {0} Lon: {1}", 
		latLng.lat().toFixed(4), latLng.lng().toFixed(4) ));
	window.location.href = Ext.String.format("#eventsbypoint/{0}/{1}", 
			latLng.lng().toFixed(4), latLng.lat().toFixed(4)  );
	if (mapwidget2){
        mapwidget2.map.setCenter(latLng);
    }
}

function initialize() {
	// build the EXT components
    setupUI();
    var default_lon = -93.653;
    var default_lat = 41.53;

	// Do the anchor tag linking, please
	var tokens = window.location.href.split("#");
	if (tokens.length == 2){
		var tokens2 = tokens[1].split("/");
		if (tokens2.length == 3){
			if (tokens2[0] == 'bypoint'){
                default_lat = tokens2[2];
                default_lon = tokens2[1];
				updateMarkerPosition(default_lon, default_lat);
			}
			if (tokens2[0] == 'eventsbypoint'){
                default_lat = tokens2[2];
                default_lon = tokens2[1];
				updateMarkerPosition2(default_lon, default_lat);
			}
		}
    }

    mapwidget1 = new MapMarkerWidget("map", default_lon, default_lat);
    mapwidget1.register(updateMarkerPosition);

    mapwidget2 = new MapMarkerWidget("map2", default_lon, default_lat);
    mapwidget2.register(updateMarkerPosition2);

}

// Onload handler to fire off the app.
google.maps.event.addDomListener(window, 'load', initialize);
