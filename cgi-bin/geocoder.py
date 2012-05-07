#!/usr/bin/env python
"""
 Geocoder used by:
  - IEM Rainfall App
$Id: $:
"""

import xmlrpclib, cgi
p = xmlrpclib.ServerProxy('http://rpc.geocoder.us/service/xmlrpc')


def main():
	form = cgi.FieldStorage()
	res = []
	if (form.has_key("address")):
		res = p.geocode( form["address"].value )
	if (form.has_key("street") and form.has_key("city") ):
		address = "%s, %s" % (form["street"].value, form["city"].value)
		res = p.geocode( address )
	if (len(res) > 0 and res[0].has_key("lat") ):
		print "%s,%s" % (res[0]["lat"], res[0]["long"])
	else:
		print "ERROR"

print 'Content-type: text/plain \n'
try:
	main()
except:
	print "ERROR"
	
