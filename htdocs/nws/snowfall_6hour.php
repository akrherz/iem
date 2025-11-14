<?php
// show any NWS 6 hour snowfall reports
require_once "../../config/settings.inc.php";
define("IEM_APPID", 106);
require_once "../../include/myview.php";
require_once "../../include/database.inc.php";
require_once "../../include/mlib.php";
require_once "../../include/forms.php";

$t = new MyView();
$t->headextra = <<<EOM
<link rel="stylesheet" href="https://unpkg.com/tabulator-tables@6.2.5/dist/css/tabulator_bootstrap5.min.css">
<link type="text/css" href="snowfall_6hour.css" rel="stylesheet" />
EOM;
$t->jsextra = <<<EOM
<script src="snowfall_6hour.module.js?v=3" type="module"></script>
EOM;

$year = get_int404("year", date("Y"));
$month = get_int404("month", date("m"));
$day = get_int404("day", date("d"));
$now = new DateTime(sprintf("%s-%s-%s 12:00", $year, $month, $day), new DateTimeZone("UTC"));
$wfo = get_str404("wfo", "DMX");
$w = get_str404("w", "all");
$state = get_str404("state", "IA");
// side logic for when $w is not set
if (!array_key_exists("w", $_REQUEST)){
    if (array_key_exists("wfo", $_REQUEST)){
        $w = "wfo";
    } else if (array_key_exists("state", $_REQUEST)){
        $w = "state";
    }
}

$t->title = "NWS Six Hour Snowfall Reports";
$t->refresh = 360;

$wselect = networkSelect("WFO", $wfo, array(), "wfo");
$yselect = yearSelect(2010, $year, "year");
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

$t->content = <<<EOM
<ol class="breadcrumb">
 <li class="breadcrumb-item"><a href="/nws/">NWS User Resources</a></li>
 <li class="breadcrumb-item active" aria-current="page">NWS Six Hour Snowfall</li>
</ol>

<p>The National Weather Service has a limited number of observers that report
snowfall totals at 6 hour intervals. This page lists any of those observations
found by the IEM whilst parsing the feed of SHEF encoded data.
<a href="/api/1/docs#/nws/service_nws__varname__6hour__fmt__get">API Service</a>
with this data.</p>

<p>This page presents one "day" of data at a time. The day is defined as starting
at 6 UTC, so the first report shown is valid at 12 UTC of the given date. The
subsequent 0, and 6 UTC values shown are with valid dates of the next day.</p>

<div class="mb-3">
    <button id="makefancy" class="btn btn-primary">
    <i class="bi bi-table"></i> Make Table Interactive
    </button>
</div>

<div class="card mb-4">
    <div class="card-header">
        <h5 class="card-title mb-0">Filter Options</h5>
    </div>
    <div class="card-body">
        <form method="GET" name="changeme">
            <div class="row g-3 align-items-end">
                <div class="col-md-2">
                    <label for="year" class="form-label"><strong>Year:</strong></label>
                    {$yselect}
                </div>
                <div class="col-md-2">
                    <label for="month" class="form-label"><strong>Month:</strong></label>
                    {$mselect}
                </div>
                <div class="col-md-2">
                    <label for="day" class="form-label"><strong>Day:</strong></label>
                    {$dselect}
                </div>
                <div class="col-md-6">
                    <div class="row g-2">
                        <div class="col-md-4">
                            <div class="form-check">
                                <input class="form-check-input" type="radio" name="w" value="all" {$allselected} id="all">
                                <label class="form-check-label" for="all">Show all data</label>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="form-check">
                                <input class="form-check-input" type="radio" name="w" value="wfo" {$wfoselected} id="wfo">
                                <label class="form-check-label" for="wfo">Select by WFO:</label>
                            </div>
                            {$wselect}
                        </div>
                        <div class="col-md-4">
                            <div class="form-check">
                                <input class="form-check-input" type="radio" name="w" value="state" {$stateselected} id="state">
                                <label class="form-check-label" for="state">Select by State:</label>
                            </div>
                            {$sselect}
                        </div>
                    </div>
                </div>
                <div class="col-md-12">
                    <button type="submit" class="btn btn-success">
                        <i class="bi bi-search"></i> View Table
                    </button>
                </div>
            </div>
        </form>
    </div>
</div>

<h3>Six Hour Snowfall</h3>

<p>Values are in inches. <span class="badge bg-info">T</span> indicates a trace of snowfall.
The table will refresh every 6 minutes.</p>

<!-- Tabulator container (initially hidden) -->
<div id="tabulator-container" style="display: none;">
    <div id="snowfall-tabulator"></div>
</div>

<!-- Original table (shown by default) -->
<div id="thetable">
    <div class="table-responsive">
        <table class="table table-striped table-sm table-bordered">
            <thead class="table-dark sticky-top">
                <tr>
                    <th>Station/Network</th>
                    <th>Name</th>
                    <th>State</th>
                    <th>WFO</th>
                    <th>12 UTC<br />(6 AM CST)</th>
                    <th>18 UTC<br />(12 PM CST)</th>
                    <th>0 UTC<br />(6 PM CST)</th>
                    <th>6 UTC<br />(12 AM CST)</th>
                </tr>
            </thead>
            <tbody>
                {$table}
            </tbody>
        </table>
    </div>
</div>
EOM;
$t->render('full.phtml');
