<?php
/*
 * List out UGCS by WFO
 */
require_once "../../config/settings.inc.php";
define("IEM_APPID", 141);
require_once "../../include/myview.php";
$t = new MyView();
$t->headextra = <<<EOM
<link type="text/css" href="/vendor/jquery-datatables/1.10.20/datatables.min.css" rel="stylesheet" />
EOM;
$t->jsextra = <<<EOM
<script src='/vendor/jquery-datatables/1.10.20/datatables.min.js'></script>
<script>
$('#makefancy').click(function(){
    $("#thetable table").DataTable();
});
</script>
EOM;

require_once "../../include/database.inc.php";
require_once "../../include/imagemaps.php";
require_once "../../include/mlib.php";
require_once "../../include/forms.php";

$wfo = isset($_REQUEST['wfo']) ? xssafe($_REQUEST['wfo']) : 'DMX';
$just_firewx = isset($_REQUEST["just_firewx"]) ? intval(xssafe($_REQUEST["just_firewx"])) : 0;
$w = isset($_REQUEST["w"]) ? xssafe($_REQUEST["w"]) : "wfo";
$state = isset($_REQUEST["state"]) ? xssafe($_REQUEST["state"]) : "IA";
if (($just_firewx != 1) && ($just_firewx != 0)){
    $just_firewx = 0;
}

$t->title = "NWS UGCs by WFO";

$wselect = networkSelect("WFO", $wfo);
$opts = Array(
    1 => "Just Fire Weather Zones",
    0 => "Show Non-Fire Weather Zones",
);
$fselect = make_select("just_firewx", $just_firewx, $opts);

$arr = array(
    "just_firewx" => $just_firewx,
);
$title = "";
if (($w == "wfo") && isset($_REQUEST["w"])) {
    $title = "for WFO: $wfo";
    $arr["wfo"] = $wfo;
}
else if ($w == "state") {
    $title = "for state: $state";
    $arr["state"] = $state;
}
$jobj = iemws_json("nws/ugcs.json", $arr);

$table = "";
foreach ($jobj["data"] as $bogus => $row) {
    $table .= sprintf('<tr><td>%s</td><td><a href="/vtec/search.php#byugc/%s">Link</a></td>'.
        '<td>%s</td><td>%s</td></tr>', $row["ugc"], $row["ugc"], $row["name"], $row["wfo"]);
}

$wfoselected = ($w == "wfo") ? 'checked="checked"': "";
$stateselected = ($w == "state") ? 'checked="checked"': "";
$sselect = stateSelect($state);

$t->content = <<<EOF
<ol class="breadcrumb">
 <li><a href="/nws/">NWS User Resources</a></li>
 <li class="active">NWS UGCs by WFO</li>
</ol>

<p>The National Weather Service issues many products associated with 
<a href="https://www.weather.gov/gis/AWIPSShapefiles">Universal
Geographic Codes</a> (UGCs).  These UGCs represent counties, forecast zones, marine zones, or
fire weather zones.  This page lists out a current listing of such codes and is powered
by an <a href="/api/1/docs#/nws/service_nws_ugcs__fmt__get">IEM Webservice</a>.
The default display <a href="list_ugcs.php">lists all non-fire weather UGCs</a> or
you can <a href="list_ugcs.php?just_firewx=1">list all fire weather UGCs</a>.</p>

<p><button id="makefancy">Make Table Interactive</button></p>

<form method="GET" name="changeme">
<table class="table table-condensed">
<tr>
<td>
<input type="radio" name="w" value="wfo" {$wfoselected} id="wfo">
<label for="wfo">Select by WFO</label>:</strong>{$wselect}
</td>
<td>
<input type="radio" name="w" value="state" {$stateselected} id="state">
<label for="state">Select by State</label>:</strong>{$sselect}
</td>
<td>{$fselect}</td>
<td><input type="submit" value="View UGCs"></td>
</tr>
</table>
</form>

<h3>UGCs listing {$title}</h3>

<div id="thetable">
<table class="table table-striped table-condensed table-bordered">
<thead><tr><th>UGC</th><th>Warning Search</th><th>Name</th><th>WFO</th></tr></thead>
<tbody>
{$table}
</tbody>
</table>
</div>
EOF;
$t->render('single.phtml');
