<?php
require_once "../../config/settings.inc.php";
define("IEM_APPID", 11);
require_once "../../include/myview.php";
$t = new MyView();
$t->title = "Agricultural Weather/Climate Information";

$y = date("Y");
$t->content = <<<EOF
<ol class="breadcrumb">
  <li><a href="/">IEM Homepage</a></li>
  <li class="active">IEM Ag Weather/Climate Information</li>
</ol>

<p>The IEM website contains data from many <a href="/sites/locate.php">different observation networks</a>. While 
you may know what you are looking for, figuring out which network has this data 
is tricky.  This table is an attempt to help you locate the data / product you
need.  Please do <a href="/info/contacts.php">contact us</a> with your 
questions!</p>

<p>IEM's most popular applications:
<a role="button" class="btn btn-success" href="/plotting/auto/"><i class="fa fa-signal"></i> Automated Data Plotting</a>
<a role="button" class="btn btn-success" href="/climodat/"><i class="fa fa-list-alt"></i> Climodat</a>
<a role="button" class="btn btn-success" href="/plotting/auto/?q=108"><i class="fa fa-signal"></i> Single Site Graphs</a>
<a role="button" class="btn btn-success" href="/COOP/current.phtml"><i class="fa fa-refresh"></i> Sortable Currents</a>
</p>


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
<td>
<a href="/agclimate/">ISU Soil Moisture</a> stations record real-time data
at one minute intervals.  <a href="/ASOS/">ASOS</a> also provides data at
such frequency, but it is delayed by ~24 hours.
</td>
<td><a href="/ASOS/">ASOS/AWOS</a> are stations located at airports and are
the baseline weather observation network. The 
<a href="/agclimate">ISU Soil Moisture</a> network has data for Iowa.</td>

<td>
<a href="/COOP/">NWS COOP</a> has high quality high and low temperature
reports for 24 hour periods, not always for the calendar day.
<ul>
 <li><a href="/data/coopHighLow.gif">COOP High + Low Temperature</a></li>
 <li><a href="/data/summary/asos_hilo.png">ASOS High/Low Temperature</a></li>
 <li><a href="/data/awos_rtp.shef">12Z AWOS RTP First Guess</a> Formatted
product generated for the National Weather Service for comparison.</li>
<li><a href="/data/climate/iowa_today_avg_hilo_pt.png">Average Hi/Low Temp</a></li>
<li><a href="/data/climate/iowa_today_rec_hilo_pt.png">Record Hi/Low Temp</a></li>
<li><a href="/COOP/dl/normals.phtml">Download Climatology Data</a></li>
</ul>
</td>

<td colspan="3">The <a href="/climodat/">Climodat</a> reports contain summarized
data from the NWS COOP network.

<br /><a href="/plotting/auto/?q=99">Plot of Daily Departures by Year</a>
</td>
</tr>

<tr><td>Growing Degree Days</td>
<td colspan="2">Not applicable</td>
<td>The <a href="/COOP/">NWS COOP</a> network data contains the best quality 
information for daily temperatures, but they are not always on a calendar date.
</td>
<td colspan="3">
The <a href="/climodat/">Climodat</a> reports present summarized GDD data.
<ul>
 <li><a href="/climodat/monitor.php">Climodat Station Monitor</a></li>
 <li><a href="/plotting/coop/gddprobs.phtml">Probabilies + Scenarios</a></li>
 <li><a href="/GIS/apps/coop/gsplot.phtml?var=gdd50&year={$y}">Map of Totals</a></li>
 <li><a href="/plotting/auto/?q=108">Single Site Graphs</a></li>
</ul>

<p>Maps of Growing Degree Days:
<ul>
 <li><a href="/data/summary/gdd_mon.png">This Month's GDD 50/86</a></li>
 <li><a href="/data/summary/gdd_jan1.png">This Years's GDD 50/86</a></li>
 <li><a href="/data/summary/gdd_may1.png">May 1 - Nov 1 GDD 50/86</a></li>
 <li><a href="/data/summary/gdd_may1_6086.png">May 1 - Nov 1 GDD 60/86</a></li>
 <li><a href="/data/summary/gdd_may1_6586.png">May 1 - Nov 1 GDD 65/86</a></li>
</ul>
</td>
</tr>

