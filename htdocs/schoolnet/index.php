<?php 
include("../../config/settings.inc.php");
include_once "../../include/myview.php";
$network = isset($_REQUEST["network"]) ? $_REQUEST["network"]: "KCCI";

$t = new MyView();
$t->thispage = 'networks-schoolnet';
$t->title = "School Network";

if ($network == 'KCCI'){
	$c = <<<EOF
<a href="alerts/">About wind gust alerts</a> sent to the Weather Service.

<table width="100%" bgcolor="white" border=0>
<tr><td valign="top" width="300">

<p><h3>Current Data</h3>
<ul>
 <li><a href="current.phtml">Current Conditions</a> (sortable)</li>
 <li><a href="/GIS/apps/snet/raining.php">Where's it raining?</a></li>
</ul>

<p><h3>Station Plots</h3>
<ul>
 <li><a href="/GIS/apps/mesoplot/plot.php">Rapid Update every Minute</a></li>
 <li><a href="/GIS/apps/mesoplot/plot.php?zoom=1">Zoomed in on Des Moines</a></li>
</ul>

</td><td valign="top" width="350">

  <p><h3>Historical Data</h3>
<ul>
 <li><a href="/schoolnet/dl/">Download</a> from the archive!</a></li>
 <li><a href="/cgi-bin/precip/catSNET.py">Hourly Rainfall</a> tables</a></li>
 <li><a href="/schoolnet/rates/">Rainfall Rates</a></li>
</ul>

<p><h3>QC Info</h3>
<ul>
 <li><a href="/QC/offline.php">Stations Offline</a></li>
 <li><a href="/QC/madis/network.phtml?network=KCCI">MADIS QC Values</a></li>
  <li>MADIS QC Messages:
  <br /><a href="http://madis-data.noaa.gov/qcms_data/qc20/qchour.txt">Last Hour</a>
  <br /><a href="http://madis-data.noaa.gov/qcms_data/qc20/qcday.txt">Today</a>
  <br /><a href="http://madis-data.noaa.gov/qcms_data/qc20/qcweek.txt">Weekly</a>
  <br /><a href="http://madis-data.noaa.gov/qcms_data/qc20/qcmonth.txt">Monthly</a>
  </li>
</ul>

<p><h3>Plotting Time Series</h3>
<ul>
 <li><a href="/plotting/snet/1station_1min.php">1 station</a> [1 minute data]</li>
 <li><a href="/plotting/compare/">Generate Interactive Comparisons</a> between two sites of your choice.</li>
</ul></p>

</td></tr></table>

</td></tr></table>
EOF;
}
else if ($network == 'KELO'){
	$c = <<<EOF
<a href="alerts/">About wind gust alerts</a> sent to the Weather Service.

<table width="100%" bgcolor="white" border=0>
<tr><td colspan=2>KELO's WeatherNet sites were added to the IEM on 11 Sept
2002.</td></tr>

<tr><td valign="top" width="300">

<p><h3>Current Data</h3>
<ul>
 <li><a href="current.phtml">Current Conditions</a> (sortable)</li>
 <li><a href="/GIS/apps/snet/raining.php">Where's it raining?</a></li>
</ul>

<p><h3>Station Plots</h3>
<ul>
 <li><a href="/GIS/apps/mesoplot/plot.php?network=KELO">Rapid Update</a></li>
 <li><a href="/GIS/apps/php/currents.phtml?layers[]=map&network=KELO&layers[]=labels&var=pres">Barometer</a></li>
 <li><a href="/GIS/apps/php/currents.phtml?layers[]=map&network=KELO&layers[]=labels&var=pday">Today's Precip Accum</a></li>
</ul>

<p><h3>Historical Data</h3><br><ul>
 <li><a href="/schoolnet/dl/">Download</a> from the archive!</a></li>
 <li><a href="/cgi-bin/precip/catSNET.py">Hourly Precipitation</a>
 tables</a></li></ul>

<p><h3>QC Info</h3>
<ul>
 <li><a href="/QC/offline.php">Stations Offline</a></li>
 <li><a href="/QC/madis/network.phtml?network=KELO">MADIS QC Values</a></li>
  <li>MADIS QC Messages:
  <br /><a href="http://madis-data.noaa.gov/qcms_data/qc20/qchour.txt">Last Hour</a>
  <br /><a href="http://madis-data.noaa.gov/qcms_data/qc20/qcday.txt">Today</a>
  <br /><a href="http://madis-data.noaa.gov/qcms_data/qc20/qcweek.txt">Weekly</a>
  <br /><a href="http://madis-data.noaa.gov/qcms_data/qc20/qcmonth.txt">Monthly</a>
  </li>
</ul>


</td><td valign="top" width="350">

<p><h3>Plotting Time Series</h3>
<ul>
 <li><a href="/plotting/snet/1station.php">1 station</a> [20 minute data]</li>
 <li><a href="/plotting/snet/1station_1min.php">1 station</a> [1 minute data]</li>
 <li><a href="/plotting/compare/">Generate Interactive Comparisons</a> between two sites of your choice.</li>
</ul></p>

</td></tr></table>

</td></tr></table>
EOF;
}
else if ($network == 'KIMT'){
	$c = <<<EOF

<ul>
 <li><a href="current.phtml">Current Conditions</a> (sortable)</li>
 <li><a href="/GIS/apps/snet/raining.php?tv=KIMT">Where is it raining?</a></li>
 <li><a href="/plotting/snet/1station_1min.php">1 minute traces</a></li>
 <li><a href="/GIS/apps/mesoplot/plot.php?network=KIMT">Rapid Update Mesoplot</a></li>
 <li><a href="/plotting/compare/">Generate Interactive Comparisons</a> between two sites of your choice.</li>
 <li><a href="/QC/madis/network.phtml?network=KIMT">MADIS Raw QC</a>.</li>
  <li>MADIS QC Messages:
  <br /><a href="http://madis-data.noaa.gov/qcms_data/qc20/qchour.txt">Last Hour</a>
  <br /><a href="http://madis-data.noaa.gov/qcms_data/qc20/qcday.txt">Today</a>
  <br /><a href="http://madis-data.noaa.gov/qcms_data/qc20/qcweek.txt">Weekly</a>
  <br /><a href="http://madis-data.noaa.gov/qcms_data/qc20/qcmonth.txt">Monthly</a>
  </li>
</ul>

</td></tr></table>
EOF;
}

