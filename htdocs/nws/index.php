<?php
require_once "../../config/settings.inc.php";
require_once "../../include/myview.php";
$t = new MyView();
$t->title = "NWS Related Information";
$t->thispage = "iem-info";

$t->content = <<<EOF

<br />
<ol class="breadcrumb">
 <li><a href="/">IEM Homepage</a></li>
 <li class="active">NWS User's Mainpage</li>
</ol>


<div class="row">
<div class="col-md-6">

<p>The IEM and NWS have enjoyed a long standing partnership.  This partnership
has collected a number of awards including a <a href="https://www.cals.iastate.edu/news/releases/isu-ag-meteorology-web-network-receives-national-award">2002 NWA Award</a>
and <a href="http://www.noaanews.noaa.gov/stories2007/s2842.htm">2007 NOAA Award</a>.  We also
worked together on the IEMChat Project, which was later rolled into the present
day <a href="https://nwschat.weather.gov">NWSChat Project</a>.</p>

<p><a href="/plotting/auto/"><i class="fa fa-signal"></i> Automated Data Plotting</a> is a very deep rabbit
hole with hundreds of plotting options for many datasets of NWS interest.</p>

</div><div class="col-md-6">

<div class="well">
<strong>Did you see an image posted to social media with the IEM logo on it?</strong><br />
	Daryl posts some interesting graphics to his 
	<a href="https://twitter.com/akrherz">Twitter @akrherz</a> page.  Generally,
	these are one-off images that are not available for dynamic generation on
	this website.
</div>

</div>
</div><!-- ./row -->

<div class="row">
<div class="col-md-6">

<h3>Interest Areas</h3>

<div class="panel panel-default">
  <div class="panel-heading">Flash Flooding / Hydrology</div>
  <div class="panel-body">
<p><strong>Precipitation Estimates/Observations</strong></p>
<ul>
  <li><a href="/DCP/plot.phtml">Archived DCP Data Plotter</a>
    <br />Simple app to plot out current/historical DCP (river gauges) data for a site
    of your choice.</li>
	<li>Daily Climate Summary (AFOS: CLI Product) 
		<a href="climap.php">Interactive Map</a> or 
		<a href="clitable.php">Text Table</a></li>
  <li><a href="/COOP/cat.phtml">Daily COOP Observations</a></li>
  <li><a href="/rainfall/obhour.phtml">Hourly Precipitation Summaries</a> for ASOS</li>
  <li><a href="/rainfall/">IEM GIS Rainfall</a><br />
    Mostly Midwest products, but includes a conversion of MRMS to ERDAS Imagine Files.</li>
  <li><a href="http://mtarchive.geol.iastate.edu">MRMS Grib Archive</a>
    <br />Archive of a handful MRMS products in Grib Format.</li>
  <li><a href="/ASOS/current.phtml">Sortable Currents</a> for ASOS, COOP, etc</li>
</ul>

<p><strong>Flood Warnings/Forecasts</strong>
<br />Many of the apps in the "Severe Weather / VTEC" section are useful as well.</p>

<ul>
  <li><a href="/plotting/auto/?q=160">HML based forecasts and observations</a>
    <br />An archive of HML processed products is used to drive an interactive
    plot of forecasts and observations.</li>
  <li><a href="/cow/">IEM Cow Polygon Verification</a><br />
    Application does LSR based verification of Flash Flood Warnings.</li>
  <li><a href="/river/">River Forecast Point Monitor</a><br />
    Summarizes FLS statements by River by WFO/State.</li>
</ul>

  </div>
</div>

<div class="panel panel-default">
  <div class="panel-heading">Severe Weather / VTEC</div>
  <div class="panel-body">

<p>The <a href="/current/severe.phtml">Severe Weather Mainpage</a> has more
options listed.</p>

<p><strong>Data / Realtime Monitoring</strong></p>
<ul>
 <li><a href="/request/gis/watchwarn.phtml">GIS Shapefiles</a>
  <br />of archived Storm Based Warning polygons.</li>
 <li><a href="/iembot/">IEMBot</a>
  <br />Realtime chatrooms, twitter posting service, RSS feeds and more.</li> 
</ul>

