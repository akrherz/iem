/*
 * IEM Time Machine
 * 
 *  Basically, a browser of archived products that have RESTish URIs
 *  
 */
var dt = moment(); // Current application time
var irealtime = true; // Is our application in realtime mode or not

function readHashLink(){
	var tokens = window.location.href.split("#");
	if (tokens.length != 2){
		return;
	}
	var tokens2 = tokens[1].split(".");
	if (tokens2.length != 2){
		return;
	}
	var pid = tokens2[0];
	var stamp = tokens2[1];
	// parse the timestamp
	if (stamp != "0"){
		dt = moment.utc(stamp, 'YYYYMMDDHHmm');
		irealtime = false;
	}
	$("#products").val(pid).trigger("change");
}
function addproducts(data){
	// Add entries into the products dropdown
	var p = $('select[name=products]');
	var groupname = '';
	var optgroup;
	$.each(data.products, function (i, item) {
		if (groupname != item.groupname){
			optgroup = $('<optgroup>');
	        optgroup.attr('label', item.groupname);
	        p.append(optgroup);
	        groupname = item.groupname;
		}
	    optgroup.append($('<option>', { 
	        value: item.id,
	        'data-avail_lag': item.avail_lag,
	        'data-interval': item.interval,
	        'data-sts': item.sts,
	        'data-template': item.template,
	        'data-time_offset': item.time_offset,
	        text : item.name 
	    }));
	});
	// now turn it into a select2 widget
	p.select2();
	p.on('change', function(e){
		update();
	});
	// read the anchor URI
	readHashLink();
}
function rectifyTime(){
	// Make sure that our current dt matches what can be provided by the
	// currently selected option.
	var opt = getSelectedOption();
	var ets = moment();
	var sts = moment(opt.attr('data-sts'));
	var interval = parseInt(opt.attr('data-interval'));
	var avail_lag = parseInt(opt.attr('data-avail_lag'));
	var time_offset = parseInt(opt.attr('data-time_offset'));
	ets.subtract(time_offset, 'minutes');
	// Check 1: Bounds check
	if (dt < sts){
		dt = sts;
	}
	if (dt > ets){
		dt = ets;
	}
	// Check 2: If our modulus is OK, we can quit early
	if ((dt.hours() * 60 + dt.minutes()) % interval == 0){
		return;
	}
	
	// Check 3: Place dt on a time that works for the given interval
	if (interval > 1440){
		dt.startOf('month');
	} else if (interval >= 60){
		// minute has to be zero
		dt.startOf('hour');
		if (interval != 60){
			dt.startOf('day');
		}
	} else {
		dt.startOf('hour');
	}
}
function update(){
	// called after a slider event, button clicked, realtime refresh
	// or new product selected
	var opt = getSelectedOption();
	rectifyTime();
	// adjust the sliders
	var sts = moment(opt.attr('data-sts'));
	var now = moment();
	$('#year_slider').slider({
		min: sts.year(),
		max: now.year(),
		value: dt.year()
	});
	$('#day_slider').slider({
		value: dt.dayOfYear()
	});
	$('#hour_slider').slider({
		value: dt.hour()
	});
	$('#minute_slider').slider({
		value: dt.minute()
	});
	if (opt.attr('data-interval') > 60){
		$('#minute_slider').css('display', 'none');
	} else {
		$('#minute_slider').css('display', 'block');		
	}
	if (opt.attr('data-interval') > 1440){
		$('#hour_slider').css('display', 'none');
	} else {
		$('#hour_slider').css('display', 'block');		
	}
	var tpl = opt.attr('data-template');
	// We support %Y %m %d %H %i %y
	var url = tpl.replace(/%Y/g, dt.utc().format('YYYY'))
		.replace(/%y/g, dt.utc().format('YY'))
		.replace(/%m/g, dt.utc().format('MM'))
		.replace(/%d/g, dt.utc().format('DD'))
		.replace(/%H/g, dt.utc().format('HH'))
		.replace(/%i/g, dt.utc().format('mm'));

	$('#imagedisplay').attr('src', url);
	window.location.href = '#' + opt.val() + '.' + dt.utc().format('YYYYMMDDHHmm');
	updateUITimestamp();
}
function updateUITimestamp(){
	$('#utctime').html(dt.utc().format('MMM Do YYYY, HH:mm'));
	$('#localtime').html(dt.local().format('MMM Do YYYY, h:mm a'));
}
function getSelectedOption(){
	return $('#products :selected');
}
function buildUI(){
	//year
	$("#year_slider").slider({
		change: function() {
			$("#year_handle").text( $( this ).slider( "value" ) );
		},
		slide: function( event, ui ) {
			$("#year_handle").text( $( this ).slider( "value" ) );
			dt.year(ui.value);
		    update();
		    irealtime = false;
		}
	});
	//hour
	$("#hour_slider").slider({
		min: 0,
		max: 23,
		change: function() {
			$("#hour_handle").text(dt.local().format('h A'));
		},
		slide: function( event, ui ) {
			$("#hour_handle").text(dt.local().format('h A'));
			dt.hour(ui.value);
		    update();
		    irealtime = false;
		}
	});
	//hour
	$("#minute_slider").slider({
		min: 0,
		max: 59,
		change: function() {
			$("#minute_handle").text( $( this ).slider( "value" ) );
		},
		slide: function( event, ui ) {
			$("#minute_handle").text( $( this ).slider( "value" ) );
			dt.minute(ui.value);
		    update();
		    irealtime = false;
		}
	});
	//day
	$("#day_slider").slider({
		min: 1,
		max: 367,
		change: function() {
			$("#day_handle").text(dt.local().format('MMM D'));
		},
		slide: function( event, ui ) {
			$("#day_handle").text(dt.local().format('MMM D'));
			dt.dayOfYear(ui.value);
		    update();
		    irealtime = false;
		}
	});

	
	// Listen for click
	$('.btn').on('click', function(){
		if (this.id == 'next'){
			var opt = getSelectedOption();
			dt.add(parseInt(opt.attr('data-interval')), 'minutes');
		} else if (this.id == 'prev'){
			var opt = getSelectedOption();
			dt.add(0 - parseInt(opt.attr('data-interval')), 'minutes');			
		} else if (this.id == 'realtime'){
			irealtime = true;
			dt = moment();
		} else {
			dt.add(parseInt($(this).attr('data-offset')), $(this).attr('data-unit'));
		}
		update();
	    irealtime = false;
		return false;
	});

	// stop depressed buttons
	$(".btn").mouseup(function(){
	    $(this).blur();
	});
}
function refresh(){
	if (irealtime){
		dt = moment();
		rectifyTime();
		update();
	}
}
function onReady(){
	buildUI();
	$.ajax("/json/products.php", {
		success: function(data){
			addproducts(data);
		}
	});
	//Start the timer
	window.setTimeout(refresh, 300000);
}

// When ready
$(onReady);