<tr><td>Precipitation (liquid + melted snow)</td>
 <td>The IEM processes the one minute <a href="/request/asos/1min.phtml">Iowa ASOS</a>
 data, but there is a month delay for receipt of this data.</td>
 <td>The <a href="/ASOS/">ASOS</a> (not AWOS) sites include a heated sensor that
 melts snowfall to produce liquid equivalent.</td>
 <td rowspan="2">The <a href="/COOP/">NWS COOP</a> network report precipitation totals that
 include melted snowfall.
 <ul>
  <li><a href="/COOP/7am.php">Map of Daily COOP Reports</a></li>
  <li><a href="/COOP/extremes.php">Daily Climatology</a></li>
  <li><a href="/data/summary/today_prec.png">Today's total</a></li>
 </ul>
 
 <br />The IEM processes gridded analyses of precipitation
 <ul>
   <li><a href="/plotting/auto/?q=86&var=p01d">IEM Reanalysis</a></li>
   <li><a href="/timemachine/#45.0">MRMS ~1km Product</a></li>
   <li><a href="/timemachine/#41.0">NCEP Stage IV</a></li>
 </ul>
 
 <br />There are daily <a href="/request/daily.phtml">ASOS precip reports</a>
 available for download.
 
 </td>
 <td colspan="3" rowspan="2"><a href="/climodat/">Climodat Reports</a> contain summarized precipitation
 data from the NWS COOP network.
 <ul>
  <li><a href="/climodat/monitor.php">Climodat Station Monitor</a></li>
  <li><a href="/GIS/apps/coop/gsplot.phtml?var=prec&smonth=1&sday=1&year={$y}">Map of Totals</a></li>
  <li><a href="/plotting/auto/?q=108">Single Site Graphs</a></li>
 </ul>
 
 <br /><a href="/plotting/auto/?q=97">Maps of Departures</a> from average.
 <br /><a href="/plotting/auto/?q=84">Multiday summaries of MRMS estimates</a>.
 
 </td>
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

<tr><td>Soil Moisture</td>
<td>Does not exist.</td>
<td>The <a href="/agclimate/">ISU Soil Moisture</a> network collects hourly
soil moisture data.</td>
<td>The <a href="http://wepp.mesonet.agron.iastate.edu/GIS/sm.phtml?pvar=vsm">Iowa Daily Erosion Project</a>
produces soil moisture analyses based on a model called WEPP.</td>
<td colspan="3">Summarized data for this timescale does not exist on the IEM 
at this time.</td>
</tr>

<tr><td>Soil Temperature</td>
<td>Does not exist.</td>
<td>The <a href="/agclimate/">ISU Soil Moisture</a> network collects hourly
soil temperature data.</td>
<td>The <a href="/agclimate/">ISU Soil Moisture</a> network produces daily
summaries of high and low temperature.
<ul>
 <li><a href="/agclimate/soilt.php">County Estimates</a></li>
 <li><a href="/timemachine/#57.0">Archived County Estimates</a></li>
</ul>
</td>
<td colspan="3">Summarized data for this timescale does not exist on the IEM 
at this time.</td>
</tr>


<tr><td>Snowfall</td>
 <td>Does not exist</td>
 <td>The NWS has paid snowfall observers that report 6 hour snowfall totals, but
 the IEM does not have a good interface to get this data.</td>
 <td>
 The IEM collects the <a href="/COOP/cat.phtml">24 hour snowfall reports</a>
 from the NWS COOP network.
 <ul>
   <li><a href="/data/coopSnowDepth.gif">COOP Snow Depth</a></li>
 </ul>
 </td>
<td colspan="3">Summarized data for this timescale does not exist on the IEM 
at this time.</td>
</tr>

<tr><td>Stress Degree Days</td>
<td colspan="2">Not applicable</td>
<td>The <a href="/COOP/">NWS COOP</a> network data contains the best quality 
information for daily temperatures, but they are not always on a calendar date.
</td>
<td colspan="3">The <a href="/climodat/">Climodat</a> reports present
summarized SDD data.
<ul>
    <li><a href="/climodat/monitor.php">Climodat Station Monitor</a></li>
  	<li><a href="/GIS/apps/coop/gsplot.phtml?var=sdd86&year={$y}">Map of Totals</a></li>
  	<li><a href="/plotting/auto/?q=108">Single Site Graphs</a></li>
</ul>
  		</td>
</tr>

<tr><td>Wind</td>
<td>
<a href="/agclimate/">ISU Soil Moisture</a> stations record real-time data
at one minute intervals.  <a href="/ASOS/">ASOS</a> also provides data at
such frequency, but it is delayed by ~24 hours.
</td>
<td>
<a href="/ASOS/">ASOS</a> data is typically the best at this temporal scale.
</td>
<td>
<ul>
  <li><a href="/data/summary/today_gust.png">Peak Wind Gust</a></li>
</ul>
</td>
<td colspan="3">...</td>
</tr>


</tbody>
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
