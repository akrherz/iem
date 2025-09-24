<?php
require_once "../../config/settings.inc.php";
require_once "../../include/myview.php";
$t = new MyView();
$t->title = "NWS Related Information";

$t->content = <<<EOM
<nav aria-label="breadcrumb">
  <ol class="breadcrumb mb-3">
    <li class="breadcrumb-item"><a href="/">IEM Homepage</a></li>
    <li class="breadcrumb-item active" aria-current="page">NWS User's Mainpage</li>
  </ol>
</nav>
<h1 class="h4 mb-4">NWS User's Mainpage</h1>
<div>

<div class="row g-3">
<div class="col-md-6">

<p>The IEM and NWS have enjoyed a long standing partnership.  This partnership
has collected a number of awards including a <a href="https://www.cals.iastate.edu/news/releases/isu-ag-meteorology-web-network-receives-national-award">2002 NWA Award</a>
and <a href="http://www.noaanews.noaa.gov/stories2007/s2842.htm">2007 NOAA Award</a>.  We also
worked together on the IEMChat Project, which was later rolled into the present
day <a href="https://nwschat.weather.gov">NWSChat Project</a>.</p>

<p><a href="/plotting/auto/"><i class="bi bi-activity" aria-hidden="true"></i> Automated Data Plotting</a> is a very deep rabbit
hole with hundreds of plotting options for many datasets of NWS interest.</p>

</div>
<div class="col-md-6">

<div class="card card-body">
<strong>Did you see an image posted to social media with the IEM logo on it?</strong>
<br />Daryl posts some interesting graphics to his
  <a href="https://bsky.app/profile/akrherz.bsky.social">akrherz.bsky.social</a> page. Generally,
  these are one-off images that are not available for dynamic generation on
  this website.
</div>

</div>
</div><!-- ./row -->

<div class="row g-3">
<div class="col-md-6">

<div class="card mb-3" role="region" aria-labelledby="card-aviation">
  <div class="card-header"><h2 class="h6 mb-0" id="card-aviation">Aviation Weather Products</h2></div>
  <div class="card-body">

  <ul>
<li><a href="/request/gis/cwas.phtml">Center Weather Advisories (CWA) in Shapefile/KML format</a></li>
<li><a href="/request/gis/awc_gairmets.phtml">Graphical AIRMETs in Shapefile/KML format</a></li>
<li><a href="/request/gis/pireps.php">PIREPs in Shapefile format</a></li>
<li><a href="/request/gis/awc_sigmets.phtml">SIGMETs in Shapefile/KML format</a></li>
<li><a href="/request/taf.php">Terminal Aerodome Forecasts (TAFs)</a></li>
<li><a href="/request/tempwind_aloft.php">Temp/Winds Aloft</a></li>
</ul>

</div>
</div>


<div class="card mb-3" role="region" aria-labelledby="card-hydro">
  <div class="card-header"><h2 class="h6 mb-0" id="card-hydro">Flash Flooding / Hydrology</h2></div>
  <div class="card-body">
<p><strong>Precipitation Estimates/Observations</strong></p>
<ul>
  <li><a href="/DCP/plot.phtml">Archived DCP Data Plotter</a><br />
    Simple app to plot out current/historical DCP (river gauges) data for a site of your choice.</li>
    <li>Daily Climate Summary (AFOS: CLI Product)
        <a href="climap.php">Interactive Map</a> or
        <a href="clitable.php">Text Table</a></li>
    <li>CF6 Summary (AFOS: CF6 Product)
        <a href="cf6map.php">Interactive Map</a> or
        <a href="cf6table.php">Text Table</a></li>
  <li><a href="/COOP/cat.phtml">Daily COOP Observations</a></li>
  <li><a href="/rainfall/obhour.phtml">Hourly Precipitation Summaries</a> for ASOS</li>
  <li><a href="/rainfall/">IEM GIS Rainfall</a><br />
    Mostly Midwest products, but includes a conversion of MRMS to ERDAS Imagine Files.</li>
  <li><a href="/archive/mrms.php">IEM Archival of MRMS</a></li>
    <li><a href="/ASOS/current.phtml">Sortable Currents</a> for ASOS, COOP, etc</li>
</ul>

<p><strong>Flood Warnings/Forecasts</strong>
<br />Many of the apps in the "Severe Weather / VTEC" section are useful as well.</p>

