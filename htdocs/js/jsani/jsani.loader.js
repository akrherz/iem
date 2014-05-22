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

(function (){

	var jsani_ver = '1.50';
	
	// determine path to JSani 
	var jsani_dir = null;  // no trailing /
	var scriptTags = document.getElementsByTagName('script');
	for (var i=0; i < scriptTags.length; i++) {
		if ( baseName(scriptTags[i].src) == 'jsani.loader' ) {
			jsani_dir = dirname(scriptTags[i].src);
			break;
		}
	}
	
	
	if ( jsani_dir != null ) {
		var jquery_dir = jsani_dir + '/jquery';  // no trailing /
	
		// tags are broken up, otherwise some browsers choke on the document.write
		document.write('<me'+'ta http-equiv="X-UA-Compatible" content="IE=8">' + "\n");
		document.write('<li'+'nk href="'+jsani_dir+'/jsani.css?' + jsani_ver + '" rel="stylesheet" type="text/css">' + "\n");
		if(!window.jQuery) {
			document.write('<scr'+'ipt language="javascript" type="text/javascript" src="'+jquery_dir+'/jquery.js?' + jsani_ver + '"></script>' + "\n");
		}
		document.write('<scr'+'ipt language="javascript" type="text/javascript" src="'+jsani_dir+'/jsani.js?' + jsani_ver + '"></script>' + "\n");
	}
	
	
	// based on http://stackoverflow.com/questions/3820381/need-a-basename-function-in-javascript
	function baseName(str) {
		var base = new String(str).substring(str.lastIndexOf('/') + 1); 
		if(base.lastIndexOf(".") != -1)       
			base = base.substring(0, base.lastIndexOf("."));
		return base;
	}
	
	// based on http://planetozh.com/blog/2008/04/javascript-basename-and-dirname/
	function dirname(path) {
		return path.replace(/\\/g,'/').replace(/\/[^\/]*$/, '');
	}
	
})();

