<?php 
 include("../../../config/settings.inc.php");
 include("$rootpath/include/forms.php");
 include("$rootpath/include/database.inc.php");

$postgis = iemdb("postgis");
pg_query($postgis, "SET TIME ZONE 'GMT'");

$spotter = isset($_GET["spotter"]) ? substr($_GET["spotter"],0,50): "";
$syear = isset($_GET["syear"]) ? intval($_GET["syear"]) : date("Y");
$smonth = isset($_GET["smonth"]) ? intval($_GET["smonth"]) : date("m");
$sday = isset($_GET["sday"]) ? intval($_GET["sday"]) : date("d");
$shour = isset($_GET["shour"]) ? intval($_GET["shour"]) : 0;
$eyear = isset($_GET["eyear"]) ? intval($_GET["eyear"]) : date("Y");
$emonth = isset($_GET["emonth"]) ? intval($_GET["emonth"]) : date("m");
$eday = isset($_GET["eday"]) ? intval($_GET["eday"]) : date("d");
$ehour = isset($_GET["ehour"]) ? intval($_GET["ehour"]) : 23;

$imgurl = sprintf("speed.php?spotter=%s&syear=%s&smonth=%s&sday=%s&shour=%s&eyear=%s&emonth=%s&eday=%s&ehour=%s", urlencode($spotter), $syear, $smonth, $sday, $shour, $eyear, $emonth, $eday, $ehour);

function haversine($lon0, $lon1, $lat0, $lat1){

    $radius = 6371.0;

    $dlat = deg2rad($lat1-$lat0);
    $dlon = deg2rad($lon1-$lon0);
    $a = sin($dlat/2.) * sin($dlat/2.) + cos(deg2rad($lat0)) * cos(deg2rad($lat1)) * sin($dlon/2.) * sin($dlon/2.);
    $c = 2. * atan2(sqrt($a), sqrt(1.-$a));
    $d = ($radius * $c) > 120 ? "": $radius * $c;
    return $d;

}
$data = "";
if ($spotter != ""){
$rs = pg_prepare($postgis, "SELECT", "SELECT x(geom) as lon, y(geom) as lat, 
  valid from spotternetwork_$syear WHERE valid BETWEEN 
  $1 and $2 and name = $3 ORDER by valid ASC");

$sts = mktime($shour, 0, 0, $smonth, $sday, $syear);
$ets = mktime($ehour, 0, 0, $emonth, $eday, $eyear);
$rs = pg_execute($postgis, "SELECT", Array( date("Y-m-d H:i", $sts),
      date("Y-m-d H:i", $ets), $spotter));

$row = pg_fetch_array($rs,0);
$olat = $row["lat"];
$olon = $row["lon"];
$ovalid = strtotime($row["valid"]);
for ($i=0;$row=@pg_fetch_array($rs,$i);$i++)
{
  $ts = strtotime(substr($row["valid"],0,18));
  if ($ovalid == $ts){ continue;}
  $distkm = haversine($olon, $row["lon"], $olat, $row["lat"]);
  $deltat = $ts - $ovalid;
  if ($deltat > 0){
    $mph = $distkm / $deltat * 3600.0 * 0.621371192;
  } else {
    $mph = 0;
  }
  if ($mph > 120){
    $mph = 0;
  } 
    $distance = $distkm * 0.621371192;
  

  $times[] = $ts;
  $speeds[] = $mph;
  $olon = $row["lon"];
  $olat = $row["lat"];
  $ovalid = $ts;
  $data .= sprintf("<tr><td>%s</td><td>%s</td><td>%.6f</td><td>%.6f</td>
  	<td>%.3f</td><td>%.2f</td></tr>\n",
  	$spotter, substr($row["valid"],0,16), $row["lon"], $row["lat"],
  	$distance, $mph );
 }
}
 
$TITLE = "SpotterNetwork Time Series";
$THISPAGE="networks-other";
include("$rootpath/include/header.php"); 
?>
<h3>SpotterNetwork - Spotter Ground Speed Estimator</h3>

<div class="warning">Application has been removed :)</div>

<?php include("$rootpath/include/footer.php"); die(); ?>
<blockquote><a href="http://www.spotternetwork.org/">SpotterNetwork</a> is
a community project that brings storm chasers together. The IEM collects the 
minute interval position reports from this project and archives then.  This
application uses those reports and attempts to produce time series plots of 
spotter ground speed.  A whole boat load of caveats apply, but the app works
well if the GPS data is good! This archive begins 
<strong>7 April 2010.</strong></blockquote>

<form method="GET" action="fe.php" name="main">
<table>
<tr>
 <th>Spotter Name</th>
 <td>Year</td><th>Month</th><th>Day</th><th>Hour</th>
 <td rowspan="3"><input type="submit" value="View Plot" /></td>
</tr>
<tr>
 <td rowspan="2"><input type="text" name="spotter" size="30" value="<?php echo $spotter; ?>"/></td>
 <td><?php echo yearSelect2(2010, $syear, "syear"); ?></td>
 <td><?php echo monthSelect($smonth, "smonth"); ?></td>
 <td><?php echo daySelect2($sday, "sday"); ?></td>
 <td><?php echo gmthourSelect($shour, "shour"); ?></td>
</tr>
<tr>
 <td><?php echo yearSelect2(2010, $eyear, "syear"); ?></td>
 <td><?php echo monthSelect($emonth, "emonth"); ?></td>
 <td><?php echo daySelect2($eday, "eday"); ?></td>
 <td><?php echo gmthourSelect($ehour, "ehour"); ?></td>
</tr>
</table>
</form>

<p>
<?php if ($spotter != "") { 
    echo "<strong>Please be patient, the page may take a bit to load...</strong>
<br /><a href=\"#data\">View Raw Data</a><br />";	
	echo "<img src=\"$imgurl\" />";
} ?>

<p><strong>Spotters with data valid for selected time [num obs]...</strong>
<?php
$sts = mktime($shour, 0, 0, $smonth, $sday, $syear);
$ets = mktime($ehour, 0, 0, $emonth, $eday, $eyear);

$rs = pg_query($postgis, "SELECT name, count(*) as cnt from spotternetwork_$syear
  WHERE valid BETWEEN '". gmdate("Y-m-d H:i", $sts) ."+00' and
  '". gmdate("Y-m-d H:i", $ets) ."+00' GROUP by name ORDER by name ASC");

for($i=0;$row=@pg_fetch_array($rs,$i);$i++){
  echo sprintf("<br /><a href=\"fe.php?spotter=%s&syear=%s&smonth=%s&sday=%s&shour=%s&eyear=%s&emonth=%s&eday=%s&ehour=%s\">%s</a> [%s]", urlencode($row["name"]), $syear, $smonth, $sday, $shour, $eyear, $emonth, $eday, $ehour, $row["name"], $row["cnt"]);

}
?>
<h4>Raw Data Report:</h4>
<a name="data"></a>
<table cellpadding="3" cellspacing="0" border="1">
<tr><th>Spotter</th><td>Valid UTC</td><td>Longitude</td><td>Latitude</td><td>Distance [mile]</td><td>Speed [mph]</td></tr>
<?php echo $data; ?>
</table>


<?php include("$rootpath/include/footer.php"); ?>
