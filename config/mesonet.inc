#
# Apache vhost configuration for IEM
# I have this set in dev: SetEnv PYTHONPATH "/home/akrherz/projects/pyIEM/src"

  Include /opt/iemwebfarm/config/vhost_common.conf

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

# Search functionality
RewriteRule ^/search /search.py [QSA]

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

  <Directory "/opt/iem/htdocs">
    # Need FollowSymLinks for mod_rewrite to work!
    Options Indexes FollowSymLinks
    AllowOverride None
    Require all granted

    # Default handler for python scripts
    WSGIProcessGroup iemwsgi_ap
    # Allow wsgi scripts to emit 404s that can come back to the handler.
    # FIXME this causes all error handling to come back, which is a problem
    # https://github.com/GrahamDumpleton/mod_wsgi/issues/825
    # WSGIErrorOverride On
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

  # BUFKIT Warehouse
  # Include /opt/bufkit_warehouse/config/apache_config.inc

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

  Alias /data "/mesonet/ldmdata"
  <Directory "/mesonet/ldmdata">
    Options Indexes MultiViews FollowSymLinks
    AllowOverride None
    Require all granted
    Redirect permanent /data/gis/images/unproj /data/gis/images/4326
      Redirect permanent /data/gis/shape/unproj /data/gis/shape/4326
  </Directory>
    
  Alias "/onsite/lapses" "/mesonet/share/lapses"
  Alias "/onsite/windrose" "/mesonet/share/windrose"
  Alias "/onsite/iemre" "/mesonet/data/iemre"
  Alias "/onsite/mrms" "/mesonet/data/mrms"
  Alias "/onsite/prism" "/mesonet/data/prism"
  Alias "/onsite/stage4" "/mesonet/data/stage4"
  Alias "/onsite/era5land" "/mesonet/data/era5land"
  Alias "/present" "/mesonet/share/present"
  Alias "/cases" "/mesonet/share/cases"
  Alias "/GIS/data/gis" "/mesonet/data/gis"
  Alias "/archive/awos" "/mesonet/ARCHIVE/awos"
  Alias "/archive/raw" "/mesonet/ARCHIVE/raw"
  Alias "/archive/rer" "/mesonet/ARCHIVE/rer"
  Alias "/m/img"     "/mesonet/share/iemmaps"
  Alias "/sites/pics"     "/mesonet/share/pics"
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
    # As a reminder, we are going via this route to take advantage of caching
    # running with the apache on this vhost
    ProxyPass "https://iem-web-services.agron.iastate.edu"
    ProxyPassReverse "https://iem-web-services.agron.iastate.edu"
  </LocationMatch>

  <Location "/archive/data">
    RequestHeader set "Host" "iem-archive.local"
    ProxyPreserveHost Off
    # Send 404s back here
    ProxyErrorOverride On
    # hacky to keep the paths matching in auto-index
    ProxyPass "http://iem-archive.local/archive/data"
    ProxyPassReverse "http://iem-archive.local/archive/data"
  </Location>

<Proxy "balancer://arcgis">
    BalancerMember "https://iem-arcgis1.agron.iastate.edu:6443/arcgis"
    BalancerMember "https://iem-arcgis2.agron.iastate.edu:6443/arcgis"
</Proxy>
  SSLProxyCheckPeerCN off
  SSLProxyCheckPeerExpire off
  SSLProxyCheckPeerName off
  SSLProxyEngine On
  SSLProxyVerify none

 <Location "/arcgis">
  ProxyPass        "balancer://arcgis"
  ProxyPassReverse "balancer://arcgis"
 </Location>

  <Directory "/opt/iem/htdocs/content">
    RewriteRule pil_([A-Z0-9]{3,6}).png$ pil.php?pil=$1
  </Directory>

  <Directory "/opt/iem/htdocs/sites">
    # Allow for python scripts to act has directories NETWORK/SID/TOOL
    RewriteRule ^([^/]{3,20})/([^/]{3,20})/([^/]+)$ $3.py
  </Directory>

  <Directory "/opt/iem/htdocs/wx/afos">
    RewriteRule ([0-9]{12})_([A-Z0-9\s]+).png$ text2png.py?e=$1&pil=$2 [B,L]
  </Directory>

  <Directory "/opt/iem/htdocs/AWOS">
    RewriteRule (.*)_metar_collective.txt metar_collective.py?state=$1
  </Directory>

  <Directory "/opt/iem/htdocs/geojson">
    # QSA causes the query string to be appended
    RewriteRule network/(.*).geojson network.py?network=$1 [QSA]
    # Le Sigh
    RewriteRule network_obs.php(.*) /api/1/currents.geojson$1 [QSA]
    # General rewrite of anything .php or .geojson to python
    RewriteRule ^([a-z_]+)\.(php|geojson) $1.py [QSA]
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
    RewriteRule live/(.*).jpg live.py?id=$1 [L]
  </Directory>

  <Directory "/opt/iem/htdocs/plotting/auto">
    RewriteRule qrcode/([0-9]{1,12})/(.*).png$ gen_qrcode.py?p=$1&q=$2&fmt=png [B]
    RewriteRule plot/([0-9]{1,12})/(.*).png$ autoplot.py?p=$1&q=$2&fmt=png [B]
    RewriteRule plot/([0-9]{1,12})/(.*).csv$ autoplot.py?p=$1&q=$2&fmt=csv [B]
    RewriteRule plot/([0-9]{1,12})/(.*).txt$ autoplot.py?p=$1&q=$2&fmt=txt [B]
    RewriteRule plot/([0-9]{1,12})/(.*).xlsx$ autoplot.py?p=$1&q=$2&fmt=xlsx [B]
    RewriteRule plot/([0-9]{1,12})/(.*).js$ autoplot.py?p=$1&q=$2&fmt=js [B]
    RewriteRule plot/([0-9]{1,12})/(.*).geojson$ autoplot.py?p=$1&q=$2&fmt=geojson [B]
    RewriteRule plot/([0-9]{1,12})/(.*).pdf$ autoplot.py?p=$1&q=$2&fmt=pdf [B]
    RewriteRule plot/([0-9]{1,12})/(.*).svg$ autoplot.py?p=$1&q=$2&fmt=svg [B]
    RewriteRule meta/([0-9]{1,12}).(json|html) meta.py?p=$1&_fmt=$2 [QSA,B]
  </Directory>

  <Directory "/opt/iem/htdocs/request">
    RewriteRule maxcsv/(.*).txt$ maxcsv.py?q=$1

    RewriteRule grx/iadot_trucks.txt grx/iadot_trucks.py
    # Legacy link was removed 5 Jan 2015
    RewriteRule grx/idot_trucks.php grx/iadot_trucks.py
    # PHP replaced by python 24 May 2020
    RewriteRule grx/time_mot_loc.(php|txt) grx/time_mot_loc.py [QSA]

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

  # 16 Jan 2023: puzzling number of hosts have this to valid URIs
  Redirect permanent /gis/ /GIS/
