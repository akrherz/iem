<?php
include("../config/settings.inc.php");
$TITLE = "IEM | Information";
$THISPAGE = "iem-info";
include("$rootpath/include/header.php"); ?>


<h3 class="heading">Information/Documents</h3><p>

<div class="text">
<table border=0 width="100%"><tr><td valign="top">

<h3 class="subtitle">Quick Links:</h3></p>
<ul>
<li><a href="/info/iem.php">IEM Info/Background</a></li>
<li><a href="/info/members.php">IEM Partners</a></li>
<li><a href="/info/links.php">Links</a></li>
<li><a href="/info/variables.phtml">Variables Collected</a></li></ul>

<p>Information about requesting a <a href="/request/ldm.php">real-time data feed</a>
<p>
<h3 class="subtitle">Station Locations: (graphical)</h3>
<ul>
	<li><a href="<?php echo $rooturl; ?>/info/network.phtml?network=IA_ASOS">ASOS Locations</a></li>
	<li><a href="<?php echo $rooturl; ?>/info/network.phtml?network=AWOS">AWOS Locations</a></li>
	<li><a href="<?php echo $rooturl; ?>/info/network.phtml?network=IA_RWIS">RWIS Locations</a></li>
	<li><a href="<?php echo $rooturl; ?>/info/network.phtml?network=IA_COOP">COOP Locations</a></li>
	<li><a href="<?php echo $rooturl; ?>/info/network.phtml?network=ISUAG">ISU Agclimate Locations</a></li>
</ul>

</td><td width="50%" valign="top">

<h3 class="subtitle">IEM Server Information:</h3>
<ul>
	<li><a href="/info/software.php">Software Utilized</a></li>
	<li><a href="/mailman/listinfo/">Mailing Lists</a></li>
</ul>

<h3 class="subtitle">Papers/Presentations</h3>
<ul>
  <li><a href="/pubs/seniorthesis/">ISU Senior Thesis Presentations</a></li>
  <li><a href="/present/">IEM Presentation Archive</a></li>
  <li><a href="docs/unidata2006">Unidata Equipment Grant Report</a> (21 Aug 2006)</li>
</ul>

</td></tr></table></div>

<?php include("$rootpath/include/footer.php"); ?>
