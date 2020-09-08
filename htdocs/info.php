<?php
require_once "../config/settings.inc.php";
require_once "../include/myview.php";
$t = new MyView();
define("IEM_APPID", 61);
$t->title = "Information Mainpage";
$t->thispage = "iem-base";

$t->content = <<<EOF
<h3>Information/Documents</h3><p>

<div class="row">
<div class="col-md-6 col-sm-6">
		
<h3>Quick Links:</h3></p>
<ul>
<li><a href="/info/iem.php">IEM Info/Background</a></li>
<li><a href="/info/links.php">Links</a></li>
<li><a href="/info/variables.phtml">Variables Collected</a></li></ul>

<p>Information about requesting a <a href="/request/ldm.php">real-time data feed</a>
<p>
<h3>Station Locations: (graphical)</h3>
<ul>
	<li><a href="/sites/locate.php?network=IA_ASOS">ASOS Locations</a></li>
	<li><a href="/sites/locate.php?network=AWOS">AWOS Locations</a></li>
	<li><a href="/sites/locate.php?network=IA_RWIS">RWIS Locations</a></li>
	<li><a href="/sites/locate.php?network=IA_COOP">COOP Locations</a></li>
	<li><a href="/sites/locate.php?network=ISUSM">ISU Soil Moisture Locations</a></li>
</ul>

</div>
<div class="col-md-6 col-sm-6">

<h3>IEM Server Information:</h3>
<ul>
	<li><a href="/usage/">Webfarm Statistics</a></li>
</ul>

<h3>Papers/Presentations</h3>
<ul>
  <li><a href="/present/">IEM Presentation Archive</a></li>
  <li><a href="/docs/unidata2006">Unidata Equipment Grant Report</a> (21 Aug 2006)</li>
</ul>

</div></div>

EOF;
$t->render('single.phtml');
?>