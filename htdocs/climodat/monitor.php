<?php 
// Monitor a bunch of climodat sites
require_once "../../config/settings.inc.php";
define("IEM_APPID", 89);
require_once "../../include/myview.php";
require_once "../../include/imagemaps.php";
require_once "../../include/database.inc.php";
require_once "../../include/network.php";
require_once "../../include/forms.php";


function ss($v){
	if ($v == '') return '';
	return intval($v);
}

$year = date("Y");
$sdate = isset($_GET["sdate"]) ? xssafe($_GET["sdate"]): "05/01/${year}";
$network = isset($_GET["network"]) ? xssafe($_GET["network"]): "IACLIMATE";
$edate = isset($_GET["edate"]) ? xssafe($_GET["edate"]): "12/31/${year}";
$gddbase = isset($_GET["gddbase"]) ? intval($_GET["gddbase"]) : 50;
$gddfloor = isset($_GET["gddfloor"]) ? ss($_GET["gddfloor"]) : 50;
$gddceil = isset($_GET["gddceil"]) ? ss($_GET["gddceil"]) : 86;

$hiddendates = <<<EOF
<input type="hidden" name="sdate" value="{$sdate}">
<input type="hidden" name="edate" value="{$edate}">
EOF;
$sdate = strtotime($sdate);
$edate = strtotime($edate);
$s = isset($_GET["s"]) ? $_GET["s"]: Array();
if (isset($_GET['r'])){
	$r = $_GET["r"];
	foreach($r as $k => $v){
		if(($key = array_search($v, $s)) !== false) {
			unset($s[$key]);
		}
	}
}
// Prevent stations from appearing twice in the display
$tmpst = Array();
foreach($s as $k => $v){
	if (in_array($v, $tmpst)){
		unset($s[$k]);
	} else{
		$tmpst[] = $v;
	}
}

$hiddenstations = "";
$table = "";
$stationgrps = Array();
foreach($s as $k => $v){
	$state = substr($v, 0, 2);
	if (! array_key_exists($state, $stationgrps)){
		$stationgrps[$state] = Array();
	}
	$stationgrps[$state][] = $v;
	$hiddenstations .= "<input type=\"hidden\" name=\"s[]\" value=\"$v\">";
}
$networks = Array();
foreach($stationgrps as $state => $v){
	$networks[] = sprintf("%sCLIMATE", $state);
}
$nt2 = new NetworkTable($networks);

$sdatestr = date("Y-m-d", $sdate);
$edatestr = date("Y-m-d", $edate);

$gddstr = "gddxx({$gddbase}, {$gddceil}, high, low)";
if ($gddfloor == '' || $gddceil == ''){
	$gddstr = "gdd_onlybase({$gddbase}, high, low)";
}
$pgconn = iemdb('coop');

// Loop over station groups
foreach($stationgrps as $state => $stations){
	$sstring = "('". implode(",", $stations) ."')";
	$sstring = str_replace(",", "','", $sstring);
	// bulk radiation bias values applied below
	$sql = <<<EOF
	WITH climo as (
	  SELECT station, sday, avg(precip) as avg_precip,
	  avg(sdd86(high,low)) as avg_sdd,
	  avg({$gddstr}) as avg_gdd,
	  avg(merra_srad) as avg_srad
	  from alldata_{$state} WHERE station in {$sstring}
	  and year > 1950 GROUP by station, sday)
	  
	select o.station,
	   sum({$gddstr}) as ogdd50,
	   sum(o.precip) as oprecip,
	   sum(c.avg_gdd) as cgdd50, sum(c.avg_precip) as cprecip,
	   sum(c.avg_srad) as csrad,
	   max(o.high) as maxtmpf, min(o.low) as mintmpf,
	   avg( (o.high + o.low) / 2.0 ) as avgtmpf,
	   sum(c.avg_sdd) as csdd86, sum(sdd86(o.high, o.low)) as osdd86,
	   sum(coalesce(merra_srad, narr_srad / 1.14, hrrr_srad * 1.09)) as osrad
	  from alldata_{$state} o, climo c WHERE
	   o.station in {$sstring}
	   and o.station = c.station
	   and day >= '{$sdatestr}' and day <= '{$edatestr}'
	   and o.sday = c.sday  GROUP by o.station
	   ORDER by o.station ASC
EOF;
	$rs = pg_query($pgconn, $sql);
	for ($i=0;$row=pg_fetch_assoc($rs);$i++){
		$table .= sprintf("<tr><td>"
				."<input type=\"checkbox\" name=\"r[]\" value=\"%s\" >"
				." %s</td><td>%s</td>"
				."<td>%.2f</td><td>%.2f</td><td>%.2f</td>"
				."<td>%.1f</td><td>%.1f</td><td>%.1f</td>"
				."<td>%.1f</td><td>%.1f</td><td>%.1f</td>"
				."<td>%s</td><td>%s</td><td>%.1f</td>"
				."<td>%.1f</td><td>%.1f %.1f%%</td></tr>", 
				$row['station'], $row['station'], $nt2->table[$row['station']]['name'], $row["oprecip"],
				$row["cprecip"], $row["oprecip"] - $row["cprecip"],
				$row["ogdd50"],
				$row["cgdd50"], $row["ogdd50"] - $row["cgdd50"],
				$row["osdd86"],
				$row["csdd86"], $row["osdd86"] - $row["csdd86"],
				$row["maxtmpf"], $row["mintmpf"], $row["avgtmpf"],
				$row['osrad'], $row['osrad'] - $row['csrad'],
				($row['osrad'] - $row['csrad']) / $row['csrad'] * 100.);
	}
}
$nselect = networkSelect($network, "IA0000", Array(), "s[]");

