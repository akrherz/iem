<?php 
 require_once "../../config/settings.inc.php";
 require_once "../../include/database.inc.php";
 require_once "setup.php";
 require_once "../../include/myview.php";
 require_once "../../include/mlib.php";

 $t = new MyView();
 
 $t->thispage = "iem-sites";
 $t->title = "Satellite Cloud Product";
 $t->sites_current = "scp";
 $year = isset($_GET["year"])? intval($_GET["year"]): date("Y");
 $month = isset($_GET["month"])? intval($_GET["month"]): date("m");
 $day = isset($_GET["day"])? intval($_GET["day"]): date("d");
 $date = mktime(0,0,0,$month, $day, $year);
 
 if ($metadata["archive_begin"]){
    $startyear = intval(date("Y", $metadata["archive_begin"]));
    if ($date < $metadata['archive_begin']){
        $date = $metadata['archive_begin'];
    }
} else {
    $startyear = 1993;
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
        $header .= "<th colspan=\"4\">Satellite $label</th>";
        $header2 .= "<th>Mid</th><th>High</th><th>Levels</th><th>ECA</th>";
    }
}

$table = <<<EOM
<table class="table table-striped table-bordered">
<thead>
<tr><th rowspan="2">SCP Valid UTC</th>$header<th colspan="2">ASOS METAR Report</th></tr>
<tr>$header2<th>Levels</th><th>METAR</th></tr> 
</thead>
<tbody>
EOM;
foreach($json["data"] as $key => $row){
    $table .= sprintf("<tr><td>%sZ</td>", gmdate("Hi", strtotime($row["utc_scp_valid"])));
    foreach($birds as $b){
        $table .= sprintf(
            "<td>%s</td><td>%s</td><td>%s - %s</td><td>%s</td>",
            $row["mid_$b"], $row["high_$b"], $row["cldtop1_$b"],
            $row["cldtop2_$b"], $row["eca_$b"]);
    }
    $table .= sprintf(
        "<td>%s %s<br />%s %s<br />%s %s<br />%s %s<td>%s</td></tr>",
        $row["skyc1"], $row["skyl1"],$row["skyc2"], $row["skyl2"],
        $row["skyc3"], $row["skyl3"], $row["skyc4"], $row["skyl4"],
        $row["metar"]);
}
$table .= "</tbody></table>";

$ys = yearSelect($startyear,date("Y", $date));
$ms = monthSelect(date("m", $date));
$ds = daySelect(date("d", $date));

$t->content = <<<EOF

<h3>Satellite Cloud Product</h3>

<p><a href="https://www.nesdis.noaa.gov/">NESDIS</a> produces a 
<a href="https://www.ospo.noaa.gov/Products/atmosphere/soundings/index.html">Satellite Cloud Product</a> (SCP)
that supplements the ASOS ceilometer readings.  This page merges the SCP data
with the METAR observations for a given UTC date.</p>

<form method="GET">
<input type="hidden" name="station" value="$station">
<input type="hidden" name="network" value="$network">
Year: {$ys}

Month: {$ms}

Day:{$ds}
<input type="submit" value="View Date">

</form>

{$table}

EOF;
$t->render('sites.phtml');
?>
