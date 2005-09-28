#!/usr/bin/python
# 		add.py
# Admin script that modifies a product information DB
# Daryl Herzmann 20 Aug 2001

import pg, cgi

mydb = pg.connect("admin")

def Main():
	form = cgi.FormContent()
	filename = form["filename"][0]



Main()
