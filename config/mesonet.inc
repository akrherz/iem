#
# Apache vhost configuration for IEM
# the master file for this is on github, so edit there!
# I have this set in dev: SetEnv PYTHONPATH "/home/akrherz/projects/pyIEM/"

  # Use a daily deadicated log file, this avoids server reloads every day
  # which are not much fun when servicing a 1,000 req/sec
  CustomLog "|/usr/sbin/rotatelogs /mesonet/www/logs/iem-%Y%m%d 86400" combined

  ServerName mesonet.agron.iastate.edu
  ServerAlias www.mesonet.agron.iastate.edu
  ServerAlias mesonet1.agron.iastate.edu
  ServerAlias mesonet2.agron.iastate.edu
  ServerAlias mesonet3.agron.iastate.edu
  ServerAlias iem.local
  ServerAdmin akrherz@iastate.edu
  DocumentRoot /mesonet/www/apps/iemwebsite/htdocs

  WSGIScriptAlias /cache/tile.py /mesonet/www/apps/iemwebsite/htdocs/cache/tile.wsgi
  WSGIScriptAlias /cache/c.py /mesonet/www/apps/iemwebsite/htdocs/cache/tile.wsgi

  WSGIScriptAlias /c/tile.py /mesonet/www/apps/iemwebsite/htdocs/c/tile.wsgi
  WSGIScriptAlias /c/c.py /mesonet/www/apps/iemwebsite/htdocs/c/tile.wsgi

  # http://enable-cors.org/server_apache.html
  Header set Access-Control-Allow-Origin "*"

  <Directory "/mesonet/www/apps/iemwebsite/htdocs">
    # Need FollowSymLinks for mod_rewrite to work!
    Options Indexes FollowSymLinks
    AllowOverride All
    Order allow,deny
    Allow from all
  </Directory>

  <Directory "/mesonet/ARCHIVE">
    Options Indexes FollowSymLinks
    AllowOverride All
    Order allow,deny
    Allow from all
  </Directory>

  <Directory "/mnt/mtarchive2">
    Options Indexes
    AllowOverride None
    Order allow,deny
    Allow from all
  </Directory>

  <Directory "/mesonet/share">
    Options Indexes FollowSymLinks
    AllowOverride All
    Order allow,deny
    Allow from all
  </Directory>

  ScriptAlias /cgi-bin/ "/mesonet/www/apps/iemwebsite/cgi-bin/"
  ScriptAlias /servlet/ "/mesonet/www/apps/iemwebsite/cgi-bin/"
  <Directory "/mesonet/www/apps/iemwebsite/cgi-bin">
    AllowOverride All
    Options FollowSymLinks
    Order allow,deny
    Allow from all
  </Directory>

  Redirect /data/mwcomp.phtml http://mesonet.agron.iastate.edu/current/mwcomp.phtml
  Redirect /RWIS/current.php http://mesonet.agron.iastate.edu/RWIS/current.phtml
  Redirect /schoolnet/current.php http://mesonet.agron.iastate.edu/schoolnet/current.phtml
  Redirect /RWIS/currentSF.php http://mesonet.agron.iastate.edu/RWIS/currentSF.phtml
  Redirect /my/current.php http://mesonet.agron.iastate.edu/my/current.phtml
  Redirect http://www.mesonet.agron.iastate.edu http://mesonet.agron.iastate.edu
  Redirect permanent /archive/nexrad http://mesonet-longterm.agron.iastate.edu/archive/nexrad
  Redirect permanent /archive/gempak http://mesonet-longterm.agron.iastate.edu/archive/gempak
  Redirect permanent /archive/raw http://mesonet-longterm.agron.iastate.edu/archive/raw
  Redirect permanent /data/nexrd2/raw http://nomads.ncep.noaa.gov/pub/data/nccf/radar/nexrad_level2

  <LocationMatch "camera">
    ErrorDocument 404 /images/missing-320x240.jpg
  </LocationMatch>

  Alias /usage "/mesonet/share/usage/mesonet.agron.iastate.edu/"
  <Directory "/mesonet/share/usage/mesonet.agron.iastate.edu/">
    Options Indexes MultiViews
    AllowOverride None
    Order allow,deny
    Allow from all
  </Directory>

  Alias /agclimate/usage "/mesonet/share/usage/agclimate/"
  <Directory "/mesonet/share/usage/agclimate/">
    Options Indexes MultiViews
    AllowOverride None
    Order allow,deny
    Allow from all
  </Directory>

  RewriteEngine On
  RewriteRule ^/index.php$ / [R]
  RewriteRule /data/gis/images/unproj/(.*)$ /data/gis/images/4326/$1 [L,R]
  RewriteRule /data/gis/shape/unproj/(.*)$ /data/gis/shape/4326/$1 [L,R]
  RewriteRule ^p.phppid=([^\.]+) p.php?pid=$1 [L]
  RewriteRule /river/wfo.phtml /river/index.php

  Alias "/onsite/features/2002" "/mesonet/share/features/2002"
  Alias "/onsite/features/2003" "/mesonet/share/features/2003"
  Alias "/onsite/features/2004" "/mesonet/share/features/2004"
  Alias "/onsite/features/2005" "/mesonet/share/features/2005"
  Alias "/onsite/features/2006" "/mesonet/share/features/2006"
  Alias "/onsite/features/2007" "/mesonet/share/features/2007"
  Alias "/onsite/features/2008" "/mesonet/share/features/2008"
  Alias "/onsite/features/2009" "/mesonet/share/features/2009"
  Alias "/onsite/features/2010" "/mesonet/share/features/2010"
  Alias "/onsite/features/2011" "/mesonet/share/features/2011"
  Alias "/onsite/features/2012" "/mesonet/share/features/2012"
  Alias "/onsite/features/2013" "/mesonet/share/features/2013"
  Alias "/onsite/features/2014" "/mesonet/share/features/2014"
  Alias "/onsite/features/2015" "/mesonet/share/features/2015"
  Alias "/onsite/features/2016" "/mesonet/share/features/2016"
  
  Alias "/onsite/lapses" "/mesonet/share/lapses"
  Alias "/onsite/windrose" "/mesonet/share/windrose"
  Alias "/onsite/iemre" "/mesonet/share/iemre"
  Alias "/present" "/mesonet/share/present"
  Alias "/cases" "/mesonet/share/cases"
  Alias "/GIS/data/gis" "/mesonet/data/gis"
  Alias "/archive/data" "/mesonet/ARCHIVE/data"
  Alias "/archive/awos" "/mesonet/ARCHIVE/awos"
  Alias "/archive/raw" "/mesonet/ARCHIVE/raw"
  Alias "/archive/rer" "/mesonet/ARCHIVE/rer"
  Alias "/pickup"    "/mesonet/share/pickup"
  
  <Directory "/mesonet/share/pickup">
    AllowOverride All
    Options FollowSymLinks Indexes MultiViews
    Order allow,deny
    Allow from all
  </Directory>
  <Directory "/mesonet/share/features">
    AllowOverride All
    Options FollowSymLinks Indexes MultiViews
    Order allow,deny
    Allow from all
  </Directory>
  
  Alias "/m/img"     "/mesonet/share/iemmaps"
  Alias "/sites/pics"     "/mesonet/share/pics"
  Alias "/climodat/everything.zip" "/mesonet/share/climodat/everything.zip"
  Alias "/climodat/reports" "/mesonet/share/climodat/reports"
  Alias "/climodat/ks" "/mesonet/share/climodat/ks"
  # Order matters here!
  RewriteRule ^/iembot(.*)$ http://weather.im/iembot$1 [R=permanent]
 
  Alias /data "/home/ldm/data"
  <Directory "/home/ldm/data">
    Options Indexes MultiViews
    AllowOverride None
    Order allow,deny
    Allow from all
  </Directory>

  <Directory "/mnt/a4">
    Options Indexes MultiViews
    AllowOverride None
    Order allow,deny
    Allow from all
  </Directory>

  # Trailing slashes are very, very important!
  ProxyPass /arcgis	http://iem-arcgis:6080/arcgis

  ErrorDocument 404 /error404.php
  