$t->content = <<<EOF

<h3>SchoolNets</h3>

<p>As the name implies, these automated weather stations are
located at schools throughout the state.  Currently, 
<a href="http://www.kcci.com/">KCCI-TV</a> (Des Moines, IA),
<a href="http://www.keloland.com">KELO-TV</a> (Sioux Falls, SD), 
and <a href="http://www.kimt.com">KIMT-TV</a> (Mason City, IA) have 
graciously provided
the IEM with the ability to process data from their observing networks.  

<p><a href="/sites/locate.php?network=KCCI">KCCI Locations</a>, 
<a href="/sites/locate.php?network=KELO">KELO Locations</a>, and
<a href="/sites/locate.php?network=KIMT">KIMT Locations</a></p>

<div class="row well">
 <div class="col-md-4 col-sm-4">
<a href="?network=KCCI" style="text-decoration: none;">
   <img src="/schoolnet/images/kcci8.jpg" border="0"><br /><b>SchoolNet8</b></a>
   
 </div>
 <div class="col-md-4 col-sm-4">
<a href="?network=KELO" style="text-decoration: none;">
    <img src="/schoolnet/images/kelo.png" border="0"><br /><b>WeatherNet</b></a>
 </div>
 <div class="col-md-4 col-sm-4">
<a href="?network=KIMT" style="text-decoration: none;">
    <img src="/schoolnet/images/kimt_logo.png" border="0"><br /><b>StormNet</b></a>

    </div></div>


{$c}



<div class="alert alert-warning">Many of the school net stations are not located in good
meteorological locations.  While the stations may be accurate, their data
may not be representative of the area in general.
Often, they are placed on top of buildings and may
have obstructions which could skew wind and temperature readings.  The
stations are placed at schools for educational purposes and to get students
interested in the weather.</div>
EOF;
$t->render('single.phtml');
?>