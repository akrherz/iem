Ext.BLANK_IMAGE_URL = '/vendor/ext/resources/images/default/s.gif';

function utcdate(v, record){
	return (Ext.Date.parseDate(v, 'c')).toUTC();
}

var marker;
var marker2;
var warnStore;
var eventStore;
var warntable;
var eventTable;
var pDict;
var map;
var map2;
var sDict;
var sdate;
var edate;
var vtec_sig_dict = [
['W','Warning'],
['Y','Advisory'],
['A','Watch'],
['S','Statement'],
['F','Forecast'],
['O','Outlook'],
['N','Synopsis']
];

var vtec_phenomena_dict = [
['SV','Severe Thunderstorm'],
['TO','Tornado'],
['MA','Marine'],
['AF','Ashfall'],
['AS','Air Stagnation'],
['AV','Avalanche'],
['BS','Blowing Snow'],
['BW', 'Brisk Wind'],
['BZ','Blizzard'],
['CF','Coastal Flood'],
['DU','Blowing Dust'],
['DS','Dust Storm'],
['EC','Extreme Cold'],
['EH','Excessive Heat'],
['EW','Extreme Wind'],
['FA','Areal Flood'],
['FF','Flash Flood'],
['FL','Flood'],
['FR','Frost'],
['FZ','Freeze'],
['FG','Dense Fog'],
['FW','Red Flag'],
['GL','Gale'],
['HF','Hurricane Force Wind'],
['HI','Inland Hurricane Wind'],
['HS','Heavy Snow'],
['HP','Heavy Sleet'],
['HT','Heat'],
['HU','Hurricane'],
['HW','High Wind'],
['HY','Hydrologic'],
['HZ','Hard Freeze'],
['IS','Ice Storm'],
['IP','Sleet'],
['LB','Lake Effect Snow and Blowing Snow'],
['LE','Lake Effect Snow'],
['LO','Low Water'],
['LS','Lakeshore Flood'],
['LW','Lake Wind'],
['RB','Small Craft for Rough Bar'],
['RH','Radiological Hazard'],
['SB','Snow and Blowing Snow'],
['SC','Small Craft'],
['SE','Hazardous Seas'],
['SI','Small Craft for Winds'],
['SM','Dense Smoke'],
['SN','Snow'],
['SR','Storm'],
['SU','High Surf'],
['TI','Inland Tropical Storm Wind'],
['TR','Tropical Storm'],
['TS','Tsunami'],
['TY','Typhoon'],
['UP','Ice Accretion'],
['VO','Volcano'],
['WC','Wind Chill'],
['WI','Wind'],
['WS','Winter Storm'],
['WW','Winter Weather'],
['ZF','Freezing Fog'],
['ZR','Freezing Rain'],
['ZY', 'Freezing Spray']
];

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
        {name: 'pstring', type: 'string', 
        	convert: function(val, record){
                var idx = pDict.find('abbr', record.data.phenomena);
                if (idx > -1) {
                    return pDict.getAt(idx).data.name;
                } else {
                        return record.data.phenomena;
                }
        	}},
        {name: 'sig_string', type: 'string',
        	convert: function(val, record){
                var idx = sDict.find('abbr', record.data.significance);
                if (idx > -1) {
                	return sDict.getAt(idx).data.name;
                } else {
                        return record.data.significance;
                }
        	}},
        {name: 'significance', type: 'string'},
        {name: 'issue', type: 'date', dateFormat: 'c'},
        {name: 'utc_issue', type: 'date', mapping: 'issue', convert: utcdate},
        {name: 'expire', type: 'date', dateFormat: 'c'},
        {name: 'utc_expire', type: 'date', mapping: 'expire', convert: utcdate}
    ]
});

function alinkUGC(){
	window.location.href = Ext.String.format("#byugc/{0}/{1}/{2}/{3}", 
			Ext.getCmp('stateselector').getValue(), 
			Ext.getCmp('ugcselector').getValue(),
			Ext.Date.format(Ext.getCmp('sdate').getValue(),'Ymd'),
			Ext.Date.format(Ext.getCmp('edate').getValue(),'Ymd')
			);
}

