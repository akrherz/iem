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
function vis_formatter($val){
	if ($val == null) return "";
	return round($val, 2);
}
function formatter($i, $row){
	$ts = strtotime(substr($row["valid"],0,16));
	$relh = relh(f2c($row["tmpf"]), f2c($row["dwpf"]) );
	$relh = ($relh != null) ? intval($relh): "";
	return sprintf("<tr style=\"background: %s;\"><td>%s</td><td>%s</td><td>%s</td>
	<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>
	<td><span class=\"high\">%s</span></td>
	<td><span class=\"low\">%s</span></td>
	<td>%s%%</td>
	<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>
	<tr style=\"background: %s;\" class=\"metar\"><td colspan=\"15\">%s</td></tr>", 
	($i % 2 == 0)? "#FFF": "#EEE", 
	date("g:i A", $ts), wind_formatter($row) , vis_formatter($row["vsby"]),
	sky_formatter($row), $row["wxcodes"], temp_formatter($row["tmpf"]), 
	temp_formatter($row["dwpf"]),
	temp_formatter($row["feel"]),
	temp_formatter($row["max_tmpf_6hr"]), temp_formatter($row["min_tmpf_6hr"]), 
	relh(f2c($row["tmpf"]), f2c($row["dwpf"])),
	$row["alti"], $row["pres"], $row["phour"], $row["p03i"], $row["p06i"],
	($i % 2 == 0)? "#FFF": "#EEE", $row["raw"]
	);
}
include("setup.php");
include_once "../../include/mlib.php";
require_once "../../include/forms.php";
$year = isset($_GET["year"])? intval($_GET["year"]): date("Y");
$month = isset($_GET["month"])? intval($_GET["month"]): date("m");
$day = isset($_GET["day"])? intval($_GET["day"]): date("d");
$date = mktime(0,0,0,$month, $day, $year);
$yesterday = $date - 86400;
$tomorrow = $date + 86400;
if ($tomorrow > time()){
	$tomorrow = null;
}
if ($metadata["archive_begin"]){
	$startyear = intval(date("Y", $metadata["archive_begin"]));
	if ($date < $metadata['archive_begin']){
		$date = $metadata['archive_begin'];
	}
} else {
	$startyear = 2010;
}

