Summary: Iowa Environmental Mesonet Requirements Metarpm
Name: iem-requirements
Version: 1
BuildArch: noarch
Release: 39%{?dist}
License: distributable

# straight forward OS requirements
Requires: httpd
Requires: php
Requires: mod_ssl
Requires: fribidi
Requires: php-pgsql
Requires: php-ZendFramework
Requires: proj-epsg
Requires: ImageMagick
Requires: gdal
Requires: tcsh
Requires: gifsicle
Requires: bc
Requires: tmpwatch
Requires: mailx
Requires: fcgi
Requires: libpng12
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
Requires: liberation-serif-fonts
Requires: liberation-sans-fonts
Requires: liberation-fonts-common
Requires: liberation-mono-fonts
Requires: php-gd
Requires: dstat
Requires: zip
Requires: php-devel
Requires: gd
Requires: ntp
Requires: net-tools
Requires: mod_auth_openidc
Requires: perl-Monitoring-Plugin
Requires: perl-Data-Dumper

# needed for pip provided rrdtool in miniconda
Requires: rrdtool

# locally built and packaged with a small patch applied for logging
Requires: mod_wsgi


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
* Mon Mar 20 2017 daryl herzmann <akrherz@iastate.edu>
- Dumped all pure-python stuff as we are now in the conda game

* Fri Mar 17 2017 daryl herzmann <akrherz@iastate.edu>
- Moving toward pip based python requirements

* Tue Feb 14 2017 daryl herzmann <akrherz@iastate.edu>
- Added python2-attrs as a requirement for updated Twisted

* Wed Jan 18 2017 daryl herzmann <akrherz@iastate.edu>
- Added functools32 and cycler for matplotlib 2.0.0

* Fri Sep  2 2016 daryl herzmann <akrherz@iastate.edu>
- Added requirements for updated nagios tcptraffic plugin

* Thu Aug  4 2016 daryl herzmann <akrherz@iastate.edu>
- Added MetPy and Pint

* Wed Jun 15 2016 daryl herzmann <akrherz@iastate.edu>
- Added tqdm

* Thu Apr 14 2016 daryl herzmann <akrherz@iastate.edu>
- Added characteristic for service_identity

* Mon Apr 11 2016 daryl herzmann <akrherz@iastate.edu>
- Added dropbox for yield project

* Wed Mar  9 2016 daryl herzmann <akrherz@iastate.edu>
- Add mod_auth_openidc

* Thu Feb 25 2016 daryl herzmann <akrherz@iastate.edu>
- Need pyasn1-modules

* Tue Feb 23 2016 daryl herzmann <akrherz@iastate.edu>
- Need rsa package for updated oauth2client

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
