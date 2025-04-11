<?php
require_once "../../config/settings.inc.php";
define("IEM_APPID", 156);
$DT = "1.13.6";
require_once "../../include/myview.php";
require_once "../../include/database.inc.php";
require_once "../../include/forms.php";
require_once "../../include/imagemaps.php";
require_once "../../include/network.php";

$nt = new NetworkTable("NWSCLI");

$station = isset($_GET["station"]) ? xssafe($_GET["station"]) : 'KDSM';
$year = get_int404("year", date("Y"));
$month = get_int404("month", null);
$day = get_int404("day", null);
$opt = isset($_GET["opt"]) ? xssafe($_GET["opt"]) : "bystation";

$ys = yearSelect(2001, $year, "year");
$ms = monthSelect($month, "month");
$ds = daySelect($day, "day");

$byday = false;
if ($opt === "bystation") {
    $title = sprintf("Station: %s for Year: %s", $station, $year);
    $col1label = "Date";
    $uri = sprintf(
        "%s/json/cli.py?station=%s&year=%s",
        $INTERNAL_BASEURL,
        $station,
        $year
    );
    $data = file_get_contents($uri);
    $json = json_decode($data, $assoc = TRUE);
    $arr = $json['results'];
} else {
    $col1label = "Station";
    $byday = true;
    $day = mktime(0, 0, 0, $month, $day, $year);
    $title = sprintf("All Stations for Date: %s", date("d F Y", $day));
    $uri = sprintf(
        "%s/geojson/cli.py?dt=%s",
        $INTERNAL_BASEURL,
        date("Y-m-d", $day)
    );
    $data = file_get_contents($uri);
    $json = json_decode($data, $assoc = TRUE);
    $arr = $json['features'];
}
$prettyurl = str_replace($INTERNAL_BASEURL, $EXTERNAL_BASEURL, $uri);

$table = <<<EOM
<style>
.empty{
    width: 0px !important;
    border: 0px !important;
    padding: 2px !important;
    background: tan !important;
}
</style>
<h3>{$title}</h3>
<table id="thetable" class="table table-condensed table-striped table-bordered table-hover"
 data-column-defs='[{"sortable": false, "targets": [7,14,21]}]'>
<thead class="sticky">
<tr class="small">
    <th rowspan="2">{$col1label}</th>
    <th colspan="6">Maximum Temperature &deg;F</th>
    <th class="empty"></th>
    <th colspan="6">Minimum Temperature &deg;F</th>
    <th class="empty"></th>
    <th colspan="6">Precip (inches)</th>
    <th class="empty"></th>
    <th colspan="5">Snow (inches)</th>
    <th class="empty"></th>
    <th colspan="1">Misc</th>
</tr>
<tr class="small">
    <th>Ob</th><th>Time</th><th>Rec</th><th>Years</th><th>Avg</th>
    <th>&Delta;</th><th class="empty"></th>

    <th>Ob</th><th>Time</th><th>Rec</th><th>Years</th><th>Avg</th>
    <th>&Delta;</th><th class="empty"></th>

    <th>Ob</th><th>Rec</th><th>Years</th>
    <th>Avg</th><th>Mon to Date</th><th>Mon Avg</th><th class="empty"></th>

    <th>Ob</th><th>Rec</th><th>Years</th><th>Mon to Date</th><th>Depth</th>
    <th class="empty"></th>

    <th>Avg Sky Cover</th>
