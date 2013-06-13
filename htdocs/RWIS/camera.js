var updateTimes = false;

function fetchtimes(findtime){
	cid = $('select[name=cid]').val();
	mydate = $('#realdate').val();
	$.getJSON('/json/webcam.py?cid='+cid+'&date='+mydate, function(data){
	    var html = '';
    	var len = data.images.length;
    	for (var i = 0; i< len; i++) {
    		ts = new Date(data.images[i].valid);
    		
    		var result = new Array();
			result[0] = $.datepicker.formatDate('M dd ', ts);
			if (ts.getHours() > 12) {
    			result[2] = ts.getHours() - 12;
			} else if (ts.getHours() == 0 ) {
    			result[2] = "12";
			} else {
    			result[2] = ts.getHours();
			}
			result[3] = (ts.getMinutes() < 10 ? ":0" : ":") + ts.getMinutes();

			if (ts.getHours() >= 12) {
    			result[4] = " PM";
			} else {
    			result[4] = " AM";
			}

			ts = result.join('');
    		
        	html += '<option ts="'+ data.images[i].valid +'" value="' + data.images[i].href + '">' + ts + '</option>';
    	}
    	if (len == 0){
    		html += "<option value='-1'>No Images Found!</option>";
    	}
    	$('select[name=times]').html(html);
    	if (findtime){
    		$('select[name=times] option[ts="'+findtime+'"]').attr('selected', 'selected');
    		getimage();
    	}
	});
}

function getimage(){
	href = $('select[name=times]').val();
	if (href){
		fn = href.split('/');
		window.location.href = '#'+ fn[ fn.length -1];
		$('#theimage').attr('src', href);
	}
}

$(document).ready(function(){
	$( "#datepicker" ).datepicker({dateFormat:"DD, d MM, yy",
		altFormat:"yymmdd", altField: "#realdate",
		minDate: new Date(2009, 11, 19)});
	$("#datepicker").datepicker('setDate', new Date());
	
	$('select[name=times]').change(function(){
		getimage();
		});
		
	// See if we have a anchor HREF already
	tokens = window.location.href.split("#");
	if (tokens.length == 2){
		fn = tokens[1];
		tokens = fn.split("_");
		if (tokens.length == 2){
			cid = tokens[0];
			tpart = tokens[1];
			/* Set camera ID */
			$('select[name=cid] option[value='+cid+']').attr("selected", "selected");
			dstr = tpart.substr(4,2) +"/"+ tpart.substr(6,2) +"/"+ tpart.substr(0,4);
			$("#datepicker").datepicker("setDate", new Date(dstr)); // mm/dd/yyyy
			isotime = tpart.substr(0,4) +'-'+ tpart.substr(4,2) +"-"+ tpart.substr(6,2) +
			          'T'+ tpart.substr(8,2) +':'+ tpart.substr(10,2) +":00Z";
			fetchtimes(isotime);
		}
	} else {
		fetchtimes(false);
	}

	$('select[name=cid]').change(function(){
		fetchtimes(false);
		});
	$("#datepicker").change(function(){
		fetchtimes(false);
		});


});