<ul>
  <li><a href="/plotting/auto/?q=160">HML based forecasts and observations</a><br />
    An archive of HML processed products is used to drive an interactive plot of forecasts and observations.</li>
  <li><a href="/request/hml.php">HML Processed Data Download</a><br />
    Download HML data for a site of your choice.</li>
  <li><a href="/cow/">IEM Cow Polygon Verification</a><br />
    Application does LSR based verification of Flash Flood Warnings.</li>
  <li><a href="/river/">River Forecast Point Monitor</a><br />
    Summarizes FLS statements by River by WFO/State.</li>
</ul>

  </div>
</div>

<div class="card mb-3" role="region" aria-labelledby="card-severe">
  <div class="card-header"><h2 class="h6 mb-0" id="card-severe">Severe Weather / VTEC</h2></div>
  <div class="card-body">

<p>The <a href="/current/severe.phtml">Severe Weather Mainpage</a> has more
options listed.</p>

<p><strong>Data / Realtime Monitoring</strong></p>
<ul>
 <li><a href="/request/gis/watchwarn.phtml">GIS Shapefiles</a><br />
  of archived Storm Based Warning polygons.</li>
 <li><a href="/iembot/">IEMBot</a><br />
  Realtime chatrooms, twitter posting service, RSS feeds and more.</li>
</ul>

<p><strong>Special Weather Statements (SPS)</strong></p>
<ul>
  <li><a href="/request/gis/sps.phtml">SPS Polygon Download</a><br />
  Download shapefiles of SPSs.</li>
  <li><a href="/nws/sps_search/">SPS Search by Point</a><br />
  Search for SPSs by point.</li>
  <li><a href="/wx/afos/p.php?pil=SPSDMX">SPS Text Download</a><br />
  Request raw SPS text over a period of your choice.</li>
</ul>

<p><strong>Maps and Graphics</strong></p>
<ul>
  <li><a href="/plotting/auto/?q=92">Days Since VTEC Product</a><br />
  Map of the number of days since a WFO issued a VTEC Product.</li>
 <li><a href="/raccoon/">IEM Raccoon</a><br />
  Generate Microsoft PowerPoint of Storm Based Warnings for a WFO and RADAR site of your choice.</li>
 <li><a href="/plotting/auto/?q=109">Number of VTEC Events by WFO</a><br />
  Map of the number of VTEC events by WFO for a time period of your choice.</li>
 <li><a href="/timemachine/?product=59">NWS WWA Map Archive</a><br />
 The IEM saves the national watch, warning, and advisory (WWA) map every five minutes.</li>
 <li><a href="/vtec/">VTEC Browser</a><br />
  Interactive display of VTEC products.</li>
 <li><a href="/vtec/search.php"><i class="bi bi-search" aria-hidden="true"></i> VTEC Search by Point or County/Zone</a><br />
  Find issued VTEC WWA products by a given zone or county. Search for a storm based warning by point on a map.</li>
</ul>

<p><strong>Statistics / Metadata</strong></p>
<ul>
 <li><a href="/nws/list_tags.php">List SVR+TOR Warning Tags</a><br />
  This application will list tags used in Severe Thunderstorm and Tornado warnings by NWS Office by Year.</li>

<li><a href="/nws/list_ugcs.php">List Universal Geographic Codes (UGC) by WFO/State</a></li>

<li><a href="/vtec/yearly_counts.php">Number of VTEC Events by year</a><br />
Table of the number of VTEC events by year.</li>

  <li><a href="/vtec/events.php">VTEC Events by WFO or State by Year</a><br />
  Simple table listing any VTEC events by a given WFO or state for a given year.</li>

  <li><a href="/vtec/maxetn.php">Maximum VTEC EventID (ETN) by year</a><br />
  This diagnostic prints out the maximum issued VTEC eventid (ETN) by year. A useful diagnostic for a NWS Office wishing to check their local VTEC eventd database.</li>

<li><a href="/vtec/emergencies.php">Tornado + Flash Flood Emergencies listing</a><br />
Simple table showing IEM indicated Tornado and Flash Flood Emergency events.</li>

<li><a href="/vtec/pds.php">Particularly Dangerous Situation Warnings</a><br />
Simple table showing IEM indicated PDS Tornado / Flash Flood Warnings.</li>


 <li><a href="/cow/sbwsum.phtml">Summary Images of Daily Storm Based Warnings</a><br />
  Displays just the storm based warning geometries for one UTC day at a time.</li>
 <li><a href="/cow/top10.phtml">Top 10 Polygon Sizes</a></li>
</ul>