</tr>
</thead>
<tbody>
EOM;
function departure($actual, $normal)
{
    // JSON upstream hacky returns M instead of null
    if ($actual == "M" || $normal == "M") return "M";
    return $actual - $normal;
}
// JSON upstream hacky returns M instead of null
function departcolor($actual, $normal)
{
    if ($actual == "M" || $normal == "M") return "#FFF";
    $diff = $actual - $normal;
    if ($diff == 0) return "#fff";
    if ($diff >= 10) return "#FF1493";
    if ($diff > 0) return "#D8BFD8";
    if ($diff > -10) return "#87CEEB";
    if ($diff <= -10) return "#00BFFF";
    return "#fff";
}
function new_record($actual, $record)
{
    if ($actual == "M" || $record == "M") return "";
    if ($actual === $record) return '<i class="fa fa-star-o"></i>';
    if ($actual > $record) return "<i class=\"fa fa-star\"></i>";
    return "";
}
function new_record2($actual, $record)
{
    if ($actual == "M" || $record == "M") return "";
    if ($actual == $record) return '<i class="fa fa-star-o"></i>';
    if ($actual < $record) return "<i class=\"fa fa-star\"></i>";
}
function new_record3($actual, $record)
{
    if ($actual == "M" || $record == "M") return "";
    if ($actual == 0) return "";
    if ($actual === $record) return '<i class="fa fa-star-o"></i>';
    // Careful of Trace
    if ($actual === "T"){
        if ($record > 0.001) return "";
        return '<i class="fa fa-star"></i>';
    }
    if ($actual > $record) return "<i class=\"fa fa-star\"></i>";
    return "";
}
foreach ($arr as $entry) {
    $row = ($opt === "bystation") ? $entry : $entry["properties"];
    $ts = strtotime($row["valid"]);
    if ($byday) {
        $link = sprintf(
            "clitable.php?station=%s&year=%s",
            $row["station"],
            date("Y", $ts)
        );
        $col1 = sprintf(
            "<a href=\"%s\" class=\"small\">%s %s</a>",
            $link,
            $row["station"],
            $nt->table[$row["station"]]['name']
        );
    } else {
        $link = sprintf(
            "clitable.php?opt=bydate&year=%s&month=%s&day=%s",
            date("Y", $ts),
            date("m", $ts),
            date("d", $ts)
        );
        $col1 = sprintf("<a href=\"%s\">%s</a>", $link, date("Md,y", $ts));
    }
    $hrecord = new_record($row["high"], $row["high_record"]);
    $lrecord = new_record2($row["low"], $row["low_record"]);
    $precord = new_record3($row["precip"], $row["precip_record"]);
    $srecord = new_record3($row["snow"], $row["snow_record"]);
    $rowlabel = "0";
    if ($hrecord != "" || $lrecord != "" || $precord != "" || $srecord != ""){
        $rowlabel = "1";
    }
    $hd = departure($row["high"], $row["high_normal"]);
    $ld = departure($row["low"], $row["low_normal"]);
    $table .= sprintf(
        "<tr data-record='%s'>
        <td nowrap><a href=\"/p.php?pid=%s\" target=\"_blank\"><i class=\"fa fa-list-alt\" alt=\"View Text\"></i></a>
            %s</td>
            <td>%s%s</td><td nowrap>%s</td><td>%s</td>
            <td>%s</td><td>%s</td>
            <td style=\"background: %s;\" data-sort=\"%s\">%s</td>
            <th class=\"empty\"></th>
            <td>%s%s</td><td nowrap>%s</td><td>%s</td>
            <td>%s</td><td>%s</td>
            <td style=\"background: %s;\" data-sort=\"%s\">%s</td>
            <th class=\"empty\"></th>
            <td>%s%s</td><td>%s</td><td>%s</td>
            <td>%s</td><td>%s</td><td>%s</td>
            <th class=\"empty\"></th>
            <td>%s%s</td><td>%s</td><td>%s</td>
            <td>%s</td><td>%s</td>
            <th class=\"empty\"></th>
            <td>%s</td>
            </tr>",
        $rowlabel,
        $row["product"],
        $col1,
        $row["high"],
        $hrecord,
        $row["high_time"],
        $row["high_record"],
        implode(" ", $row["high_record_years"]),
        $row["high_normal"],
        departcolor($row["high"], $row["high_normal"]),
        ($hd == "M") ? "": $hd,
        $hd,

        $row["low"],
        $lrecord,
        $row["low_time"],
        $row["low_record"],
        implode(" ", $row["low_record_years"]),
        $row["low_normal"],
        departcolor($row["low"], $row["low_normal"]),
        ($ld == "M") ? "": $ld,
        $ld,

        $row["precip"],
        $precord,
        $row["precip_record"],
        implode(" ", $row["precip_record_years"]),
        $row["precip_normal"],
        $row["precip_month"],
        $row["precip_month_normal"],

        $row["snow"],
        $srecord,
        $row["snow_record"],
        implode(' ', $row["snow_record_years"]),
        $row["snow_month"],
        $row["snowdepth"],

        $row["average_sky_cover"],
    );
}
$table .= "</tbody></table>";

$sselect = networkSelect("NWSCLI", $station);

$t = new MyView();
$t->iemselect2 = TRUE;
$t->title = "Tabular CLI Report Data";

$t->content = <<<EOM
<ol class="breadcrumb">
    <li><a href="/climate/">Climate Data</a></li>
    <li class="active">Tabular CLI Report Data</li>		
</ol>

<div class="row">
    <div class="col-md-3">This application lists out parsed data from 
    National Weather Service issued daily climate reports.  These reports
    contain 24 hour totals for a period between midnight <b>local standard time</b>.
    This means that during daylight saving time, this period is from 1 AM to 
    1 AM local daylight time!
    </div>
    <div class="col-md-6 well">
    <h4>Option 1: One Station for One Year</h4>
<form method="GET" name="one">
<input type="hidden" name="opt" value="bystation" />
<p><strong>Select Station:</strong>
    <br />{$sselect}
    <br /><strong>Year:</strong>
    <br />{$ys}
    <br /><input type="submit" value="Generate Table" />
</form>

    </div>
    <div class="col-md-3 well">

<h4>Option 2: One Day for Stations</h4>
<form method="GET" name="two">
<input type="hidden" name="opt" value="bydate" />
    {$ys} {$ms} {$ds}
    <br /><input type="submit" value="Generate Table" />
</form>

    </div>
</div>

<p>There is a <a href="/json/">JSON(P) webservice</a> that backends this table presentation, you can
directly access it here:
<br /><code>{$prettyurl}</code></p>

<p>
<button id="makefancy">Make Table Interactive</button> &nbsp;
<button id="makerecords" data-toggle="0"><span id="makerecordslabel">Show Rows with Records</span></button>
</p>

{$table}

<p><strong>Key:</strong> &nbsp; &nbsp;
    <i class="fa fa-star-o"></i> Record Tied,
    <i class="fa fa-star"></i> Record Set.</p>

EOM;
$t->headextra = <<<EOM
<link type="text/css" href="/vendor/jquery-datatables/{$DT}/datatables.min.css" rel="stylesheet" />
EOM;
$t->jsextra = <<<EOM
<script src='/vendor/jquery-datatables/{$DT}/datatables.min.js'></script>
<script src="clitable.js"></script>
EOM;
$t->render('full.phtml');
