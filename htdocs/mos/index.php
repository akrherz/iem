<?php 
include("../../config/settings.inc.php");
define("IEM_APPID", 74);
$THISPAGE = "archive-mos";
$TITLE = "IEM | Model Output Statistics";
include("$rootpath/include/header.php"); ?>

<div style="width:640px;">

<h3 class="heading">Archived Model Output Statistics (MOS)</h3>

<p class="story">The National Weather Service operates a number of operational
weather prediction models.  These models produce a gridded forecast that is
then processed thru a series of equations (Model Output Statistics) to 
produce a site specific forecast. You can find out more about
<a href="http://www.weather.gov/mdl/synop/products.php">MOS</a> on the
NWS's website.  The IEM maintains an interactive MOS archive to support
local research and makes it available for others to use as well.</p>

<p><strong>Archive Status:</strong> 
<table cellpadding='3' cellspacing='0' border='1'>
<tr><th>Model</th><th>Start</th><th>End</th></tr>
<tr><th>AVN</th><td>1 June 2000</td><td>16 Dec 2003</td></tr>
<tr><th>ETA</th><td>24 Feb 2002</td><td>9 Dec 2008</td></tr>
<tr><th>GFS</th><td>16 Dec 2003</td><td>--Realtime--</td></tr>
<tr><th>NAM</th><td>9 Dec 2008</td><td>--Realtime--</td></tr>
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
csv.php?station=KAMW&ts=2009-01-10%2012:00                  (all data 10 days)
csv.php?station=KAMW&runtime=2009-01-10%2012:00&model=GFS  (explicit)
</pre></li>
 <li><a href="fe.phtml">Download the raw data!</a>
  <br />This application returns the raw MOS data for a location and time
  period of your choice.</li>
</ul>

<p><strong>Note:</strong> MOS variables are stored as their raw encodings 
in the text product, except <strong>wdr</strong> (wind direction) which is
multiplied by 10 for its true value.

<h3>Current Plots</h3>
 <div style="float:left; margin:5px;">
<a href="../timemachine/#52.0"><img src="../data/conus_nam_mos_T_bias.png" 
 width="320" border="1"/></a>
 </div>
 
 <div style="float:left; margin:5px;">
<a href="../timemachine/#51.0"><img src="../data/conus_gfs_mos_T_bias.png" 
 width="320" border="1"/></a>
 </div>
 
<p>We will probably back fill the archive based on how much interest this
application generates, so please <a href="../info/contacts.php">let us</a>
know if you find this page useful. 

</div>

<?php include("$rootpath/include/footer.php"); ?>
