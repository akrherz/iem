<?php
require_once "../../config/settings.inc.php";
define("IEM_APPID", 123);
require_once "../../include/myview.php";
$t = new MyView();
$t->title = "API Documentation";

$t->content = <<< EOM

<h2>IEM Web Services and APIs</h2>

<div class="alert alert-warning">
<p><strong>Disclaimer:</strong> All of these services are provided as-is and
without warranty.  You are free to use these services for any lawful purpose
(including commercial whereby your company makes lots of money using these)
and please do not sue us if they do not work as you expect or if one of them
breaks during your critical time of need.</p>
</div>

<p>The primary goal of this website is to make data freely available in an
open manner. This page presents details the IEM's various Web Services and
Application Programming Interfaces (API). These services are structured into
four categories.</p>

<div class="row">
<div class="col-md-3">
<strong>API v1</strong><br />
<a class="btn btn-primary" href="/api/1/docs"><i class="fa fa-info"></i> IEM API v1 Docs</a>
represent a more formal API using the wonderful <a href="https://fastapi.tiangolo.com/">FastAPI</a>
framework.  This API generates JSON Table Schema responses and is more geared toward smallish
requests that can be serviced within a second or two.  The source code for these services
is found within the <a href="https://github.com/akrherz/iem-web-services">iem-web-services repo</a>.

</div>
<div class="col-md-3">
<strong>Ad-hoc Services</strong><br />

<a class="btn btn-primary" href="#json"><i class="fa fa-info"></i> (Geo)-JSON Services</a>
represent a hodge-podge of services invented over the past many years that are not necessarily
well thought out and nor structured.  They individually have help pages that attempt to explain
how to use them. The source code for these services is found with the main
<a href="https://github.com/akrherz/iem/tree/main/pylib/iemweb">iem repo</a>.

</div>
<div class="col-md-3">
<strong>Ad-hoc CGI Services</strong><br />

<a class="btn btn-primary" href="#cgi"><i class="fa fa-info"></i> Scriptable CGI Services</a>
represent a collection of backends that often service various bulk data download portals.  These
services are heavily trafficked and typically emit simple CSV responses.  None of these will
do JSON, often due to various lame constraints. The source code for these services is found with the main
<a href="https://github.com/akrherz/iem/tree/main/pylib/iemweb">iem repo</a>.

</div>
<div class="col-md-3">
<strong>OGC Services</strong><br />

<a class="btn btn-primary" href="/ogc/"><i class="fa fa-info"></i> OGC Services</a>
represent a collection of Open Geospatial Consortium services.
The source code for these services is found with the main
<a href="https://github.com/akrherz/iem/tree/main/pylib/iemweb">iem repo</a>.

</div>
</div><!-- ./row -->

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
 <li><a href="https://xweather.com/docs">Vaisala Xweather</a></li>
 <li><a href="https://www.visualcrossing.com/weather-api">Visual Crossing Weather</a></li>
 <li><a href="https://www.weatherbit.io/api/">Weatherbit API</a></li>
</ul>
</blockquote>

<h3>
<a href="#json"><i class="fa fa-bookmark"></i></a>
<a name="json"></a>(Geo)-JSON Services</h3>

<div class="row">
<div class="col-md-4">

<div class="panel panel-default">
  <div class="panel-heading">IEM Data / Metadata</div>
  <div class="panel-body">
  <ul>
    <li><a href="/json/climodat_stclimo.py?help">Climodat State Climatology</a></li>
    <li><a href="/json/current.py?help">Current Obs</a></li>
    <li><a href="/geojson/7am.py?help">COOP and other data valid @ 7 AM</a></li>
    <li><a href="/json/dcp_vars.py?help">HADS/DCP Reporting SHEF Vars</a></li>
    <li><a href="/json/products.py?help">Archive IEM Web Products</a></li>
    <li><a href="/geojson/network.py?help">Network GeoJSON</a></li>
    <li><a href="/geojson/networks.py?help">Network Identifiers</a></li>
    <li><a href="/json/reference.py?help">pyIEM reference data</a></li>
    <li><a href="/geojson/recent_metar.py?help">Recent "Interesting" METAR Reports</a></li>
    <li><a href="/json/stations.py?help">Station Metadata Changes</a></li>
    <li><a href="/json/tms.py?help">Tile Map Services metadata</a></li>
    <li>Webcam Archive Metadata:
        <a href="/geojson/webcam.py?help">GeoJSON</a> or
        <a href="/json/webcams.py?help">JSON</a></li>
  </ul>
  </div>
