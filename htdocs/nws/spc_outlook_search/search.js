Ext.BLANK_IMAGE_URL = '/ext/resources/images/default/s.gif';

function utcdate(v, record){
	return (Ext.Date.parseDate(v, 'c')).toUTC();
}

var marker;
var outlookStore;
var outlookTable;
var map;

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


Ext.define('Outlook', {
    extend: 'Ext.data.Model',
    fields: [
        {name: 'threshold',  type: 'string'},
        {name: 'day', type: 'int', mapping: 'day'},
        {name: 'utc_issue', type: 'date', mapping: 'issue', convert: utcdate},
        {name: 'utc_valid', type: 'date', mapping: 'valid', convert: utcdate},
        {name: 'utc_expire', type: 'date', mapping: 'expire', convert: utcdate},
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

Ext.onReady(function() {

	outlookStore = new Ext.data.Store({
		autoLoad : false,
		model : 'Outlook',
		proxy : {
			type : 'ajax',
			url : '/json/spcoutlook.py',
	        reader: {
	            type: 'json',
	            rootProperty: 'outlooks'
	        }
		}
	});
		
	outlookTable = Ext.create('My.grid.ExcelGridPanel', {
		height : 500,
		title : 'Drag marker on map to load data...',
		loadMask : {
			msg : 'Loading Data...'
		},
		store : outlookStore,
		tbar : [{
			id : 'grid-excel-button22',
			icon : '/lsr/icons/excel.png',
			text : 'Export to Excel...',
			handler : function(b, e) {
				b.up('grid').downloadExcelXml();
			}
		}],
		columns : [{
			'header' : 'Day',
			sortable : true,
			dataIndex : 'day',
			width : 50
		},{
			'header' : 'Threshold',
			sortable : true,
			dataIndex : 'threshold',
			width : 100
		},{
			'header' : 'Outlook Issued At (UTC)',
			sortable : true,
			dataIndex : 'utc_valid',
			width : 200,
			renderer : function(value) {
				return Ext.Date.format(value,
						'M d, Y H:i');
			}
		},{
			'header' : 'Outlook Begins (UTC)',
			sortable : true,
			dataIndex : 'utc_issue',
			width : 200,
			renderer : function(value) {
				return Ext.Date.format(value,
						'M d, Y H:i');
			}
		}, {
			'header' : 'Outlook Ends (UTC)',
			sortable : true,
			dataIndex : 'utc_expire',
			width : 200,
			renderer : function(value) {
				return Ext.Date.format(value,
						'M d, Y H:i');
			}
		}]
	});
	outlookTable.render('warntable');
	outlookTable.doLayout();

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
	$('#last').change(function() {
		outlookStore.load({add: false, params: {
			lon: $("#lon").val(),
			lat: $("#lat").val(),
			last: $('#last').is(":checked") ? '1': '0',
			day: $("input[name='day']:checked").val(),
			cat: $("input[name='cat']:checked").val()
		}});      
		updateTableTitle();
    });
	$('input[type=radio][name=day]').change(function() {
		outlookStore.load({add: false, params: {
			lon: $("#lon").val(),
			lat: $("#lat").val(),
			last: $('#last').is(":checked") ? '1': '0',
			day: this.value,
			cat: $("input[name='cat']:checked").val()
		}});		
		updateTableTitle();
	});
	$('input[type=radio][name=cat]').change(function() {
		outlookStore.load({add: false, params: {
			lon: $("#lon").val(),
			lat: $("#lat").val(),
			last: $('#last').is(":checked") ? '1': '0',
			day: $("input[name='day']:checked").val(),
			cat: this.value
		}});
		updateTableTitle();
	});
});

function updateTableTitle(){
	latLng = marker.getPosition();
	outlookTable.setTitle( Ext.String.format("SPC Day {2} {3} Outlook Events for Lat: {0} Lon: {1}", 
			latLng.lat().toFixed(4), latLng.lng().toFixed(4),
			$("input[name='day']:checked").val(),
			$("input[name='cat']:checked").val()));
}

function updateMarkerPosition(latLng) {
	// callback on when the map marker is moved
	outlookStore.load({add: false, params: {
		lon: latLng.lng(),
		lat: latLng.lat(),
		last: $('#last').is(":checked") ? '1': '0',
		day: $("input[name='day']:checked").val(),
		cat: $("input[name='cat']:checked").val()
	}});
	$("#lat").val(latLng.lat().toFixed(4));
	$("#lon").val(latLng.lng().toFixed(4));
	updateTableTitle();
	window.location.href = Ext.String.format("#bypoint/{0}/{1}", 
			latLng.lng().toFixed(4), latLng.lat().toFixed(4)  );
	map.setCenter(latLng);
}


function initialize() {
	var latLng = new google.maps.LatLng(41.53, -93.653);
	map = new google.maps.Map(document.getElementById('map'), {
		zoom: 5,
		center: latLng,
		mapTypeId: google.maps.MapTypeId.ROADMAP
	});
	marker = new google.maps.Marker({
		position: latLng,
		title: 'Point A',
		map: map,
		draggable: true
	});

	google.maps.event.addListener(marker, 'dragend', function() {
		updateMarkerPosition(marker.getPosition());
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