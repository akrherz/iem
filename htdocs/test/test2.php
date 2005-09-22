<html>
<head>
 <link rel="stylesheet" type="text/css" href="main.css">
 <link rel="stylesheet" type="text/css" href="main-theme.css">
 <link rel="alternate stylesheet" type="text/css" media="screen" href="red.css" title="red">
 <link rel="alternate stylesheet" type="text/css" media="screen" href="slashdot.css" title="slashdot">
 <script type="text/javascript" src="nrcs.js"></script>
</head>
<body style="background: #666666;">
<div id="iem-main">

<div id="iem-header">

<div id="iem-header-logo">
<a href="http://mesonet.agron.iastate.edu/"><img 
src="http://mesonet.agron.iastate.edu/images/Logo_new_small.png" alt="IEM" width="100" height="49"></a>
</div>

<div id="iem-header-title">
<h3>Iowa Environmental Mesonet</h3>
<h4>Iowa State University Department of Agronomy</h4>
</div>

<div id="iem-header-items">
<b>Select Theme:</b>
<br /><a title="Small Text Size" id="navSmallText" href="#" onClick="setActiveStyleSheet('default'); return false">Default</a>
| <a title="Small Text Size" id="navSmallText" href="#" onClick="setActiveStyleSheet('red'); return false">Red</a>
| <a title="Small Text Size" id="navSmallText" href="#" onClick="setActiveStyleSheet('slashdot'); return false">Slashdot</a>
</div>


<div class="iem-menu">
 <a href="http://mesonet.agron.iastate.edu/archive/">Archive</a>
 &middot; <a href="http://mesonet.agron.iastate.edu/current/">Current</a>
 &middot; <a href="http://mesonet.agron.iastate.edu/climate/">Climatology</a>
 &middot; <a href="http://mesonet.agron.iastate.edu/climodat/">Climodat</a>
 &middot; <a href="http://mesonet.agron.iastate.edu/sites/locate.php">IEM Sites</a>
 &middot; <a href="http://mesonet.agron.iastate.edu/GIS/">GIS</a>
 &middot; <a href="http://mesonet.agron.iastate.edu/info.php">Info</a>
 &middot; <a href="http://mesonet.agron.iastate.edu/plotting/">Plotting</a>
 &middot; <a href="http://mesonet.agron.iastate.edu/QC/">Quality Control</a>
</div>
</div>
<div id="iem-content">
<div id="iem-section">
<center><table>
<tr><th>Surface Data</th>
<th><a href="radar.phtml">RADAR/Sat Data</a></th>
<th><a href="misc.phtml">Advanced Met Plots</a></th>
<th><a href="camera.phtml">Web Cameras</a></th>
<th>&nbsp;</th>
</tr></table></center></div>

<table border=0 width=780px>
<tr><td valign="top">

<h3 class="subtitle">Mesonet Plots</h3>
<ul>
 <li><a href="/data/mesonet.gif">Iowa Mesonet Plot</a> [<a href="/data/loop.phtml?prod=mesonet">Loop</a>]</li>
 <li><a href="/data/MWmesonet.gif">Upper Mid-West</a> [<a href="/data/loop.phtml?prod=mwmesonet">Loop</a>]</li>
 <li><a href="/data/iem_gray.gif">Large Font</a></li>
</ul>

<h3 class="subtitle">Zoomed In Mesonet Plots</h3>
<ul>
  <li><a href="/data/CBF_mesonet.gif">Council Bluffs</a></li>
  <li><a href="/data/CID_mesonet.gif">Cedar Rapids</a></li>
  <li><a href="/data/DSM_mesonet.gif">Des Moines</a></li>
</ul>

<h3 class="subtitle">Precipitation</h3>
<ul>
  <li><a href="/data/1hprecip.gif">ASOS + AWOS (Last Hour)</a></li>
  <li><a href="/data/summary/today_prec.gif">ASOS + AWOS (Today)</a></li>
  <li><a href="/data/nexradPrecip1h.gif">NEXRAD 1 hour est.</a></li>
</ul>

</td><td valign="top">

