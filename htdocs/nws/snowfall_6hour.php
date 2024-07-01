<?php
// show any NWS 6 hour snowfall reports
require_once "../../config/settings.inc.php";
define("IEM_APPID", 106);
require_once "../../include/myview.php";
require_once "../../include/database.inc.php";
require_once "../../include/imagemaps.php";
require_once "../../include/mlib.php";
require_once "../../include/forms.php";

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

$year = get_int404("year", date("Y"));
$month = get_int404("month", date("m"));
$day = get_int404("day", date("d"));
$now = new DateTime(sprintf("%s-%s-%s 12:00", $year, $month, $day), new DateTimeZone("UTC"));
$wfo = isset($_REQUEST["wfo"]) ? xssafe($_REQUEST["wfo"]) : "DMX";
$w = isset($_REQUEST["w"]) ? xssafe($_REQUEST["w"]) : "all";
$state = isset($_REQUEST["state"]) ? xssafe($_REQUEST["state"]) : "IA";
// side logic for when $w is not set
if (!isset($_REQUEST["w"])){
    if (isset($_REQUEST["wfo"])){
        $w = "wfo";
    } else if (isset($_REQUEST["state"])){
        $w = "state";
    }
}

$t->title = "NWS Six Hour Snowfall Reports";
$t->refresh = 360;

$wselect = networkSelect("WFO", $wfo, array(), "wfo");
$yselect = yearSelect2(2010, $year, "year");
$mselect = monthSelect($month, "month");
$dselect = daySelect($day);

// We need to loop over the date, so starting at 12z and to 6z of the next day
$station_data = Array();
$hrs = Array(12, 18, 0, 6);
// loop over hrs array
foreach($hrs as $hr){
    $arr = array("valid" => $now->format("Y-m-d\TH:i"));
    $jobj = iemws_json("nws/snowfall_6hour.json", $arr);
    foreach ($jobj["data"] as $bogus => $row) {
        $station = $row["station"];
        if ($w == "wfo" && $row["wfo"] != $wfo){
            continue;
        }
        if ($w == "state" && $row["state"] != $state){
            continue;
        }
        if (! array_key_exists($station, $station_data)){
            $station_data[$station] = Array(
                "network" => $row["network"],
                "station" => $station,
                "name" => $row["name"],
                "state" => $row["state"],
                "wfo" => $row["wfo"],
                "value" => Array(12 => "M", 18 => "M", 0 => "M", 6 => "M"),
            );
        }
        $station_data[$station]["value"][$hr] = ($row["value"] == 0.0001) ? "T": $row["value"];
    }
    // add 6 hours to $now
    $now->modify("+6 hours");
}


$table = "";
foreach ($station_data as $row) {
    $table .= sprintf(
        '<tr><td><a href="/sites/site.php?network=%s&amp;station=%s">%s[%s]</td>' .
            '<td>%s</td><td>%s</td><td>%s</td><td>%s</td>'.
            '<td>%s</td><td>%s</td><td>%s</td></tr>',
        $row["network"],
        $row["station"],
        $row["station"],
        $row["network"],
        $row["name"],
        $row["state"],
        $row["wfo"],
        $row["value"][12],
        $row["value"][18],
        $row["value"][0],
        $row["value"][6],
    );
}

$wfoselected = ($w == "wfo") ? 'checked="checked"' : "";
$allselected = ($w == "all") ? 'checked="checked"' : "";
$stateselected = ($w == "state") ? 'checked="checked"' : "";
$sselect = stateSelect($state);

$t->content = <<<EOF
<ol class="breadcrumb">
 <li><a href="/nws/">NWS User Resources</a></li>
 <li class="active">NWS Six Hour Snowfall</li>
</ol>

<p>The National Weather Service has a limited number of observers that report
snowfall totals at 6 hour intervals.  This page lists any of those observations
found by the IEM whilst parsing the feed of SHEF encoded data.
<a href="/api/1/docs#/nws/service_nws_snowfall_6hour__fmt__get">API Service</a>
with this data.</p>

<p>This page presents one "day" of data at a time. The day is defined as starting
at 6 UTC, so the first report shown is valid at 12 UTC of the given date.  The
subsequent 0, and 6 UTC values shown are with valid dates of the next day.</p>

<p><button id="makefancy">Make Table Interactive</button></p>

<form method="GET" name="changeme">
<table class="table table-condensed">
<tr>
<td><strong>Year:</strong> {$yselect}</td>
<td><strong>Month:</strong> {$mselect}</td>
<td><strong>Day:</strong> {$dselect}</td>
<td>
<input type="radio" name="w" value="all" {$allselected} id="all">
<label for="all">Show all data</label>
</td>
<td>
<input type="radio" name="w" value="wfo" {$wfoselected} id="wfo">
<label for="wfo">Select by WFO</label>:</strong>{$wselect}
</td>
<td>
<input type="radio" name="w" value="state" {$stateselected} id="state">
<label for="state">Select by State</label>:</strong>{$sselect}
</td>
<td><input type="submit" value="View Table"></td>
</tr>
</table>
</form>

<h3>Six Hour Snowfall</h3>

<p>Values are in inches. T indicates a trace of snowfall. The table will
refresh every 6 minutes.</p>

<div id="thetable">
<table class="table table-striped table-condensed table-bordered">
<thead class="sticky">
<tr><th>Station/Network</th><th>Name</th><th>State</th>
<th>WFO</th>
<th>12 UTC<br />(6 AM CST)</th><th>18 UTC<br />(12 PM CST)</th>
<th>0 UTC<br />(6 PM CST)</th>
<th>6 UTC<br />(12 AM CST)</th></tr>
</thead>
<tbody>
{$table}
</tbody>
</table>
</div>
EOF;
$t->render('full.phtml');