<p><strong>Maps and Graphics</strong></p>
<ul>
  <li><a href="/plotting/auto/?q=92">Days Since VTEC Product</a>
  <br />Map of the number of days since a WFO issued a VTEC Product.</li>
 <li><a href="/raccoon/">IEM Raccoon</a>
  <br />Generate Microsoft Powerpoint of Storm Based Warnings for a WFO 
  and RADAR site of your choice.</li>
 <li><a href="/plotting/auto/?q=109">Number of VTEC Events by WFO</a>
  <br />Map of the number of VTEC events by WFO for a time period of your choice.</li>
 <li><a href="/timemachine/#59.0">NWS WWA Map Archive</a>
 <br />The IEM saves the national watch, warning, and advisory (WWA) map every
 five minutes.</li>
 <li><a href="/vtec/">VTEC Browser</a>
  <br />Interactive display of VTEC products.</li>
 <li><a href="/vtec/search.php"><i class="fa fa-search"></i> VTEC Search by Point or County/Zone</a>
  <br />Find issued VTEC WWA products by a given zone or county. Search
  for a storm based warning by point on a map.</li>
</ul>

<p><strong>Statistics / Metadata</strong></p>
<ul>
 <li><a href="/nws/list_tags.php">List SVR+TOR Warning Tags</a>
  <br />This application will list tags used in Severe Thunderstorm and
		Tornado warnings by NWS Office by Year.</li>
   <li><a href="/vtec/yearly_counts.php">Number of VTEC Events by year</a>
  <br />Table of the number of VTEC events by year.</li>

  <li><a href="/vtec/events.php">VTEC Events by WFO or State by Year</a>
  <br />Simple table listing any VTEC events by a given WFO or state for
  a given year.</li>

   <li><a href="/vtec/maxetn.php">Maximum VTEC EventID (ETN) by year</a>
  <br />This diagnostic prints out the maximum issued VTEC eventid (ETN) by
year.  A useful diagnostic for a NWS Office wishing to check their local VTEC
eventd database.</li>

<li><a href="/vtec/emergencies.php">Tornado + Flash Flood Emergencies listing</a>
<br />Simple table showing IEM indicated Tornado and Flash Flood Emergency 
events.</li>

 <li><a href="/cow/sbwsum.phtml">Summary Images of Daily Storm Based Warnings</a>
  <br />Displays just the storm based warning geometries for one UTC day
		at a time.</li>
 <li><a href="/cow/top10.phtml">Top 10 Polygon Sizes</a></li>
</ul>

<p><strong>Verification</strong></p>
<ul>
 <li><a href="vtec_obs.php">ASOS/AWOS Obs during WFO WWA</a>
  <br />Prints out ASOS/AWOS observations during selected VTEC warning types.</li>
 <li><a href="/cow/">IEM Cow</a>
  <br />Interactive Storm Based Warning verification app</li>
</ul>

<ul>
</ul>

  </div>
</div>

</div><div class="col-md-6">

<h3>NWS Processed Datasets</h3>

<div class="panel panel-default">
  <div class="panel-heading">ASOS/AWOS METAR</div>
  <div class="panel-body">
<ul>
	<li>Daily Climate Summary (AFOS: CLI Product) 
		<a href="climap.php">Interactive Map</a> or 
		<a href="clitable.php">Text Table</a></li>
 <li><a href="obs.php">Sortable Currents by WFO</a></li>
</ul>

<h4>Iowa AWOS RTP First Guess</h4>
<p>The IEM processes an auxillary feed of Iowa AWOS data direct
from the Iowa DOT.  This information is used to produce a more accurate
first guess at fields the NWS needs for their RTP product.</p>
<ul>
 <li><a href="/data/awos_rtp_00z.shef">0Z SHEF</a></li>
 <li><a href="/data/awos_rtp.shef">12Z SHEF</a></li>
</ul>

  </div>
</div><!-- ASOS/AWOS/METAR -->

<div class="panel panel-default">
  <div class="panel-heading">Cooperative Observer Program - COOP</div>
  <div class="panel-body">
