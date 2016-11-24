#
# Apache vhost configuration for IEM
# the master file for this is on github, so edit there!
# I have this set in dev: SetEnv PYTHONPATH "/home/akrherz/projects/pyIEM/"

  ServerName mesonet.agron.iastate.edu
  ServerAlias www.mesonet.agron.iastate.edu
  ServerAlias mesonet1.agron.iastate.edu
  ServerAlias mesonet2.agron.iastate.edu
  ServerAlias mesonet3.agron.iastate.edu
  ServerAlias iem.local
  ServerAdmin akrherz@iastate.edu
  DocumentRoot /opt/iem/htdocs

  WSGIScriptAlias /cache/tile.py /opt/iem/htdocs/cache/tile.wsgi
  WSGIScriptAlias /cache/c.py /opt/iem/htdocs/cache/tile.wsgi

  WSGIScriptAlias /c/tile.py /opt/iem/htdocs/c/tile.wsgi
  WSGIScriptAlias /c/c.py /opt/iem/htdocs/c/tile.wsgi

  # http://enable-cors.org/server_apache.html
  Header set Access-Control-Allow-Origin "*"

  <Directory "/opt/iem/htdocs">
    # Need FollowSymLinks for mod_rewrite to work!
    Options Indexes FollowSymLinks
    AllowOverride None
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

  ScriptAlias /cgi-bin/ "/opt/iem/cgi-bin/"
  ScriptAlias /servlet/ "/opt/iem/cgi-bin/"
  <Directory "/opt/iem/cgi-bin">
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
  # Useful for debugging
  # LogLevel alert rewrite:trace3
  RewriteRule ^/index.php$ / [R]
  RewriteRule ^/p.phppid=([^\.]+) /p.php?pid=$1 [L]
  RewriteRule ^/iembot(.*)$ https://weather.im/iembot$1 [R=permanent]
  <Location "/river">
	 RewriteRule wfo.phtml /river/index.php
  </Location>

  Alias /data "/home/ldm/data"
  <Directory "/home/ldm/data">
    Options Indexes MultiViews FollowSymLinks
    AllowOverride None
    Order allow,deny
    Allow from all
	Redirect permanent /data/gis/images/unproj /data/gis/images/4326
  	Redirect permanent /data/gis/shape/unproj /data/gis/shape/4326
  </Directory>
  

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
 

  <Directory "/mnt/a4">
    Options Indexes MultiViews
    AllowOverride None
    Order allow,deny
    Allow from all
  </Directory>

Alias /tmp /var/webtmp
<Directory "/var/webtmp">
  AllowOverride None
</Directory>


  # Trailing slashes are very, very important!
  ProxyPass /arcgis	http://iem-arcgis:6080/arcgis

  ErrorDocument 404 /error404.php

  <Directory "/opt/iem/cgi-bin/wms/nexrad">
    RewriteEngine On
    RewriteRule n0r.cgi?$ /cgi-bin/mapserv/mapserv.fcgi?map=/opt/iem/data/wms/nexrad/n0r.map& [QSA,L]
    RewriteRule n0q.cgi?$ /cgi-bin/mapserv/mapserv.fcgi?map=/opt/iem/data/wms/nexrad/n0q.map& [QSA,L]
  </Directory>

  <Location "/DCP">
    AddHandler cgi-script .py
    Options +ExecCGI

    RewriteEngine On
    RewriteRule ahpsxml2wxc/([0-9A-Z]{3,5}).txt$ ahpsxml2wxc.py?nwsli=$1
  </Location>
  
  <Location "/GIS/apps/iem">
    AddHandler cgi-script .py
    Options +ExecCGI

    RewriteRule snowfall_oa.png snowfall_oa.py [QSA]
  </Location>
  <Location "/GIS">
    RewriteRule vtec_(.*).png radmap.php?layers[]=places&layers[]=nexrad&layers[]=cities&layers[]=interstates&layers[]=uscounties&vtec=$1&width=797&height=400
  </Location>
  
  <Location "/agclimate">
  RewriteEngine On
# Lots of old links out there to bad URIs
RewriteRule index\.(html|pl|php)$ /agclimate/ [R]

Redirect /agclimate/daily-pics https://mesonet.agron.iastate.edu/agclimate/daily_pics
Redirect /agclimate/daily_pics https://mesonet.agron.iastate.edu/data/agclimate
Redirect /agclimate/info.txt https://mesonet.agron.iastate.edu/agclimate/info.phtml

AddHandler cgi-script .py
Options +ExecCGI

# 
RewriteRule smplot/([0-9]{1,12})/(.*).png$ isusm.py?t=$1&v=$2
RewriteRule isusm.csv nmp_csv.py
  </Location>
  <Location "/c">
	#AddHandler python-program .py
