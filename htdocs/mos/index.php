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
<tr><th>GFS LAMP (abbr LAV) [0, 6, 12, 18]</th><td>12 Jul 2020</td><td>--Realtime--</td></tr>
<tr><th>GFS Extended (abbr MEX)</th><td>12 Jul 2020</td><td>--Realtime--</td></tr>
<tr><th>NAM</th><td>9 Dec 2008</td><td>--Realtime--</td></tr>
<tr><th>NBS [0, 7, 12, 19z]</th><td>7 Nov 2018</td><td>25 Feb 2020</td></tr>
<tr><th>NBS [1, 7, 13, 19z]</th><td>26 Feb 2020</td><td>--Realtime--</td></tr>
</tbody>
</table>
<br />The MOS products are processed in realtime and immediately available from
the applications listed below.

<h3>Current Tools:</h3>
<ul>
 <li><a href="/wx/afos/">ASCII Data Tables</a>
 <br />The raw text-based MOS data comes in collectives with multiple sites
 found within one product.  The IEM splits these and then assigns 6 character
 AWIPS/AFOS like IDs to them, such that you can easily retrieve the raw ASCII
 MOS data.  The general identifier form is <code>&lt;model&gt;&lt;3-char station&gt;</code>.
 For example, <code>LAVDSM</code> for GFS LAMP for Des Moines.</li>

 <li><a href="/cgi-bin/afos/retrieve.py?pil=LAVDSM">Sample link to latest GFS LAMP for KDSM</a>
 <br />Please see the discussion above about the identifiers used.  This page just
 provides the text and not much else.  Best for if you want to bookmark direct links
 or do some of your own MOS parsing, gasp.  Just adjust the <code>pil=</code> value
 as you see fit.</li>

 <li><a href="table.phtml">Interactive MOS Tables</a>
  <br />Generates a simple table of how a variable changes over time
   and by model run.</li>
 <li><a href="https://meteor.geol.iastate.edu/~ckarsten/bufkit/image_loader.phtml">Meteogram Generator</a>
  <br />Fancy application to generate graphs of current MOS data.</li>
 <li><a href="/api/1/docs#/default/service_mos__fmt__get">Comma Delimited / JSON output</a>
  <br />Simple web service provides csv/json data for one or more sites for a
  given model and optional runtime.  An example URL call would be:<br />
  <pre>
/api/1/mos.txt?station=KAMW&runtime=2009-01-10%2012:00Z&model=GFS  (explicit)
/api/1/mos.txt?station=KAMW&model=GFS  (last available GFS run for Ames in csv)
/api/1/mos.json?station=KAMW&model=GFS  (last available GFS run for Ames in JSON)
/api/1/mos.txt?station=KDSM&station=KAMW&model=GFS  (last available GFS run for Ames and Des Moines)
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
