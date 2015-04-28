<?php 
include("../../config/settings.inc.php");
include_once "../../include/myview.php";
$t = new MyView();
$t->title = "ISU Soil Moisture Plots";
$t->thispage = "networks-agclimate";

include("../../include/forms.php"); 
include("../../include/imagemaps.php"); 

$now = time();
$d2 = time() - 3 * 86400;
$station = isset($_GET["station"]) ? $_GET["station"] : "CAMI4";
$year1 = isset($_REQUEST['year1']) ? intval($_REQUEST['year1']): date("Y", $d2);
$month1 = isset($_REQUEST['month1']) ? intval($_REQUEST['month1']): date("m", $d2);
$day1 = isset($_REQUEST['day1']) ? intval($_REQUEST['day1']): date("d", $d2);
$hour1 = isset($_REQUEST['hour1']) ? intval($_REQUEST['hour1']): 0;
$year2 = isset($_REQUEST['year2']) ? intval($_REQUEST['year2']): date("Y", $now);
$month2 = isset($_REQUEST['month2']) ? intval($_REQUEST['month2']): date("m", $now);
$day2 = isset($_REQUEST['day2']) ? intval($_REQUEST['day2']): date("d", $now);
$hour2 = isset($_REQUEST['hour2']) ? intval($_REQUEST['hour2']): date("H", $now);
$opt = isset($_REQUEST['opt']) ? $_REQUEST['opt'] : '1';

$sselect = networkSelect("ISUSM", $station);
$y1 = yearSelect2(2012, $year1, "year1");
$m1 = monthSelect($month1, "month1");
$d1 = daySelect2($day1, "day1");
$h1 = hourSelect($hour1, "hour1");
$y2 = yearSelect2(2012, $year2, "year2");
$m2 = monthSelect($month2, "month2");
$d2 = daySelect2($day2, "day2");
$h2 = hourSelect($hour2, "hour2");

$ar = Array("1" => "3 Panel Plot",
		"2" => "Just Soil Temps",
		"3" => "Daily Max/Min 4 Inch Soil Temps",
		"4" => "Daily Solar Radiation");
$oselect = make_select("opt", $opt, $ar);

$img = sprintf("smts.py?opt=%s&amp;station=%s&amp;year1=%s&amp;year2=%s"
		."&amp;month1=%s&amp;month2=%s&amp;day1=%s&amp;day2=%s&amp;"
		."hour1=%s&amp;hour2=%s", 
		$opt, $station, $year1, $year2, $month1, $month2, $day1, $day2, 
		$hour1, $hour2);

$t->content = <<<EOF
<ol class="breadcrumb">
 <li><a href="/agclimate/">AgClimate Network</a></li>
 <li class="active">Soil Moisture Plots</li>
</ol>

<h3>Soil Moisture and Precipitation Timeseries</h3>

<p>This application plots a timeseries of soil moisture and precipitation from
a ISU Soil Moisture station of your choice.  Please select a start and end time
and click the 'Make Plot' button below.

<form name="selector" method="GET" name='getter'>

<table class="table table-bordered">
<thead><tr><th>Station</th><th>Plot Option</th><td></td><th>Year</th><th>Month</th><th>Day</th><th>Hour</th></tr></thead>

<tbody>
<tr><td rowspan='2'>{$sselect}</td>
 <td rowspan="2">{$oselect}</td>
<td>Start Time</td>
	<td>{$y1}</td>
	<td>{$m1}</td>
	<td>{$d1}</td>
	<td>{$h1}</td>
	</tr>
<tr>
<td>End Time</td>
	<td>{$y2}</td>
	<td>{$m2}</td>
	<td>{$d2}</td>
	<td>{$h2}</td>
	</tr>

</tbody>
</table>

<input type="submit" value="Make Plot">
</form>


<p><img src="{$img}" class="img img-responsive">

<p><strong>Plot Description:</strong> This plot is a time series graph of
observations from a time period and ISU Soil Moisture station of your choice.
</p>
EOF;
$t->render('single.phtml');
?>
