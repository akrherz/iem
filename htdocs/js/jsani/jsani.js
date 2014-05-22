/************************************
* JSani - JavaScript Animator
* http://www.ssec.wisc.edu/~billb/jsani/
*
* Copyright 2010, Bill Bellon
* Licensed under the GPL Version 3 licenses.
* http://www.ssec.wisc.edu/~billb/jsani/license
*
* Includes jQuery.js 
* http://jquery.com/
* Copyright 2010, John Resig
* Dual licensed under the MIT or GPL Version 2 licenses.
* http://jquery.org/license
*
* Includes Sizzle.js
* http://sizzlejs.com/
* Copyright 2010, The Dojo Foundation
* Released under the MIT, BSD, and GPL Licenses. 
************************************/

$(document).ready( function(){ // IMPROVE - consider using onpageshow
	if ( !utils.optionExists('disable_auto_start') ) {	
		jsani.init( 'start' );
	}
});



//==============================================================
var dragImg = {
	// based on http://elouai.com/javascript-drag-and-drop.php
	ie:             document.all,
	nn6:            document.getElementById&&!document.all,
	isdrag:         false,
	x:              false,
	y:              false,
	tx:             false, 
	ty:             false,
	dobj:           false,
	dragID:         false,
	imageWasDragged:  false,
	
	// method-------------------------------------------
	init: function(id) {
		dragImg.dragID = id;
		document.onmousedown = dragImg.selectmouse;
		document.onmouseup = new Function("speedSlider.isdrag=false; dragImg.isdrag=false;");
	},
	
	// method-------------------------------------------
	movemouse: function(e) {
		if (dragImg.isdrag && jsani.zoomEnabled)  {     
			dragImg.imageWasMoved = true;
			dragImg.dobj.style.left = dragImg.nn6 ? dragImg.tx + e.clientX - dragImg.x + "px": dragImg.tx + event.clientX - dragImg.x + "px";
			dragImg.dobj.style.top  = dragImg.nn6 ? dragImg.ty + e.clientY - dragImg.y + "px": dragImg.ty + event.clientY - dragImg.y + "px";
			return false;
		}
	},
	
	// method-------------------------------------------
	selectmouse: function(e) {
		var fobj       = dragImg.nn6 ? e.target : event.srcElement;
		var topelement = dragImg.nn6 ? "HTML" : "BODY";
		
		while (fobj.tagName != topelement && fobj.getAttribute("id") != dragImg.dragID)  {
			fobj = dragImg.nn6 ? fobj.parentNode : fobj.parentElement;
		}
		
		if (fobj.getAttribute("id") == dragImg.dragID)  {
			dragImg.isdrag = true;
			dragImg.dobj = fobj;
			dragImg.tx = parseInt(dragImg.dobj.style.left+0);
			dragImg.ty = parseInt(dragImg.dobj.style.top+0);
			dragImg.x = dragImg.nn6 ? e.clientX : event.clientX;
			dragImg.y = dragImg.nn6 ? e.clientY : event.clientY;
			dragImg.imageWasMoved = false;
			document.onmousemove = dragImg.movemouse;
			return false;
		}
	}
}
//==============================================================

//==============================================================
var speedSlider = {
	// based on http://elouai.com/javascript-drag-and-drop.php
	ie:             document.all,
	nn6:            document.getElementById&&!document.all,
	isdrag:         false,
	x:              false,
	y:              false,
	tx:             false, 
	ty:             false,
	dobj:           false,
	dragID:         false,
	minX:           false,
	maxX:           false,
	sliderStepRate: false,
	direction: false,
	
	// method-------------------------------------------
	init: function(id) {
		this.dragID = id;
		
		var speedContainer_newWidth = parseInt($("#speedBar").width(),10) + 30;
		$("#speedContainer").css('width', speedContainer_newWidth + 'px');    
		
		// the area that the parent of the speedButton covers is too small and produces a weird
		// bug where you have to do the mouseup inside the element tied to the event handler 
		document.getElementById(id).parentNode.onmousedown = speedSlider.selectmouse;
		document.onmouseup = new Function("speedSlider.isdrag=false; dragImg.isdrag=false;");  
		
		// if you don't account for the border width of the speed slider then you can
		// end up with situations where the minDwell is reached but the sliderButton
		// isn't quite at the end of the speed slider
		var borderWidth = $("#speedBar").css('borderRightWidth');
		borderWidth = parseInt(borderWidth.replace('px', ''), 10);
		
		this.minX = utils.findPosX("speedBar");
		this.maxX = parseInt(this.minX, 10) + parseInt( $("#speedBar").width(), 10 ) + borderWidth - parseInt( $("#speedButton").width(), 10 );
		
		// set initial position of slider button so that it's position corresponds to the initial imgDwell
		var initial_x = parseInt( (jsani.minDwell - jsani.imgDwell) * 
		(speedSlider.maxX - speedSlider.minX) / (jsani.maxDwell - jsani.minDwell) + 
		speedSlider.maxX, 10 );
		$("#speedButton").css('left', initial_x - this.minX + "px");    
		this.sliderStepRate = parseInt( ( (this.maxX - this.minX) / jsani.nSteps ) + 0.9, 10);    
	
	},
	
	// method-------------------------------------------
	movemouse: function(e) {
		if (speedSlider.isdrag)  {
		
			posx = utils.findPosX("speedButton");
		
			speedSlider.imageWasMoved = true;
			if (e.clientX < speedSlider.minX) {
				speedSlider.dobj.style.left = "0px";
			} else if (e.clientX > speedSlider.maxX) {
				speedSlider.dobj.style.left = parseInt(speedSlider.maxX - speedSlider.minX, 10) + "px";
			} else {
				speedSlider.dobj.style.left = speedSlider.nn6 ? speedSlider.tx + e.clientX - speedSlider.x + "px": 
				speedSlider.tx + event.clientX - speedSlider.x + "px";
			}
		
			if (utils.findPosX("speedButton") - posx >=0) {
				speedSlider.direction = 'right';
			} else {
				speedSlider.direction = 'left';
			}
		
			return false;
		}
	},
	
	// method-------------------------------------------
	moveSpeedButtonToRight: function() {
	
		posx = utils.findPosX("speedButton");
		
		var curLeft = utils.findPosX("speedButton");
		var newLeft = parseInt(curLeft + speedSlider.sliderStepRate, 10);
		newLeft = newLeft - utils.findPosX("speedBar");
		if (newLeft > parseInt(speedSlider.maxX - speedSlider.minX, 10)) {
			newLeft = parseInt(speedSlider.maxX - speedSlider.minX, 10);
		}
		
		document.getElementById("speedButton").style.left = newLeft + "px";
		
		if (utils.findPosX("speedButton") - posx >=0) {
			speedSlider.direction = 'right';
		} else {
			speedSlider.direction = 'left';
		}
	},
	
	// method-------------------------------------------
	moveSpeedButtonToLeft: function() {
	
		posx = utils.findPosX("speedButton");
		
		var curLeft = utils.findPosX("speedButton");
		var newLeft = parseInt(curLeft - speedSlider.sliderStepRate, 10);
		newLeft = newLeft - utils.findPosX("speedBar");
		if (newLeft < 0) {
			newLeft = 0;
		}
		
		document.getElementById("speedButton").style.left = newLeft + "px";
		
		if (utils.findPosX("speedButton") - posx >=0) {
			speedSlider.direction = 'right';
		} else {
			speedSlider.direction = 'left';
		}
	},
	
	// method-------------------------------------------
	selectmouse: function(e) {
	
		posx = utils.findPosX("speedButton");
		
		var fobj       = speedSlider.nn6 ? e.target : event.srcElement;
		var topelement = speedSlider.nn6 ? "HTML" : "BODY";
		
		while (fobj.tagName != topelement && fobj.getAttribute("id") != speedSlider.dragID)  {
			fobj = speedSlider.nn6 ? fobj.parentNode : fobj.parentElement;
		}
		
		if (fobj.getAttribute("id") == speedSlider.dragID)  {
			speedSlider.isdrag = true;
			speedSlider.dobj = fobj;
			speedSlider.tx = parseInt(speedSlider.dobj.style.left+0, 10);
			speedSlider.x = speedSlider.nn6 ? e.clientX : event.clientX;
			speedSlider.imageWasMoved = false;
			document.onmousemove = speedSlider.movemouse;
		
			if (utils.findPosX("speedButton") - posx >=0) {
				speedSlider.direction = 'right';
			} else {
				speedSlider.direction = 'left';
			}
			
			return false;
		}
	}
}
//==============================================================

