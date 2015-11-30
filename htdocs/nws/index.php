<?php
include("../../config/settings.inc.php");
include("../../include/myview.php");
$t = new MyView();
$t->title = "NWS Related Information";
$t->thispage = "iem-info";

$t->north = <<<EOF
<h3>IEM Data for NWS Users</h3><p>

<div class="alert alert-info">
Please <a href="/info/contacts.php">suggest</a> features for this page.  
We are looking to collect all relevant IEM provided archives/applications 
of NWS data.</div>
EOF;

$t->west = <<<EOF
<h4>IEM Apps</h4>
<ul>
 <li><a href="/DCP/plot.phtml">Archived DCP Data Plotter</a>
 <br />Simple app to plot out current/historical DCP (river gauges) data for a site
 of your choice.</li>
	<li>Daily Climate Summary (AFOS: CLI Product) 
		<a href="climap.php">Interactive Map</a> or 
		<a href="clitable.php">Text Table</a></li>
 <li><a href="/COOP/current.phtml">Sortable Current COOP Reports</a>
		<br />View today's COOP reports by WFO or by state.  Includes derived
		frozen to liquid ratio and SWE reports.</li>
 <li><a href="obs.php">Sortable Currents by WFO</a></li>
 <li><a href="/timemachine/#59.0">NWS WWA Map Archive</a>
 <br />The IEM saves the national watch, warning, and advisory (WWA) map every
 five minutes.</li>
</ul>

<h4>Iowa AWOS RTP First Guess</h4>
<blockquote>The IEM processes an auxillary feed of Iowa AWOS data direct
from the Iowa DOT.  This information is used to produce a more accurate
first guess at fields the NWS needs for their RTP product.</blockquote>
<ul>
 <li><a href="/data/awos_rtp_00z.shef">0Z SHEF</a></li>
 <li><a href="/data/awos_rtp.shef">12Z SHEF</a></li>
</ul>

<h4>Local Storm Reports (LSR)</h4>
<p>The IEM processes LSRs issued by the NWS in real-time. A number of
	applications on this website utilize this source of reports.</p>
<ul>
	<li><a href="/data/lsr_snowfall.png">Snowfall Analysis [Iowa]</a> of
		recent LSRs. <a href="/data/lsr_snowfall_nv.png">Iowa map without
		labels</a>.</li>
	<li><a href="/data/mw_lsr_snowfall.pnh">Snowfall Analysis [MidWest]</a>
		of recent LSRs.</li>
	<li><a href="/data/gis/shape/4326/us/lsr_24hour.zip">Past 24 hours of Storm Reports</a>
 <br />A shapefile of Local Storm Reports (LSRs) valid for the past 24 hours.  The file is updated every 5 minutes.</li>
 <li><a href="/request/gis/lsrs.phtml">Archived Local Storm Reports</a>
 <br />Generate a shapefile of LSRs for a period of your choice dating back 
  to 2003!</li>
		<li><a href="/lsr/">Local Storm Report App</a></li>
</ul>

<h4>Model Data</h4>
<ul>
 <li><a href="/mos/">Model Output Statistics</a>
 <br />Archive of MOS back to 3 May 2007.</li>
 <li>HRRR MidWest 1km Reflectivity [animated GIF]
 <br />Animated GIF of HRRR Forecasted Reflectivity. 
  <a href="/data/model/hrrr/hrrr_1km_ref.gif">Latest Run</a> or
  <a href="/timemachine/#61.0">Archived plots</a></li> 
 </ul>

<h4>NEXRAD / RADAR Data</h4>
<ul>
 <li><a href="/request/gis/nexrad_storm_attrs.php">NEXRAD Storm Attributes</a>
 <br />Download shapefiles of NEXRAD storm attribute data and view histogram 
 summaries.</li>
</ul>

EOF;
$t->east = <<<EOF

<div class="well">
<strong>Did you see an image posted to social media with the IEM logo on it?</strong><br />
	Daryl posts some interesting graphics to his 
	<a href="https://twitter.com/akrherz">Twitter @akrherz</a> page.  Generally,
	these are one-off images that are not available for dynamic generation on
	this website.
</div>

<h4>Valid Time Extent Code (VTEC) Apps</h4>
<ul>
 <li><a href="vtec_obs.php">ASOS/AWOS Obs during WFO WWA</a>
  <br />Prints out ASOS/AWOS observations during selected VTEC warning types.</li>
 <li><a href="/plotting/auto/?q=109">Number of VTEC Events by WFO</a>
  <br />Map of the number of VTEC events by WFO for a time period of your choice.</li>
   <li><a href="/vtec/yearly_counts.php">Number of VTEC Events by year</a>
  <br />Table of the number of VTEC events by year.</li>
  <li><a href="/plotting/auto/?q=92">Days Since VTEC Product</a>
  <br />Map of the number of days since a WFO issued a VTEC Product.</li>
 <li><a href="/vtec/">VTEC Browser</a>
  <br />Interactive display of VTEC products.</li>
 <li><a href="/vtec/search.php">VTEC Search by Point or County/Zone</a>
  <br />Find issued VTEC WWA products by a given zone or county. Search
  for a storm based warning by point on a map.</li>
</ul>

<h4>Storm Based Warnings</h4>
<ul>
 <li><a href="/cow/">IEM Cow</a>
  <br />Interactive Storm Based Warning verification app</li>
   <li><a href="/raccoon/">IEM Raccoon</a>
  <br />Generate Microsoft Powerpoint of Storm Based Warnings for a WFO 
  and RADAR site of your choice.</li>
 <li><a href="/request/gis/watchwarn.phtml">GIS Shapefiles</a>
  <br />of archived Storm Based Warning polygons.</li>
 <li><a href="/nws/list_tags.php">List SVR+TOR Warning Tags</a>
  <br />This application will list tags used in Severe Thunderstorm and
		Tornado warnings by NWS Office by Year.</li>
</ul>

<h4>Text Product Archives</h4>
<ul>
 <li><a href="/wx/afos/">AFOS Product Viewer</a>
  <br />Web based version of TextDB.</li>
 <li><a href="/wx/afos/list.phtml">View Products by WFO by Date</a>
  <br />View quick listings of issued products by forecast office and by 
    date.</li>
</ul>
EOF;
$t->render('single.phtml');
?>