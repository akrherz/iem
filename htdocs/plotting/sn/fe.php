<?php 
 include("../../../config/settings.inc.php");
 include("$rootpath/include/forms.php");
 include("$rootpath/include/database.inc.php");
$postgis = iemdb("postgis");

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

$TITLE = "SpotterNetwork Time Series";
include("$rootpath/include/header.php"); 
?>
<h3>SpotterNetwork - Spotter Ground Speed Estimator</h3>

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

<p><strong>Please be patient, the image may take a bit to load...</strong>
<img src="<?php echo $imgurl; ?>" />

<p><strong>Other Spotters with data valid for selected time [num obs]...</strong>
<?php
$sts = mktime($shour, 0, 0, $smonth, $sday, $syear);
$ets = mktime($ehour, 0, 0, $emonth, $eday, $eyear);

$rs = pg_query($postgis, "SELECT name, count(*) as cnt from spotternetwork_$syear
  WHERE valid BETWEEN '". gmdate("Y-m-d H:i", $sts) ."+00' and
  '". gmdate("Y-m-d H:i", $ets) ."+00' GROUP by name ORDER by name ASC");

for($i=0;$row=@pg_fetch_array($rs,$i);$i++){
  echo sprintf("<br /><a href=\"fe.php?spotter=%s&syear=%s&smonth=%s&sday=%s&shour=%s&eyear=%s&emonth=%s&eday=%s&ehour=%s\">%s [%s]</a>", urlencode($row["name"]), $syear, $smonth, $sday, $shour, $eyear, $emonth, $eday, $ehour, $row["name"], $row["cnt"]);

}
?>

<?php include("$rootpath/include/footer.php"); ?>
