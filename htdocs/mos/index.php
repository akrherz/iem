<?php 
define("IEM_APPID", 74);
require_once "../../config/settings.inc.php";
require_once "../../include/myview.php";
$t = new MyView();
$t->title = "Model Output Statistics (MOS)";
$t->thispage = "archive-mos"; 

$t->content = <<<EOF

<h3>Archived Model Output Statistics (MOS)</h3>

<p>The National Weather Service operates a number of operational
weather prediction models.  These models produce a gridded forecast that is
then processed thru a series of equations (Model Output Statistics) to 
produce a site specific forecast. You can find out more about
<a href="http://www.weather.gov/mdl/synop/products.php">MOS</a> on the
NWS's website.  The IEM maintains an interactive MOS archive to support
local research and makes it available for others to use as well.</p>

<p><strong>Archive Status:</strong> 
<table class="table table-condensed table-striped">
<thead><tr><th>Model</th><th>Start</th><th>End</th></tr></thead>
<tbody>
<tr><th>AVN</th><td>1 June 2000</td><td>16 Dec 2003</td></tr>
<tr><th>ETA</th><td>24 Feb 2002</td><td>9 Dec 2008</td></tr>
<tr><th>GFS</th><td>16 Dec 2003</td><td>--Realtime--</td></tr>
<tr><th>NAM</th><td>9 Dec 2008</td><td>--Realtime--</td></tr>
<tr><th>NBS [0, 7, 12, 19z]</th><td>7 Nov 2018</td><td>--Realtime--</td></tr>
</tbody>
</table>
<br />The MOS products are processed in realtime and immediately available from
the applications listed below.

<h3>Current Tools:</h3>
<ul>
 <li><a href="table.phtml">Interactive MOS Tables</a>
  <br />Generates a simple table of how a variable changes over time
   and by model run.</li>
 <li><a href="http://www.meteor.iastate.edu/~ckarsten/bufkit/image_loader.phtml">Meteogram Generator</a>
  <br />Fancy application to generate graphs of current MOS data.</li>
 <li><a href="csv.php">Comma Delimited output</a>
  <br />Simple web service provides csv data for a site and for a period
   of ten days forecast.  An example URL call would be:<br />
  <pre>
csv.php?station=KAMW&valid=2009-01-10%2012:00              (all data 10 days)
csv.php?station=KAMW&runtime=2009-01-10%2012:00&model=GFS  (explicit)
</pre></li>
 <li><a href="fe.phtml">Download the raw data!</a>
  <br />This application returns the raw MOS data for a location and time
  period of your choice.</li>
 <li><a href="/plotting/auto/?q=37">Monthly Plots of Station Temperature Forecasts</a>
  <br />This application creates a graph of daily MOS forecasts and actual
		temperatures for a month and station of your choice.</li>
</ul>

<p><strong>Note:</strong> MOS variables are stored as their raw encodings 
in the text product, except <strong>wdr</strong> (wind direction) which is
multiplied by 10 for its true value.

<h3>Current Plots</h3>
<div class="row">
	<div class="col-md-6">
<a href="/timemachine/#52.0"><img src="/data/conus_nam_mos_T_bias.png" 
 class="img img-responsive" border="1"/></a>
 </div>
	<div class="col-md-6">
		
<a href="/timemachine/#51.0"><img src="/data/conus_gfs_mos_T_bias.png" 
 class="img img-responsive" border="1"/></a>
 </div>
</div>
EOF;
$t->render('single.phtml');
?>