$iemarchive = mktime(0,0,0,date("m"), date("d"), date("Y")) - 86400;
if ($date >= $iemarchive){
	$db = "iem";
	$sql = sprintf("SELECT distinct c.*
	from current_log c JOIN stations s on (s.iemid = c.iemid)
	and s.id = $1 and s.network = $2 and 
	valid  >= $3 and valid  < $4 
	ORDER by valid DESC");
} else {
	if (preg_match("/RWIS/", $network)){
		$db = "rwis";
		$sql = sprintf("SELECT *, null as pres, null as raw, null as phour,
				null as relh, null as skyc1, null as skyl1, 
				null as skyc2, null as skyl2, null as alti,
				null as skyc3, null as skyl3, null as wxcodes,
				null as skyc4, null as skyl4, null as max_tmpf_6hr,
				null as feel,
				null as p06i, null as min_tmpf_6hr, null as p03i
		from alldata where 
		station = $1  and valid  >= $3 and valid  < $4 
		and $2 = $2 ORDER by valid DESC");
	} else if (preg_match("/ISUSM/", $network)){
		$db = "isuag";
		$sql = sprintf("SELECT *, null as pres, null as raw, null as feel
		from alldata where 
		station = $1  and valid  >= $3 and valid  < $4 
		and $2 = $2 ORDER by valid DESC");
	} else {
		$db = "asos";
		$sql = sprintf("SELECT *, mslp as pres, metar as raw, p01i as phour,
				null as relh
				from alldata where
				station = $1  and valid  >= $3 and valid  < $4
				and $2 = $2 ORDER by valid DESC");
		
	}
}
$dbconn = iemdb($db);
pg_query($dbconn, "SET TIME ZONE '". $metadata["tzname"] ."'");
$rs = pg_prepare($dbconn, "_MYSELECT", $sql);
$rs = pg_execute($dbconn, "_MYSELECT", Array($station, $network,
	date("Y-m-d", $date), date("Y-m-d", $date + 90400)));
$table = "";
for ($i=0;$row=@pg_fetch_assoc($rs,$i);$i++){
	if ($row['dwpf'] == null && $row['relh'] != null){
		$row['dwpf'] = dwpf($row["tmpf"], $row["relh"]);
	}
	$table .= formatter($i, $row);
}
pg_close($dbconn);

include("../../include/myview.php");
$t = new MyView();

$t->thispage = "iem-sites";
$t->title = "Observation History";
$t->sites_current = 'obhistory';

$savevars = Array("year"=>date("Y", $date),
 "month"=>date("m", $date), "day"=>date("d", $date)); 
$t->jsextra = <<<EOF
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
EOF;
$dstr = date("d F Y", $date);
$tzname =  $metadata["tzname"];

$ys = yearSelect($startyear,date("Y", $date));
$ms = monthSelect(date("m", $date));
$ds = daySelect(date("d", $date));

$mbutton = (preg_match("/ASOS|AWOS/", $network)) ? 
"<a onclick=\"javascript:hideMetars();\" class=\"btn btn-default\" id=\"metar_toggle\">Show Metars</a>"
: "";

$content = <<<EOF
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

<h3>{$dstr} Observation History, [{$station}] {$metadata["name"]}, timezone: {$tzname}</h3>
<form name="theform" method="GET">
<strong>Select Date:</strong>
<input type="hidden" value="{$station}" name="station" />
<input type="hidden" value="{$network}" name="network" />
{$ys}
{$ms}
{$ds}
<input type="submit" value="Change Date" />
</form>
{$mbutton}
EOF;
$content .= sprintf("<a rel=\"nofollow\" href=\"obhistory.php?network=%s&station=%s&year=%s&month=%s&day=%s\" 
  class=\"btn btn-default\">Previous Day</a>", $network, $station, date("Y", $yesterday),
  date("m", $yesterday), date("d", $yesterday));
  
if ($tomorrow){
  $content .= sprintf("<a rel=\"nofollow\" href=\"obhistory.php?network=%s&station=%s&year=%s&month=%s&day=%s\" 
  class=\"btn btn-default\">Next Day</a>", $network, $station, date("Y", $tomorrow),
  date("m", $tomorrow), date("d", $tomorrow));
}
$notes = '';
if ($network == "ISUSM"){
	$notes .= "<li>Wind direction and wind speed are 10 minute averages at 10 feet above the ground.</li>";
}

$content .= <<<EOF
<table class="table table-striped table-bordered" id="datatable">
<thead>
<tr align="center" bgcolor="#b0c4de">
<th rowspan="3">Time</th>
<th rowspan="3">Wind<br>(mph)</th>
<th rowspan="3">Vis.<br>(mi.)</th>
<th rowspan="3">Sky Cond.<br />(100s ft)</th>
<th rowspan="3">Present Wx</th>
<th colspan="5">Temperature (&ordm;F)</th>
<th rowspan="3">Relative<br>Humidity</th>
<th colspan="2">Pressure</th>
<th colspan="3">Precipitation (in.)</th></tr>

<tr align="center" bgcolor="#b0c4de">
<th rowspan="2">Air</th>
<th rowspan="2">Dwpt</th>
<th rowspan="2">Feels Like</th>
<th colspan="2">6 hour</th>
<th rowspan="2">altimeter<br>(in.)</th>
<th rowspan="2">sea level<br>(mb)</th>
<th rowspan="2">1 hr</th>
<th rowspan="2">3 hr</th>
<th rowspan="2">6 hr</th>
</tr>

<tr align="center" bgcolor="#b0c4de"><th>Max.</th><th>Min.</th></tr>

</thead>
<tbody>
{$table}
</tbody>
</table>
<h4>Data Notes</h4>
<ul>
{$notes}
</ul>
EOF;
$t->content = $content;
$t->render('sites.phtml');
?>