<?php 
 require_once "../../config/settings.inc.php";
 require_once "../../include/database.inc.php";
 require_once "setup.php";
 require_once "../../include/myview.php";
 require_once "../../include/mlib.php";

 $t = new MyView();
 
 $t->title = "Satellite Cloud Product";
 $t->sites_current = "scp";
$sortdir = isset($_GET["sortdir"]) ? xssafe($_GET["sortdir"]) : $_GET["sortdir"];
 $year = isset($_GET["year"])? intval($_GET["year"]): gmdate("Y");
 $month = isset($_GET["month"])? intval($_GET["month"]): gmdate("m");
 $day = isset($_GET["day"])? intval($_GET["day"]): gmdate("d");
 $date = mktime(0,0,0,$month, $day, $year);
 
$sortopts = Array(
    "asc" => "Ascending",
    "desc" => "Descending",
);
$sortform = make_select("sortdir", $sortdir, $sortopts);

$startyear = 1993;
if ($metadata["archive_begin"]){
    $astart = intval(date("Y", $metadata["archive_begin"]));
    if ($astart > $startyear){
        $startyear = $astart;
    }
    if ($date < $metadata['archive_begin']){
        $date = $metadata['archive_begin'];
    }
}

$wsuri = sprintf("http://iem.local/api/1/scp.json?station=%s&date=%s",
    $station, date("Y-m-d", $date));
$exturi = sprintf("https://mesonet.agron.iastate.edu/".
    "api/1/scp.json?station=%s&amp;date=%s",
    $station, date("Y-m-d", $date));
$data = file_get_contents($wsuri);
$json = json_decode($data, $assoc=TRUE);

$birds = Array();
$possible = Array("1" => "East Sounder", "2" => "West Sounder", "3" => "Imager");
$header = "";
$header2 = "";
foreach($possible as $value => $label){
    $lookup = sprintf("mid_%s", $value);
    if (array_key_exists($lookup, $json["data"][0])){
        $birds[] = $value;
        $header .= "<th colspan=\"4\" class=\"rl\">Satellite $label</th>";
        $header2 .= "<th>Mid Clouds</th><th>High Clouds</th><th>Levels [ft]</th><th class=\"rl\">ECA [%]</th>";
    }
}

function cldtop($val1, $val2){
    if ($val1 === null || $val2 === null){
        return "-";
    }
    return sprintf("%s - %s", $val1, $val2);
}
function skyc($coverage, $level){
    $res = "";
    if ($coverage !== null){
        $res .= $coverage;
    }
    if ($level > 0){
        $res .= sprintf("@%s<br />", $level);
    }
    return $res;
}

$table = <<<EOM
<table>
<thead>
<tr><th rowspan="2" class="rl">SCP Valid UTC</th>$header<th colspan="2">ASOS METAR Report</th></tr>
<tr>$header2<th>Levels ft</th><th>METAR</th></tr> 
</thead>
<tbody>
EOM;
$data = $json["data"];
if ($sortdir == "desc"){
    $data = array_reverse($data);
}
foreach($data as $key => $row){
    $table .= sprintf("<tr><td class=\"rl\">%sZ</td>", gmdate("Hi", strtotime($row["utc_scp_valid"])));
    foreach($birds as $b){
        $table .= sprintf(
            "<td>%s</td><td>%s</td><td>%s</td><td class=\"rl\">%s</td>",
            $row["mid_$b"], $row["high_$b"],
            cldtop($row["cldtop1_$b"], $row["cldtop2_$b"]), $row["eca_$b"]);
    }
    $table .= sprintf(
        "<td>%s %s %s %s<td>%s</td></tr>",
        skyc($row["skyc1"], $row["skyl1"]),
        skyc($row["skyc2"], $row["skyl2"]),
        skyc($row["skyc3"], $row["skyl3"]),
        skyc($row["skyc4"], $row["skyl4"]),
        $row["metar"]);
}
$table .= "</tbody></table>";

$ys = yearSelect($startyear, date("Y", $date));
$ms = monthSelect(date("m", $date));
$ds = daySelect(date("d", $date));

$t->content = <<<EOF
<style>
.rl {
    border-right: 2px solid;
}
tbody>tr:nth-child(even) {
    background-color: #dddddd;
}
</style>

<h3>Satellite Cloud Product</h3>

<p><a href="https://www.nesdis.noaa.gov/">NESDIS</a> produces a 
<a href="https://www.ospo.noaa.gov/Products/atmosphere/soundings/index.html">Satellite Cloud Product</a> (SCP)
that supplements the ASOS ceilometer readings.  This page merges the SCP data
with the METAR observations for a given <strong>UTC date</strong>. Cloud level
values are presented in feet above ground level.  <strong>ECA</strong> represents
estimated cloud amount expressed in percentage. An 
<a href="/api/1/docs#/default/service_scp_json_get">IEM Web Service</a> provided
the following <a href="$exturi">JSON dataset</a> for this page. Data is available
for some sites back to 1993.</p>

<form method="GET">
<input type="hidden" name="station" value="$station">
<input type="hidden" name="network" value="$network">
Year: {$ys}

Month: {$ms}

Day:{$ds}

Time Order:{$sortform}
<input type="submit" value="View Date">

</form>

<p>&nbsp;</p>

{$table}

EOF;
$t->render('sites.phtml');
?>
