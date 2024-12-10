<?php 
require_once "../../config/settings.inc.php";
require_once "../../include/forms.php";
define("IEM_APPID", 115);
$year = get_int404("year", intval(date("Y")));

require_once "../../include/myview.php";
require_once "../../include/vtec.php";
require_once "../../include/imagemaps.php";

$uri = sprintf("http://iem.local/json/vtec_max_etn.py?year=%s&format=html", 
        $year);
$wsuri = sprintf("https://mesonet.agron.iastate.edu/json/vtec_max_etn.py?year=%s",
    $year);
$table = file_get_contents($uri);

$t = new MyView();
$t->title = "VTEC Event Listing for $year";
$t->headextra = <<<EOM
<link type="text/css" href="/vendor/jquery-datatables/1.10.20/datatables.min.css" rel="stylesheet" />
EOM;

$yselect = yearSelect2(2005, $year, 'year');

$t->content = <<<EOM
<ol class="breadcrumb">
 <li><a href="/nws/">NWS Resources</a></li>
 <li class="active">Max VTEC EventID Listing</li>
</ol>

<p>The National Weather Service uses a system called
<a href="http://www.nws.noaa.gov/om/vtec/">Valid Time Event Code (VTEC)</a> to provide
more accurate tracking of its watch, warning, and advisories.  The IEM attempts to provide a
high fidelity database of these products.  The following table is a diagnostic providing the
largest VTEC eventids (ETN) for each NWS Forecast Office, each phenomena and significance for
the given year. <strong>Pro-tip</strong>: Use the search box to the upper right of the
table to search for a specific WFO.</p>

<p>The following <a href="/json/">JSON(P) Webservice</a> provided the data you
see presented on this page<br />
<code>{$wsuri}</code></p>

<form method="GET" action="maxetn.php">
        Select Year: $yselect
        <input type="submit" value="Generate Table">
</form>

<hr >
<h3>Max VTEC ETN listing for {$year}</h3>
<div id="thetable">
{$table}
</div>


EOM;
$t->jsextra = <<<EOM
<script src='/vendor/jquery-datatables/1.10.20/datatables.min.js'></script>
<script>
$(document).ready(() => {
    $("#thetable table").DataTable();
});
</script>
EOM;
$t->render("full.phtml");
