<?php
require_once "../../config/settings.inc.php";
define("IEM_APPID", 123);
require_once "../../include/myview.php";
$t = new MyView();
$t->title = "API Documentation";

$t->content = <<< EOF

<h2>IEM API</h2>

<p><a class="btn btn-default" href="/api/1/docs"><i class="fa fa-info"></i> IEM API v1 Docs</a></p>

<p>The primary goal of this website is to make data freely available in an
open manner. This page presents details the IEM's Application Programming
Interface (API).</p>

<h3>But first, perhaps there are better alternatives!</h3>

<blockquote>
<p>The following is a list of other web service providers.  They all do a better
job than this website does.  Some of these are commercial and this listing should
not be implied as an endorsement. Of course, you can just search google for
<a href="https://www.google.com/search?q=weather+api">Weather API</a> :)</p>

<ul>
 <li><a href="https://developer.baronweather.com/">Baron Weather</a></li>
 <li><a href="https://openweathermap.org/api">OpenWeatherMap</a></li>
 <li><a href="https://realearth.ssec.wisc.edu/doc/api.php">SSEC RealEarth API</a></li>
 <li><a href="https://www.tomorrow.io/weather-api/">Tomorrow.io</a></li>
 <li><a href="https://www.visualcrossing.com/weather-api">Visual Crossing Weather</a></li>
 <li><a href="https://xweather.com/docs">Vaisala Xweather</a></li>
 <li><a href="https://www.weatherbit.io/api/">Weatherbit API</a></li>
</ul>
</blockquote>

<p>But you are here wondering about the IEM's API services?  Presently, there are
two portals with information about IEM APIs:

<ol>
 <li><a href="/json/">Legacy ad-hoc/legacy (Geo)JSON services</a>
  <br />These have been around for a while and while they work, they are generally
  somewhat brittle.</li>
 <li><a href="/api/1/docs">IEM API v1 Documentation</a>
  <br />Work is ongoing now to migrate the services found in #1 above into a more
  robust and self-documenting API system.  This is the future and will see
  significant expansion during 2020.</li> 
</ol>

<h3>Scriptable CGI Services</h3>

<p>Some of the IEM data services are not ammenable to being used within a API
service that aims for sub-second response times.  These services also consume
a lot of resources and are not as scalable.  As such, we have a few services
rooted within <code>/cgi-bin/</code> style 2000s era web services.  There are primative
help pages for these services:</p>