//==============================================================
var utils = {

	//-------------------------------------------
	optionExists: function(optName) {
		if ( $("#jsani input[name='" + optName + "']").length != 0 ) {
			return true;
		} else {
			return false;
		}
	},

	//-------------------------------------------
	findPosX:  function(id) {
		var position = $("#"+id).offset(); 
		return parseInt(position.left, 10);
	},
	
	//-------------------------------------------
	findPosY:  function(id) {
		var position = $("#"+id).offset(); 
		return parseInt(position.top, 10);  
	},
	
	//-------------------------------------------
	clickPosX:  function(e) {    
		var x = parseInt(e.pageX,10) - utils.findPosX("jsaniContainer");
		return x;
	},
	
	//-------------------------------------------
	clickPosY:  function(e) {    
		var y = parseInt(e.pageY,10) - utils.findPosY("jsaniContainer");   
		return y;
	},  

	//-------------------------------------------		
	show_: function(elem) {
		$(elem).show();
	},

	//-------------------------------------------
	hide_: function(elem) {
		$(elem).hide();
	},
	
	//-------------------------------------------
	getQueryStringArray: function() {
		/*
		get the query string and then return as an array of
		[param] = value
		pairs
		*/
		
		// get query string
		var rExp = /\?.*$/;
		var queryString = window.top.location.href.substr(window.top.location.href.search(rExp) + 1);
		rExp = /#/;
		var ind = queryString.search(rExp);
		if (ind != -1) {
			queryString = queryString.substr(0, ind);
		}
		
		// break up into an array
		var paramStrings = queryString.split('&');
		var params = new Array();
		var k = new Array();
		for (var i=0; i < paramStrings.length; i++) {
			k = paramStrings[i].split('=');
			params[k[0]] = k[1];
		}
		
		return params;
	},
	
	//--------------------------------------------------------
	basename: function(path, suffix) {
		// Returns the filename component of the path  
		// version: 1004.2314
		// discuss at: http://phpjs.org/functions/basename    
		// +   original by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
		//
		var b = path.replace(/^.*[\/\\]/g, '');
		if (typeof(suffix) == 'string' && b.substr(b.length-suffix.length) == suffix) {
			b = b.substr(0, b.length-suffix.length);
		}
		
		return b;
	},  
	
	//--------------------------------------------------------
	is_array: function(mixed_var) {
		// Returns true if variable is an array  
		// version: 1004.2314
		// discuss at: http://phpjs.org/functions/is_array    
		// +   original by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
		var key = '';    var getFuncName = function (fn) {
			var name = (/\W*function\s+([\w\$]+)\s*\(/).exec(fn);
			if (!name) {
				return '(Anonymous)';
			}  return name[1];
		};
		
		if (!mixed_var) {
			return false;   
		}
		
		// BEGIN REDUNDANT
		this.php_js = this.php_js || {};
		this.php_js.ini = this.php_js.ini || {};    // END REDUNDANT
		
		if (typeof mixed_var === 'object') {
			if (this.php_js.ini['phpjs.objectsAsArrays'] &&  
			   (
			    (this.php_js.ini['phpjs.objectsAsArrays'].local_value.toLowerCase &&
			     this.php_js.ini['phpjs.objectsAsArrays'].local_value.toLowerCase() === 'off') ||
			     parseInt(this.php_js.ini['phpjs.objectsAsArrays'].local_value, 10) === 0)
			    ) {
					return mixed_var.hasOwnProperty('length') && !mixed_var.propertyIsEnumerable('length') && 
					       getFuncName(mixed_var.constructor) !== 'String'; 
			}
			
			if (mixed_var.hasOwnProperty) {
				for (key in mixed_var) {
					if (false === mixed_var.hasOwnProperty(key)) {                    
						return false;
					}
				}
			}
			return true;
		}
		
		return false;
	},
  
	//--------------------------------------------------------
	is_mobile_browser: function() {
		// IMPROVE - consider using http://modernizr.com/ instead
		
		// based on code from http://detectmobilebrowser.com/
		var reg1 = /android|avantgo|blackberry|blazer|compal|elaine|fennec|hiptop|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile|o2|opera m(ob|in)i|palm( os)?|p(ixi|re)\/|plucker|pocket|psp|smartphone|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce\; (iemobile|ppc)|xiino/i;
  
		var reg2 = /1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|e\-|e\/|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(di|rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|xda(\-|2|g)|yas\-|your|zeto|zte\-/i;
    
		
		if ( reg1.test(navigator.userAgent||navigator.vendor||window.opera) || reg2.test(navigator.userAgent||navigator.vendor||window.opera) ) {
			return true;
		} else {
			return false;
		}
	},
	
	//-------------------------------------------
	transpose: function(arr) {
		// transpose 2d, numerically indexed array
		var t = new Array();
		for (var i=0; i < arr.length; i++) {
			for (var j=0; j < arr[i].length; j++) {
				if ( typeof t[j] == "undefined" )  t[j] = new Array();
				t[j][i] = arr[i][j];
			}
		}
		
		return t;
	},

	//-------------------------------------------
	print_r: function(theObj) {
		var output = '';
		
		if (theObj.constructor == Array || theObj.constructor == Object) {
			output = "<ul>";
			output = output + '<li style="list-style-type:none;position: relative; left: -2em;">{</li>'+"\n";      
			for (var p in theObj) {
				if (theObj[p].constructor == Array || theObj[p].constructor == Object) {
					output = output + "<li>["+p+"] => "+typeof(theObj)+"</li>\n";
					output = output + "<ul>";
					output = output + utils.print_r(theObj[p]);
					output = output + "</ul>\n";
				} else {
					output = output + "<li>["+p+"] => "+theObj[p]+"</li>\n";
				}
			}
			output = output + '<li style="list-style-type:none; position: relative; left: -2em;">}</li>'+"\n";      
			output = output + "</ul>\n";
		}
		
		return output;
	},
	
	//-------------------------------------------
	printDebug: function(input) { // query string must include debug=true
		// get 2nd optional parameter
		if (arguments.length == 2) {
			var varName = ' (' + arguments[1] + ')';
		} else {
			var varName = '';
		}
		
		// don't print out anything if not in debug mode
		var querystringParams = utils.getQueryStringArray();
		if ( querystringParams['debug'] != 'true' ) {
			return;
		} 
		
		// create a debug container if not present
		if ( !document.getElementById("jsani_debug") ) {
			$("#jsani").after('<div id="jsani_debug"><ul id="jsani_lev_one"></ul></div>');
		}
		
		if (input.constructor == Array || input.constructor == Object) {
			var print_r_output = utils.print_r(input);
			$("#jsani_debug ul").prepend('<li>Array/Object' + varName + ': ' + print_r_output + '</li>');
		} else {
			$("#jsani_debug ul").prepend('<li>' + input + varName + '</li>'); 
		}
		
		return;
	}	

};
//==============================================================

//==============================================================
var controls = {
	// method-------------------------------------------
	createControls:  function( ) {
	
		// possible controls
		var user_controls = new Array();
		user_controls['previous'] =  '<td id="previousButton" class="button">&lt;</td>';                                  
		user_controls['stopplay'] = '<td id="stopButton" class="button">stop</td>' + "\n";        
		user_controls['next'] = '<td id="nextButton" class="button">&gt;</td>';
		user_controls['speedslider'] = '<td id="speedContainer">' +
		                               '<div id="speedBarContainer">' +
		                               '<div id="speedMinus" class="speedPlusMinus">&ndash;</div>' +
		                               '<div id="speedBar"><div id="speedLine"><div id="speedButton"></div></div></div>' +
		                               '<div id="speedPlus" class="speedPlusMinus">+</div>' +
		                               '</div>'+
		                               '</td>';
		user_controls['slowfast'] = '<td id="slowButton" class="button">slower</td>'+
		                            '<td id="fastButton" class="button">faster</td>';
		user_controls['refresh'] = '<td id="refreshButton" class="button">refresh</td>';
		user_controls['looprock'] = '<td id="looprockButton" class="button">rock</td>';    
		user_controls['zoom'] = '<td id="zoomButton" class="button">zoom</td>';
		
		// equivalent FlAniS controls (for partial compatability with FlAniS config files)
		user_controls['step'] = user_controls['previous'] + user_controls['next'];
		user_controls['startstop'] = user_controls['stopplay'];
		user_controls['speed'] = user_controls['slowfast'];

		// list of specified controls
		var c = $("#jsani input[name='controls']").val().split(/[ ]*,[ ]*/);
		if ( jsani.imgURLs.length == 1 )  c = new Array('zoom', 'refresh');
		
		/**************************************************************************
		// removed for now because this is treating desktop OS X as a mobile device		
		
		// remove zoom if mobile browser
		if ( utils.is_mobile_browser() ) { 
			var c_new = new Array();
			for (i=0; i < c.length; i++) {
				if ( c[i] != 'zoom' ) c_new.push(c[i]);
			}
			c = c_new;
		}
		**************************************************************************/
		
		// print specified controls
		var controlsHTML = '<div id="controlsContainer"><table cellpadding="0" cellspacing="0" class="controlSet" id="controlSet_1"><tr>';
		for (i=0; i < c.length; i++) {
			if ( typeof user_controls[c[i]] != 'undefined' ) {				
				controlsHTML += user_controls[c[i]];
			} 
		}
		controlsHTML += '</tr></table>';	
		// overlay controls are added elsewhere after overlays have finished preloading	
		controlsHTML += '</div>';                          

		if ( document.getElementById("controlsContainer") )  $("#controlsContainer").remove();
		if ( document.getElementById("jsaniContainer") )  $("#jsaniContainer").remove();    
		$("#jsani").append(controlsHTML);		
		if ( utils.optionExists('overlay_labels') ) 	controls.addOverlayControls('init_container');
		
		// remove right border on last button and left border on first button here rather than in css 
		// because f'ing IE doesn't handle css properly
		$("#controlsContainer .button:first-child").css('border-left', 'none');    
		$("#controlsContainer .button:last-child").css('border-right', 'none');
		
		if ( document.getElementById("speedBar") ) {
			speedSlider.init('speedButton');    
		}
		
		$("#slowButton").bind('click', controls.slower);
		$("#fastButton").bind('click', controls.faster);
		$("#speedBarContainer").bind('click', controls.adjustSpeed);
		
		$("#stopButton").bind('click', controls.stopPlay);
		$("#previousButton").bind('click', controls.showPreviousFrame);
		$("#nextButton").bind('click', controls.showNextFrame);   
		
		$("#refreshButton").bind('click', controls.refreshImages);    
		
		$("#looprockButton").bind('click', controls.toggleLoopRock);        
		
		$("#zoomButton").bind('click', controls.toggleZoom);        
		
	},
	
	//-------------------------------------------
	addOverlayControls:  function( action ) {  	
	
		if ( action == 'init_container' ) {
			var controlsHTML = '<div class="controlSet" id="controlSet_2">Overlays Loading &hellip;</div>';			
			$(controlsHTML).insertAfter("#controlSet_1");			
		} else {
			var controlsHTML = '';
			var overlay_labels = $("#jsani input[name='overlay_labels']").val().split(',');
			var overlayLabel = '';
			var checked = '';
			for (var i=0; i < jsani.overlays.length; i++) { 
				if ( typeof overlay_labels[i] != "undefined" ) {
					overlayLabel = $.trim(overlay_labels[i]).split(/[ ]*\/[ ]*/);
					if ( overlayLabel.length == 1 ) overlayLabel[1] = 'off'; // off is default for overlay visibility
				} else {
					overlayLabel = new Array('Overlay ' + i, 'off');
				}
				if (overlayLabel[1] == 'on') {
					checked = 'checked="checked"';
				} else {
					checked = '';
				}
				controlsHTML += '	<label><input type="checkbox" name="overlay_' + i + '" value="' + i + '" ' + checked + '> <span class="unselectable">' + overlayLabel[0] + '</span></label>';						
			}
			$("#controlSet_2").html(controlsHTML);		
			
			for (var i=0; i < jsani.overlays.length; i++) { 
				$("input[name=overlay_"+i+"]").bind('change', jsani.updateOverlayVis);
			}

			//IMPROVE - this code is duplicated elsewhere - put into a function
			var containerHeight = $("#jsani").height();
			var controlHeight = $("#controlsContainer").height();    
			//var top = parseInt(controlHeight, 10) + 1;
			var top = $("#controlsContainer").outerHeight();			
			$("#jsaniContainer").css('height', parseInt(containerHeight - controlHeight, 10) + "px");
			$("#jsaniContainer").css('top', top + "px");   
			
			$("#panel").css('height', jsani.imgHeight + 'px');
			$("#panel").css('width', jsani.imgWidth + 'px');     
			
			jsani.resizeImage();
			
			jsani.horizCenterImage();			
		}


	},
	
	//-------------------------------------------
	toggleZoom:  function( ) {  

		if ( $("#zoomButton").html() == 'zoom' ) { // zoom mode is disabled
			jsani.zoomEnabled = true;
			$("#zoomButton").html('un-zoom');
		} else { // zoom mode is enabled
			jsani.zoomEnabled = false;     
			jsani.unzoom();
			$("#zoomButton").html('zoom');      
		}  	
	},
	//---------------------------------------------------   
	
	//-------------------------------------------
	toggleLoopRock:  function( ) {
		if ( $("#looprockButton").html() == 'rock' ) { // animation is looping
			jsani.looprock = 'rock';
			$("#looprockButton").html('loop');
		} else { // animation is rocking
			jsani.looprock = 'loop';
			jsani.direction = 'forward'; // looping always goes forward       
			$("#looprockButton").html('rock');      
		}  
	},
	//--------------------------------------------------- 
	
	//-------------------------------------------
	slower:  function( ) {

		controls.slowDownAni();
		
		if ( jsani.imgDwell >= jsani.maxDwell ) {
			$("#slowButton").attr('class', 'button_disabled');
		} else {
			$("#slowButton").attr('class', 'button');     
		}   
		if ( jsani.imgDwell <= jsani.minDwell ) {
			$("#fastButton").attr('class', 'button_disabled');
		} else {
			$("#fastButton").attr('class', 'button');     
		}
	},
	//---------------------------------------------------    
	
	// method-------------------------------------------
	faster:  function( ) { 	

		controls.speedUpAni();
		
		if ( jsani.imgDwell >= jsani.maxDwell ) {
			$("#slowButton").attr('class', 'button_disabled');
		} else {
			$("#slowButton").attr('class', 'button');     
		}   
		if ( jsani.imgDwell <= jsani.minDwell ) {
			$("#fastButton").attr('class', 'button_disabled');
		} else {
			$("#fastButton").attr('class', 'button');     
		}
	},
	//---------------------------------------------------   
	
	// method-------------------------------------------
	refreshImages:  function( ) {
	
		// stop animation
		controls.stopAnimation();
		
		// add a query string on end of image urls to force browser to redownload images from server
		var d = new Date();
		var tmpArr = new Array();
		var img = '';
		var filename = '';
		d = d.getTime();
		for (var i=0; i < jsani.imgURLs.length; i++) {
			tmpArr = jsani.imgURLs[i].split('?');
			img = tmpArr[0];
			jsani.imgURLs[i] = img + '?' + d;
			
			tmpArr = jsani.filenames[i].split('?');
			filename = tmpArr[0];
			jsani.filenames[i] = filename + '?' + d;
		}
		
		// reset certain aspects of animation
		jsani.direction = 'forward';
		jsani.looprock = 'loop';
		
		// restart animation by preloading images (which then starts loop when done)
		jsani.preloadImages();
	},
	//--------------------------------------------------- 
	
	// method-------------------------------------------
	showNextFrame:  function( ) {
		// stop animation
		controls.stopAnimation();
		jsani.changeFrame('forward');
		return;
	},
	//--------------------------------------------------- 
	
	// method-------------------------------------------
	showPreviousFrame:  function( ) {
		// stop animation
		controls.stopAnimation();
		jsani.changeFrame('backward');
		return;
	},
	//--------------------------------------------------- 
	
	// method-------------------------------------------
	stopPlay:  function( ) {
		var stopStatus = $("#stopButton").html();    
		
		if (stopStatus == 'stop') { // stop animation
			controls.stopAnimation();
		} else {  // start animation
			controls.playAnimation();
		}
	},
	//--------------------------------------------------- 
	
	// method-------------------------------------------
	stopAnimation:  function( ) {
		window.clearInterval(jsani.timerID);
		$("#stopButton").html('play');    
	},
	//--------------------------------------------------- 
	
	// method-------------------------------------------
	playAnimation:  function( ) {
		jsani.timerID = window.setInterval('jsani.changeFrame()', jsani.imgDwell);     
		$("#stopButton").html('stop');    
	},
	//---------------------------------------------------   
	
	// method-------------------------------------------
	adjustSpeed:  function(e) {
	
		// move slider button to the left or right depending on where user clicked
		if ( utils.findPosX("speedButton") <= e.clientX ) {
			speedSlider.moveSpeedButtonToRight();   
		} else {
			speedSlider.moveSpeedButtonToLeft();        
		}
		
		// calculate new dwell rate based on new x position of speed button with respect to the speed bar
		var x = utils.findPosX("speedButton");    
		// this is the x position of far rightside of the speedslider - this isn't the same as speedSlider.maxX,
		// which is the max x position the speedButton should go to the right which takes into account the width of
		// the speedButton
		var speedSlider_maxX = parseInt(speedSlider.minX, 10) + parseInt( $("#speedBar").width(), 10 ); 
		var newDwell = (x - speedSlider.maxX) * (jsani.maxDwell - jsani.minDwell) / (speedSlider.maxX - speedSlider.minX) + jsani.minDwell;
		newDwell = -newDwell;
		
		if (newDwell > jsani.maxDwell) {
			newDwell = jsani.maxDwell;
		}
		if (newDwell < jsani.minDwell) {
			newDwell = jsani.minDwell;
		}
		
		jsani.imgDwell = newDwell;
		
		window.clearInterval(jsani.timerID);
		jsani.timerID = window.setInterval('jsani.changeFrame()', jsani.imgDwell);     
		$("#stopButton").html('stop');    
		
		return true;
	},
	//--------------------------------------------------- 
	
	// method-------------------------------------------
	slowDownAni:  function( ) {
		var newDwell = jsani.imgDwell + jsani.dwellStepRate;
		if (newDwell > jsani.maxDwell) {
			newDwell = jsani.maxDwell;
		}
		jsani.imgDwell = newDwell;
		
		window.clearInterval(jsani.timerID);
		jsani.timerID = window.setInterval('jsani.changeFrame()', jsani.imgDwell);     
		$("#stopButton").html('stop');    
	},
	//--------------------------------------------------- 
	
	// method-------------------------------------------
	speedUpAni:  function( ) {
		var newDwell = jsani.imgDwell - jsani.dwellStepRate;
		if (newDwell < jsani.minDwell) {
			newDwell = jsani.minDwell;
		}
		jsani.imgDwell = newDwell;
		
		window.clearInterval(jsani.timerID);
		jsani.timerID = window.setInterval('jsani.changeFrame()', jsani.imgDwell);    
		$("#stopButton").html('stop');    
	}
	//--------------------------------------------------- 

};
//==============================================================

//==============================================================
var jsani = {
	imgURLs:                 false,
	overlays:                [],  
	overlay_labels:          [],  
	imgBaseURL:              false,
	imgWidth:                false,
	imgHeight:               false,
	imgIndex:                0,
	imgDwell:                300,  
	timerID:                 false,
	nLeft:                   false,
	nOverlaysLeft:           false,
	dwellStepRate:           false,
	maxDwell:                1400,
	minDwell:                80,
	nSteps:                  25,     // set the number of steps for the slider and to speed up/down  
	looprock:                'loop', // whether animation should be looping or rocking
	direction:               'forward', // or 'backward'
	maxIndex:                false, 
	resizedImgWidth:         false,
	resizedImgHeight:        false,  
	zoomLevel:               1,
	zoomFactor:              1.25, 
	zoomEnabled:             false,
	filenames:               [],
	missingImages:           [],
	frameDwell:              [],
	frameDwellCounter:       [],
	jsani_started:           false,
	
	// method-------------------------------------------
	init: function( action ) {
		if( !document.getElementById ||
		    !document.getElementsByTagName ||
		    !document.getElementById( 'jsani' ) ) return;
			
		if ( action == 'start' && utils.optionExists('config_file') ) {
			jsani.load_config( $("#jsani input[name='config_file']").val() );
			return;
		}
		
		$("#jsani").show();		
		
		// make all hidden input parameters lower case 
		var parameters = $("#jsani input[type='hidden']");
		var name = '';
		var value = '';
		for (var i=0; i < parameters.length; i++) {
			name = $(parameters[i]).attr('name').toLowerCase();
			value = $(parameters[i]).attr('value');
			$(parameters[i]).replaceWith('<input type="hidden" name="'+name+'" value="'+value+'">');
		}
		
		// rename supported FlAniS config options to equivalent JSani config options
		$("[name=image_base]").attr('name', 'imgbaseurl');
		
		// get filenames
		if ( jsani.filenames.length == 0 ) { // && action != load_file_list_done
			if ( utils.optionExists('filenames') ) {  
				jsani.filenames = $("#jsani input[name='filenames']").val().split('::');
				if ( utils.optionExists('overlay_labels') && utils.optionExists('overlay_filenames') ) {  
					jsani.overlays = jsani.parse_overlay_filenames();          
        		}
			} else if ( utils.optionExists('file_of_filenames') ) {        
				jsani.load_file_list( $("#jsani input[name='file_of_filenames']").val(), utils.optionExists('overlay_labels') );
				return; // load_file_list will asynchronously use ajax to load filenames and then call this function again
			} else {
				// IMPROVE put in code here to handle this error gracefully
			}
		}
		
		jsani.makeImgURLs();

		// initialize frame pauses/dwells 
		for (var i=0; i < jsani.imgURLs.length; i++) {
			this.frameDwell[i] = 0;
			this.frameDwellCounter[i] = this.frameDwell[i];		
		}

		if ( utils.optionExists('frame_pause') ) {
			var pause = $("#jsani input[name='frame_pause']").val();
			pause = pause.split(',');
			var tmp = new Array();
			var n = 0;
			var m = 0;
			for (var i=0; i < pause.length; i++) {
				tmp = pause[i].split(':');
				n = parseInt(tmp[0], 10);
				m = parseInt(tmp[1], 10);
				this.frameDwell[n] = m;
				this.frameDwellCounter[n] = this.frameDwell[n];
			}
		}
		
		if ( utils.optionExists('first_frame_pause') ) {
			this.frameDwell[0] = parseInt($("#jsani input[name='first_frame_pause']").val(), 10);
			this.frameDwellCounter[0] = this.frameDwell[0];
		}

		if ( utils.optionExists('last_frame_pause') ) {
			var lastFrame = jsani.imgURLs.length - 1;
			this.frameDwell[lastFrame] = parseInt($("#jsani input[name='last_frame_pause']").val(), 10);
			this.frameDwellCounter[lastFrame] = this.frameDwell[lastFrame];
		}
				
		// get dwell rates
		if ( utils.optionExists('maxdwell') ) {
			var maxdwell = $("#jsani input[name='maxdwell']").val();
			if ( maxdwell <= 2.0 ) {
				this.maxDwell = parseInt(maxdwell*1000, 10);
			} else {
				this.maxDwell = parseInt(maxdwell, 10);       
			}
		}
		
		if ( utils.optionExists('mindwell') ) {
			var mindwell = $("#jsani input[name='mindwell']").val();
			if ( mindwell <= 2.0 ) {
				this.minDwell = parseInt(mindwell*1000, 10);       
			} else {
				this.minDwell = parseInt(mindwell, 10);             
			}
		}
		
		if ( utils.optionExists('initdwell') ) {
			var initdwell = $("#jsani input[name='initdwell']").val();
			if ( initdwell <= 2.0 ) {
				this.imgDwell = parseInt(initdwell*1000, 10);                    
			} else {
				this.imgDwell = parseInt(initdwell, 10);             
			}
		}
		
		if ( utils.optionExists('nsteps') ) {
			this.nSteps = parseInt($("#jsani input[name='nsteps']").val(), 10);
		}    
		
		this.dwellStepRate = (this.maxDwell - this.minDwell) / this.nSteps;    
		
		this.preloadImages();
	},  
	
	// method-------------------------------------------
	makeImgURLs:  function( ) {
	
		this.maxIndex = jsani.filenames.length - 1;    
		
		this.imgURLs = new Array();    
		if ( utils.optionExists('imgbaseurl') ) {     
			this.imgBaseURL = $("#jsani input[name='imgbaseurl']").val();
			this.imgBaseURL = this.imgBaseURL.replace(/\/$/, '');
		} 
		if (this.imgBaseURL != false) {
			var prefix = this.imgBaseURL + '/';
		} else {
			var prefix = '';
		}
		for (var i=0; i < jsani.filenames.length; i++) {
			jsani.filenames[i] = jQuery.trim(jsani.filenames[i]);     
			this.imgURLs[i] = prefix + jsani.filenames[i];
		}  
	
		// overlay urls
		var overlayMaxIndex = 0;
		for (var i=0; i < jsani.overlays.length; i++) { // loop over overlays
			overlayMaxIndex = jsani.overlays[i].length - 1;
			/**************
			IMPROVE - check to make sure the # of animation frames in overlays is the same as the base animation
			if ( this.maxIndex != overlayMaxIndex ) {
			// what should I do?
			}      
			**************/
			for (var j=0; j < jsani.overlays[i].length; j++) {
				this.overlays[i][j].url = prefix + jsani.overlays[i][j].filename;
			}              
		}
    
	},  
	
	// method-------------------------------------------
	startLoop:  function( ) {
		
		var index = 0;
		if (arguments.length > 0) {
			index = arguments[0];
		}
		
		// remove missing images from animation and recreate frame list
		var missingimages = 'hide';
		if ( utils.optionExists('missingimages') )  missingimages = $("#jsani input[name='missingimages']").val();
		if ( missingimages == 'hide' ) {
			var tmp = new Array();
			for (var i=0; i < jsani.missingImages.length; i++) {
				for (var j=0; j < jsani.filenames.length; j++) {
					if ( jsani.missingImages[i] == jsani.filenames[j] ) {
						jsani.filenames.splice(j, 1);
						for (k=0; k < jsani.overlays.length; k++) { // remove all corresponding overlays for missing base images
							jsani.overlays[k].splice(j,1);
						}
					}
				}
			}
			jsani.makeImgURLs();
		}      
		
		// create controls
		controls.createControls();    
		
		// create image container
		$("#jsani").append('<div id="jsaniContainer"></div>');
		var containerHeight = $("#jsani").height();
		var controlHeight = $("#controlsContainer").height();    
		//var top = parseInt(controlHeight, 10) + 1;
		var top = $("#controlsContainer").outerHeight();
		$("#jsaniContainer").css('width', '100%');							
		$("#jsaniContainer").css('height', parseInt(containerHeight - controlHeight, 10) + "px");
		$("#jsaniContainer").css('top', top + "px");    
		$("#jsaniContainer").css('overflow', 'hidden');
		$("#jsaniContainer").css('position', 'absolute');
				
		// create panel container
		$("#jsaniContainer").append('<div id="panel"></div>');
		$("#panel").css('position', 'absolute');
		$("#panel").css('top', "0px");
		$("#panel").css('left', '0px');
		$("#panel").css('height', jsani.imgHeight + 'px');
		$("#panel").css('width', jsani.imgWidth + 'px');     
    
		// create frames
		for (var i=0; i < jsani.imgURLs.length; i++) {
			jsani.createFrame("panel", i);
		}
		
		this.resizeImage();
		
		jsani.horizCenterImage();
		
		// show first frame
		utils.show_('#frame_0');
		
		// set click to zoom/center event handler
		$("#jsaniContainer").bind('mouseup', this.zoomImage);
		
		// enable drag and drop
		dragImg.init('panel');
		
		if ( jsani.imgURLs.length > 1 ) {
			jsani.timerID = window.setInterval('jsani.changeFrame()', jsani.imgDwell);     
		}

		// create a custom event for when JSani is done loading / has started (this is done before loading the overlays
		// because they are meant to be preloaded and displayed AFTER the animation has started)
		$.event.trigger({
			type: "jsani_is_loaded",
			message: "JSani has started",
			time: new Date()
		});	
		jsani.jsani_started = true;
				
		this.preloadOverlays(); // overlays will show once they are done preloading
	},
	
	//--------------------------------------------------
	jsaniResizeHandler:  function() {  	
		var containerHeight = $("#jsani").height();
		var controlHeight = $("#controlsContainer").height();
		$("#jsaniContainer").css('height', parseInt(containerHeight - controlHeight, 10) + "px");
		jsani.unzoom(); // IMRPOVE - allow view to remain zoomed in while resizing JSani
		$("#zoomButton").html('zoom');		
		jsani.resizeImage();
		jsani.horizCenterImage();
	},
	
	//--------------------------------------------------
	updateOverlayVis:  function() {  
	
		// IMPROVE - clicking on the Refresh button resets overlays to the initial state (should remember state instead)
		
		for (var i=0; i < jsani.overlays.length; i++) {	// loop over overlays
			var overlay = 'overlay_' + i;
			if ( $("input[name=" + overlay + "]").is(':checked') ) {
				utils.show_("." + overlay);		
			} else {
				utils.hide_("." + overlay);						
			}
		}
	},

	// method-------------------------------------------
	createFrame:  function(parent_id, index ) {  
		var id = 'frame_' + index;
		$("#" + parent_id).append('<div id="'+id+'" class="frame"></div>');
		$("#"+id).css('width', '100%');        
		$("#"+id).css('height', '100%');        
		$("#"+id).css('position', 'absolute');        
		$("#"+id).css('top', '0');        
		$("#"+id).css('left', '0');        
		//    $("#"+id).hide();
		//    $("#"+id).css('display', 'none');
		utils.hide_("#"+id);

		jsani.createBaseImage(id, this.imgURLs[index]);
    
		// create overlays
		for (var i=0; i < jsani.overlays.length; i++) {
			jsani.createOverlay(i, id);						
		}
	},
  
	// method-------------------------------------------
	createBaseImage:  function(parent_id, url ) {    
		$("#" + parent_id).append('<img src="'+url+'" class="jsaniImg" alt="IMAGE NOT FOUND">');          
		var jsaniImg = "#" + parent_id + " .jsaniImg";
		$(jsaniImg).css("position", "absolute");
		$(jsaniImg).css("top", "0");
		$(jsaniImg).css("left", "0");
		$(jsaniImg).css("display", "inline");
		$(jsaniImg).css("z-index", "1");
		$(jsaniImg).css("width", "100%"); 
		$(jsaniImg).css("height", "100%");
	},
  
	// method-------------------------------------------
	createOverlay:  function(overlay_index, parent_id) {	
		var overlayClass = 'overlay_' + overlay_index;
		var overlayImg = "#" + parent_id + " .overlayImg";    
		var zIndex = 1 + parseInt(overlay_index, 10) + 1; // assuming overlay_index starts at 0 and base image is at z-index: 1
    
		$("#" + parent_id).append('<img class="overlayImg '+overlayClass+'" alt="">');          				
    
		utils.hide_(overlayImg);
				
		$(overlayImg).css("position", "absolute");
		$(overlayImg).css("top", "0");
		$(overlayImg).css("left", "0");
		$(overlayImg).css("z-index", zIndex);
		$(overlayImg).css("width", "100%"); 
		$(overlayImg).css("height", "100%"); 
	},
	
	// method-------------------------------------------
	horizCenterImage:  function( ) {  
		var w = $("#panel").width();    
		var wc = $("#jsaniContainer").width();
		
		if ( w < wc ) {
			var left = (wc - w) / 2;
		} else {
			var left = 0;
		}

		$("#panel").css('left', left + 'px' );        
	},
	
	// method-------------------------------------------
	resizeImage:  function( ) {
	
		// set width/height
		var containerWidth = $("#jsaniContainer").width();
		var containerHeight = $("#jsaniContainer").height();
		var newImageWidth = $("#panel").width();
		var newImageHeight = $("#panel").height();          
		
		if ( !isNaN(containerWidth) && !isNaN(containerHeight) ) { // container has defined dimensions
			newImageWidth = this.imgWidth;
			newImageHeight = this.imgHeight;     
			if (newImageWidth > containerWidth) {
					newImageHeight = parseInt((newImageHeight/newImageWidth)*containerWidth, 10);
					newImageWidth = containerWidth;
			}
			if (newImageHeight > containerHeight) {
				newImageWidth = parseInt((newImageWidth/newImageHeight)*containerHeight, 10);
				newImageHeight = containerHeight;
			}
		
			document.getElementById("panel").style.left = "0px";
			document.getElementById("panel").style.top = "0px";

		}
		
		document.getElementById("panel").style.width = newImageWidth + 'px';
		document.getElementById("panel").style.height = newImageHeight + 'px';
		
		this.resizedImgWidth = newImageWidth;
		this.resizedImgHeight = newImageHeight;    
		
		return;
	
	},
	
	// method-------------------------------------------
	changeFrame:  function( ) {

		// pause on the current frame for the specified amount
		if ( arguments.length == 0 ) { // if changeImage() called with arguments then previous/next buttons used and therefore ignore pause/dwell
			if (this.frameDwellCounter[this.imgIndex] > 0) {
				this.frameDwellCounter[this.imgIndex]--;
				return;
			} else {
				this.frameDwellCounter[this.imgIndex] = this.frameDwell[this.imgIndex];
			}
		}
	
		// toggle direction based on looprock status and what frame is currently being displayed
		if ( this.looprock == 'loop' ) {
			this.direction = 'forward'; // looping always goes forward
		} else { 
			if ( this.imgIndex == this.maxIndex ) { // end of animation - go backwards
				this.direction = 'backward';
			} else if ( this.imgIndex == 0 ) { // beginning of animation - go forward
				this.direction = 'forward';       
			}    
		}
		
		// if method called with a specific direction override jsani.direction temporarily
		var anim_direction = this.direction;
		if (arguments.length > 0) {
			anim_direction = arguments[0];
		}
		
		var currentIndex = this.imgIndex;
		
		if (anim_direction == 'forward') { // IMPROVE - shouldn't I use this.maxIndex instead of this.imgURLs.length? 
			var newIndex = this.imgIndex + 1;
			if (newIndex > this.imgURLs.length - 1) {
				newIndex = 0;
			}
		
			utils.show_("#frame_"+newIndex);
			utils.hide_("#frame_"+currentIndex);
			this.imgIndex++; // IMPROVE - maybe rename this.imgIndex to this.frameIndex?
			if (this.imgIndex > this.imgURLs.length - 1) {
				this.imgIndex = 0;
			}

		} else {
			var newIndex = this.imgIndex - 1;
			if (newIndex < 0) {
				newIndex = this.imgURLs.length - 1;
			}
		
			utils.show_("#frame_"+newIndex);
			utils.hide_("#frame_"+currentIndex);
			this.imgIndex--;
			if (this.imgIndex < 0) {
				this.imgIndex = this.imgURLs.length - 1;
			}
      
		}
        
	},
	
	// method-------------------------------------------
	preloadImages:  function( ) {
	
		this.nLeft = this.imgURLs.length;   
		
		var imgArr = new Array();
		this.createCountDownTimer();
		for (var i=0; i < this.imgURLs.length; i++) {
			imgArr[i] = new Image();
			$(imgArr[i]).bind('load', jsani.finishedPreloadingImages);
			$(imgArr[i]).bind('error', jsani.badImage);
			imgArr[i].src = this.imgURLs[i];
		} 
	},
	
	// method-------------------------------------------
	preloadOverlays:  function( ) {
				
		// overlays are loaded AFTER animation starts and they are preloaded in the background with no visual 
		// indication of their preloading
			
		jsani.nOverlaysLeft = 0;
		for (var i=0; i < this.overlays.length; i++) {
			for (var j=0; j < this.overlays[i].length; j++) {				 
				jsani.nOverlaysLeft++;
			}
		}			

		// IMPROVE - missing overlays need to be handled similar to how missing base images are

		for (var i=0; i < this.overlays.length; i++) {
			for (var j=0; j < this.overlays[i].length; j++) {				 
				this.overlays[i][j].image = new Image();
				$(this.overlays[i][j].image).bind('load', jsani.finishedPreloadingOverlays);
				$(this.overlays[i][j].image).bind('error', jsani.finishedPreloadingOverlays); 
				this.overlays[i][j].image.src = this.overlays[i][j].url;
			}
		}

	
	},		

	// method-------------------------------------------
	createCountDownTimer:  function( ) {   
		$("#jsani").append('<div id="countDownTimerContainer"><div id="countDownTimerBarContainer">' +
		                   '<span id="loadingText">Loading</span>' +
		                   '<div id="countDownTimerBar">' +
		                   '</div></div></div>');
	},
	
	// method-------------------------------------------
	badImage:  function(event) {
	
		var filename = $(event.currentTarget).attr('src');
		jsani.missingImages.push( utils.basename(filename, '') );
		
		jsani.finishedPreloadingImages();
	
	},   
	
	// method-------------------------------------------
	finishedPreloadingImages:  function(e) {
		jsani.nLeft--;
		
		jsani.imgWidth = this.width;
		jsani.imgHeight = this.height;		
		
		$("#countDownTimerBar").width( (jsani.nLeft / jsani.imgURLs.length)*100.0 + '%' );
		
		if (jsani.nLeft <= 0) {
			$("#countDownTimerContainer").remove();
			jsani.startLoop();
		}
	},

	// method-------------------------------------------
	finishedPreloadingOverlays:  function(e) {
		jsani.nOverlaysLeft--;

		if (jsani.nOverlaysLeft <= 0) {
			
			if ( utils.optionExists('overlay_filter') ) {  
				var overlay_filter = $("#jsani input[name='overlay_filter']").val();
			} else {
				var overlay_filter = 'default'; // remove background
			}
			
			if ( overlay_filter == 'default' ) {
				jsani.removeOverlayBackgrounds();
			}

			controls.addOverlayControls('add_controls');

			// set image src for overlays
			var overlayImg = '';
			for (var i=0; i < jsani.overlays.length; i++) {								
				for (var j=0; j < jsani.overlays[i].length; j++) {	// loop over frames
					overlayImg = "#frame_" + j + " .overlay_" + i;    													
					$(overlayImg).attr("src", jsani.overlays[i][j].url);
				}			
			}			

			jsani.updateOverlayVis();
		}
	},
		  
	// method-------------------------------------------
	centerImg:  function(e) {
	
		// calculate variables to recenter image
		var clickX = utils.clickPosX(e);
		var clickY = utils.clickPosY(e);        
		
		var imgX = utils.findPosX("panel") - utils.findPosX("jsaniContainer");
		var imgY = utils.findPosY("panel") - utils.findPosY("jsaniContainer");    
		
		var jsaniContainerWidth = $("#jsaniContainer").width();
		var jsaniContainerHeight = $("#jsaniContainer").height();        
		
		var newLeft = (jsaniContainerWidth/2) - clickX + imgX;
		var newTop = (jsaniContainerHeight/2) - clickY + imgY;    
		
		// recenter image  
		$("#panel").css('margin', '0'); 
		$("#panel").css('left', newLeft + 'px');
		$("#panel").css('top', newTop + 'px');            				
				
	},
	
	// method-------------------------------------------
	zoomImage:  function(e) {
	

		if ( dragImg.imageWasMoved ) return;
		
		if ( !jsani.zoomEnabled ) return;
		
		// original image "x,y" coordinates 

		var imgX = ((dragImg.nn6 ? e.clientX : event.clientX) - utils.findPosX("panel"))/jsani.zoomLevel; 
		var imgY = ((dragImg.nn6 ? e.clientY : event.clientY) - utils.findPosY("panel"))/jsani.zoomLevel; 
		
		if (e.ctrlKey) {
		    jsani.zoomLevel = jsani.zoomLevel / jsani.zoomFactor;
		    if (jsani.zoomLevel < 1.0) jsani.zoomLevel = 1.0;
		} else {
		    jsani.zoomLevel = jsani.zoomLevel * jsani.zoomFactor;
		}

		// zoom by re-sizing the panel
                var imgWidth_new = parseInt(Math.round(jsani.resizedImgWidth * jsani.zoomLevel), 10);
                var imgHeight_new = parseInt(Math.round(jsani.resizedImgHeight * jsani.zoomLevel), 10);

		$("#panel").css('width', imgWidth_new + 'px'); 
		$("#panel").css('height', imgHeight_new + 'px');				
		
		// set the zoomed origin to make sure zoom in/out at same spot in origin image
		var xOffset = parseInt(Math.round(utils.clickPosX(e) - imgX * jsani.zoomLevel), 10);
		var yOffset = parseInt(Math.round(utils.clickPosY(e) - imgY * jsani.zoomLevel), 10);

		$("#panel").css('left', xOffset + 'px');
		$("#panel").css('top', yOffset + 'px');  
	},
	
	//-------------------------------------------
	unzoom:  function() {
		jsani.zoomLevel = 1;
		
		// reset to original size 
		$("#panel").css('width', jsani.resizedImgWidth + 'px'); 
		$("#panel").css('height', jsani.resizedImgHeight + 'px');				
		
		// reposition image
		jsani.horizCenterImage();    
		$("#panel").css('top', 0);						
	},
	
	//---------------------------------------------------
	parse_overlay_filenames: function() { // optional arguments: overlayInput
		/************************************************
		INPUT:
		A HTML hidden form field in the DOM that is read/parsed via jQuery
		
		<input type="hidden" name="overlay_filenames" value="{overlay_1_images}, {overlay_2_images}, ....">
		
		where {overlay_n_images} is the list of images for overlay "n" to animate in sync with the base images, separated
		by |
		
		Example:
		A 3 image animation with two overlays
		
		<input type="hidden" name="overlay_filenames" value="overlay_0_time_000.gif | overlay_0_time_001.gif | overlay_0_time_002.gif,
		                                                     overlay_1_time_000.gif | overlay_1_time_001.gif | overlay_1_time_002.gif">
															 
		OUTPUT:	
		A 2 dimensional array - 1st dimension: overlay number, 2nd dimension: time or animation frame number
		
		Example: 
		array[0][0].filename = overlay_0_time_000.gif
		array[1][0].filename = overlay_1_time_000.gif
		array[0][1].filename = overlay_0_time_001.gif
		array[0][2].filename = overlay_0_time_002.gif
		and so on

		.filename is used because this array that is returned is the basis for a global class property that is used
		to store other information for overlays besides filenames
		************************************************/

		// IMPROVE - need to refactor code to make simpler - for example, this function and makeImgURLs() could be combined possibly
		
		if ( arguments.length == 0 ) {
			var overlayInput = $("#jsani input[name='overlay_filenames']").val();
		} else {
			var overlayInput = arguments[0];
		}

		// commas separate overlays, pipes separate times
		var overlay_filenames = new Array();
		var overlays = overlayInput.split(',');
		for (var i=0; i < overlays.length; i++) { // loop over N overlays
			overlays[i] = jQuery.trim(overlays[i]);
			overlay_filenames = overlays[i].split('|');
			overlays[i] = new Array();
			for (var j=0; j < overlay_filenames.length; j++) { // loop over time frames for each overlay
				overlays[i][j] = {};
				overlays[i][j].filename = jQuery.trim(overlay_filenames[j]);         
			}
		}
		
		return overlays;
	},	

	//---------------------------------------------------
	load_file_list: function(file_of_filenames, readOverlays) {
		
		// if readOverlays is false then any overlays specified in file_of_filenames are ignored, otherwise they are read and returned along with filenames
	
		$.ajax({
			url: file_of_filenames,
			success: function(data) {
			
				var isNonBlankLinkRegEx = /\S/;
				var commentRegEx = /#.*$/;
				var file_list = data.split("\n");
				
				// remove empty lines, comments and trim space from begin and end of line
				var f = new Array(); 
				var tmp = new Array();
				var o = new Array();
				for (var i=0; i < file_list.length; i++) {
					file_list[i] = file_list[i].replace(commentRegEx, ''); // remove comments
					if ( isNonBlankLinkRegEx.test(file_list[i]) ) {
						file_list[i] = $.trim(file_list[i]);
						
						// get base image filename
						tmp = file_list[i].split(/[ ]+/);
						f.push( tmp[0] );
						
						// get overlay filenames
						if ( readOverlays && tmp.length > 1 ) {
							tmp = file_list[i].split(/overlay[ ]*=[ ]*/);
							o.push(tmp[1].split(/[ ]*,[ ]*/));
						}
					}
				}
				
				if ( readOverlays ) {
					o = utils.transpose(o);
					// IMPROVE - this is kind of a screwy way to handle overlays (by taking an array, converting to a string and feeding into another
					// function to split into an array again) but is done because it's easy to do but might be better handled
					var overlays = new Array();
					for (var i=0; i < o.length; i++) {
						overlays[i] = o[i].join('|');
					}
					jsani.overlays = jsani.parse_overlay_filenames(overlays.join(','));										
				}
				
				jsani.filenames = f; 
				jsani.init('load_file_list_done');  // start jsani.init again to finish initializing animation
			}
		});
	},
	
	//---------------------------------------------------
	load_config: function(configFile) {	
		// read configFile and add config options from configFile into JSani container (the JSani code expects to find them there)
		$.ajax({
			url: configFile,
			success: function(data) {
			
				var isNonBlankLinkRegEx = /\S/;
				var commentRegEx = /#.*$/;
				var config = data.split("\n");
				
				// remove empty lines, comments and trim space from begin and end of line
				var c = new Array();
				for (var i=0; i < config.length; i++) {
					config[i] = config[i].replace(/#([0-9]{6,6})/, "x$1"); // change hex colors of the form #RRGGBB to xRRGGBB so that it's not treated as a comment
					config[i] = config[i].replace(commentRegEx, ''); // remove comments
					if ( isNonBlankLinkRegEx.test(config[i]) ) {
						config[i] = $.trim(config[i]);
						c = config[i].split(/[ ]*=[ ]*/);
						//$("#jsani").append('<input type="hidden" name="'+c[0]+'" value="'+c[1]+'">');
						$("#jsani").append('<input type="hidden" name="'+c[0]+'" value="'+c.slice(1).join('=')+'">');					
					}
				}
				
				jsani.init('load_config_done');  // start jsani.init again to finish initializing animation
			}
		});
	},

	//---------------------------------------------------
	removeOverlayBackgrounds: function() {	

		// IMRPOVE - use "this" instead of jsani to refer to parent object (and do the same for other "classes")

		// create canvas if it doesn't exist
		if ( !document.getElementById("jsaniCanvas") ) {
			var style = 'position: absolute; display: none;';
			var dimensions = 'width="' + this.imgWidth + '" height="' + this.imgHeight + '"';
			$("body").append('<canvas id="jsaniCanvas" style="' + style + '" ' + dimensions + '></canvas>');
		}

		var ctx = document.getElementById("jsaniCanvas").getContext("2d");
		
		var t = $("#jsani input[name='transparency']").val(); // assume #RRGGBB format
		var trans = new Array();
		trans[0] = parseInt(t.substr(1,2), 16);
		trans[1] = parseInt(t.substr(3,2), 16);
		trans[2] = parseInt(t.substr(5,2), 16);		

		// remove background from overlay images
		for (var i=0; i < jsani.overlays.length; i++) {
			for (var j=0; j < jsani.overlays[i].length; j++) {
				ctx.drawImage(jsani.overlays[i][j].image,0,0); 
	
				var myImageData = ctx.getImageData(0, 0, this.imgWidth, this.imgHeight);
		
				var strDataURI;
				var pos = 0;
				var r, g, b, a;
				for (y = 0; y < this.imgHeight; y++) {
					for (x = 0; x < this.imgWidth; x++) {
	
						r = myImageData.data[pos]; // red
						g = myImageData.data[pos + 1]; // green
						b = myImageData.data[pos + 2]; // blue
						a = myImageData.data[pos + 3]; // alpha
		
						if ( r == trans[0] && g == trans[1] && b == trans[2] ) { 
							a = 0;
						}
		
						myImageData.data[pos] = r;
						myImageData.data[pos+1] = g;
						myImageData.data[pos+2] = b;
						myImageData.data[pos+3] = a;
	
						pos = pos + 4;
					}
				}
				ctx.putImageData(myImageData, 0, 0);
	
				strDataURI = document.getElementById("jsaniCanvas").toDataURL();
	
				this.overlays[i][j].url = strDataURI;
	
				ctx.clearRect(0,0,ctx.canvas.width,ctx.canvas.height)
			}
		}

		return;
	}
  
};
//==============================================================

///////////////////////////////////////////////////////////////////
// DISABLE TEXT SELECTION ON DOUBLE CLICK:
// http://chris-barr.com/entry/disable_text_selection_with_jquery/
///////////////////////////////////////////////////////////////////
$(function(){
	$.extend($.fn.disableTextSelect = function() {
		return this.each(function(){
				$(this).mousedown(function(){return false;});
		});
	});
	$('.noSelect').disableTextSelect();//No text selection on elements with a class of 'noSelect'
});
