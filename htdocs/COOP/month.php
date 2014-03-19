<?php
include("../../config/settings.inc.php");
define("IEM_APPID", 30);
include("../../include/myview.php");
$t = new MyView();
$t->title = "Removed Page";
$t->thispage = "networks-coop";

$t->content = <<<EOF

<h4>NWS COOP Observations by Month</h4>
		
<div class="alert alert-info">This page has been removed as it was providing 
		confusing information.</div>
		
<p>The <a href="/sites/locate.php?network=IA_COOP">IEM Station Data and Metadata</a>
	section has a "Data Calendar" which provides similiar functionality to what
	was on this page.  For example, here is the calendar for 
	<a href="/sites/hist.phtml?station=AMSI4&network=IA_COOP">Ames (AMSI4)</a></p>

EOF;
$t->render('single.phtml');
?>
