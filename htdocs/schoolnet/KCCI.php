<a href="alerts/">About wind gust alerts</a> sent to the Weather Service.

<table width="100%" bgcolor="white" border=0>
<tr><td valign="top" width="300">

<p><h3 class="subtitle">Current Data</h3>
<ul>
 <li><a href="current.phtml">Current Conditions</a> (sortable)</li>
 <li><a href="<?php echo $rooturl; ?>/GIS/apps/snet/raining.php">Where's it raining?</a></li>
</ul>

<p><h3 class="subtitle">Station Plots</h3>
<ul>
 <li><a href="<?php echo $rooturl; ?>/GIS/apps/mesoplot/plot.php">Rapid Update every Minute</a></li>
 <li><a href="<?php echo $rooturl; ?>/GIS/apps/mesoplot/plot.php?zoom=1">Zoomed in on Des Moines</a></li>
 <li><a href="<?php echo $rooturl; ?>/GIS/apps/delta/plot.php?i=15m">15min Pressure Change</a></li>
 <li><a href="<?php echo $rooturl; ?>/GIS/apps/delta/plot.php">1 hour Pressure Change</a></li>
</ul>

</td><td valign="top" width="350">

  <p><h3 class="subtitle">Historical Data</h3>
<ul>
 <li><a href="<?php echo $rooturl; ?>/schoolnet/dl/">Download</a> from the archive!</a></li>
 <li><a href="<?php echo $rooturl; ?>/cgi-bin/precip/catSNET.py">Hourly Rainfall</a> tables</a></li>
 <li><a href="<?php echo $rooturl; ?>/schoolnet/rates/">Rainfall Rates</a></li>
</ul>

<p><h3 class="subtitle">QC Info</h3>
<ul>
 <li><a href="<?php echo $rooturl; ?>/QC/offline.php">Stations Offline</a> [<a href="<?php echo $rooturl; ?>/GIS/apps/stations/offline.php?network=snet">Graphical View</a>]</li>
 <li><a href="<?php echo $rooturl; ?>/QC/madis/network.phtml?network=KCCI">MADIS QC Values</a></li>
  <li>MADIS QC Messages:
  <br /><a href="http://madis-data.noaa.gov/qcms_data/qc20/qchour.txt">Last Hour</a>
  <br /><a href="http://madis-data.noaa.gov/qcms_data/qc20/qcday.txt">Today</a>
  <br /><a href="http://madis-data.noaa.gov/qcms_data/qc20/qcweek.txt">Weekly</a>
  <br /><a href="http://madis-data.noaa.gov/qcms_data/qc20/qcmonth.txt">Monthly</a>
  </li>
</ul>

<p><h3 class="subtitle">Plotting Time Series</h3>
<ul>
 <li><a href="<?php echo $rooturl; ?>/plotting/snet/1station_1min.php">1 station</a> [1 minute data]</li>
 <li><a href="<?php echo $rooturl; ?>/plotting/compare/">Generate Interactive Comparisons</a> between two sites of your choice.</li>
</ul></p>

</td></tr></table>

</td></tr></table>
