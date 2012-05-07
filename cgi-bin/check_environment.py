#!/usr/bin/env python
"""
Check the server environment our python code needs to run

$Id: $:
"""
# custom imports
import sys
sys.path.insert(0, '/mesonet/www/apps/iemwebsite/scripts/lib')
import wellknowntext
import iemdb

# python imports
import zipfile
import os
import shutil
import cgi
import psycopg2
import psycopg2.extras

# RHN channel provided packages
import shapelib
import dbflib
import mx.DateTime


print 'Content-type: text/plain\n'
print 'OK'