</div>

<div class="panel panel-default">
  <div class="panel-heading">Aviation Services</div>
  <div class="panel-body">
  <ul>
    <li><a href="/geojson/convective_sigmet.py?help">SIGMETs</a></li>
  </ul>
  </div>
</div>


</div>
<div class="col-md-4">

<div class="panel panel-default">
  <div class="panel-heading">NWS Data</div>
  <div class="panel-body">
  <ul>
      <li>CF6 Data: <a href="/geojson/cf6.py?help">GeoJSON</a> or
      <a href="/json/cf6.py?help">JSON</a></li>
      <li>CLI Data: <a href="/geojson/cli.py?help">GeoJSON</a> or
      <a href="/json/cli.py?help">JSON</a></li>
      <li><a href="/geojson/lsr.py?help">Local Storm Reports</a></li>
      <li><a href="/geojson/nexrad_attr.py?help">NEXRAD Storm Attributes</a></li>
      <li><a href="/json/ibw_tags.py?help">Impact Based Warning Tags</a></li>
      <li><a href="/json/radar.py?help">NEXRAD/TWDR Archive Metadata</a></li>
      <li><a href="/json/ridge_current.py?help">NEXRAD/TWDR Current Metadata</a></li>
      <li><a href="/json/spcmcd.py?help">SPC Mesoscale Discussions</a></li>
      <li><a href="/json/spcoutlook.py?help">SPC Outlooks</a></li>
      <li><a href="/json/spc_bysize.py?help">SPC Outlooks by Size</a></li>
      <li><a href="/json/spcwatch.py?help">SPC Watches</a></li>
      <li><a href="/json/raob.py?help">Sounding/RAOB Data</a></li>
      <li><a href="/geojson/sps.py?help">Special Weather Statements (SPS)</a></li>
      <li><a href="/json/sps_by_point.py?help">Special Weather Statements (SPS) by Point</a></li>
      <li><a href="/json/nwstext.py?help">Text Data</a></li>
      <li><a href="/json/nwstext_search.py?help">Text Product Metadata Search</a></li>
  </ul>
  </div>
</div>


</div>
<div class="col-md-4">

<div class="panel panel-default">
  <div class="panel-heading">NWS Watch, Warning, and Advisories</div>
  <div class="panel-body">
      <li><a href="/geojson/sbw.py?help">Storm Based Warnings</a></li>
      <li><a href="/json/sbw_by_point.py?help">Storm Based Warnings by Point</a></li>
      <li><a href="/geojson/vtec_event.py?help">VTEC Event Data</a></li>
      <li><a href="/json/vtec_events.py?help">VTEC Events</a></li>
      <li><a href="/json/vtec_events_bypoint.py?help">VTEC Events by Point</a></li>
      <li><a href="/json/vtec_events_bystate.py?help">VTEC Events by State</a></li>
      <li><a href="/json/vtec_events_byugc.py?help">VTEC Events by UGC</a></a>
      <li><a href="/json/vtec_events_bywfo.py?help">VTEC Events by WFO</a></li>
      <li><a href="/json/vtec_max_etn.py?help">VTEC Max Event ID</a></li>
  <ul>
  </ul>
  </div>
</div>

<div class="panel panel-default">
  <div class="panel-heading">Miscellaneous</div>
  <div class="panel-body">
  <ul>
    <li><a href="/geojson/winter_roads.py?help">Iowa Winter Road Conditions</a></li>
    <li><a href="/json/state_ugc.py?help">NWS State UGC Codes</a></li>
    <li><a href="/json/prism.py?help">PRISM</a></li>
    <li><a href="/json/stage4.py?help">Stage IV</a></li>
    <li><a href="/geojson/usdm.py?help">US Drought Monitor</a></li>
  </ul>
  </div>
</div>

</div>
</div><!-- ./row -->

<h3>
<a href="#cgi"><i class="fa fa-bookmark"></i></a>
<a name="cgi"></a>Scriptable CGI Services</h3>

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

<p>In general, we do not try to break things but bugs happen.  As always,
please <a href="/info/contacts.php">email us</a> with any concerns you have.  We
are extremely responsive to email :)


EOM;

$t->render('single.phtml');
