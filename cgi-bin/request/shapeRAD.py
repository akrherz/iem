#!/usr/bin/python
# Script to place converted shape files in a dir for 
# conversion on the Windblows box
# Daryl Herzmann 19 Feb 2002

import cgi

def Main():
	form = cgi.FormContent()
	site = form["site"][0]

Main()