<ul>
 <li><a href="/nws/coop-cnts.php">Monthly COOP Frequency Reports</a>
  <br />Quantity of observations received by variable for the COOP network</li>
 <li><a href="/COOP/current.phtml">Sortable Current COOP Reports</a>
		<br />View today's COOP reports by WFO or by state.  Includes derived
		frozen to liquid ratio and SWE reports.</li>
</ul>
  </div>
</div>


<div class="panel panel-default">
  <div class="panel-heading">HADS / DCP / GOES</div>
  <div class="panel-body">
<ul>
 <li><a href="/DCP/plot.phtml">Archived DCP Data Plotter</a>
 <br />Simple app to plot out current/historical DCP (river gauges) data for a site
 of your choice.</li>
</ul>
  </div>
</div>

<div class="panel panel-default">
  <div class="panel-heading">Local Storm Reports (LSR)</div>
  <div class="panel-body">
<p>The IEM processes LSRs issued by the NWS in real-time. A number of
	applications on this website utilize this source of reports.</p>
<ul>
	<li><a href="/data/lsr_snowfall.png">Snowfall Analysis [Iowa]</a> of
		recent LSRs. <a href="/data/lsr_snowfall_nv.png">Iowa map without
		labels</a>.</li>
	<li><a href="/data/mw_lsr_snowfall.png">Snowfall Analysis [MidWest]</a>
		of recent LSRs.</li>
  
    <li>Past 24 hours of Storm Reports
    <br /><a href="/data/gis/shape/4326/us/lsr_24hour.zip">ESRI Shapefile</a>, 
    <a href="/data/gis/shape/4326/us/lsr_24hour.csv">Comma Delimited</a>,
    <a href="/data/gis/shape/4326/us/lsr_24hour.geojson">GeoJSON</a>
    <br />The IEM parses the realtime feed of NWS Local Storm Reports.  Every
    5 minutes, a process collects up the last 24 hours worth of reports and
    dumps them to the above files.</li>

     <li><a href="/request/gis/lsrs.phtml">Archived Local Storm Reports</a>
 <br />Generate a shapefile of LSRs for a period of your choice dating back 
  to 2003!</li>
		<li><a href="/lsr/">Local Storm Report App</a></li>
</ul>
  </div>
</div>


<div class="panel panel-default">
  <div class="panel-heading">NEXRAD RADAR</div>
  <div class="panel-body">
<ul>
 <li><a href="/request/gis/nexrad_storm_attrs.php">NEXRAD Storm Attributes</a>
 <br />Download shapefiles of NEXRAD storm attribute data and view histogram 
 summaries.</li>
</ul>
  </div>
</div>

<div class="panel panel-default">
  <div class="panel-heading">Storm Prediction Center Products</div>
  <div class="panel-body">
<ul>
 <li><a href="/GIS/apps/rview/watch.phtml">Convective Watches Information</a>
  <br />Lists out some simple details on each convective watch.</li>
 <li><a href="/nws/spc_outlook_search/"><i class="fa fa-search"></i> SPC Outlook / MCD search by point</a>
  <br />Allows answering of the question of when was a given point last under
some convective outlook or the number of outlooks for a given point.</li>
</ul>
  </div>
</div>


<div class="panel panel-default">
  <div class="panel-heading">Numerical Model Data</div>
  <div class="panel-body">
<ul>
 <li><a href="/mos/">Model Output Statistics</a>
 <br />Archive of MOS back to 3 May 2007.</li>
 <li>HRRR MidWest 1km Reflectivity [animated GIF]
 <br />Animated GIF of HRRR Forecasted Reflectivity. 
  <a href="/data/model/hrrr/hrrr_1km_ref.gif">Latest Run</a> or
  <a href="/timemachine/#61.0">Archived plots</a></li> 
</ul>
  </div>
</div>

<div class="panel panel-default">
  <div class="panel-heading">Text Product Archives</div>
  <div class="panel-body">
<ul>
 <li><a href="/wx/afos/">AFOS Product Viewer</a>
  <br />Web based version of TextDB.</li>
 <li><a href="/wx/afos/list.phtml">View Products by WFO by Date</a>
  <br />View quick listings of issued products by forecast office and by 
    date.</li>
</ul>
  </div>
</div>


</div>
</div><!-- ./row -->

EOF;
$t->render('single.phtml');
?>