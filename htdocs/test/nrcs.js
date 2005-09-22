
// Clear "Enter Keywords" text from search box
function ClearSearch(inputBox) {
	if (inputBox.value == "Enter Keywords") {
		inputBox.value = "";
	}
}


// Style Switcher functions
// For details, refer to http://www.alistapart.com/stories/alternate/

function setActiveStyleSheet(title) {
	var i, a, main;
	if (document.getElementsByTagName) {
		for(i=0; (a = document.getElementsByTagName("link")[i]); i++) {
			if(a.getAttribute("rel").indexOf("style") != -1 && a.getAttribute("title")) {
				a.disabled = true;
				if(a.getAttribute("title") == title) a.disabled = false;
			}
		}
	}
}

function getActiveStyleSheet() {
	var i, a;
	if (document.getElementsByTagName) {
		for(i=0; (a = document.getElementsByTagName("link")[i]); i++) {
			if(a.getAttribute("rel").indexOf("style") != -1 && a.getAttribute("title") && !a.disabled) return a.getAttribute("title");
		}
		return null;
	}
}

function getPreferredStyleSheet() {
	var i, a;
	if (document.getElementsByTagName) {
		for(i=0; (a = document.getElementsByTagName("link")[i]); i++) {
			if(a.getAttribute("rel").indexOf("style") != -1
			&& a.getAttribute("rel").indexOf("alt") == -1
			&& a.getAttribute("title")
			) return a.getAttribute("title");
		}
		return null;
	}
}

function createCookie(name,value,days) {
	if (days) {
		var date = new Date();
		date.setTime(date.getTime()+(days*24*60*60*1000));
		var expires = "; expires="+date.toGMTString();
	}
	else expires = "";
	document.cookie = name+"="+value+expires+"; path=/";
}

function readCookie(name) {
	var nameEQ = name + "=";
	var ca = document.cookie.split(';');
	for(var i=0;i < ca.length;i++) {
		var c = ca[i];
		while (c.charAt(0)==' ') c = c.substring(1,c.length);
			if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
	}
	return null;
}

window.onload = function(e) {
	if (document.getElementsByTagName) {
		var cookie = readCookie("style");
		var title = cookie ? cookie : getPreferredStyleSheet();
		setActiveStyleSheet(title);
	}
}

window.onunload = function(e) {
	if (document.getElementsByTagName) {
		var title = getActiveStyleSheet();
		createCookie("style", title, 1);
	}
}

var cookie = readCookie("style");
var title = cookie ? cookie : getPreferredStyleSheet();
setActiveStyleSheet(title);