function setupUI() {

	pDict = new Ext.data.SimpleStore({
				idIndex : 0,
				fields : ['abbr', 'name'],
				data : vtec_phenomena_dict
			});
	sDict = new Ext.data.SimpleStore({
				idIndex : 0,
				fields : ['abbr', 'name'],
				data : vtec_sig_dict
			});

	eventStore = new Ext.data.Store({
		autoLoad : false,
		model : 'SBW',
		proxy : {
			type : 'ajax',
			url : '/json/vtec_events_byugc.py',
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

	
	var ugcStore = new Ext.data.Store({
		autoLoad : false,
		model : 'UGC',
		proxy : {
			type: 'ajax',
			url : '/json/state_ugc.php',
	        reader: {
	            type: 'json',
	            rootProperty: 'ugcs'
	        }
		}
	});

	var ugcCB = new Ext.form.ComboBox({
		id : 'ugcselector',
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
	
	var stateCB = new Ext.form.ComboBox({
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
		id : 'stateselector',
		listeners : {
			select : function(cb, record, idx) {
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
		items : [stateCB, ugcCB, sdate, edate],
		buttons : [{
			id : 'eventbutton',
			text : 'Load Grid with Settings Above',
			handler : function(){

				eventStore.getProxy().setUrl('/json/vtec_events_byugc.py');

				eventStore.load({
					add : false,
					params : {
						ugc : ugcCB.getValue(),
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
	eventTable = Ext.create('My.grid.ExcelGridPanel', {
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
						b.up('grid').downloadExcelXml();
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
						}, {
							header : 'VTEC Significance',
							hidden : true,
							dataIndex : 'significance'
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
			url : '/json/sbw_by_point.py',
	        reader: {
	            type: 'json',
	            rootProperty: 'sbws'
	        }
		}
	});

	
	warntable = Ext.create('My.grid.ExcelGridPanel', {
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
				b.up('grid').downloadExcelXml();
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
	warntable.render('warntable');
	warntable.doLayout();

	// Do the anchor tag linking, please
	var tokens = window.location.href.split("#");
	if (tokens.length == 2){
		var tokens2 = tokens[1].split("/");
		if (tokens2.length == 5){
			if (tokens2[0] == 'byugc'){
				sdate = tokens2[3].substr(0,4) +"/"+
						tokens2[3].substr(4,2) +"/"+
						tokens2[3].substr(6,2) ;
				Ext.getCmp("sdate").setValue(new Date(sdate));
				edate = tokens2[4].substr(0,4) +"/"+
						tokens2[4].substr(4,2) +"/"+
						tokens2[4].substr(6,2) ;
				Ext.getCmp("edate").setValue(new Date(edate));
				Ext.getCmp("stateselector").setValue(tokens2[1]);
				Ext.getCmp("ugcselector").setValue(tokens2[2]);
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
		marker.setPosition(latlng);
		updateMarkerPosition(latlng);
	});
	$("#manualpt2").click(function(){
		var la = $("#lat2").val();
		var lo = $("#lon2").val();
		var latlng = new google.maps.LatLng(parseFloat(la), parseFloat(lo))
		marker2.setPosition(latlng);
		updateMarkerPosition2(latlng);
	});
};


function updateMarkerPosition(latLng) {
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
	map.setCenter(latLng);
}

function updateMarkerPosition2(latLng) {
	// callback on when the map marker is moved
	eventStore.getProxy().setUrl('/json/vtec_events_bypoint.py');
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
	map2.setCenter(latLng);
}

function initialize() {
	// build the EXT components
	setupUI();
	var latLng = new google.maps.LatLng(41.53, -93.653);
	map = new google.maps.Map(document.getElementById('map'), {
		zoom: 3,
		center: latLng,
		mapTypeId: google.maps.MapTypeId.ROADMAP
	});
	map2 = new google.maps.Map(document.getElementById('map2'), {
		zoom: 3,
		center: latLng,
		mapTypeId: google.maps.MapTypeId.ROADMAP
	});
	marker = new google.maps.Marker({
		position: latLng,
		title: 'Point A',
		map: map,
		draggable: true
	});
	marker2 = new google.maps.Marker({
		position: latLng,
		title: 'Point A',
		map: map2,
		draggable: true
	});

	google.maps.event.addListener(marker, 'dragend', function() {
		updateMarkerPosition(marker.getPosition());
	});
	google.maps.event.addListener(marker2, 'dragend', function() {
		updateMarkerPosition2(marker2.getPosition());
	});

	// Do the anchor tag linking, please
	var tokens = window.location.href.split("#");
	if (tokens.length == 2){
		var tokens2 = tokens[1].split("/");
		if (tokens2.length == 3){
			if (tokens2[0] == 'bypoint'){
				var latlng = new google.maps.LatLng(tokens2[2], tokens2[1]);
				marker.setPosition(latlng);
				updateMarkerPosition(latlng);
			}
			if (tokens2[0] == 'eventsbypoint'){
				var latlng = new google.maps.LatLng(tokens2[2], tokens2[1]);
				marker2.setPosition(latlng);
				updateMarkerPosition2(latlng);
			}
		}
	}

}

// Onload handler to fire off the app.
google.maps.event.addDomListener(window, 'load', initialize);
