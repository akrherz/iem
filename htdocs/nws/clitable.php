<?php 
include("../../config/settings.inc.php");
define("IEM_APPID", 156);
include_once "../../include/myview.php";
include_once "../../include/database.inc.php";
include_once "../../include/forms.php";
include_once "../../include/imagemaps.php";
include_once "../../include/network.php";

$nt = new NetworkTable("NWSCLI");

$station = isset($_GET["station"]) ? $_GET["station"]: 'KDSM';
$year = isset($_GET["year"]) ? intval($_GET["year"]): date("Y");
$month = isset($_GET["month"]) ? intval($_GET["month"]): null;
$day = isset($_GET["day"]) ? intval($_GET["day"]): null;
$opt = isset($_GET["opt"]) ? $_GET["opt"]: "bystation";

$ys = yearSelect(2009, $year, "year");
$ms = monthSelect($month, "month");
$ds = daySelect($day, "day");

$pgconn = iemdb("iem");
$byday = false;
if ($opt === "bystation"){
	$title = sprintf("Station: %s for Year: %s", $station, $year);
	$col1label = "Date";
	$rs = pg_prepare($pgconn, "SELECT", "SELECT *,
			array_to_string(high_record_years, ' ') as hry,
			array_to_string(low_record_years, ' ') as lry,
			array_to_string(precip_record_years, ' ') as pry,
			array_to_string(snow_record_years, ' ') as sry
			from cli_data where
			station = $1 and valid BETWEEN $2 and $3 ORDER by valid ASC");
	$rs = pg_execute($pgconn, "SELECT", Array($station, "{$year}-01-01",
		"{$year}-12-31"));
} else {
	$col1label = "Station";
	$byday = true;
	$day = mktime(0,0,0, $month, $day, $year);
	$title = sprintf("All Stations for Date: %s", date("d F Y", $day));
	$rs = pg_prepare($pgconn, "SELECT", "SELECT *,
			array_to_string(high_record_years, ' ') as hry,
			array_to_string(low_record_years, ' ') as lry,
			array_to_string(precip_record_years, ' ') as pry,
			array_to_string(snow_record_years, ' ') as sry
			from cli_data where
			valid = $1 ORDER by station ASC");
	$rs = pg_execute($pgconn, "SELECT", Array(date("Y-m-d", $day)));
}

$table = <<<EOF
<style>
.empty{
	width: 0px !important;
	border: 0px !important;
	padding: 2px !important;
	background: tan !important;
}	
</style>
<h3>{$title}</h3>
<table class="table table-condensed table-striped table-bordered table-hover">
<thead>
<tr class="small">
	<th rowspan="2">{$col1label}</th>
	<th colspan="6">Maximum Temperature &deg;F</th>
	<th class="empty"></th>
	<th colspan="6">Minimum Temperature &deg;F</th>
	<th class="empty"></th>
	<th colspan="6">Precip (inches)</th>
	<th class="empty"></th>
	<th colspan="4">Snow (inches)</th>
</tr>
<tr class="small">
	<th>Ob</th><th>Time</th><th>Rec</th><th>Years</th><th>Avg</th>
	<th>&Delta;</th><th class="empty"></th>
	
	<th>Ob</th><th>Time</th><th>Rec</th><th>Years</th><th>Avg</th>
	<th>&Delta;</th><th class="empty"></th>
	
	<th>Ob</th><th>Rec</th><th>Years</th>
	<th>Avg</th><th>Mon to Date</th><th>Mon Avg</th><th class="empty"></th>
			
	<th>Ob</th><th>Rec</th><th>Years</th><th>Mon to Date</th>
</tr>
</thead>
EOF;
function departure($actual, $normal){
	if ($actual == null || $normal == null) return "M";
	return $actual - $normal;
}
function departcolor($actual, $normal){
	if ($actual == null || $normal == null) return "#FFF";
	$diff = $actual - $normal;
	if ($diff == 0) return "#fff";
	if ($diff >= 10) return "#FF1493";
	if ($diff > 0) return "#D8BFD8";
	if ($diff > -10) return "#87CEEB";
	if ($diff <= -10) return "#00BFFF";
	return "#fff";
}
function trace($val){
	if ($val == 0.0001) return 'T';
	return $val;
}
function new_record($actual, $record){
	if ($actual == null || $record == null) return "";
	if ($actual == $record) return "<i class=\"glyphicon glyphicon-star-empty\"></i>";
	if ($actual > $record) return "<i class=\"glyphicon glyphicon-star\"></i>";
}
function new_record2($actual, $record){
	if ($actual == null || $record == null) return "";
	if ($actual == $record) return "<i class=\"glyphicon glyphicon-star-empty\"></i>";
	if ($actual < $record) return "<i class=\"glyphicon glyphicon-star\"></i>";
}
for($i=0; $row=@pg_fetch_assoc($rs,$i); $i++){
	$uri = sprintf("/p.php?pid=%s", $row["product"]);
	$ts = strtotime($row["valid"]);
	if ($byday){
		$link = sprintf("clitable.php?station=%s&year=%s", $row["station"],
				date("Y", $ts));
		$col1 = sprintf("<a href=\"%s\" class=\"small\">%s %s</a>", $link, $row["station"],
				$nt->table[$row["station"]]['name']);
	}else {
		$link = sprintf("clitable.php?opt=bydate&year=%s&month=%s&day=%s", date("Y", $ts),
				date("m", $ts), date("d", $ts));
		$col1 = sprintf("<a href=\"%s\">%s</a>", $link, date("Md,y", $ts));
	}
	$table .= sprintf("<tr><td nowrap><a href=\"%s\"><i class=\"glyphicon glyphicon-list-alt\" alt=\"View Text\"></i></a>
			%s</td>
			<td>%s%s</td><td nowrap>%s</td><td>%s</td>
			<td>%s</td><td>%s</td><td style='background: %s;'>%s</td>
			<th class=\"empty\"></th>
			<td>%s%s</td><td nowrap>%s</td><td>%s</td>
			<td>%s</td><td>%s</td><td style='background: %s;'>%s</td>
			<th class=\"empty\"></th>
			<td>%s%s</td><td>%s</td><td>%s</td>
			<td>%s</td><td>%s</td><td>%s</td>
			<th class=\"empty\"></th>
			<td>%s%s</td><td>%s</td><td>%s</td>
			<td>%s</td>
			</tr>", $uri, $col1, 
			$row["high"], new_record($row["high"], $row["high_record"]),
			$row["high_time"], $row["high_record"],
			$row["hry"], $row["high_normal"],
			departcolor($row["high"], $row["high_normal"]),
			departure($row["high"], $row["high_normal"]),
			
			$row["low"], new_record2($row["low"], $row["low_record"]),
			$row["low_time"], $row["low_record"],
			$row["lry"], $row["low_normal"],
			departcolor($row["low"], $row["low_normal"]),
			departure($row["low"], $row["low_normal"]),
			
			trace($row["precip"]),
			new_record($row["precip"], $row["precip_record"]),
			trace($row["precip_record"]), $row["pry"],
			trace($row["precip_normal"]), trace($row["precip_month"]), 
			trace($row["precip_month_normal"]),
			
			trace($row["snow"]),
			new_record($row["snow"], $row["snow_record"]),
			trace($row["snow_record"]), $row["sry"],
			trace($row["snow_month"])
				
		);
}
$table .= "</table>";

$sselect = networkSelect("NWSCLI", $station);

$t = new MyView();
$t->title = "Tabular CLI Report Data";

$t->content = <<<EOF
<ol class="breadcrumb">
	<li><a href="/climate/">Climate Data</a></li>
	<li class="active">Tabular CLI Report Data</li>		
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
			

<div class="table-responsive">
	{$table}
</div>

<p><strong>Key:</strong> &nbsp; &nbsp;
			<i class="glyphicon glyphicon-star-empty"></i> Record Tied,
			<i class="glyphicon glyphicon-star"></i> Record Set.</p>

EOF;

$t->render('single.phtml');
?>