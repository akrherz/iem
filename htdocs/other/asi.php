<?php 
require_once "../../config/settings.inc.php";
require_once "../../include/forms.php";
require_once "../../include/database.inc.php";
require_once "../../include/imagemaps.php";
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
	for ($i=0;$row=pg_fetch_assoc($rs);$i++){
		echo sprintf("%s,%s,", $row['station'], $row['valid']);
		for ($j=1;$j<13;$j++){
			echo sprintf("%s,%s,%s,%s,", $row["ch${j}avg"],
				$row["ch${j}sd"], $row["ch${j}max"], $row["ch${j}min"]);
		}
		echo "\n";
	}
	
} // End of download_data

$syear = isset($_GET["syear"]) ? intval($_GET["syear"]) : date("Y", time() - 86400);
$eyear = isset($_GET["eyear"]) ? intval($_GET["eyear"]) : date("Y", time() - 86400);
$emonth = isset($_GET["emonth"]) ? intval($_GET["emonth"]) : date("m", time());
$eday = isset($_GET["eday"]) ? intval($_GET["eday"]) : date("d", time() );
$smonth = isset($_GET["smonth"]) ? intval($_GET["smonth"]) : date("m", time()- 86400 );
$sday = isset($_GET["sday"]) ? intval($_GET["sday"]) : date("d", time() - 86400);
$ehour = isset($_GET["ehour"]) ? intval($_GET["ehour"]): 0;
$shour = isset($_GET["shour"]) ? intval($_GET["shour"]): 0;
$station = isset($_REQUEST['station']) ? xssafe($_REQUEST['station']): 'ISU4003';

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
include("../../include/myview.php");
$t = new MyView();

$t->title = "Atmospheric Structure Instrumentation";

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

$c="";
foreach($channels as $key => $ch){
	$c .= sprintf("<tr><td>%s</td><td>%s</td></tr>", $key, $ch);
}

$nselect = networkSelect("ISUASI", $station);
$ys = yearSelect2(2012, $syear, "syear");
$ms = monthSelect($smonth, "smonth");
$ds = daySelect2($sday, "sday");
$hs = hourSelect($shour, "shour");
$ye = yearSelect2(2012, $eyear, "eyear");
$me = monthSelect($emonth, "emonth");
$de = daySelect2($eday, "eday");
$he = hourSelect($ehour, "ehour");
$t->content = <<<EOF
<h3>Atmospheric Structure Data</h3>

<p>The IEM is collecting and providing data from an instrumentation project
that outfitted two towers with wind and temperature sensors.  
(Insert more details here).

<h3>Plots of this data</h3>
<form method="GET" name="plot">
<input type="hidden" name="action" value="plot" />

<strong>Select station:</strong>{$nselect}

<table>
<tr><td></td><th>Year:</th>
  <th>Month:</th>
  <th>Day:</th>
  <th>Hour:</th>
  </tr>

<tr><th>Start Date:</th>
  <td>{$ys}</td>
  <td>{$ms}</td>
  <td>{$ds}</td>
  <td>{$hs}</td>
  </tr>

<tr><th>End Date:</th>
  <td>{$ye}</td>
  <td>{$me}</td>
  <td>{$de}</td>
  <td>{$he}</td>
  </tr>
  
</table>
<input type="submit" value="Generate Plot">
</form>

<img src="{$imguri}" />

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
  <td>{$ys}</td>
  <td>{$ms}</td>
  <td>{$ds}</td></tr>

<tr><th>End Date:</th>
  <td>{$ye}</td>
  <td>{$me}</td>
  <td>{$de}</td></tr>

</table>
<input type="submit" value="Download Data">
</form>

<h3>Decoder Ring for Data Columns</h3>

<p>Each tower has twelve instruments.  Each instrument reports a ten minute
average, standard deviation, maximum, and minimum value.  Each instrument
is labelled as a channel within the datafile.

<p><table cellpadding="3" cellspacing="0" border="1">
<tr><th>Channel</th><th>Measurement @heightAGL [units]</th></tr>
{$c}
</table>
EOF;
$t->render('single.phtml');