<p><strong>Verification</strong></p>
<ul>
 <li><a href="vtec_obs.php">ASOS/AWOS Obs during WFO WWA</a>
  <br />Prints out ASOS/AWOS observations during selected VTEC warning types.</li>
 <li><a href="/nws/debug_latlon/">Debug / Create Simple Graphic</a> from LAT...LON text.</li>
   <li><a href="/cow/">IEM Cow</a><br />
    Interactive Storm Based Warning verification app.</li>
</ul>

<!-- Removed empty list -->

  </div>
</div>

</div>
<div class="col-md-6">

<div class="card mb-3" role="region" aria-labelledby="card-asos">
  <div class="card-header"><h2 class="h6 mb-0" id="card-asos">ASOS/AWOS METAR</h2></div>
  <div class="card-body">
<ul>
  <li><a href="obs.php">Sortable Currents by WFO</a></li>
</ul>

<h4>Regional Temperature &amp; Precipitation (RTP)</h4>
<p>The IEM attempts to generate RTP products as the NWS has discontinued
them.</p>
<ul>
 <li><a href="/plotting/auto/?q=256">IEM Autoplot 256</a> generator tool.</li>
 <li><a href="/data/awos_rtp_00z.shef">0Z SHEF for Iowa</a></li>
 <li><a href="/data/awos_rtp.shef">12Z SHEF for Iowa</a></li>
</ul>

  </div>
</div>

<div class="card mb-3" role="region" aria-labelledby="card-coop">
  <div class="card-header"><h2 class="h6 mb-0" id="card-coop">Cooperative Observer Program - COOP</h2></div>
  <div class="card-body">
<ul>
 <li><a href="/nws/coop-cnts.php">Monthly COOP Frequency Reports</a><br />
  Quantity of observations received by variable for the COOP network.</li>
 <li><a href="/COOP/current.phtml">Sortable Current COOP Reports</a><br />
   View today's COOP reports by WFO or by state. Includes derived frozen to liquid ratio and SWE reports.</li>
</ul>
  </div>
</div>


<div class="card mb-3" role="region" aria-labelledby="card-hads">
  <div class="card-header"><h2 class="h6 mb-0" id="card-hads">HADS / DCP / GOES</h2></div>
  <div class="card-body">
<ul>
 <li><a href="/DCP/plot.phtml">Archived DCP Data Plotter</a><br />
 Simple app to plot out current/historical DCP (river gauges) data for a site of your choice.</li>
</ul>
  </div>
</div>

<div class="card mb-3" role="region" aria-labelledby="card-lsr">
  <div class="card-header"><h2 class="h6 mb-0" id="card-lsr">Local Storm Reports (LSR)</h2></div>
  <div class="card-body">
<p>The IEM processes LSRs issued by the NWS in real-time. A number of
    applications on this website utilize this source of reports.</p>
<ul>
  <li><a href="https://groups.google.com/g/nws-damage-survey-pns">NWS Damage Survey PNS Email List</a><br />
  An email list that provides any NWS issued Damage Survey PNS statements.</li>

  <li><a href="/plotting/auto/?q=207">LSR + COOP Snowfall Analysis Autoplot #207</a><br />
  Dynamic analysis of available LSR and COOP reports that is used to generate these static maps for: <a href="/data/lsr_snowfall.png">Iowa</a>, <a href="/data/lsr_snowfall_nv.png">Iowa map without labels</a>, and <a href="/data/mw_lsr_snowfall.png">Midwest</a>.</li>

  <li>Past 24 hours of Storm Reports<br />
  <a href="/data/gis/shape/4326/us/lsr_24hour.zip">ESRI Shapefile</a>, <a href="/data/gis/shape/4326/us/lsr_24hour.csv">Comma Delimited</a>, <a href="/data/gis/shape/4326/us/lsr_24hour.geojson">GeoJSON</a>. The IEM parses the realtime feed of NWS Local Storm Reports. Every 5 minutes, a process collects up the last 24 hours worth of reports and dumps them to the above files.</li>

   <li><a href="/request/gis/lsrs.phtml">Archived Local Storm Reports</a><br />
 Generate a shapefile of LSRs for a period of your choice dating back to 2003!</li>
        <li><a href="/lsr/">Local Storm Report App</a></li>
</ul>
  </div>
</div>


<div class="card mb-3" role="region" aria-labelledby="card-nexrad">
  <div class="card-header"><h2 class="h6 mb-0" id="card-nexrad">NEXRAD RADAR</h2></div>
  <div class="card-body">
<ul>
 <li><a href="/request/gis/nexrad_storm_attrs.php">NEXRAD Storm Attributes</a><br />
 Download shapefiles of NEXRAD storm attribute data and view histogram summaries.</li>