<h3 class="subtitle">Individual Network Plots</h3>
<ul>
  <li><a href="/data/asos.gif">ASOS + AWOS</a></li>
  <li><a href="/data/awos.gif">AWOS</a></li>
  <li><a href="/data/rwis.gif">RWIS</a></li>
  <li><a href="/data/snet/mesonet.gif">SchoolNets</a></li>
</ul>

<h3 class="subtitle">Parameter 
Plots</h3>
<ul>  <li><a href="/data/mesonet_altm.gif">Altimeter</a></li>
  <li><a href="/data/ceil.gif">Ceiling</a></li>
  <li><a href="/data/heat.gif">Heat Index</a></li>
  <li><a href="/data/relh.gif">Relative Humidity</a></li>
  <li><a href="/data/vsby.gif">Visibility</a></li>
  <li><a href="/data/wcht.gif">Wind Chill Index</a></li>
</ul>

</td><td valign="top">

<h3 class="subtitle">Temporal Change Plots</h3>
<ul>
  <li><a href="http://mesonet.agron.iastate.edu/GIS/apps/delta/plot.php?i=15m">15min Pressure Change</a></li>
  <li><a href="http://mesonet.agron.iastate.edu/GIS/apps/delta/plot.php">1 hour Pressure Change</a></li>
</ul>


<h3 class="subtitle">Sortable Current Conditions</h3>
<ul>
 <li><a href="/ASOS/current.php">ASOS</a></li>
 <li><a href="/AWOS/current.php">AWOS</a></li>
 <li><a href="/COOP/current.phtml">COOP</a></li>
 <li><a href="/DCP/current.phtml">DCP</a></li>
 <li><a href="/schoolnet/current.php">SchoolNet</a></li>
 <li><a href="/RWIS/current.php">RWIS</a></li>
 <li><a href="/current/neighbors.php">Neighbors</a></li>
</ul>

<p><a href="/wx/afos/">NWS Text Product Finder</a>

</td></tr></table></div>

<div id="iem-footer">
<table class="footer"><tr><td>
<b>IEM Networks:</b> <a href="http://mesonet.agron.iastate.edu/ASOS/"><acronym title="Automated Surface Observing System">ASOS</acronym></a>
 &middot; <a href="http://mesonet.agron.iastate.edu/AWOS/"><acronym title="Automated Weather Observing System">AWOS</acronym></a>
 &middot; <a href="http://mesonet.agron.iastate.edu/COOP/"><acronym title="Cooperative Observation Program">COOP</acronym></a>
 &middot; <a href="http://mesonet.agron.iastate.edu/DCP/"><acronym title="Data Collection Platforms">DCP</acronym></a>
 &middot; <a href="http://mesonet.agron.iastate.edu/agclimate/"><acronym title="Iowa State Ag Climate Network">ISU AG</acronym></a>
 &middot; <a href="http://mesonet.agron.iastate.edu/RWIS/"><acronym title="Roadway Weather Information System">RWIS</acronym></a>
 &middot; <a href="http://mesonet.agron.iastate.edu/scan/"><acronym title="Soil Climate Analysis Network">SCAN</acronym></a>
 &middot; <a href="http://mesonet.agron.iastate.edu/schoolnet/"><acronym title="School Network">School Net</acronym></a>
 &middot; <a href="http://mesonet.agron.iastate.edu/other/"><acronym title="Other Networks">Other</acronym></a>

<div class="iem-footer-text">
Copyright &copy; 2001-2004, Iowa State University of Science and 
Technology.
All rights reserved.
<br>

 <a href="http://mesonet.agron.iastate.edu/help/abbreviations.php">abbreviations</a>
 &middot; <a href="http://mesonet.agron.iastate.edu/bugzilla/">bugzilla</a>
 &middot; <a href="http://mesonet.agron.iastate.edu/info/contacts.php">contact us</a>
 &middot; <a href="http://mesonet.agron.iastate.edu/disclaimer.php">disclaimer</a>
 </div></td><td>

  <b>Search Site with Google:</b><br>
<form method="GET" action="http://www.google.com/search" name="search">
<input value="mesonet.agron.iastate.edu" name="sitesearch" type="hidden">
<input type="text" size="15" name="q"><input type="submit" value="Search"></form>
</td></table>
</div></div>
</html>
