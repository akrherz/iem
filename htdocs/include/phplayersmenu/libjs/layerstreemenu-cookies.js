// PHP Layers Menu 3.1.0 (C) 2001-2003 Marco Pratesi (marco at telug dot it)

function setLMCookie(name, value) {
	document.cookie = name + "=" + value;
}

function getLMCookie(name) {
	foobar = document.cookie.split(name + "=");
	if (foobar.length < 2) {
		return null;
	}
	tempString = foobar[1];
	if (tempString.indexOf(";") == -1) {
		return tempString;
	}
	yafoobar = tempString.split(";");
	return yafoobar[0];
}

function parseExpandString() {
	expandString = getLMCookie("expand");
	expand = new Array();
	if (expandString) {
		expanded = expandString.split("|");
		for (i=0; i<expanded.length-1; i++) {
			expand[expanded[i]] = 1;
		}
	}
}

function parseCollapseString() {
	collapseString = getLMCookie("collapse");
	collapse = new Array();
	if (collapseString) {
		collapsed = collapseString.split("|");
		for (i=0; i<collapsed.length-1; i++) {
			collapse[collapsed[i]] = 1;
		}
	}
}

parseExpandString();
parseCollapseString();

function saveExpandString() {
	expandString = "";
	for (i=0; i<expand.length; i++) {
		if (expand[i] == 1) {
			expandString += i + "|";
		}
	}
	setLMCookie("expand", expandString);
}

function saveCollapseString() {
	collapseString = "";
	for (i=0; i<collapse.length; i++) {
		if (collapse[i] == 1) {
			collapseString += i + "|";
		}
	}
	setLMCookie("collapse", collapseString);
}