</ul>
  </div>
</div>

<div class="card mb-3" role="region" aria-labelledby="card-snowfall">
  <div class="card-header"><h2 class="h6 mb-0" id="card-snowfall">Snowfall</h2></div>
  <div class="card-body">
<ul>
 <li><a href="/nws/snowfall_6hour.php">Six Hour Snowfall Totals</a><br />
 Simple table of available 6 hour snowfall total reports.</li>
</ul>
  </div>
</div>


<div class="card mb-3" role="region" aria-labelledby="card-spc">
  <div class="card-header"><h2 class="h6 mb-0" id="card-spc">Storm Prediction Center Products</h2></div>
  <div class="card-body">
<ul>
<li><a href="/request/gis/spc_mcd.phtml">
<i class="bi bi-download" aria-hidden="true"></i> SPC Mesoscale Discussion Shapefile Download</a></li>

<li><a href="mcd_top10.phtml">
<i class="bi bi-list-ul" aria-hidden="true"></i> SPC Top 10 MCD Sizes</a></li>

<li><a href="/request/gis/outlooks.phtml">
 <i class="bi bi-download" aria-hidden="true"></i> SPC/WPC Outlook Shapefile Download</a></li>

 <li><a href="spc_top10.phtml">
 <i class="bi bi-list-ul" aria-hidden="true"></i> SPC Top 10 Outlook Sizes</a></li>

 <li><a href="/request/gis/spc_watch.phtml">
 <i class="bi bi-download" aria-hidden="true"></i> SPC Watch Polygon Shapefile Download</a></li>

 <li><a href="/GIS/apps/rview/watch.phtml">Convective Watches Information</a>
  <br />Lists out some simple details on each convective watch.</li>

  <li><a href="/nws/watches.php">List SPC Watches by Year</a>
  <br />Lists out some simple details on all watches for a year.</li>

  <li><a href="/nws/pds_watches.php">Lists All SPC PDS Watches</a>
  <br />Lists out watches tagged as Particularly Dangerous Situations (PDS).</li>

  <li><a href="/nws/spc_outlook_search/"><i class="bi bi-search" aria-hidden="true"></i> SPC Outlook / MCD search by point</a>
  <br />Allows answering of the question of when was a given point last under
some convective outlook or the number of outlooks for a given point.</li>
</ul>
 </div>
</div>

<div class="card mb-3" role="region" aria-labelledby="card-wpc">
  <div class="card-header"><h2 class="h6 mb-0" id="card-wpc">Weather Prediction Center Products</h2></div>
  <div class="card-body">
<ul>
<li><a href="/request/gis/wpc_mpd.phtml">
<i class="bi bi-download" aria-hidden="true"></i> WPC Precipitation Discussion Shapefile Download</a></li>
<li><a href="/nws/wpc_national_hilo/">WPC National High Low Listing</a></li>
<li><a href="/request/gis/outlooks.phtml">
 <i class="bi bi-download" aria-hidden="true"></i> SPC/WPC Outlook Shapefile Download</a></li>
  <li><a href="/nws/wpc_outlook_search/"><i class="bi bi-search" aria-hidden="true"></i> WPC Outlook / MPD search by point</a>
  <br />Allows answering of the question of when was a given point last under
some convective outlook or the number of outlooks for a given point.</li>
 </ul>
  </div>
</div>


<div class="card mb-3" role="region" aria-labelledby="card-model">
  <div class="card-header"><h2 class="h6 mb-0" id="card-model">Numerical Model Data</h2></div>
  <div class="card-body">
<ul>
 <li><a href="/mos/">Model Output Statistics</a><br />
 Archive of MOS back to 3 May 2007.</li>
 <li>HRRR MidWest 1km Reflectivity [animated GIF]
 <br />Animated GIF of HRRR Forecasted Reflectivity.
  <a href="/data/model/hrrr/hrrr_1km_ref.gif">Latest Run</a> or
  <a href="/timemachine/?product=61">Archived plots</a></li>
</ul>
  </div>
</div>

<div class="card mb-3" role="region" aria-labelledby="card-textprod">
  <div class="card-header"><h2 class="h6 mb-0" id="card-textprod">Text Product Archives</h2></div>
  <div class="card-body">

<p>Please visit this <a href="text.php">dedicated page</a> for information
about the IEM's text product archives.</p>

  </div>
</div>


</div>
</div><!-- ./row -->

</div>

EOM;
$t->render('single.phtml');
