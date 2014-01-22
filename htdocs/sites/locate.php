<?php
/*
 * Main landing page for the IEM Sites stuff
 */
if (isset($_GET["station"]) && isset($_GET["network"]))
{
	$uri = sprintf("site.php?station=%s&network=%s", $_REQUEST["station"],
		$_REQUEST["network"]);
  	header("Location: $uri");
  	exit();
}
 include("../../config/settings.inc.php");
 define("IEM_APPID", 5);
 include("../../include/database.inc.php");
 include("../../include/imagemaps.php");
 include("../../include/myview.php");
 $t = new MyView();
 $network = isset($_GET["network"]) ? $_GET["network"] : "IA_ASOS";

$t->title = "Site Locator";
$t->thispage = "iem-sites";
$t->headextra = "<script src='https://maps.googleapis.com/maps/api/js?sensor=false'></script>
<script src='http://openlayers.org/api/2.12/OpenLayers.js'></script>
<script src='/js/olselect.php?network=${network}'></script>";
$t->bodyextra = "onload=\"init()\"";

$nselect = selectNetwork($network);
$n2select = networkSelect($network, "");
$t->content = <<<EOF
<style type="text/css">
        #map {
            width: 640px;
            height: 400px;
            border: 2px solid black;
        }
</style>
<h3 class="heading">IEM Site Information</h3><p>
<p>The IEM collects information from many sites.  These sites are organized into
networks based on their geography and/or the organization who administers the
network.  This application provides some metadata and site specific applications
you may find useful.</p>

<div align="center">

<form name="switcher">
<table>
<tr><th>Select By Network:</th>
<td>{$nselect}</td>
<td><input type="submit" value="Switch Network"></td>
</tr></table>
</form>

<form name="olselect">
<input type="hidden" name="network" value="{$network}">
<table>
<tr><th>Select By Station:</th>
<td>{$n2select}</td>
<td><input type="submit" value="Select Station"></td>
</tr></table>
<br />Or select site from this map by clicking on the black dot....
<div id="map"></div>
<div id="sname" unselectable="on">No site selected</div>
</form>

</div>
EOF;
$t->render('single.phtml');
?>
