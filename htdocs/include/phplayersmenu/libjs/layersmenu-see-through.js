// PHP Layers Menu 3.1.0 (C) 2001-2003 Marco Pratesi (marco at telug dot it)

function scanChildren(element) {
	var counter = element.childNodes.length;
        for (var i=0; i<counter; i++) {
                foobar = element.childNodes.item(i);
		if (	( Konqueror &&
			 (  foobar.nodeName == "INPUT" || foobar.nodeName == "input"
			 || foobar.nodeName == "SELECT" || foobar.nodeName == "select"
			 || foobar.nodeName == "TEXTAREA" || foobar.nodeName == "textarea"
			 )
			)
			|| 
			( IE &&
			 ( foobar.nodeName == "SELECT" || foobar.nodeName == "select" )
			)
		) {
			toBeHidden[toBeHidden.length] = foobar;
		}
                if (foobar.childNodes.length > 0) {
                        scanChildren(foobar);
                }
        }
}

//document.write("<br />\nSCANNING STARTED<br />\n");
//scanChildren(document.getElementsByTagName("BODY").item(0));
if ((Konqueror || IE5) && document.getElementById("phplmseethrough")) {
	scanChildren(document.getElementById("phplmseethrough"));
}
//document.write("<br />\nSCANNING COMPLETED<br />\n");

if ((Konqueror && !Konqueror22) || IE5) {
	for (i=0; i<toBeHidden.length; i++) {
		object = toBeHidden[i];
		toBeHiddenLeft[i] = object.offsetLeft;
		while (object.tagName != "BODY" && object.offsetParent) {
			object = object.offsetParent;
			toBeHiddenLeft[i] += object.offsetLeft;
		}
		object = toBeHidden[i];
		toBeHiddenTop[i] = object.offsetTop;
		while (object.tagName != "BODY" && object.offsetParent) {
			object = object.offsetParent;
			toBeHiddenTop[i] += object.offsetTop;
		}
	}
}

