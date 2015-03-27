<?php
include("../../config/settings.inc.php");
include("../../include/myview.php");
$t = new MyView();
define("IEM_APPID", 11);
$t->title = "Agricultural Weather/Climate Information";
$t->thispage = "iem-info";

$y = date("Y");
$t->content = <<<EOF
<ol class="breadcrumb">
  <li><a href="/">IEM Homepage</a></li>
  <li class="active">IEM Ag Weather/Climate Information</li>
</ol>

<h3>Are you looking for data?</h3>

<table class="table table-striped table-bordered">
<thead>
<tr>
 <th rowspan="2">Variable</th>
 <th colspan="6">Timescale / Reporting Interval</th>
</tr>
<tr>
<th>Seconds/Minutes</th>
<th>Hourly</th>
<th>Daily</th>
<th>Weekly/Monthly</th>
<th>Seasonal</th>
<th>Yearly</th>
</tr>
</thead>
<tbody>

<tr><td>Air Temperature</td>
<td><a href="/schoolnet/">SchoolNet</a> is the only option for sub-hourly
data, but it is not of the best quality and the sensors are located on the top
of buildings.</td>
<td><a href="/ASOS/">ASOS/AWOS</a> are stations located at airports and are
the baseline weather observation network. The 
<a href="/agclimate">ISU Soil Moisture</a> network has data for Iowa.</td>
<td><a href="/COOP/">NWS COOP</a> has high quality high and low temperature
reports for 24 hour periods, not always for the calendar day.</td>
<td colspan="3">The <a href="/climodat/">Climodat</a> reports contain summarized
data from the NWS COOP network.</td>
</tr>

<tr><td>Precipitation (liquid + melted snow)</td>
 <td>The IEM processes the one minute <a href="/request/asos/1min.phtml">Iowa ASOS</a>
 data, but there is a month delay for receipt of this data.</td>
 <td>The <a href="/ASOS/">ASOS</a> (not AWOS) sites include a heated sensor that
 melts snowfall to produce liquid equivalent.</td>
 <td rowspan="2">The <a href="/COOP/">NWS COOP</a> network report precipitation totals that
 include melted snowfall.</td>
 <td colspan="3" rowspan="2"><a href="/climodat/">Climodat Reports</a> contain summarized precipitation
 data from the NWS COOP network.</td>
</tr>

<tr><td>Rainfall (liquid only)</td>
 <td>The <a href="/schoolnet/">SchoolNet</a> sensors do report minute rainfall, 
 but the data is not of great quality.</td>
 <td>The <a href="/ASOS/">ASOS/AWOS</a> sites report hourly rainfall as well as
 the <a href="/agclimate/">ISU Soil Moisture</a> network.</td>
</tr>


<tr><td>Solar Radiation</td>
<td>Most of the <a href="/schoolnet/">SchoolNet</a> sites report radiation
data at minute intervals, but the data is not of great quality.</td>
<td>The <a href="/agclimate/">ISU Soil Moisture</a> network collects solar 
radiation data hourly.</td>
<td>The <a href="/agclimate/">ISU Soil Moisture</a> network makes daily 
summaries available. The IEM also provides estimated radiation data for download
for <a href="/request/coop/fe.phtml">NWS COOP</a> sites based on model analyses.</td>
<td colspan="3">Summarized data for this timescale does not exist on the IEM 
at this time.</td>
</tr>

<tr><td>Snowfall</td>
 <td>Does not exist</td>
 <td>The NWS has paid snowfall observers that report 6 hour snowfall totals, but
 the IEM does not have a good interface to get this data.</td>
 <td>The IEM collects the <a href="/COOP/cat.phtml">24 hour snowfall reports</a>
 from the NWS COOP network.</td>
 <td></td>
 <td></td>
 <td></td>
</tr>

</tbody>
</table>

<p>

<table class="table table-striped">
<tr>
 <th></th>
 <th>Current</th>
 <th>Growing Season</th>
</tr>



<tr>
  <th>Growing Degree Days</th>
  <td><a href="/plotting/coop/gddprobs.phtml">Probabilies + Scenarios</a></td>
  <td><a href="/GIS/apps/coop/gsplot.phtml?var=gdd50&year={$y}">Map of Totals</a>
  <br /><a href="/plotting/coop/acc.phtml">Single Site Graphs</a></td>
</tr>

<tr>
  <th>Precipitation</th>
  <td><a href="/data/summary/today_prec.png">Today's total</a></td>
  <td><a href="/GIS/apps/coop/gsplot.phtml?var=prec&smonth=1&sday=1&year={$y}">Map of Totals</a>
  <br /><a href="/plotting/coop/acc.phtml">Single Site Graphs</a></td>
</tr>


<tr>
 <th>Soil Moisture</th>
 <td>
 <a href="http://wepp.mesonet.agron.iastate.edu/GIS/sm.phtml?pvar=vsm">Modelled Estimates</a>
 <br /><span class="badge">new!</span> <a href="/agclimate/">ISU Soil Moisture Network</a>
 </td>
 <td></td>
</tr>

<tr>
 <th>Soil Temperatures</th>
 <td><a href="/agclimate/soilt.php">County Estimates</a>
  <br /><a href="/timemachine/#57.0">Archived County Estimates</a>
 <br /><span class="badge">new!</span> <a href="/agclimate/">ISU Soil Moisture Network</a>
 </td>
 <td></td>
</tr>

<tr>
  <th>Stress Degree Days</th>
  <td></td>
  <td><a href="/GIS/apps/coop/gsplot.phtml?var=sdd86&year={$y}">Map of Totals</a>
  <br /><a href="/plotting/coop/acc.phtml">Single Site Graphs</a></td>
</tr>

</table>

<h4>Aridity Index for Corn Belt</h4>

<blockquote>
 How Temperature and Precipitation have influenced corn by reporting district. 
 <a href="/~windmill/AIpage.html">view here</a>.
</blockquote>

<h4>Historical Freeze Risk</h4>

<blockquote>An air temperature less than 27 is generally considered to be the Hard Freeze, 
that is a crop killing event, although plant damage and yield loss is often observed at 
less extreme low temperatures. Crop threshold temperatures for plant damage in Fall differ
from Spring thresholds (mainly because of plant size/height).</blockquote>

<ul>
 <li><a href="/COOP/freezing.php">Fall Freezing Dates</a></li>
 <li><a href="/climodat/index.phtml?station=IA0200&report=22">First Fall Freeze Probabilities</a></li>
 <li><a href="/plotting/coop/threshold_histogram_fe.phtml">Winter Minimum Temperature Frequencies</a></li>
</ul>

<h4>External Links</h4>
<ul>
 <li><a href="http://www.iowaagriculture.gov/climatology.asp">State of Iowa Climatologist</a></li>
 <li><a href="http://www.nass.usda.gov/Charts_and_Maps/Crop_Progress_&_Condition/index.asp">USDA Charts &amp; Maps of Crop Progress</a></li>
 <li><a href="http://www.nass.usda.gov/Publications/State_Crop_Progress_and_Condition/index.asp">USDA State Crop Progress &amp; Condition</a></li>
 <li><a href="http://planthardiness.ars.usda.gov/PHZMWeb/">USDA Plant Hardiness Map</a> (enter
 your zipcode or click on the map)</li>
</ul>
EOF;
$t->render('single.phtml');
?>
