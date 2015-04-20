Summary: Iowa Environmental Mesonet Requirements Metarpm
Name: iem-requirements
Version: 1
BuildArch: noarch
Release: 8%{?dist}
License: distributable

Requires: pyIEM
Requires: mod_wsgi
Requires: python-paste
Requires: openpyxl
Requires: jdcal
Requires: python-lxml
Requires: Shapely
Requires: Twisted
Requires: PyRSS2Gen
Requires: twittytwister
Requires: python-oauth
Requires: python-simplejson
Requires: httpd
Requires: php
Requires: mod_ssl
#Requires: odfpy
#Requires: unoconv
Requires: fribidi
Requires: php-pgsql
Requires: php-ZendFramework
Requires: proj-epsg
Requires: python-zope-interface
Requires: nwnserver
Requires: pyproj
Requires: numpy
Requires: python-pillow
Requires: ImageMagick
Requires: gdal
Requires: pygrib
Requires: gdal-python
Requires: python-matplotlib
Requires: python-basemap
Requires: pyshapelib
# remove this at some point :(
Requires: egenix-mx-base
Requires: netcdf4-python
Requires: scipy
Requires: pandas
# remove this at some point
Requires: tcsh
Requires: gifsicle
Requires: PyGreSQL
Requires: bc
Requires: tmpwatch
Requires: gdata
Requires: pyephem
Requires: mailx
Requires: xlwt
Requires: xlrd
Requires: fcgi
Requires: libpng12

%description
A virtual package which makes sure that various requirements are installed
to make sure the IEM code runs on a system it is deployed on.

%prep

%build

%clean 

%install

%post

%files 


%changelog
* Mon Apr 20 2015 daryl herzmann <ahrherz@iastate.edu>
- Adding requirements found for fastcgi/mapserver

* Wed Apr  1 2015 daryl herzmann <ahrherz@iastate.edu>
- Adding python excel library needed for some scripts

* Thu Mar 19 2015 daryl herzmann <akrherz@iastate.edu>
- Add requirements found by moving scripts to iem12

* Wed Mar 18 2015 daryl herzmann <akrherz@iastate.edu>
- Add webserver requirements

* Tue Mar 17 2015 daryl herzmann <akrherz@iastate.edu>
- Add more requirements to run iembot

* Thu Dec 4 2014 daryl herzmann <akrherz@iastate.edu>
- Add requirements to run mod_wsgi applications, ie TileCache

* Fri Jun 27 2014 daryl herzmann <akrherz@iastate.edu>
- initial release