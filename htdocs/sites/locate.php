<?php
// Main landing page for the IEM Sites stuff
$OL = "8.1.0";
define("IEM_APPID", 5);
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
require_once "../../include/database.inc.php";
require_once "../../include/myview.php";

$network = isset($_GET["network"]) ? xssafe($_GET["network"]) : "IA_ASOS";

$t = new MyView();
$t->iemselect2 = TRUE;
$t->title = "Site Locator";
$t->headextra = <<<EOM
<link rel="stylesheet" href="/vendor/openlayers/{$OL}/ol.css" type="text/css">
<link type="text/css" href="/vendor/openlayers/{$OL}/ol-layerswitcher.css" rel="stylesheet" />
EOM;
$t->jsextra = <<<EOM
<script src="/vendor/openlayers/{$OL}/ol.js" type="text/javascript"></script>
<script src='/vendor/openlayers/{$OL}/ol-layerswitcher.js'></script>
<script src="/js/olselect.js"></script>
EOM;

$nselect = selectNetwork($network);
$n2select = networkSelect($network, "");

$t->content = <<<EOM
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
EOM;
$t->render('single.phtml');
