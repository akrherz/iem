<?php
/*
 * List out COOP extremes table
 */
require_once "../../config/settings.inc.php";
require_once "../../include/myview.php";
$t = new MyView();

define("IEM_APPID", 2);
require_once "../../include/forms.php";
require_once "../../include/database.inc.php";
require_once "../../include/network.php";
require_once "../../include/mlib.php";
require_once "../../include/imagemaps.php";

$tbl = isset($_GET["tbl"]) ? substr($_GET["tbl"], 0, 10) : "climate";
$month = get_int404("month", date("m"));
$day = get_int404("day", date("d"));
$valid = mktime(0, 0, 0, $month, $day, 2000);
$sortcol = isset($_GET["sortcol"]) ? xssafe($_GET["sortcol"]) : "station";
$network = isset($_GET['network']) ? substr($_GET['network'], 0, 9) : 'IACLIMATE';
$station = isset($_GET["station"]) ? xssafe($_GET["station"]) : null;
$sortdir = isset($_GET["sortdir"]) ? xssafe($_GET['sortdir']) : 'ASC';

$syear = 1800;
$eyear = intval(date("Y")) + 1;
if ($tbl == "climate51") {
    $syear = 1951;
} else if ($tbl == "climate71") {
    $syear = 1971;
    $eyear = 2001;
} else if ($tbl == "climate81") {
    $syear = 1981;
    $eyear = 2011;
}

$t->title = "NWS COOP Daily Climatology";

$nt = new NetworkTable($network);
$cities = $nt->table;

$connection = iemdb("coop");

$td = date("Y-m-d", $valid);
// Option 1, we want climo for one station!
if ($station != null) {
    if ($sortcol == 'station') $sortcol = 'valid';
    $jdata = file_get_contents("http://iem.local/json/climodat_stclimo.py?station={$station}&syear={$syear}&eyear={$eyear}");
    $URI = sprintf("https://mesonet.agron.iastate.edu/json/climodat_stclimo.py?station={$station}&syear={$syear}&eyear={$eyear}");
    $json = json_decode($jdata, $assoc = TRUE);
    $data = array();
    $table = "";
    foreach ($json['climatology'] as $key => $val) {
        $val["valid"]  = mktime(0, 0, 0, $val["month"], $val["day"], 2000);
        $data[] = $val;
    }
    if ($sortdir == 'ASC') {
        $sorted_data = aSortBySecondIndex($data, $sortcol, "asc");
    } else {
        $sorted_data = aSortBySecondIndex($data, $sortcol, "desc");
    }
    foreach ($sorted_data as $key => $val) {
        $link = sprintf(
            "extremes.php?day=%s&amp;month=%s&amp;network=%s&amp;tbl=%s",
            $day,
            $month,
            $network,
            $tbl
        );
        $table .= sprintf(
            "<tr><td><a href=\"%s\">%s</a></td><td>%s</td>
                 <td>%.1f</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>
                 <td></td>
                 <td>%.1f</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>
                 <td></td>
                 <td>%.2f</td><td>%.2f</td><td>%s</td>
                 </tr>",
            $link,
            date("d M", $val["valid"]),
            $val["years"],
            $val["avg_high"],
            $val["max_high"],
            implode(", ", $val["max_high_years"]),
            $val["min_high"],
            implode(", ", $val["min_high_years"]),
            $val["avg_low"],
            $val["max_low"],
            implode(", ", $val["max_low_years"]),
            $val["min_low"],
            implode(", ", $val["min_low_years"]),
            $val["avg_precip"],
            $val["max_precip"],
            implode(", ", $val["max_precip_years"])
        );
    }

    $h3 = "<h3 class=\"heading\">NWS COOP Climatology for " . $cities[strtoupper($station)]["name"] . " (ID: " . $station . ")</h3>";
    // Option 2, just a single date
} else {
    if ($sortcol == 'valid') $sortcol = 'station';
    $jdata = file_get_contents("http://iem.local/geojson/climodat_dayclimo.py?network={$network}&month={$month}&day={$day}&syear={$syear}&eyear={$eyear}");
    $URI = sprintf("https://mesonet.agron.iastate.edu/geojson/climodat_dayclimo.py?network={$network}&month={$month}&day={$day}&syear={$syear}&eyear={$eyear}");
    $json = json_decode($jdata, $assoc = TRUE);
    $data = array();
    $table = "";
    foreach ($json['features'] as $key => $val) {
        $data[] = $val['properties'];
    }
    if ($sortdir == 'ASC') {
        $sorted_data = aSortBySecondIndex($data, $sortcol, "asc");
    } else {
        $sorted_data = aSortBySecondIndex($data, $sortcol, "desc");
    }
    foreach ($sorted_data as $key => $val) {
        $link = sprintf(
            "extremes.php?station=%s&amp;network=%s&amp;tbl=%s",
            $val["station"],
            $network,
            $tbl
        );
        $table .= sprintf(
            "<tr><td><a href=\"%s\">%s</a> (%s)</td><td>%s</td>
                 <td>%.1f</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>
                 <td></td>
                 <td>%.1f</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>
                 <td></td>
                 <td>%.2f</td><td>%.2f</td><td>%s</td>
                 </tr>",
            $link,
            $cities[$val["station"]]['name'],
            $val["station"],
            $val["years"],
            $val["avg_high"],
            $val["max_high"],
            implode(", ", $val["max_high_years"]),
            $val["min_high"],
            implode(", ", $val["min_high_years"]),
            $val["avg_low"],
            $val["max_low"],
            implode(", ", $val["max_low_years"]),
            $val["min_low"],
            implode(", ", $val["min_low_years"]),
            $val["avg_precip"],
            $val["max_precip"],
            implode(", ", $val["max_precip_years"])
        );
    }

    $h3 = "<h3>NWS COOP Climatology for " . date("d F", $valid) . "</h3>";
}

