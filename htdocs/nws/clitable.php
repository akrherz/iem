<?php 
require_once "../../config/settings.inc.php";
define("IEM_APPID", 156);
require_once "../../include/myview.php";
require_once "../../include/database.inc.php";
require_once "../../include/forms.php";
require_once "../../include/imagemaps.php";
require_once "../../include/network.php";

$nt = new NetworkTable("NWSCLI");

$station = isset($_GET["station"]) ? xssafe($_GET["station"]): 'KDSM';
$year = isset($_GET["year"]) ? intval($_GET["year"]): date("Y");
$month = isset($_GET["month"]) ? intval($_GET["month"]): null;
$day = isset($_GET["day"]) ? intval($_GET["day"]): null;
$opt = isset($_GET["opt"]) ? xssafe($_GET["opt"]): "bystation";

$ys = yearSelect(2009, $year, "year");
$ms = monthSelect($month, "month");
$ds = daySelect($day, "day");

$byday = false;
if ($opt === "bystation"){
	$title = sprintf("Station: %s for Year: %s", $station, $year);
	$col1label = "Date";
	$uri = sprintf("http://iem.local/json/cli.py?station=%s&year=%s",
		$station, $year);
	$data = file_get_contents($uri);
	$json = json_decode($data, $assoc=TRUE);
	$arr = $json['results'];
} else {
	$col1label = "Station";
	$byday = true;
	$day = mktime(0,0,0, $month, $day, $year);
	$title = sprintf("All Stations for Date: %s", date("d F Y", $day));
	$uri = sprintf("http://iem.local/geojson/cli.py?dt=%s",
		date("Y-m-d", $day));
	$data = file_get_contents($uri);
	$json = json_decode($data, $assoc=TRUE);
	$arr = $json['features'];
}
$prettyurl = str_replace("http://iem.local", "https://mesonet.agron.iastate.edu", $uri);

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
<table id="thetable" class="table table-condensed table-striped table-bordered table-hover">
<thead>
<tr class="small">
	<th rowspan="2">{$col1label}</th>
	<th colspan="6">Maximum Temperature &deg;F</th>
	<th class="empty"></th>
	<th colspan="6">Minimum Temperature &deg;F</th>
	<th class="empty"></th>
	<th colspan="6">Precip (inches)</th>
	<th class="empty"></th>
	<th colspan="5">Snow (inches)</th>
</tr>
<tr class="small">
	<th>Ob</th><th>Time</th><th>Rec</th><th>Years</th><th>Avg</th>
	<th>&Delta;</th><th class="empty"></th>
	
	<th>Ob</th><th>Time</th><th>Rec</th><th>Years</th><th>Avg</th>
	<th>&Delta;</th><th class="empty"></th>
	
	<th>Ob</th><th>Rec</th><th>Years</th>
	<th>Avg</th><th>Mon to Date</th><th>Mon Avg</th><th class="empty"></th>
			
	<th>Ob</th><th>Rec</th><th>Years</th><th>Mon to Date</th><th>Depth</th>
</tr>
</thead>
EOF;
function departure($actual, $normal){
    // JSON upstream hacky returns M instead of null
    if ($actual == "M" || $normal == "M") return "M";
	return $actual - $normal;
}
    // JSON upstream hacky returns M instead of null
    function departcolor($actual, $normal){
	if ($actual == "M" || $normal == "M") return "#FFF";
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
	if ($actual == "M" || $record == "M") return "";
	if ($actual == $record) return "<i class=\"fa fa-star-empty\"></i>";
	if ($actual > $record) return "<i class=\"fa fa-star\"></i>";
}
function new_record2($actual, $record){
	if ($actual == "M" || $record == "M") return "";
	if ($actual == $record) return "<i class=\"fa fa-star-empty\"></i>";
	if ($actual < $record) return "<i class=\"fa fa-star\"></i>";
}
foreach($arr as $entry){
	$row = ($opt === "bystation") ? $entry: $entry["properties"];
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
	$table .= sprintf("<tr><td nowrap><a href=\"%s\"><i class=\"fa fa-list-alt\" alt=\"View Text\"></i></a>
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
			<td>%s</td><td>%s</td>
			</tr>", $uri, $col1, 
			$row["high"], new_record($row["high"], $row["high_record"]),
			$row["high_time"], $row["high_record"],
			implode(" ", $row["high_record_years"]), $row["high_normal"],
			departcolor($row["high"], $row["high_normal"]),
			departure($row["high"], $row["high_normal"]),
			
			$row["low"], new_record2($row["low"], $row["low_record"]),
			$row["low_time"], $row["low_record"],
			implode(" ", $row["low_record_years"]), $row["low_normal"],
			departcolor($row["low"], $row["low_normal"]),
			departure($row["low"], $row["low_normal"]),
			
			trace($row["precip"]),
			new_record($row["precip"], $row["precip_record"]),
			trace($row["precip_record"]),
			implode(" ", $row["precip_record_years"]),
			trace($row["precip_normal"]), trace($row["precip_month"]), 
			trace($row["precip_month_normal"]),
			
			trace($row["snow"]),
			new_record($row["snow"], $row["snow_record"]),
			trace($row["snow_record"]),
			implode(' ', $row["snow_record_years"]),
			trace($row["snow_month"]), trace($row["snowdepth"]),

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

<p>There is a <a href="/json/">JSON(P) webservice</a> that backends this table presentation, you can
directly access it here:
<br /><code>{$prettyurl}</code></p>

<p><button id="makefancy">Make Table Interactive</button></p>

<div class="table-responsive">
	{$table}
</div>

<p><strong>Key:</strong> &nbsp; &nbsp;
			<i class="fa fa-star-empty"></i> Record Tied,
			<i class="fa fa-star"></i> Record Set.</p>

EOF;
$t->headextra = <<<EOF
<link rel="stylesheet" type="text/css" href="/vendor/select2/4.0.3/select2.min.css"/ >
<link type="text/css" href="/vendor/jquery-datatables/1.10.20/datatables.min.css" rel="stylesheet" />
EOF;
$t->jsextra = <<<EOF
<script src="/vendor/select2/4.0.3/select2.min.js"></script>
<script src='/vendor/jquery-datatables/1.10.20/datatables.min.js'></script>
<script>
$(document).ready(function(){
	$(".iemselect2").select2();
});
$('#makefancy').click(function(){
    $("#thetable").DataTable();
});
</script>
EOF;
$t->render('full.phtml');
?>