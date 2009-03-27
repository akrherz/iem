#!/mesonet/python-2.4/bin/python
# Need something for a Camera Interface

import cgi
from pyIEM import cameras

def printHeader():
	print """
<html>
<head>
	<title>KCCI WebCams</title>
</head>
<body>"""

def printForm(selcam):
	print '<form method="GET" action="camera.py">'
	print "<b>Select Camera:</b>"
	print '<select name="id">'
	k = cameras.cams.keys()
	k.sort()
	for cam in k:
		print '<option value="'+ cam +'" ',
		if (cam == selcam): print " SELECTED ",
		print '>[%s] %s' % (cam, cameras.cams[cam]['name'])
	print '</select><input type="submit"></form>'

def printInterface(cam):
	print "<applet archive=\"LiveApplet.zip\" codebase=\"http://%(ip)s:%(port)s/-wvdoc-01-/LiveApplet/\" \
 code=\"LiveApplet.class\" width=450 height=380>\
<param name=cabbase	value=\"LiveApplet.cab\">\
<param name=video_width	value=\"320\">\
<param name=url		value=\"http://%(ip)s:%(port)s/\">\
<param name=locale	value=\"english\">\
</applet>\
<p><a href=\"http://%(ip)s/admin/\">Admin Interface</a>\
</body>\
</html>" % cameras.cams[cam]

def main():
	print 'Content-type: text/html \n\n'

	form = cgi.FormContent()
	cam = 'SMAI4'
	if (form.has_key("id")):
		cam = form["id"][0]

	printHeader()
	printForm(cam)
	if (cameras.cams.has_key(cam)):
		printInterface(cam)


main()
