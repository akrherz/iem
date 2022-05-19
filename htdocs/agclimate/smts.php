<?php 
define("IEM_APPID", 114);
require_once "../../config/settings.inc.php";
require_once "../../include/forms.php"; 
require_once "../../include/imagemaps.php"; 
require_once "../../include/myview.php";

$t = new MyView();
$t->title = "ISU Soil Moisture Plots";

$now = time();
$d2 = time() - 5 * 86400;
$station = isset($_GET["station"]) ? xssafe($_GET["station"]): "AEEI4";
$year1 = get_int404('year1', date("Y", $d2));
$month1 = get_int404('month1', date("m", $d2));
$day1 = get_int404('day1', date("d", $d2));
$hour1 = get_int404('hour1', 0);

$year2 = get_int404('year2', date("Y", $now));
$month2 = get_int404('month2', date("m", $now));
$day2 = get_int404('day2', date("d", $now));
$hour2 = get_int404('hour2', date("H", $now));

$opt = isset($_GET["opt"]) ? xssafe($_GET["opt"]): 1;

$sts = mktime($hour1, 0, 0, $month1, $day1, $year1);
$ets = mktime($hour2, 0, 0, $month2, $day2, $year2);
$errmsg = "";
if ($ets <= $sts){
	$errmsg = "<div class=\"alert alert-warning\">Error, your requested".
			" End Time is before the Start Time.  Please adjust your selection".
			" and try once again.</div>";
}

$sselect = networkSelect("ISUSM", $station);
$y1 = yearSelect2(2012, $year1, "year1");
$m1 = monthSelect($month1, "month1");
$d1 = daySelect2($day1, "day1");
$h1 = hourSelect($hour1, "hour1");
$y2 = yearSelect2(2012, $year2, "year2");
$m2 = monthSelect($month2, "month2");
$d2 = daySelect2($day2, "day2");
$h2 = hourSelect($hour2, "hour2");

$ar = Array(
    1 => "3 Panel Plot",
    2 => "Just Soil Temps",
    "sm" => "Just Soil Moisture",
    3 => "Daily Max/Min 4 Inch Soil Temps",
    4 => "Daily Solar Radiation",
    5 => "Daily Potential Evapotranspiration",
    6 => "Histogram of Volumetric Soil Moisture",
    7 => "Daily Soil Water + Change",
    8 => "Battery Voltage",
    9 => "Daily Rainfall, 4 inch Soil Temp, and RH",
    10 => "Inversion Diagnostic Plot (BOOI4, CAMI4, CRFI4) Only",
);
$dd = "This plot is a time series graph of
observations from a time period and ISU Soil Moisture station of your choice.";
$desc = Array(1 => $dd,
		2 => $dd,
        "sm" => $dd,
		3 => $dd,
		4 => $dd,
		5 => $dd,
		6 => $dd,
		7 => $dd,
		8 => $dd);
$desc[6] = <<<EOF
This plot presents a histogram of hourly volumetric soil moisture observations.
The y-axis is expressed in logarithmic to better show the low frequency obs
within the distribution.
EOF;
$desc[7] = <<<EOF
This plot computes the daily change in soil water approximately between
the depths of 6 to 30 inches.  This is using only two measurements at
12, and 24 inch depths.  The 12 inch depth is assumed to cover the
6-18 inch layer and the 24 inch depth to cover 18-30 layer.  If you select a
period of less than 60 days, the daily rainfall will be plotted as well.
EOF;
$desc[10] = <<<EOF
This plot provides a diagnostic of the data being provided by the inversion
sensors.  These temperature sensors are installed at 1.5 and 10 feet above the
ground, which then can sense if temperature increases with height.  This
sensor package was installed in 2021 and only found at three sites BOOI4 - Ames
AEA, CRFI4 - Crawfordsville, and CAMI4 - Sutherland.
EOF;

$thedescription = $desc[$opt];
$oselect = make_select("opt", $opt, $ar);

$img = sprintf("<img src=\"/plotting/auto/plot/177/network:ISUSM::".
		"station:%s::opt:%s::sts:%d-%02d-%02d%%20%02d00::".
		"ets:%d-%02d-%02d%%20%02d00.png".
		"\">",
		$station, $opt,
		$year1, $month1, $day1, $hour1,
		$year2, $month2, $day2, $hour2);
if ($errmsg != ""){
	$img = $errmsg;
}

$t->content = <<<EOF
<ol class="breadcrumb">
 <li><a href="/agclimate/">ISU Soil Moisture Network</a></li>
 <li class="active">Soil Moisture Plots</li>
</ol>

<h3>Soil Moisture and Precipitation Timeseries</h3>

<p>This application plots a timeseries of soil moisture and precipitation from
a ISU Soil Moisture station of your choice.  Please select a start and end time
and click the 'Make Plot' button below.

<form name="selector" method="GET" name='getter'>

<table class="table table-bordered">
<thead>
<tr>
<th>Station</th><th>Plot Option</th>
<td></td><th>Year</th><th>Month</th><th>Day</th><th>Hour</th>
</tr>
</thead>

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


<p>{$img}

<p><strong>Plot Description:</strong> {$thedescription}
</p>
EOF;
$t->render('single.phtml');
