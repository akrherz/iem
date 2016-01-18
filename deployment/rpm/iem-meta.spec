Summary: Iowa Environmental Mesonet Requirements Metarpm
Name: iem-requirements
Version: 1
BuildArch: noarch
Release: 26%{?dist}
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
Requires: pyparsing
Requires: python-basemap
Requires: pyshapelib
# remove this at some point :(
Requires: egenix-mx-base
Requires: netcdf4-python
Requires: scipy
# EPEL
Requires: python-pandas
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
Requires: metar
Requires: python-nose
Requires: python-six
Requires: oauth2client
Requires: python-httplib2
Requires: google-api-python-client
Requires: uritemplate
Requires: mod_fcgid
Requires: lftp
Requires: nfs-utils
Requires: make
Requires: gcc
Requires: perl
Requires: zlib-devel
Requires: libxml2-devel
Requires: git
Requires: sysstat
Requires: unzip
Requires: keepalived
Requires: links
Requires: wget
Requires: nrpe
Requires: nagios-plugins-disk
Requires: perl-Nagios-Plugin
Requires: perl-Readonly
Requires: php-pecl-memcache
Requires: python-memcached
Requires: liberation-serif-fonts
Requires: liberation-sans-fonts
Requires: liberation-fonts-common
Requires: liberation-mono-fonts
Requires: php-gd
Requires: dstat
Requires: pyshp
Requires: zip
Requires: php-devel
Requires: pyLDM
Requires: gd
Requires: ntp
Requires: jenks
Requires: windrose
Requires: net-tools
Requires: service_identity
Requires: XlsxWriter
Requires: python-requests
Requires: requests-toolbelt
Requires: smartsheet-python-sdk
Requires: certifi
Requires: Fiona
Requires: geopandas
Requires: rasterio
Requires: python-enum34
Requires: affine

%description
A virtual package which makes sure that various requirements are installed
to make sure the IEM code runs on a system it is deployed on.

%prep

%build

%clean 

%install

%post
# pecl install dbase
# echo "extension=dbase.so" > /etc/php.d/dbase.ini

%files 


%changelog
* Mon Jan 18 2016 daryl herzmann <akrherz@iastate.edu>
- Added GeoPandas requirement

* Thu Jan 14 2016 daryl herzmann <akrherz@iastate.edu>
- Added Smartsheet SDK and requirements

* Mon Oct 19 2015 daryl herzmann <akrherz@iastate.edu>
- Added XlsxWriter for usage by pandas

* Wed Oct 14 2015 daryl herzmann <akrherz@iastate.edu>
- Added pyparsing as matplotlib needs it

* Mon Sep 14 2015 daryl herzmann <akrherz@iastate.edu>
- Added support lib for Twisted, service_identity

* Fri Aug  7 2015 daryl herzmann <akrherz@iastate.edu>
- Added net-tools so that we have ifconfig

* Mon Jul 20 2015 daryl herzmann <akrherz@iastate.edu>
- Take pandas from EPEL and not local version

* Thu Jul 16 2015 daryl herzmann <akrherz@iastate.edu>
- Add windrose package requirements

* Tue Jul  7 2015 daryl herzmann <akrherz@iastate.edu>
- Add requirement for jenks python package

* Tue Jun 30 2015 daryl herzmann <akrherz@iastate.edu>
- Add ntp

* Fri Jun 12 2015 daryl herzmann <akrherz@iastate.edu>
- Migrating iem30 to rhel7 found a missing gd lib

* Tue Jun  2 2015 daryl herzmann <akrherz@iastate.edu>
- Add pyshp, zip as a requirement

* Mon Jun  1 2015 daryl herzmann <akrherz@iastate.edu>
- Add requirements found with iemvs migration

* Wed May 27 2015 daryl herzmann <akrherz@iastate.edu>
- Add requirements found with iem50 migration

* Thu Apr 30 2015 daryl herzmann <akrherz@iastate.edu>
- Add mod_fcgid in as a requirement

* Mon Apr 27 2015 daryl herzmann <akrherz@iastate.edu>
- Google Openauth requirements added

* Thu Apr 23 2015 daryl herzmann <akrherz@iastate.edu>
- Adding requirements found for python metar

* Mon Apr 20 2015 daryl herzmann <akrherz@iastate.edu>
- Adding requirements found for fastcgi/mapserver

* Wed Apr  1 2015 daryl herzmann <akrherz@iastate.edu>
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