$netselect = selectClimodatNetwork($network, "network");
$mselect = monthSelect($month, "month");
$dselect = daySelect($day, "day");

$ar = array(
    "climate" => "All Available",
    "climate51" => "Since 1951",
    "climate71" => "1971-2000",
    "climate81" => "1981-2010"
);
$tblselect = make_select("tbl", $tbl, $ar);

$sortdir2 = $sortdir == 'ASC' ? 'DESC' : 'ASC';
if ($station != null) {
    $uribase = sprintf("&station=%s&network=%s&tbl=%s&amp;sortdir=%s", $station, $network, $tbl, $sortdir2);
    $h4 = "<a href='extremes.php?sortcol=valid" . $uribase . "'>Date</a>";
} else {
    $uribase = sprintf("&day=%s&month=%s&network=%s&tbl=%s&amp;sortdir=%s", $day, $month, $network, $tbl, $sortdir2);
    $h4 = "<a href='extremes.php?sortcol=station&day=" . $day . "&month=" . $month . "'>Station</a>";
}


$t->content = <<<EOF
 
 {$h3}
 
<p>This table gives a listing of <b>unofficial</b> daily records for NWS
COOP stations.  Some records may have occured on multiple years, only one
is listed here.  You may click on a column to sort it.  You can click on the station
name to get all daily records for that station or click on the date to get all records
for that date.</p>

<p>The data found in this table was derived from the following
<a href="/json/">JSON webservice</a>:<br />
<code>{$URI}</code>
</p>

<form method="GET" action="extremes.php" name="myform">
<table class="table table-bordered">
<thead>
<tr>
 <th>Select State:</th>
 <th>Select Date:</th>
 <th>Select Record Database:</th>
 <th></th>
</tr>
</thead>
<tbody>
<tr>
 <td>{$netselect}</td>
 <td>{$mselect} {$dselect}</td>
 <td>{$tblselect}</td>
<td><input type="submit" value="Request"></td>
</tr>
</tbody>
</table>
</form>

<br />

<table class="table table-bordered table-condensed table-striped">
<thead>
  <tr>
   <th rowspan='2' class='subtitle' valign='top'>
{$h4}
</th>
<th rowspan='2' class='subtitle' valign='top'>Years</th>
   <th colspan='5' class='subtitle'>High Temperature [F]</th>
   <td>&nbsp;</td>
   <th colspan='5' class='subtitle'>Low Temperature [F]</th>
   <td>&nbsp;</td>
   <th colspan='3' class='subtitle'>Precipitation [inch]</th>
  </tr>
  <tr>
    <th><a href='extremes.php?sortcol=avg_high{$uribase}'>Avg:</a></th>
    <th><a href='extremes.php?sortcol=max_high{$uribase}'>Max:</a></th>
    <th><a href='extremes.php?sortcol=max_high_years{$uribase}'>Year:</a></th>
    <th><a href='extremes.php?sortcol=min_high{$uribase}'>Min:</a></th>
    <th><a href='extremes.php?sortcol=min_high_years{$uribase}'>Year:</a></th>
    <td>&nbsp;</td>
    <th><a href='extremes.php?sortcol=avg_low{$uribase}'>Avg:</a></th>
    <th><a href='extremes.php?sortcol=max_low{$uribase}'>Max:</a></th>
    <th><a href='extremes.php?sortcol=max_low_years{$uribase}'>Year:</a></th>
    <th><a href='extremes.php?sortcol=min_low{$uribase}'>Min:</a></th>
    <th><a href='extremes.php?sortcol=min_low_years{$uribase}'>Year:</a></th>
    <td>&nbsp;</td>
    <th><a href='extremes.php?sortcol=avg_precip{$uribase}'>Avg:</a></th>
    <th><a href='extremes.php?sortcol=max_precip{$uribase}'>Max:</a></th>
    <th><a href='extremes.php?sortcol=max_precip_years{$uribase}'>Year:</a></th>
  </tr>
</thead>
<tbody>
{$table}
</tbody>
</table>
EOF;
$t->render('single.phtml');
