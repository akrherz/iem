<?php
$OL = "7.2.2";
/*
 * Main landing page for the IEM Sites stuff
 */
require_once "../../include/forms.php";
if (isset($_GET["station"]) && isset($_GET["network"])) {
    $uri = sprintf(
        "site.php?station=%s&network=%s",
        xssafe($_REQUEST["station"]),
        xssafe($_REQUEST["network"])
    );
    header("Location: $uri");
    exit();
}
require_once "../../include/mlib.php";
force_https();
require_once "../../config/settings.inc.php";
define("IEM_APPID", 5);
require_once "../../include/database.inc.php";
require_once "../../include/imagemaps.php";
require_once "../../include/myview.php";

$network = isset($_GET["network"]) ? xssafe($_GET["network"]) : "IA_ASOS";

$t = new MyView();
$t->title = "Site Locator";
$t->headextra = <<<EOF
<link rel="stylesheet" href="/vendor/openlayers/{$OL}/ol.css" type="text/css">
<link type="text/css" href="/vendor/openlayers/{$OL}/ol-layerswitcher.css" rel="stylesheet" />
<link rel="stylesheet" type="text/css" href="/vendor/select2/4.0.3/select2.min.css"/ >
EOF;
$t->jsextra = <<<EOF
<script src="/vendor/openlayers/{$OL}/ol.js" type="text/javascript"></script>
<script src='/vendor/openlayers/{$OL}/ol-layerswitcher.js'></script>
<script src="/js/olselect.js"></script>
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
<p>Green dots represent stations online with current data.  Yellow dots are
stations that are no longer active.  Click on a dot to select a station, then click
the 'Select Station' button above.</p>

<div id="map" style="width:100%; height: 400px;" data-network="{$network}"></div>

</form>

</div>
EOF;
$t->render('single.phtml');
