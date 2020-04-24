#
# Apache vhost configuration for IEM
# the master file for this is on github, so edit there!
# I have this set in dev: SetEnv PYTHONPATH "/home/akrherz/projects/pyIEM/src"

  ServerName mesonet.agron.iastate.edu
  ServerAlias www.mesonet.agron.iastate.edu
  ServerAlias mesonet1.agron.iastate.edu
  ServerAlias mesonet2.agron.iastate.edu
  ServerAlias mesonet3.agron.iastate.edu
  ServerAlias iem.local
  ServerAdmin akrherz@iastate.edu
  DocumentRoot /opt/iem/htdocs

  # http://enable-cors.org/server_apache.html
  Header set Access-Control-Allow-Origin "*"

  # RewriteEngine is not enabled for vhosts by default
  RewriteEngine On
  # Useful for debugging
  # LogLevel alert rewrite:trace3
  RewriteRule ^/index.php$ / [R]
  RewriteRule ^/p.phppid=([^\.]+) /p.php?pid=$1 [L]
  RewriteRule ^/iembot(.*)$ https://weather.im/iembot$1 [R=permanent]

  Redirect /data/mwcomp.phtml https://mesonet.agron.iastate.edu/current/mwcomp.phtml
  Redirect /RWIS/current.php https://mesonet.agron.iastate.edu/RWIS/current.phtml
  Redirect /schoolnet/current.php https://mesonet.agron.iastate.edu/schoolnet/current.phtml
  Redirect /RWIS/currentSF.php https://mesonet.agron.iastate.edu/RWIS/currentSF.phtml
  Redirect /my/current.php https://mesonet.agron.iastate.edu/my/current.phtml
  Redirect http://www.mesonet.agron.iastate.edu https://mesonet.agron.iastate.edu
  Redirect permanent /archive/nexrad http://mesonet-longterm.agron.iastate.edu/archive/nexrad
  Redirect permanent /archive/gempak http://mesonet-longterm.agron.iastate.edu/archive/gempak
  Redirect permanent /archive/raw http://mesonet-longterm.agron.iastate.edu/archive/raw
  Redirect permanent /data/nexrd2/raw http://nomads.ncep.noaa.gov/pub/data/nccf/radar/nexrad_level2
  Redirect permanent /cscap https://datateam.agron.iastate.edu/cscap

  ErrorDocument 404 /http_errors/error404.py

  <Location "/http_errors/">
    # https://bz.apache.org/bugzilla/show_bug.cgi?id=55415
    ProxyErrorOverride Off
  </Location>

  <Directory "/opt/iem/htdocs">
    # Need FollowSymLinks for mod_rewrite to work!
    Options Indexes FollowSymLinks
    AllowOverride None
    Require all granted

    # Default handler for python scripts
    WSGIProcessGroup iemwsgi_ap
    AddHandler wsgi-script .py
    Options +ExecCGI

  </Directory>

  <Directory "/mesonet/ARCHIVE">
    Options Indexes FollowSymLinks
    AllowOverride All
    Require all granted
  </Directory>

  <Directory "/mesonet/data">
    Options Indexes FollowSymLinks
    AllowOverride All
    Require all granted
  </Directory>

  <Directory "/mesonet/share">
    Options Indexes FollowSymLinks
    AllowOverride All
    Require all granted
  </Directory>

  Alias /cgi-bin/ "/opt/iem/cgi-bin/"
  <Directory "/opt/iem/cgi-bin">
    AllowOverride All
    Options FollowSymLinks
    Require all granted

    # Default handler for python scripts
    WSGIProcessGroup iemwsgi_ap
    AddHandler wsgi-script .py
    AddHandler cgi-script .cgi
    Options +ExecCGI
  </Directory>

  # Since the above does not cover mapserv binaries
  <Directory "/opt/iem/cgi-bin/mapserv">
    SetHandler fcgid-script
    Options +ExecCGI
  </Directory>

  <LocationMatch "camera">
    ErrorDocument 404 /images/missing-320x240.jpg
  </LocationMatch>

  Alias /usage "/mesonet/share/usage/mesonet.agron.iastate.edu/"
  <Directory "/mesonet/share/usage/mesonet.agron.iastate.edu/">
    Options Indexes MultiViews
    AllowOverride None
    Require all granted
  </Directory>

  Alias /agclimate/usage "/mesonet/share/usage/agclimate/"
  <Directory "/mesonet/share/usage/agclimate/">
    Options Indexes MultiViews
    AllowOverride None
    Require all granted
  </Directory>

  <Directory "/opt/iem/htdocs/river">
	 RewriteRule wfo.phtml index.php
  </Directory>

  Alias /data "/home/ldm/data"
  <Directory "/home/ldm/data">
    Options Indexes MultiViews FollowSymLinks
    AllowOverride None
    Require all granted
	Redirect permanent /data/gis/images/unproj /data/gis/images/4326
  	Redirect permanent /data/gis/shape/unproj /data/gis/shape/4326
  </Directory>
    
  Alias "/onsite/lapses" "/mesonet/share/lapses"
  Alias "/onsite/windrose" "/mesonet/share/windrose"
  Alias "/onsite/iemre" "/mesonet/data/iemre"
  Alias "/onsite/prism" "/mesonet/data/prism"
  Alias "/onsite/stage4" "/mesonet/data/stage4"
  Alias "/present" "/mesonet/share/present"
  Alias "/cases" "/mesonet/share/cases"
  Alias "/GIS/data/gis" "/mesonet/data/gis"
  Alias "/archive/awos" "/mesonet/ARCHIVE/awos"
  Alias "/archive/raw" "/mesonet/ARCHIVE/raw"
  Alias "/archive/rer" "/mesonet/ARCHIVE/rer"
  Alias "/m/img"     "/mesonet/share/iemmaps"
  Alias "/sites/pics"     "/mesonet/share/pics"
  Alias "/climodat/everything.zip" "/mesonet/share/climodat/everything.zip"
  Alias "/climodat/reports" "/mesonet/share/climodat/reports"
  Alias "/climodat/ks" "/mesonet/share/climodat/ks"

  Alias "/pickup"    "/mesonet/share/pickup"  
  <Directory "/mesonet/share/pickup">
    AllowOverride All
    Options FollowSymLinks Indexes MultiViews
    Require all granted
  </Directory>

  Alias /tmp /var/webtmp
  <Directory "/var/webtmp">
    AllowOverride None
  </Directory>

  <Directory "/opt/iem/cgi-bin/wms/nexrad">
    RewriteRule n0r.cgi /cgi-bin/mapserv/mapserv.fcgi?map=/opt/iem/data/wms/nexrad/n0r.map& [QSA,L]
    RewriteRule n0q.cgi /cgi-bin/mapserv/mapserv.fcgi?map=/opt/iem/data/wms/nexrad/n0q.map& [QSA,L]
  </Directory>

  <Directory "/opt/iem/cgi-bin/wms/us">
    RewriteRule wwa.cgi /cgi-bin/mapserv/mapserv.fcgi?map=/opt/iem/data/wms/us/wwa.map& [QSA,L]
  </Directory>


  <Directory "/opt/iem/htdocs/c">
    WSGIProcessGroup iemwsgi_tc

    # http://lists.osgeo.org/pipermail/tilecache/2010-June/002453.html
    ExpiresActive On
    ExpiresDefault "access plus 14 days"
  </Directory>

  <Directory "/opt/iem/htdocs/cache">
    WSGIProcessGroup iemwsgi_tc

    # http://lists.osgeo.org/pipermail/tilecache/2010-June/002453.html
    ExpiresActive On
    ExpiresDefault "access plus 5 minutes"
  </Directory>

  <Directory "/opt/iem/htdocs/DCP">

    RewriteRule ahpsxml2wxc/([0-9A-Z]{3,5}).txt$ ahpsxml2wxc.py?nwsli=$1
  </Directory>

  <Directory "/opt/iem/htdocs/GIS">
    RewriteRule vtec_(.*).png radmap.php?layers[]=places&layers[]=nexrad&layers[]=cities&layers[]=interstates&layers[]=uscounties&vtec=$1&width=797&height=400
  </Directory>
  
  <Directory "/opt/iem/htdocs/agclimate">
    # Lots of old links out there to bad URIs
    RewriteRule index\.(html|pl|php)$ /agclimate/ [R]

    Redirect /agclimate/daily-pics https://mesonet.agron.iastate.edu/agclimate/daily_pics
    Redirect /agclimate/daily_pics https://mesonet.agron.iastate.edu/data/agclimate
    Redirect /agclimate/info.txt https://mesonet.agron.iastate.edu/agclimate/info.phtml

    # 
    RewriteRule smplot/([0-9]{1,12})/(.*).png$ isusm.py?t=$1&v=$2
    RewriteRule isusm.csv nmp_csv.py
  </Directory>

  <Directory "/opt/iem/htdocs/info">
    RewriteRule datasets/([a-z_]+).html$ datasets.php?id=$1 [QSA]
    RewriteRule datasets/?$ datasets.php [QSA]
  </Directory>

  <LocationMatch "/api/1">
    ProxyPass "http://iem-web-services.local:8000"
    ProxyPassReverse "http://iem-web-services.local:8000"
  </LocationMatch>

  <Location "/archive/data">
    RequestHeader set "Host" "iem-archive.local"
    ProxyPreserveHost Off
    # hacky to keep the paths matching in auto-index
    ProxyPass "http://iem-archive.local/archive/data"
    ProxyPassReverse "http://iem-archive.local/archive/data"
  </Location>


  <Directory "/opt/iem/htdocs/content">
    RewriteRule pil_([A-Z0-9]{3,6}).png$ pil.php?pil=$1
  </Directory>

  <Directory "/opt/iem/htdocs/wx/afos">
    RewriteRule ([0-9]{12})_([A-Z0-9\s]+).png$ text2png.py?e=$1&pil=$2
  </Directory>


  <Directory "/opt/iem/htdocs/frost">
    RewriteRule frost_ts_([a-z]+)_([\-\.0-9]+)_([\.0-9]+).png$ frost_ts.py?lon=$2&lat=$3&model=$1
  </Directory>

  <Directory "/opt/iem/htdocs/geojson">
	## QSA causes the query string to be appended
	RewriteRule network/(.*).geojson network.py?network=$1 [QSA]
	# 7 Dec 2016: Rewrote service as Python
	RewriteRule network.php(.*) network.py$1 [QSA]
    RewriteRule sbw.geojson(.*) sbw.py$1 [QSA]
    RewriteRule sps.geojson(.*) sps.py$1 [QSA]
    RewriteRule winter_roads.geojson(.*) winter_roads.py$1 [QSA]
    RewriteRule networks.geojson(.*) networks.py$1 [QSA]
    RewriteRule nexrad_attr.geojson(.*) nexrad_attr.py$1 [QSA]
  </Directory>

  <Directory "/opt/iem/htdocs/iemre">
    RewriteRule daily/([0-9\-]+)/([0-9\.]+)/([0-9\.\-]+)/(json) daily.py?date=$1&lat=$2&lon=$3&format=$4
    RewriteRule hourly/([0-9\-]+)/([0-9\.]+)/([0-9\.\-]+)/(json) hourly.py?date=$1&lat=$2&lon=$3&format=$4
    RewriteRule multiday/([0-9\-]+)/([0-9\-]+)/([0-9\.]+)/([0-9\.\-]+)/(json) multiday.py?date1=$1&date2=$2&lat=$3&lon=$4&format=$5
    RewriteRule cum/([0-9\-]+)/([0-9\-]+)/(shp) cum.py?date0=$1&date1=$2&format=$3&base=50&ceil=86
    RewriteRule cumcounty/([0-9]+)/([0-9\-]+)/([0-9\-]+)/([0-9]+)/([0-9]+)/(json) cum.py?county=$1&date0=$2&date1=$3&format=$6&base=$4&ceil=$5
  </Directory>

  <Directory "/opt/iem/htdocs/json">
    RewriteRule radar$ radar.py
    RewriteRule tms.json tms.py [QSA]
    RewriteRule qpe/([0-9\.\-]+)/([0-9\.\-]+)/(json) qpe.py?lat=$2&lon=$1&format=$3
    RewriteRule raob/([0-9]{12})/([A-Z0-9]{3,4})$ raob.py?ts=$1&station=$2 [QSA]
    RewriteRule prism/([0-9\.\-]+)/([0-9\.\-]+)/([0-9\.\-]+)$ prism.py?lon=$1&lat=$2&valid=$3 [QSA]
    RewriteRule stage4/([0-9\.\-]+)/([0-9\.\-]+)/([0-9\.\-]+)$ stage4.py?lon=$1&lat=$2&valid=$3 [QSA]
    RewriteRule network/([0-9\.\-A-Z]+).geojson network.py?network=$1 [QSA]
    # 15 Feb 2020 migration from PHP to python
	RewriteRule vtec_events_byugc.php(.*) vtec_events_byugc.py$1 [QSA]
  </Directory>

  <Directory "/opt/iem/htdocs/kml">
    RewriteRule roadcond.kml roadcond.php
    RewriteRule roadcond_v2.kml roadcond.php?linewidth=6&maxtype=2
  </Directory>

  <Directory "/opt/iem/htdocs/lsr">
    # This looks odd, but I think it happens for some poor clients that encode
    # the hash link somehow
    RewriteRule #(.*)$ /lsr/#$1 [R=301,NE]
  </Directory>

  <Directory "/opt/iem/htdocs/mec">
    AuthUserFile /opt/iem/config/admin.users
    AuthGroupFile /dev/null
    AuthName Administrative
    AuthType Basic

    require user mec

    RewriteRule i/([A-Za-z\-_0-9]*).png$ image.php?i=$1
    RewriteRule map_power_([0-9]*)_(yaw2?).png$ map_power.py?ts=$1&yawsource=$2
    RewriteRule turbine_ts_([0-9]*)_(.*).png$ turbine_ts.py?date=$1&turbinename=$2
  </Directory>

  <Directory "/opt/iem/htdocs/nws">
    RewriteRule days_since_([A-Z][A-Z])_([A-Z]).png /plotting/auto/plot/92/phenomena:$1::significance:$2::dpi:100.png
  </Directory>

  <Directory "/opt/iem/htdocs/onsite/features">
    RewriteRule tags/([^\.]+)\.html tags/index.php?tag=$1 [L]
    RewriteRule vote/(good|bad|abstain).json$ vote.py?vote=$1
    RewriteRule vote.json$ vote.py
    RewriteRule ^[0-9]{4}/[0-9]{2}/.*$ content.py [PT]
  </Directory>

  <Directory "/opt/iem/htdocs/current">
	RewriteRule live.php(.*)$ live.py$1
    RewriteRule live/(.*).jpg live.py?id=$1 [L]
  </Directory>

  <Directory "/opt/iem/htdocs/other">
    RewriteRule kymn.phtml current.phtml?network=KYMN
  </Directory>

  <Directory "/opt/iem/htdocs/plotting/auto">
    RewriteRule plot/([0-9]{1,12})/(.*).png$ autoplot.py?p=$1&q=$2&fmt=png
    RewriteRule plot/([0-9]{1,12})/(.*).csv$ autoplot.py?p=$1&q=$2&fmt=csv
    RewriteRule plot/([0-9]{1,12})/(.*).txt$ autoplot.py?p=$1&q=$2&fmt=txt
    RewriteRule plot/([0-9]{1,12})/(.*).xlsx$ autoplot.py?p=$1&q=$2&fmt=xlsx
    RewriteRule plot/([0-9]{1,12})/(.*).js$ autoplot.py?p=$1&q=$2&fmt=js
    RewriteRule plot/([0-9]{1,12})/(.*).mapbox$ autoplot.py?p=$1&q=$2&fmt=mapbox
    RewriteRule plot/([0-9]{1,12})/(.*).pdf$ autoplot.py?p=$1&q=$2&fmt=pdf
    RewriteRule plot/([0-9]{1,12})/(.*).svg$ autoplot.py?p=$1&q=$2&fmt=svg
    RewriteRule meta/([0-9]{1,12}).(json|html) meta.py?p=$1&_fmt=$2 [QSA]
  </Directory>

  <Directory "/opt/iem/htdocs/request">
    RewriteRule maxcsv/(.*).txt$ maxcsv.py?q=$1

    RewriteRule grx/iadot_trucks.txt grx/iadot_trucks.py
    # Legacy link was removed 5 Jan 2015
    RewriteRule grx/idot_trucks.php grx/iadot_trucks.py

    # .php was legacy stuff, lets not break old paths
    RewriteRule grx/l3attr.(php|txt) grx/l3attr.py [QSA]

    RewriteRule wxc/idot_trucks.txt wxc/idot_trucks.py
  </Directory>

  <Directory "/opt/iem/htdocs/roads">
    RewriteRule kcau.jpg kcau.php
    RewriteRule ktiv.jpg ktiv.php
    RewriteRule kwwl.jpg kwwl.php?v2
  </Directory>

  <Directory "/opt/iem/htdocs/vtec">
    RewriteRule ([^\.]+)\.html index.php?vtec=$1 [L]
    RewriteRule f/(.*)$ f.py [QSA]
  </Directory>

  <Directory "/opt/iem/htdocs/metadata/xml">
    RewriteRule pl_(.*)_(.*).xml pl.py?network=$1&station=$2 [QSA]
    RewriteRule sd_(.*)_(.*).xml sd.py?network=$1&station=$2 [QSA]
  </Directory>

  <Directory "/opt/iem/htdocs/scada">
    AuthUserFile /opt/iem/config/admin.users
    AuthGroupFile /dev/null
    AuthName Administrative
    AuthType Basic

    require user mec

    RewriteRule i/([A-Za-z\-_0-9]*).png$ image.php?i=$1
    RewriteRule map_power_([0-9]*).png$ map_power.py?ts=$1
    RewriteRule turbine_ts_([0-9]*)_(.*).png$ turbine_ts.py?date=$1&turbinename=$2
  </Directory>
  
