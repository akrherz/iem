<?php
require_once "../../config/settings.inc.php";
define("IEM_APPID", 130);
require_once "../../include/myview.php";
require_once "../../include/database.inc.php";
require_once "../../include/forms.php";
require_once "../../include/imagemaps.php";
require_once "../../include/network.php";

$nt = new NetworkTable("NWSCLI");

$station = isset($_GET["station"]) ? xssafe($_GET["station"]) : 'KDSM';
$year = get_int404("year", date("Y"));
$month = get_int404("month");
$day = get_int404("day");
$opt = isset($_GET["opt"]) ? xssafe($_GET["opt"]) : "bystation";

$ys = yearSelect(2001, $year, "year");
$ms = monthSelect($month, "month");
$ds = daySelect($day, "day");

$byday = false;
if ($opt === "bystation") {
    $title = sprintf("Station: %s for Year: %s", $station, $year);
    $col1label = "Date";
    $uri = sprintf(
        "%s/json/cf6.py?station=%s&year=%s",
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
        "%s/geojson/cf6.py?dt=%s",
        $INTERNAL_BASEURL,
        date("Y-m-d", $day)
    );
    $data = file_get_contents($uri);
    $json = json_decode($data, $assoc = TRUE);
    $arr = $json['features'];
}
$generated_at = $json['generated_at'];
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
<table id="thetable" class="table table-condensed table-striped table-bordered table-hover">
<thead class="sticky">
<tr class="small">
    <th rowspan="2">{$col1label}</th>
    <th colspan="6">Temperature &deg;F</th>
    <th colspan="3">Precipitation</th>
    <th colspan="5">Wind MPH</th>
    <th colspan="4">Misc/Sky</th>
</tr>
<tr class="small">
    <th>High</th><th>Low</th><th>Avg</th><th>Departure</th><th>HDD</th>
    <th>CDD</th>
    <th>Precip</th><th>Snow</th><th>Snow Depth 12z</th>
    <th>Avg Speed</th><th>Max Speed</th><th>Avg Drct</th>
    <th>Max Gust</th><th>Gust Drct</th>
    <th>Minutes Sunshine</th><th>Poss Sunshine</th>
    <th>Cloud SS</th>
    <th>Weather Codes [<a href="#wxcodes">1</a>]</th>
</tr>
</thead>
<tbody>
EOM;

$wxlookup = Array(
    "1" => "FG",
    "2" => "DNSEFG",
    "3" => "TS",
    "4" => "IP",
    "5" => "GR",
    "6" => "FZRA",
    "7" => "DSTSTM",
    "8" => "HZ",
    "9" => "BLSN",
    "X" => "TOR",
    "M" => "M",
    " " => "",  # GIGO
);


foreach ($arr as $entry) {
    $row = ($opt === "bystation") ? $entry : $entry["properties"];
    $ts = strtotime($row["valid"]);
    if ($byday) {
        $link = sprintf(
            "cf6table.php?station=%s&year=%s",
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
            "cf6table.php?opt=bydate&year=%s&month=%s&day=%s",
            date("Y", $ts),
            date("m", $ts),
            date("d", $ts)
        );
        $col1 = sprintf("<a href=\"%s\">%s</a>", $link, date("Md,y", $ts));
    }
    $wxcodes = "";
    if (!is_null($row["wxcodes"])){
        foreach (str_split($row["wxcodes"]) as $code) {
            $wxcodes .= sprintf("%s ", $wxlookup[$code]);
        }
    }
    $table .= sprintf(
        "
        <tr><td nowrap><a href=\"/p.php?pid=%s\" target=\"_blank\"><i class=\"fa fa-list-alt\" alt=\"View Text\"></i></a>
            %s</td>
            <td>%s</td><td nowrap>%s</td><td>%s</td>
            <td>%s</td><td>%s</td><td>%s</td>
            <td>%s</td><td>%s</td><td>%s</td>
            <td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>
            <td>%s</td><td>%s</td><td>%s</td><td>%s</td>
            </tr>",
        $row["product"],
        $col1,
        $row["high"],
        $row["low"],
        $row["avg_temp"],
        $row["dep_temp"],
        $row["hdd"],
        $row["cdd"],
        $row["precip"],
        $row["snow"],
        $row["snowd_12z"],
        $row["avg_smph"],
        $row["max_smph"],
        $row["avg_drct"],
        $row["gust_smph"],
        $row["gust_drct"],
        $row["minutes_sunshine"],
        $row["possible_sunshine"],
        $row["cloud_ss"],
        trim($wxcodes),
    );
}
$table .= "</tbody></table>";

$sselect = networkSelect("NWSCLI", $station);

$t = new MyView();
$t->title = "Tabular CF6 Report Data";

$t->content = <<<EOM
<ol class="breadcrumb">
    <li><a href="/climate/">Climate Data</a></li>
    <li class="active">Tabular CF6 Report Data</li>		
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

<p>This table's data was generated at: <code>{$generated_at}</code> by a
<a href="/json/">JSON(P) webservice</a>, you can directly access it here:
<br /><code>{$prettyurl}</code></p>

<p><button id="makefancy">Make Table Interactive</button></p>

{$table}

<p><a name="wxcodes">1. Weather Codes</a>:

<br />The original CF6 text files use a symbol code to identify weather
conditions.  The table presented on this page converts these codes into
perhaps a slightly more human readable format.  The codes are as follows:

<br />
<table class="table table-condensed table-striped table-bordered table-hover">
<thead>
<tr><th>CF6 Code</th><th>Abbrev</th><th>Meaning</th></tr>
</thead>
<tbody>
<tr><td>1</td><td>FG</td><td>Fog or Mist</td></tr>
<tr><td>2</td><td>DNSEFG</td><td>Fog or Vis 0.25 mile or less</td></tr>
<tr><td>3</td><td>TS</td><td>Thunder</td></tr>
<tr><td>4</td><td>IP</td><td>Ice pellets</td></tr>
<tr><td>5</td><td>GR</td><td>Hail</td></tr>
<tr><td>6</td><td>FZRA</td><td>Freezing Rain or Drizzle</td></tr>
<tr><td>7</td><td>DSTSTM</td><td>Duststorm or Sandstorm vis 0.25 mile or less</td></tr>
<tr><td>8</td><td>HZ</td><td>Smoke or Haze</td></tr>
<tr><td>9</td><td>BLSN</td><td>Blowing Snow</td></tr>
<tr><td>X</td><td>TOR</td><td>Tornado</td></tr>
<tr><td>M</td><td>M</td><td>Missing Data</td></tr>
</tbody>
</table></p>

EOM;

$t->headextra = <<<EOM
<link rel="stylesheet" type="text/css" href="/vendor/select2/4.0.3/select2.min.css"/ >
<link type="text/css" href="/vendor/jquery-datatables/1.10.20/datatables.min.css" rel="stylesheet" />
EOM;
$t->jsextra = <<<EOM
<script src="/vendor/select2/4.0.3/select2.min.js"></script>
<script src='/vendor/jquery-datatables/1.10.20/datatables.min.js'></script>
<script src="cf6table.js"></script>
EOM;
$t->render('full.phtml');