$t = new MyView();
$showmap = " hidden";
if (isset($_GET['map'])){
	$t->iemss = True;
	$showmap = "";
}
$t->title = "Climodat Station Monitor";
$t->thispage = "climatology-climodatm";
$t->headextra = <<<EOF
<link rel="stylesheet" href="/vendor/jquery-ui/1.11.4/jquery-ui.min.css" />
EOF;

$sdatestr = date("m/d/Y", $sdate);
$edatestr = date("m/d/Y", $edate);
$t->jsextra = <<<EOF
<script src="/vendor/jquery-ui/1.11.4/jquery-ui.min.js"></script>
<script type="text/javascript">
$(document).ready(function(){
	sdate = $("#sdate").datepicker({altFormat:"yymmdd"});
	sdate.datepicker('setDate', "$sdatestr");
	edate = $("#edate").datepicker({altFormat:"yymmdd"});	
	edate.datepicker('setDate', "$edatestr");

	//Make into more PHP friendly
	$('#addmapstations').on('click', function(){
		$('#stations_out').attr('name', 's[]');
	});
});
</script>
EOF;

$sselect = selectClimodatNetwork($network, 'network');

$snice = date("d M Y", $sdate);
$today = ($edate > time()) ? time() : $edate;
$enice = date("d M Y", $today);
$t->content = <<<EOF
<ol class="breadcrumb">
 <li><a href="/climodat/">Climodat Reports</a></li>
 <li class="active">IEM Climodat Station Monitor</li>
</ol>

<p>The purpose of this page is to provide a one-stop view of summarized 
IEM Climodat data for a period of your choice.  Once you have configured 
your favorite sites, <strong>please bookmark the page</strong>. There are
options presented on this page on how to compute Growing Degree Days.  Here
is a description of the three options.</p>

<ul>
 <li><i>base</i>: This is the base temperature (F) to substract the daily
 average [(high + low) / 2] temperature from.  The resulting value is 
 always non-negative.</li>
 <li><i>floor</i>: If the high or low temperature is below this value, the
 temperature is set to this value before the averaging is done. Delete the
 entry to remove this calculation.</li>
 <li><i>ceiling</i>: If the high temperature is above this value, the 
 high temperature is set to this value prior to averaging.  Delete the
 entry to remove this calculation.</li>
</ul>

<p><strong>Updated 4 Oct 2018:</strong>  Model based solar radiation
values are now included.  These values are based on the combination of
NASA MERRA, NARR, and HRRR data. See <a href="/plotting/auto/?q=38">IEM Autoplot 38</a>
for a bias assessment of these values.</p>

<hr />
<h4>Available States with Data</h4>

<form name="switch">
{$hiddendates}
{$hiddenstations}
{$sselect}
<input type="submit" value="Select State">
</form>

<hr />
<div class="row">
<div class="col-md-6">
<h4>Available Stations within Selected State</h4>

<form name="add">
<input type="hidden" name="network" value="{$network}">
{$hiddendates}
{$hiddenstations}
	{$nselect}
	<input type="submit" value="Add Station">
</form>
<form name="addfrommap">
<input type="hidden" name="network" value="{$network}">
<input type="hidden" name="map" value="1">
{$hiddendates}
{$hiddenstations}
<br /><input type="submit" value="Select Stations From Map">
</form>
</div>
<div class="col-md-6 {$showmap}" id="mappanel">
<!-- The map, when appropriate -->
<form name="iemss">
<input type="hidden" name="network" value="{$network}">
{$hiddendates}
{$hiddenstations}
<div id="iemss" data-network="{$network}"></div>

<br /><input id="addmapstations" type="submit" value="Add Station(s)">
</form>
</div>
</div>

<hr />
<h4>Table Options</h4>

<form name="dates">
<input type="hidden" name="network" value="{$network}">
{$hiddenstations}
<table class="table table-condensed">
<tr><th>Growing Degree Days</th>
 <td>base: <input type="text" name="gddbase" size="4" value="{$gddbase}">
 floor: <input type="text" name="gddfloor" size="4" value="{$gddfloor}">
 ceiling: <input type="text" name="gddceil" size="4" value="{$gddceil}">
 </td></tr>

<tr><th>Period</th><td>start: <input type="text" id="sdate" name="sdate">
    end: <input type="text" id="edate" name="edate"> (inclusive)</td></tr>

<tr><td colspan="2">
<input type="submit" value="Apply Table Options">
</td></tr>
</table>
</form>

<hr />
<h4>The following table is valid for a period from {$snice} to {$enice} (inclusive).</h4>

<p><i>"Climo"</i> is the climatology value, which is computed over the period of
1951-2015.</p>

<form name="remove">
<input type="hidden" name="network" value="{$network}">
{$hiddenstations}
{$hiddendates}
<table class="table table-bordered table-striped table-condensed">
<thead><tr>
	<th rowspan="2">ID</th>
	<th rowspan="2">Name</th>
	<th colspan="3">Precipitation [inch]</th>
	<th colspan="3">Growing Degree Days (base {$gddbase}, floor {$gddfloor}, ceil {$gddceil})</th>
	<th colspan="3">Stress Degree Days (base 86)</th>
	<th colspan="3">Daily Temperature [F]</th>
	<th colspan="2">Solar Rad [MJ]</th>
</tr>
<tr>
	<th>Total</th><th>Climo</th><th>Departure</th>
	<th>Total</th><th>Climo</th><th>Departure</th>
	<th>Total</th><th>Climo</th><th>Departure</th>
	<th>Max</th><th>Min</th><th>Avg</th>
	<th>Total</th><th>Departure</th>
</tr>
</thead>
<tbody>{$table}</tbody>
</table>

<br /><input type="submit" value="Remove Selected Stations From List">
</form>
EOF;

$t->render('full.phtml');
?>