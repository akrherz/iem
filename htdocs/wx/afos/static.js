/*
 * NWS Text Product Finder
 *  - uses cookies and hashlinks to save info
 */
var tabs;
var NO_DATE_SET = 'No Limit';

function readAnchorTags(){
	var tokens = window.location.href.split("#");
	if (tokens.length != 2){
		return;
	}
	$(tokens[1].split(",")).each(function(idx, pil_limit){
		var tokens = pil_limit.split("-");
		if (tokens.length == 1){
			tokens.push(1);
		}
		addTab(tokens[0], "", "", tokens[1], NO_DATE_SET, NO_DATE_SET, false);
	});
}
function readCookies(){
	var afospils = Cookies.get('afospils');
	if (afospils === undefined || afospils == ''){
		return;
	}
	$(afospils.split(",")).each(function(idx, pil_limit){
		var tokens = pil_limit.split("-");
		if (tokens.length == 1){
			tokens.push(1);
		}
		addTab(tokens[0], "", "", tokens[1], NO_DATE_SET, NO_DATE_SET, false);
	});
}
function saveCookies(){
	var afospils = [];
	$(".nav-tabs li[data-pil]").each(function(idx, li){
		// these are currently temporary
		if ($(li).data('sdate') != NO_DATE_SET){
			return;
		}
		afospils.push($(li).data('pil')+"-"+$(li).data('limit'));
	});
	
	Cookies.set('afospils', afospils.join(","), {'path': '/wx/afos/',
		'expires': 3650});
	window.location.href = "#"+ afospils.join(",");
};

function loadTabContent(div, pil, center, ttaaii, limit, sdate, edate){
	div.html('<img src="/images/wait24trans.gif"> Searching the database ...');
	sdate = (sdate == NO_DATE_SET) ? "": sdate;
	edate = (edate == NO_DATE_SET) ? "": edate;
	$.ajax({
		method: 'GET',
		url: "/cgi-bin/afos/retrieve.py?fmt=html&pil="+pil+"&center="+
			center +"&limit="+ limit +"&sdate="+ sdate +"&edate="+
			edate +"&ttaaii="+ ttaaii,
		success: function(text){
			div.html(text);
		},
		failure: function(text){
			div.html(text);
		}
	});
}

function refreshActiveTab(){
	//refresh the content found in the active tab
	var pil = $(".nav-tabs li.active").data('pil');
	var limit = $(".nav-tabs li.active").data('limit');
	var center = $(".nav-tabs li.active").data('center');
	var ttaaii = $(".nav-tabs li.active").data('ttaaii');
	var sdate = $(".nav-tabs li.active").data('sdate');
	var edate = $(".nav-tabs li.active").data('edate');
	if (pil === undefined){
		return;
	}
	var tabid = $(".nav-tabs li.active a").attr('href');
	var tabdiv = $(tabid);
	loadTabContent(tabdiv, pil, center, ttaaii, limit, sdate, edate);	
}

function addTab(pil, center, ttaaii, limit, sdate, edate, doCookieSave){
	// Make sure the pil is something
	if (pil == null || pil == "") {
		return;
	}
	// Make sure this isn't a dup
	if ($("#thetabs .nav-tabs li[data-pil='" + pil +"']").length > 0){
		return;
	}
	var pos = $(".nav-tabs").children().length;
	$("#thetabs .nav-tabs").append('<li data-center="'+center+'" '+
			'data-sdate="'+sdate+'" data-edate="'+edate+'" '+
			'data-ttaaii="' + ttaaii + '" ' +
			'data-limit="'+limit+'" data-pil="'+pil+'">'+
			'<a href="#tab'+pos+'" data-toggle="tab">'+pil+'</a></li>');
	$('.tab-content').append('<div class="tab-pane" id="tab'+pos+'"></div>');
	var newdiv = $("#tab"+pos);
	$('.nav-tabs li:nth-child(' + (pos + 1) + ') a').click();
	loadTabContent(newdiv, pil, center, ttaaii, limit, sdate, edate);
	if (doCookieSave){
		saveCookies();		
	}
}
function dlbtn(btn, fmt){
    var pil = $(".nav-tabs li.active").data('pil');
    if (pil === undefined){
        return;
    }
    var limit = $(".nav-tabs li.active").data('limit');
    var center = $(".nav-tabs li.active").data('center');
    var ttaaii = $(".nav-tabs li.active").data('ttaaii');
    var sdate = $(".nav-tabs li.active").data('sdate');
    var edate = $(".nav-tabs li.active").data('edate');
    sdate = (sdate == NO_DATE_SET) ? "": sdate;
    edate = (edate == NO_DATE_SET) ? "": edate;
    window.location = "/cgi-bin/afos/retrieve.py?dl=1&fmt="+ fmt +"&pil="+pil+"&center="+
            center +"&limit="+ limit +"&sdate="+ sdate +"&edate="+ edate +
            "&ttaaii=" + ttaaii;
    $(btn).blur();
}
function buildUI(){
	// listen for refresh clicks
	$("#toolbar-refresh").click(function(){
		refreshActiveTab();
		$(this).blur();
	});
	// Print!
	$("#toolbar-print").click(function(){
		$(this).blur();
		var pil = $(".nav-tabs li.active").data('pil');
		if (pil === undefined){
			return;
		}
		var tabid = $(".nav-tabs li.active a").attr('href');
		// https://stackoverflow.com/questions/33732739
		var divToPrint=$(tabid)[0];
		var newWin=window.open('','Print-Window');
		newWin.document.open();
		newWin.document.write('<html><body onload="window.print()">'+divToPrint.innerHTML+'</body></html>');
		newWin.document.close();
		setTimeout(function(){newWin.close();},10);
	});
	// Close
	$("#toolbar-close").click(function(){
		$(this).blur();
		var pil = $(".nav-tabs li.active").data('pil');
		if (pil === undefined){
			return;
		}
		var tabid = $(".nav-tabs li.active a").attr('href');
		$(".nav-tabs li.active").remove();
		$(tabid).remove();
		$(".nav-tabs li a").last().click();
		saveCookies();
	});
	$("#myform-submit").click(function(){
		var pil = $("#myform input[name='pil']").val().toUpperCase();
		var center = $("#myform input[name='center']").val().toUpperCase();
		var ttaaii = $("#myform input[name='ttaaii']").val().toUpperCase();
		var limit = parseInt($("#myform input[name='limit']").val());
		var sdate = $("#sdate").val();
		var edate = $("#edate").val();
		addTab(pil, center, ttaaii, limit, sdate, edate, true);
		$(this).blur();
	});
	$("#sdate").datepicker({
		dateFormat:"yy-m-d",
		minDate: new Date(1983, 0, 1),
		maxDate: new Date(),
		defaultDate: new Date(1983, 0, 1)
	});
	$("#edate").datepicker({
		dateFormat:"yy-m-d",
		minDate: new Date(1983, 0, 2),
		maxDate: new Date(new Date().getTime() + 24 * 60 * 60 * 1000),
		defaultDate: new Date(new Date().getTime() + 24 * 60 * 60 * 1000)		
	});
}

$(function(){
    // jquery on-ready
    buildUI();
    readAnchorTags();
    readCookies();
    saveCookies();
});
