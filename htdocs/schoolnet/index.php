<?php 
require_once "../../config/settings.inc.php";
require_once "../../include/myview.php";

$t = new MyView();

$t->content = <<<EOF

<h3>SchoolNet</h3>

<p>Over the years, the IEM partnered with 
<a href="http://www.kcci.com/">KCCI-TV</a> (Des Moines, IA),
<a href="http://www.keloland.com">KELO-TV</a> (Sioux Falls, SD), 
and <a href="http://www.kimt.com">KIMT-TV</a> (Mason City, IA) to collect data
from their respective school-based weather stations.  Sadly, the observation
equipment fell into disrepair and the various networks were wound down or
replaced with proprietary solutions.
<strong>On 13 May 2019, all data collection was discontinued.</strong></p>

<p>This page presents some legacy links and means yet to download the data.</p>

<div class="row">
  <div class="col-md-4">
    <h4>Information</h4>
    <ul>
      <li><a href="alerts/">About wind gust alerts</a> sent to the Weather Service.</li>
    </ul>
  </div>

  <div class="col-md-4">
  <h4>Historical Data</h4>
  <ul>
   <li><a href="/schoolnet/dl/">Download</a> from the archive!</a></li>
   <li><a href="/cgi-bin/precip/catSNET.py">Hourly Rainfall</a> tables</a></li>
   <li><a href="/schoolnet/rates/">Rainfall Rates</a></li>
  </ul>

  </div>
  <div class="col-md-4">
  <h3>Plotting Time Series</h3>
  <ul>
   <li><a href="/plotting/snet/1station.php">1 station</a> [20 minute data]</li>
   <li><a href="/plotting/snet/1station_1min.php">1 station</a> [1 minute data]</li>
   <li><a href="/plotting/compare/">Generate Interactive Comparisons</a> between two sites of your choice.</li>
  </ul>

  </div>

</div>

<div class="alert alert-warning">Many of the school net stations are not located in good
meteorological locations.  While the stations may be accurate, their data
may not be representative of the area in general.
Often, they are placed on top of buildings and may
have obstructions which could skew wind and temperature readings.  The
stations are placed at schools for educational purposes and to get students
interested in the weather.</div>
EOF;
$t->render('single.phtml');