#PythonPath "sys.path + ['/opt/iem/include/python/']"
#PythonInterpPerDirectory On
#PythonHandler TileCache.Service
#PythonOption TileCacheConfig /opt/iem/htdocs/c/tilecache.cfg
  
# http://lists.osgeo.org/pipermail/tilecache/2010-June/002453.html
ExpiresActive On
ExpiresDefault "access plus 14 days"
	
  </Location>
  
<Location "/cache">
#AddHandler python-program .py
#PythonPath "sys.path + ['/opt/iem/include/python/']"
#PythonInterpPerDirectory On
#PythonHandler TileCache.Service
#PythonOption TileCacheConfig /opt/iem/htdocs/cache/tilecache.cfg

#WSGIScriptAlias /cache/tile.py /opt/iem/include/python/TileCache/Service.py

# http://lists.osgeo.org/pipermail/tilecache/2010-June/002453.html
ExpiresActive On
ExpiresDefault "access plus 5 minutes"
</Location>

<Location "/api">
# http://enable-cors.org/server_apache.html
Header set Access-Control-Allow-Origin "*"

AddHandler cgi-script .py
Options +ExecCGI

RewriteRule sql/database/([a-z]+)$ sql.py?database=$1 [QSA]
RewriteRule nwstext/([0-9A-Z\-]{31}).txt$ nwstext.py?p=$1 [QSA]
</Location>

<Location "/content">
RewriteRule pil_([A-Z0-9]{3,6}).png$ pil.php?pil=$1
</Location>

<Location "/cscap">
Redirect permanent / https://datateam.agron.iastate.edu/
</Location>

<Location "/css">
# http://lists.osgeo.org/pipermail/tilecache/2010-June/002453.html
ExpiresActive On
ExpiresDefault "access plus 365 days"
</Location>

<Location "/frost">
AddHandler cgi-script .py
Options +ExecCGI

RewriteRule frost_ts_([a-z]+)_([\-\.0-9]+)_([\.0-9]+).png$ frost_ts.py?lon=$2&lat=$3&model=$1
</Location>

<Location "/geojson">
AddHandler cgi-script .py
Options +ExecCGI

RewriteRule sbw.geojson(.*) sbw.py$1 [QSA]
RewriteRule sps.geojson(.*) sps.py$1 [QSA]
RewriteRule winter_roads.geojson(.*) winter_roads.py$1 [QSA]
RewriteRule networks.geojson(.*) networks.py$1 [QSA]
RewriteRule nexrad_attr.geojson(.*) nexrad_attr.py$1 [QSA]
</Location>

<Location "/iemre">
# http://enable-cors.org/server_apache.html
Header set Access-Control-Allow-Origin "*"

AddHandler cgi-script .py
Options +ExecCGI

RewriteRule daily/([0-9\-]+)/([0-9\.]+)/([0-9\.\-]+)/(json) daily.py?date=$1&lat=$2&lon=$3&format=$4
RewriteRule multiday/([0-9\-]+)/([0-9\-]+)/([0-9\.]+)/([0-9\.\-]+)/(json) multiday.py?date1=$1&date2=$2&lat=$3&lon=$4&format=$5
RewriteRule cum/([0-9\-]+)/([0-9\-]+)/(shp) cum.py?date0=$1&date1=$2&format=$3&base=50&ceil=86
RewriteRule cumcounty/([0-9]+)/([0-9\-]+)/([0-9\-]+)/([0-9]+)/([0-9]+)/(json) cum.py?county=$1&date0=$2&date1=$3&format=$6&base=$4&ceil=$5
RewriteRule map/daily/([0-9]{8})_([a-z0-9_]+).png map.py?type=daily&date=$1&plot=$2
</Location>

<Location "/json">
AddHandler cgi-script .py
Options +ExecCGI

RewriteRule json/radar$ radar.py
RewriteRule tms.json tms.py [QSA]
RewriteRule qpe/([0-9\.\-]+)/([0-9\.\-]+)/(json) qpe.py?lat=$2&lon=$1&format=$3
RewriteRule raob/([0-9]{12})/([A-Z0-9]{3,4})$ raob.py?ts=$1&station=$2 [QSA]
RewriteRule prism/([0-9\.\-]+)/([0-9\.\-]+)/([0-9\.\-]+)$ prism.py?lon=$1&lat=$2&valid=$3 [QSA]
</Location>

<Location "/kml">
AddHandler cgi-script .py
Options +ExecCGI

RewriteRule roadcond.kml roadcond.php
</Location>

<Location "/lsr">
RewriteEngine On
RewriteRule #(.*)$ /lsr/#$1 [R=301,NE]
</Location>

<Location "/mec">
AuthUserFile /opt/iem/config/admin.users
AuthGroupFile /dev/null
AuthName Administrative
AuthType Basic

order deny,allow
require user mec

AddHandler cgi-script .py
Options +ExecCGI

