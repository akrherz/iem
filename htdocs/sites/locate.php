<?php
$OL = "3.18.2";
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

$network = isset($_GET["network"]) ? $_GET["network"] : "IA_ASOS";
  
$t = new MyView();
$t->title = "Site Locator";
$t->thispage = "iem-sites";
$t->headextra = <<<EOF
<link rel="stylesheet" href="/vendor/openlayers/{$OL}/ol.css" type="text/css">
<link type="text/css" href="/vendor/openlayers/{$OL}/ol3-layerswitcher.css" rel="stylesheet" />
<link rel="stylesheet" type="text/css" href="/vendor/select2/4.0.3/select2.min.css"/ >
EOF;
$t->jsextra = <<<EOF
<script src="/vendor/openlayers/{$OL}/ol.js" type="text/javascript"></script>
<script src='/vendor/openlayers/{$OL}/ol3-layerswitcher.js'></script>
<script src="/js/olselect.php?network=${network}"></script>
<script src="/vendor/select2/4.0.3/select2.min.js"></script>
<script type="text/javascript">
$(document).ready(function(){
	$(".iemselect2").select2();	
});
</script>
EOF;

$nselect = selectNetwork($network);
$n2select = networkSelect($network, "");

$t->content = <<<EOF
<h3>IEM Site Information</h3><p>

<p>The IEM collects information from many sites.  These sites are organized into
networks based on their geography and/or the organization who administers the
network.  This application provides some metadata and site specific applications
you may find useful.</p>

<p>
<form name="switcher">
<table class="table table-condensed table-striped">
<tr>
 <th>Select By Network:</th>
 <td>{$nselect}</td>
 <td><input type="submit" value="Switch Network"></td>
</tr>
</table>
</form>

<form name="olselect">
<input type="hidden" name="network" value="{$network}">
<table class="table table-condensed table-striped">
<tr><th>Select By Station:</th>
<td>{$n2select}</td>
<td><input type="submit" value="Select Station"></td>
</tr></table>
<br />Or select site from this map by clicking on the black dot....
<div id="map" style="width:100%; height: 400px;"></div>
</form>

</div>
EOF;
$t->render('single.phtml');
?>