<ul>
<li><a href="/cgi-bin/request/asos.py?help">ASOS/METAR Data (/cgi-bin/request/asos.py)</a></li>
<li><a href="/cgi-bin/request/asos1min.py?help">ASOS 1 Minute NCEI Data (/cgi-bin/request/asos1min.py)</a></li>
<li><a href="/cgi-bin/request/scp.py?help">ASOS Satellite + Cloud Product (/cgi-bin/request/scp.py)</a></li>
<li><a href="/cgi-bin/request/gis/awc_gairmets.py?help">AWC Graphical Airmets (/cgi-bin/request/gis/awc_gairmets.py)</a></li>
<li><a href="/cgi-bin/request/gis/cwas.py?help">Center Weather Advisories (/cgi-bin/request/gis/cwas.py)</a></li>
<li><a href="/cgi-bin/request/hads.py?help">HADS/DCP/SHEF Data (/cgi-bin/request/hads.py)</a></li>
<li><a href="/cgi-bin/request/hourlyprecip.py?help">Hourly Precip (/cgi-bin/request/hourlyprecip.py)</a></li>
<li><a href="/cgi-bin/request/nass_iowa.py?help">Iowa NASS (/cgi-bin/request/nass_iowa.py)</a></li>
<li><a href="/cgi-bin/request/isusm.py?help">Iowa State Soil Moisture Network (/cgi-bin/request/isusm.py)</a></li>
<li><a href="/cgi-bin/request/coop.py?help">IEM Climodat stations (/cgi-bin/request/coop.py)</a></li>
<li><a href="/cgi-bin/request/daily.py?help">IEM Computed Daily Summaries (/cgi-bin/request/daily.py)</a></li>
<li><a href="/cgi-bin/request/gis/lsr.py?help">Local Storm Reports (/cgi-bin/request/gis/lsr.py)</a></li>
<li><a href="/cgi-bin/request/metars.py?help">METARs (/cgi-bin/request/metars.py)</a></li>
<li><a href="/cgi-bin/request/other.py?help">Miscellaneous/Other (/cgi-bin/request/other.py)</a></li>
<li><a href="/cgi-bin/request/mos.py?help">Model Output Statistics (/cgi-bin/request/mos.py)</a></li>
<li><a href="/cgi-bin/request/nlaeflux.py?help">NLAE Flux Stations (/cgi-bin/request/nlaeflux.py)</a></li>
<li><a href="/cgi-bin/request/gis/nexrad_storm_attrs.py?help">NEXRAD Storm Attributes (/cgi-bin/request/gis/nexrad_storm_attrs.py)</a></li>
<li><a href="/cgi-bin/afos/retrieve.py?help">NWS Text Data (/cgi-bin/afos/retrieve.py)</a></li>
<li><a href="/cgi-bin/request/gis/watchwarn.py?help">NWS Watch/Warning/Advisories (/cgi-bin/request/gis/watchwarn.py)</a></li>
<li><a href="/cgi-bin/request/gis/pireps.py?help">Pilot Reports PIREPS (/cgi-bin/request/gis/pireps.py)</a></li>
<li><a href="/cgi-bin/request/raster2netcdf.py?help">RASTER 2 netcdf (/cgi-bin/request/raster2netcdf.py)</a></li>
<li><a href="/cgi-bin/request/raob.py?help">RAOB Soundings (/cgi-bin/request/raob.py)</a></li>
<li><a href="/cgi-bin/request/rwis.py?help">Roadway Weather Information (RWIS) (/cgi-bin/request/rwis.py)</a></li>
<li><a href="/cgi-bin/request/scan.py?help">Soil Climate Analysis Network (/cgi-bin/request/scan.py)</a></li>
<li><a href="/cgi-bin/request/gis/sigmets.py?help">SIGMETs (/cgi-bin/request/gis/sigmets.py)</a></li>
<li><a href="/cgi-bin/request/gis/spc_mcd.py?help">SPC MCD (/cgi-bin/request/gis/spc_mcd.py)</a></li>
<li><a href="/cgi-bin/request/gis/spc_outlooks.py?help">SPC/WPC Outlooks (/cgi-bin/request/gis/spc_outlooks.py)</a></li>
<li><a href="/cgi-bin/request/gis/spc_watch.py?help">SPC Convective Watches (/cgi-bin/request/gis/spc_watch.py)</a></li>
<li><a href="/cgi-bin/request/gis/sps.py?help">Special Weather Statements SPS (/cgi-bin/request/gis/sps.py)</a></li>
<li><a href="/cgi-bin/request/gis/watch_by_county.py?help">SPC Watch by County (/cgi-bin/request/gis/watch_by_county.py)</a></li>
<li><a href="/cgi-bin/request/tempwind_aloft.py?help">Temp Winds Aloft (/cgi-bin/request/tempwind_aloft.py)</a></li>
<li><a href="/cgi-bin/request/taf.py?help">Terminal Aerodome Forecast TAF (/cgi-bin/request/taf.py)</a></li>
<li><a href="/cgi-bin/request/gis/wpc_mpd.py?help">WPC Mesoscale Precip Discussions (/cgi-bin/request/gis/wpc_mpd.py)</a></li>
<li><a href="/cgi-bin/mywindrose.py?help">Windrose Generator (/cgi-bin/mywindrose.py)</a></li>

</ul>

<h3>API Stability?</h3>

<p>In general, we do not try to break things but bugs happen.  The plan is to
auto-redirect any of the legacy services into the more modern API system.  As always,
please <a href="/info/contacts.php">email us</a> with any concerns you have.  We
are extremely responsive to email :)

<h3>Service Changes</h3>

<ul>
 <li><strong>24 April 2020:</strong> Update this page to reflect the new API services
 and migrate the backend to use it!</li>
</ul>

EOF;

$t->render('single.phtml');
