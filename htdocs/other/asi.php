<?php 
include("../../config/settings.inc.php");
include ("$rootpath/include/forms.php");
include "$rootpath/include/database.inc.php";
function download_data($sts, $ets){
	
	$dbconn = iemdb('other');
	$rs = pg_prepare($dbconn, "SELECT", "SELECT * from asi_data WHERE
			valid >= $1 and valid < $2 ORDER by valid ASC");
	$rs = pg_execute($dbconn, "SELECT", Array(date("Y-m-d", $sts), 
			date("Y-m-d", $ets)));
	header("Content-type: text/plain");
	echo "station,valid,";
	for ($i=1;$i<13;$i++){
		echo sprintf("ch%savg,ch%ssd,ch%smax,ch%smin,", $i, $i, $i,$i);
	}
	echo "\n";
	for ($i=0;$row=@pg_fetch_assoc($rs,$i);$i++){
		echo sprintf("%s,%s,", $row['station'], $row['valid']);
		for ($j=1;$j<13;$j++){
			echo sprintf("%s,%s,%s,%s,", $row["ch${j}avg"],
				$row["ch${j}sd"], $row["ch${j}max"], $row["ch${j}min"]);
		}
		echo "\n";
	}
	
} // End of download_data

$syear = isset($_GET["syear"]) ? $_GET["syear"] : date("Y", time() - 86400);
$eyear = isset($_GET["eyear"]) ? $_GET["eyear"] : date("Y", time() - 86400);
$emonth = isset($_GET["emonth"]) ? $_GET["emonth"] : date("m", time());
$eday = isset($_GET["eday"]) ? $_GET["eday"] : date("d", time() );
$smonth = isset($_GET["smonth"]) ? $_GET["smonth"] : date("m", time()- 86400 );
$sday = isset($_GET["sday"]) ? $_GET["sday"] : date("d", time() - 86400);
$ehour = isset($_GET["ehour"]) ? $_GET["ehour"] : 0;
$shour = isset($_GET["shour"]) ? $_GET["shour"] : 0;
$station = isset($_REQUEST['station']) ? $_REQUEST['station']: 'ISU4003';

$imguri = sprintf("asi_plot.py?station=%s&syear=%s&smonth=%s&sday=%s&shour=%s&eyear=%s&emonth=%s&eday=%s&ehour=%s",
		$station, $syear, $smonth, $sday, $shour, $eyear, $emonth, $eday, $ehour);

if (isset($_REQUEST["action"])){

	
	$sts = mktime(0,0,0,$smonth, $sday, $syear);
	$ets = mktime(0,0,0,$emonth, $eday, $eyear);
	
	if ($_REQUEST["action"] == 'dl'){
		download_data($sts, $ets);
		die();
	}
}

$TITLE = "IEM | Atmospheric Structure Instrumentation";
$THISPAGE = "networks-other";
include("$rootpath/include/header.php");  

$channels = Array(
	"ch1" => "Wind Speed @48.5m [m/s]",
	"ch2" => "Wind Speed @48.5m [m/s]",
	"ch3" => "Wind Speed @32m [m/s]",
	"ch4" => "Wind Speed @32m [m/s]",
	"ch5" => "Wind Speed @10m [m/s]",
	"ch6" => "Wind Speed @10m [m/s]",
	"ch7" => "Wind Direction @47m [deg]",
	"ch8" => "Wind Direction @40m [deg]",
	"ch9" => "Wind Direction @10m [deg]",
	"ch10" => "Air Temperature @3m [C]",
	"ch11" => "Air Temperature @48.5m [C]",
	"ch12" => "Barometer @48.5m [mb]"
				);

?>
<h3 class="heading">Atmospheric Structure Data</h3>

<p>The IEM is collecting and providing data from an instrumentation project
that outfitted two towers with wind and temperature sensors.  
(Insert more details here).

<h3>Plots of this data</h3>
<form method="GET" name="plot">
<input type="hidden" name="action" value="plot" />

<table>
<tr><td></td><th>Year:</th>
  <th>Month:</th>
  <th>Day:</th>
  <th>Hour:</th>
  </tr>

<tr><th>Start Date:</th>
  <td><?php echo yearSelect(2012, $syear, "syear"); ?></td>
  <td><?php echo monthSelect($smonth, "smonth"); ?></td>
  <td><?php echo daySelect2($sday, "sday"); ?></td>
  <td><?php echo hourSelect($shour, "shour"); ?></td>
  </tr>

<tr><th>End Date:</th>
  <td><?php echo yearSelect(2012, $eyear, "eyear"); ?></td>
  <td><?php echo monthSelect($emonth, "emonth"); ?></td>
  <td><?php echo daySelect2($eday, "eday"); ?></td>
  <td><?php echo hourSelect($ehour, "ehour"); ?></td>
  </tr>
  
</table>
<input type="submit" value="Generate Plot">
</form>

<img src="<?php echo $imguri; ?>" />

<h3>Download this data</h3>
<form method="GET" name="dl">
<input type="hidden" name="action" value="dl" />

<p>This form will give you all variables for the day interval of your choice.
The archive begins on 1 October 2012.
<br />Timestamps and date periods are in local Central time.

<table>
<tr><td></td><th>Year:</th>
  <th>Month:</th>
  <th>Day:</th></tr>

<tr><th>Start Date:</th>
  <td><?php echo yearSelect(2012, date("Y"), "syear"); ?></td>
  <td><?php echo monthSelect(date("m"), "smonth"); ?></td>
  <td><?php echo daySelect2(date("d"), "sday"); ?></td></tr>

<tr><th>End Date:</th>
  <td><?php echo yearSelect(2012, date("Y"), "eyear"); ?></td>
  <td><?php echo monthSelect(date("m"), "emonth"); ?></td>
  <td><?php echo daySelect2(date("d"), "eday"); ?></td></tr>

</table>
<input type="submit" value="Download Data">
</form>

<h3>Decoder Ring for Data Columns</h3>

<p>Each tower has twelve instruments.  Each instrument reports a five minute
average, standard deviation, maximum, and minimum value.  Each instrument
is labelled as a channel within the datafile.

<p><table cellpadding="3" cellspacing="0" border="1">
<tr><th>Channel</th><th>Measurement @heightAGL [units]</th></tr>
<?php 
while (list($key,$ch)=each($channels)){
	echo sprintf("<tr><td>%s</td><td>%s</td></tr>", $key, $ch);
}
?>
</table>
<?php include("$rootpath/include/footer.php"); ?>
