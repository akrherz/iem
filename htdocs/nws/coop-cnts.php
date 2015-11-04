<?php 
/*
 * Print out a listing of COOP sites and observation frequency
 */
include("../../config/settings.inc.php");
define("IEM_APPID", 113);
include("../../include/myview.php");
$t = new MyView();

include("../../include/database.inc.php");
include("../../include/network.php");
$nt = new NetworkTable("WFO");
include("../../include/forms.php");
$dbconn = iemdb("iem");

$wfo = isset($_REQUEST['wfo']) ? $_REQUEST['wfo'] : 'DMX';
$year = isset($_REQUEST["year"]) ? intval($_REQUEST["year"]): date("Y"); 
$month = isset($_REQUEST["month"]) ? $_REQUEST["month"]: date("m"); 

$rs = pg_prepare($dbconn, "MYSELECT", "select id, name,
 count(*) as total, 
 sum(case when pday >= 0 then 1 else 0 end) as pobs, 
 sum(case when snow >= 0 then 1 else 0 end) as sobs, 
 sum(case when snowd >= 0 then 1 else 0 end) as sdobs, 
 sum(case when max_tmpf > -60 then 1 else 0 end) as tobs 
 from summary_$year s JOIN stations t on (t.iemid = s.iemid) 
 WHERE day >= $1 and day < ($1::date + '1 month'::interval) 
 and day < 'TOMORROW'::date
 and t.wfo = $2 and t.network ~* 'COOP' GROUP by id, name ORDER by id ASC");


$tstring = sprintf("%s-%02d-01", $year, intval($month));
$data = pg_execute($dbconn, "MYSELECT", Array($tstring, $wfo));

$t->title = "NWS COOP Obs per month per WFO";

$wselect = "";
while( list($key, $value) = each($nt->table) ){
	$wselect .= "<option value=\"$key\" ";
	if ($wfo == $key) $wselect .= "SELECTED";
	$wselect .= ">[".$key."] ". $nt->table[$key]["name"] ."\n";
}

$ys = yearSelect("2010", $year);
$ms = monthSelect($month);

$table = "";
for($i=0;$row=@pg_fetch_assoc($data,$i);$i++){
	$table .= sprintf("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>", $row["id"], 
	$row["name"], $row["total"], $row["pobs"], $row["tobs"], $row["sobs"],
	$row["sdobs"]);
}


$t->content = <<<EOF
<ol class="breadcrumb">
 <li><a href="/nws/">NWS User Resources</a></li>
 <li class="active">NWS COOP Observation Counts by Month by WFO</li>
</ol>

<p>This application prints out a summary of COOP reports received by the IEM 
on a per month and per WFO basis.  Errors do occur and perhaps the IEM's ingestor
is "missing" data from sites.  Please <a href="/info/contacts.php">let us know</a> of any errors you may suspect!

<form method="GET" name="changeme">
<table class="table table-condensed">
<tr>
<td><strong>Select WFO:</strong><select name="wfo">
{$wselect}
</select></td>
<td><strong>Select Year:</strong>{$ys}</td>
<td><strong>Select Month:</strong>{$ms}</td>
</tr>
</table>
<input type="submit" value="View Report" />
</form>

<h3>COOP Report for wfo: {$wfo}, month: {$month}, year: {$year}</h3>

<table class="table table-striped table-condensed table-bordered">
<tr><th>NWSLI</th><th>Name</th><th>Possible</th>
<th>Precip Obs</th><th>Temperature Obs</th><th>Snowfall Obs</th><th>Snowdepth Obs</th></tr>
{$table}
</table>
EOF;
$t->render('single.phtml');
?>