RewriteRule i/([A-Za-z\-_0-9]*).png$ image.php?i=$1
RewriteRule map_power_([0-9]*)_(yaw2?).png$ map_power.py?ts=$1&yawsource=$2
RewriteRule turbine_ts_([0-9]*)_(.*).png$ turbine_ts.py?date=$1&turbinename=$2
</Location>

<Location "/nws">
AddHandler cgi-script .py
Options +ExecCGI

RewriteRule days_since_([A-Z][A-Z])_([A-Z]).png /plotting/auto/plot/92/phenomena:$1::significance:$2::dpi:100.png
</Location>

<Location "/onsite">
AddHandler cgi-script .py
Options +ExecCGI

  RewriteRule onsite/features/tags/([^\.]+)\.html features/tags/index.php?tag=$1 [L]
RewriteRule vote/(good|bad|abstain).json$ features/vote.py?vote=$1
RewriteRule vote.json$ features/vote.py
</Location>

<Location "/other">
AddHandler cgi-script .py
Options +ExecCGI

RewriteRule kymn.phtml current.phtml?network=KYMN
RewriteRule wtm.phtml current.phtml?network=WTM
</Location>

<Location "/plotting/auto">
AddHandler cgi-script .py
Options +ExecCGI

RewriteRule plot/([0-9]{1,12})/(.*).png$ plotfe.py?p=$1&q=$2&fmt=png
RewriteRule plot/([0-9]{1,12})/(.*).csv$ plotfe.py?p=$1&q=$2&fmt=csv
RewriteRule plot/([0-9]{1,12})/(.*).txt$ plotfe.py?p=$1&q=$2&fmt=txt
RewriteRule plot/([0-9]{1,12})/(.*).xlsx$ plotfe.py?p=$1&q=$2&fmt=xlsx
RewriteRule plot/([0-9]{1,12})/(.*).js$ plotfe.py?p=$1&q=$2&fmt=js
RewriteRule plot/([0-9]{1,12})/(.*).pdf$ plotfe.py?p=$1&q=$2&fmt=pdf
RewriteRule plot/([0-9]{1,12})/(.*).svg$ plotfe.py?p=$1&q=$2&fmt=svg
RewriteRule meta/([0-9]{1,12}).json$ plotmeta.py?p=$1
</Location>

<Location "/rainfall">
AddHandler cgi-script .py
Options +ExecCGI
</Location>

<Location "/request">
AddHandler cgi-script .py
Options +ExecCGI
RewriteRule maxcsv/(.*).txt$ maxcsv.py?q=$1

RewriteRule grx/iadot_trucks.txt grx/iadot_trucks.py
# Legacy link was removed 5 Jan 2015
RewriteRule grx/idot_trucks.php grx/iadot_trucks.py

# .php was legacy stuff, lets not break old paths
RewriteRule grx/l3attr.(php|txt) grx/l3attr.py [QSA]

RewriteRule wxc/idot_trucks.txt wxc/idot_trucks.py

</Location>

<Location "/roads">
RewriteRule kcau.jpg kcau.php
RewriteRule ktiv.jpg ktiv.php
RewriteRule kwwl.jpg kwwl.php?v2
</Location>

<Location "/squaw/scenario">
AuthUserFile /home/akrherz/projects/squaw/security/htpasswd
AuthGroupFile /dev/null
AuthName Administrative
AuthType Basic

<LIMIT GET>
order deny,allow
require user ames
</LIMIT>
</Location>

<Location "/squaw/storm">
AuthUserFile /opt/iem/config/admin.users
AuthGroupFile /dev/null
AuthName Administrative
AuthType Basic

<LIMIT GET>
order deny,allow
require user ames
require user iowastate
</LIMIT>
</Location>

<Location "/vtec">
RewriteEngine On
RewriteRule ([^\.]+)\.html index.php?vtec=$1 [L]
RewriteRule f/(.*)$ f.php?vtec=$1 [L]
</Location>

<Location "/fonts">
# http://lists.osgeo.org/pipermail/tilecache/2010-June/002453.html
ExpiresActive On
ExpiresDefault "access plus 365 days"
</Location>

<Location "/metadata/xml">
AddHandler cgi-script .py
Options +ExecCGI

RewriteRule pl_(.*)_(.*).xml pl.py?network=$1&station=$2 [QSA]
RewriteRule sd_(.*)_(.*).xml sd.py?network=$1&station=$2 [QSA]

</Location>

<Location "/scada">
AuthUserFile /opt/iem/config/admin.users
AuthGroupFile /dev/null
AuthName Administrative
AuthType Basic

order deny,allow
require user mec

AddHandler cgi-script .py
Options +ExecCGI

RewriteRule i/([A-Za-z\-_0-9]*).png$ image.php?i=$1
RewriteRule map_power_([0-9]*).png$ map_power.py?ts=$1
RewriteRule turbine_ts_([0-9]*)_(.*).png$ turbine_ts.py?date=$1&turbinename=$2
</Location>
  