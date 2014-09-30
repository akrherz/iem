<?php 
include("../../config/settings.inc.php");
include_once "../../include/myview.php";
include_once "../../include/database.inc.php";
include_once "../../include/forms.php";


$station = isset($_GET["station"]) ? $_GET["station"]: 'KDSM';
$year = isset($_GET["year"]) ? intval($_GET["year"]): date("Y");

$ys = yearSelect(2010, $year, "year");

$pgconn = iemdb("iem");
$rs = pg_prepare($pgconn, "SELECT", "SELECT *,
		array_to_string(high_record_years, ' ') as hry,
		array_to_string(low_record_years, ' ') as lry,
		array_to_string(precip_record_years, ' ') as pry,
		array_to_string(snow_record_years, ' ') as sry
		from cli_data where
		station = $1 and valid BETWEEN $2 and $3 ORDER by valid ASC");
$rs = pg_execute($pgconn, "SELECT", Array($station, "{$year}-01-01",
	"{$year}-12-31"));
$table = <<<EOF
<form method="GET" name="dl">
	<p><strong>Select Station:</strong> <input type="text" name="station"
		value="{$station}" size="10" />
	<br /><strong>Year:</strong> {$ys}
	<br /><input type="submit" value="Generate Table" />
</form>
<table class="table table-condensed table-striped table-bordered">
<thead>
<tr>
	<th rowspan="2">Date</th>
	<th colspan="6">Maximum Temperature &deg;F</th>
	<th colspan="6">Minimum Temperature &deg;F</th>
	<th colspan="6">Precip (inches)</th>
	<th colspan="4">Snow (inches)</th>
</tr>
<tr>
	<th>Value</th><th>Time</th><th>Record</th><th>Years</th><th>Normal</th>
	<th>Depart</th>
	<th>Value</th><th>Time</th><th>Record</th><th>Years</th><th>Normal</th>
	<th>Depart</th>
	<th>Value</th><th>Record</th><th>Years</th>
	<th>Normal</th><th>Mon to Date</th><th>Mon Normal</th>
	<th>Value</th><th>Record</th><th>Years</th><th>Mon to Date</th>
</tr>
</thead>
EOF;
function departcolor($actual, $normal){
	if ($actual > $normal) return "#FD96B1";
	if ($actual < $normal) return "#A5EAFF";
	return "#fff";
}
for($i=0; $row=@pg_fetch_assoc($rs,$i); $i++){
	$table .= sprintf("<tr><td>%s</td>
			<td>%s</td><td>%s</td><td>%s</td>
			<td>%s</td><td>%s</td><td style='background: %s;'>%s</td>
			<td>%s</td><td>%s</td><td>%s</td>
			<td>%s</td><td>%s</td><td style='background: %s;'>%s</td>
			<td>%s</td><td>%s</td><td>%s</td>
			<td>%s</td><td>%s</td><td>%s</td>
			<td>%s</td><td>%s</td><td>%s</td>
			<td>%s</td>
			</tr>", $row["valid"],
			$row["high"], $row["high_time"], $row["high_record"],
			$row["hry"], $row["high_normal"],
			departcolor($row["high"], $row["high_normal"]),
			$row["high"] - $row["high_normal"],
			
			$row["low"], $row["low_time"], $row["low_record"],
			$row["lry"], $row["low_normal"],
			departcolor($row["low"], $row["low_normal"]),
			$row["low"] - $row["low_normal"],
			
			$row["precip"], $row["precip_record"], $row["pry"],
			$row["precip_normal"], $row["precip_month"], $row["precip_month_normal"],
			
			$row["snow"], $row["snow_record"], $row["sry"],
			$row["snow_month"]
				
		);
}
$table .= "</table>";

$t = new MyView();
$t->title = "Tabular CLI Report Data";

$t->content = <<<EOF
<ol class="breadcrumb">
	<li><a href="/climate/">Climate Data</a></li>
	<li class="active">Tabular CLI Report Data</li>		
</ol>

	{$table}

EOF;

$t->render('single.phtml');
?>