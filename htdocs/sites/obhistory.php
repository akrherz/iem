<?php 
/*
 * Rip off weather bureau website, but do it better
 */
function wind_formatter($row){
	if ($row["drct"] == null){
		return "M";
	} 
	$gust_text = "";
	if ($row["gust"] > 0){
		$gust_text = sprintf("G %.0f", $row["gust"] * 1.15);
	}
	return sprintf("%s %.0f%s", drct2txt($row["drct"]), $row["sknt"] * 1.15,
	$gust_text );
}
function indy_sky_formatter($skyc, $skyl){
	if (intval($skyl) > 0){ $skyl = sprintf("%03d", $skyl/100); }
	else { $skyl = "";}	
	if ($skyc == null || trim($skyc) == "") return "";
	return sprintf("%s%s<br />", $skyc,$skyl);
}
function sky_formatter($row){
	return sprintf("%s%s%s%s", 
	indy_sky_formatter($row["skyc1"], $row["skyl1"]),
	indy_sky_formatter($row["skyc2"], $row["skyl2"]),
	indy_sky_formatter($row["skyc3"], $row["skyl3"]),
	indy_sky_formatter($row["skyc4"], $row["skyl4"])
	);
}
function temp_formatter($val){
	if ($val == null) return "";
	return sprintf("%.0f", $val);
}
function formatter($i, $row){
	$ts = strtotime(substr($row["valid"],0,16));
	return sprintf("<tr style=\"background: %s;\"><td>%s</td><td>%s</td><td>%s</td>
	<td>%s</td><td>%s</td><td>%s</td><td>%s</td>
	<td><span class=\"high\">%s</span></td><td><span class=\"low\">%s</span></td><td>%.0f%%</td>
	<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>
	<tr style=\"background: %s;\" class=\"metar\"><td colspan=\"15\">%s</td></tr>", 
	($i % 2 == 0)? "#FFF": "#EEE", 
	date("g:i A", $ts), wind_formatter($row) , round($row["vsby"],2),
	sky_formatter($row), $row["presentwx"], temp_formatter($row["tmpf"]), 
	temp_formatter($row["dwpf"]),
	temp_formatter($row["max_tmpf_6hr"]), temp_formatter($row["min_tmpf_6hr"]), 
	relh(f2c($row["tmpf"]), f2c($row["dwpf"])),
	$row["alti"], $row["pres"], $row["phour"], $row["p03i"], $row["p06i"],
	($i % 2 == 0)? "#FFF": "#EEE", $row["raw"]
	);
}
include("setup.php");
include_once "$rootpath/include/mlib.php";
include_once "$rootpath/include/forms.php";
$year = isset($_REQUEST["year"])? $_REQUEST["year"]: date("Y");
$month = isset($_REQUEST["month"])? $_REQUEST["month"]: date("m");
$day = isset($_REQUEST["day"])? $_REQUEST["day"]: date("d");
$date = mktime(0,0,0,$month, $day, $year);
$yesterday = $date - 86400;
$tomorrow = $date + 86400;
if ($tomorrow > time()){
	$tomorrow = null;
}
$iemarchive = mktime(0,0,0,date("m"), date("d"), date("Y")) - 86400;
if ($date >= $iemarchive){
	$db = "iem";
	$sql = sprintf("SELECT c.*
	from current_log c JOIN stations s on (s.iemid = c.iemid)
	and s.id = $1 and s.network = $2 and 
	valid  >= $3 and valid  < $4 
	ORDER by valid DESC");
} else {
	$db = "asos";
	$sql = sprintf("SELECT *, mslp as pres, metar as raw, p01i as phour
	from t$year where 
	station = $1  and valid  >= $3 and valid  < $4 
	and $2 = $2 ORDER by valid DESC");
}
$dbconn = iemdb($db);
pg_query($dbconn, "SET TIME ZONE '". $metadata["tzname"] ."'");
$rs = pg_prepare($dbconn, "_MYSELECT", $sql);
$rs = pg_execute($dbconn, "_MYSELECT", Array($station, $network,
	date("Y-m-d", $date), date("Y-m-d", $date + 86400)));
$table = "";
for ($i=0;$row=@pg_fetch_array($rs,$i);$i++){
	$table .= formatter($i, $row);
}
pg_close($dbconn);

$THISPAGE="iem-sites";
$TITLE = "IEM | Observation History";
include("$rootpath/include/header.php"); 

$savevars = Array("year"=>$year,
 "month"=>$month, "day"=>$day); $current = "obhistory"; include("sidebar.php");
?>
<script type="text/javascript">
var hide = false;
function hideMetars(){
	var table = document.getElementById("datatable");
	var len = table.rows.length;
	var rowStyle = (hide)? "none":"table-row";
	for(i=1 ; i< len; i++){
		if (table.rows[i].className == 'metar'){
	    	table.rows[i].style.display = rowStyle;
		}
	}
	if (hide){
		document.getElementById("metar_toggle").innerHTML = "Show METARs";
	} else{
		document.getElementById("metar_toggle").innerHTML = "Hide METARs";
	}
	hide = !hide;
}
</script>
<style>
.high {
  color: #F00;
}
.low {
  color: #00F;
}
.metar {
  display: none;
}
</style>

<h3><?php echo date("d F Y", $date); ?> Observation History, timezone: <?php echo $metadata["tzname"]; ?></h3>
<form method="GET" style="float: left;">
<strong>Select Date:</strong>
<input type="hidden" value="<?php echo $station; ?>" name="station" />
<input type="hidden" value="<?php echo $network; ?>" name="network" />
<?php echo yearSelect(1933,$year); ?>
<?php echo monthSelect($month); ?>
<?php echo daySelect($day); ?>
<input type="submit" value="Change Date" />
</form>
<a onclick="javascript:hideMetars();" class="button" id="metar_toggle">Show Metars</a>
<?php 
  echo sprintf("<a rel=\"nofollow\" href=\"obhistory.php?network=%s&station=%s&year=%s&month=%s&day=%s\" 
  class=\"button down\">Previous Day</a>", $network, $station, date("Y", $yesterday),
  date("m", $yesterday), date("d", $yesterday));
  
  if ($tomorrow){
  echo sprintf("<a rel=\"nofollow\" href=\"obhistory.php?network=%s&station=%s&year=%s&month=%s&day=%s\" 
  class=\"button up\">Next Day</a>", $network, $station, date("Y", $tomorrow),
  date("m", $tomorrow), date("d", $tomorrow));
  }
?>
<table cellspacing="3" cellpadding="2" border="0" id="datatable">
<tr align="center" bgcolor="#b0c4de">
<th rowspan="3">Time</th>
<th rowspan="3">Wind<br>(mph)</th><th rowspan="3">Vis.<br>(mi.)</th>
<th rowspan="3">Sky Cond.<br />(100s ft)</th><th rowspan="3">Present Wx</th>
<th colspan="4">Temperature (&ordm;F)</th><th rowspan="3">Relative<br>Humidity</th><th colspan="2">Pressure</th><th colspan="3">Precipitation (in.)</th></tr>
<tr align="center" bgcolor="#b0c4de"><th rowspan="2">Air</th><th rowspan="2">Dwpt</th><th colspan="2">6 hour</th>
<th rowspan="2">altimeter<br>(in.)</th><th rowspan="2">sea level<br>(mb)</th><th rowspan="2">1 hr</th>
<th rowspan="2">3 hr</th><th rowspan="2">6 hr</th></tr>
<tr align="center" bgcolor="#b0c4de"><th>Max.</th><th>Min.</th></tr>
<?php echo $table; ?>
</table>
<?php 
include("$rootpath/include/footer.php");
?>