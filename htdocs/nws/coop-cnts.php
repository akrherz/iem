<?php 
/*
 * Print out a listing of COOP sites and observation frequency
 */
include("../../config/settings.inc.php");

include("$rootpath/include/database.inc.php");
include("$rootpath/include/wfoLocs.php");
include("$rootpath/include/forms.php");
$dbconn = iemdb("iem");

$wfo = isset($_REQUEST['wfo']) ? $_REQUEST['wfo'] : 'DMX';
$year = isset($_REQUEST["year"]) ? $_REQUEST["year"]: date("Y"); 
$month = isset($_REQUEST["month"]) ? $_REQUEST["month"]: date("m"); 

$rs = pg_prepare($dbconn, "MYSELECT", "select id, name,
 count(*) as total, 
 sum(case when pday >= 0 then 1 else 0 end) as pobs, 
 sum(case when max_tmpf > -60 then 1 else 0 end) as tobs 
 from summary_$year s JOIN stations t on (t.iemid = s.iemid) 
 WHERE day >= $1 and day < ($1::date + '1 month'::interval) 
 and day < 'TOMORROW'::date
 and t.wfo = $2 and t.network ~* 'COOP' GROUP by id, name ORDER by id ASC");


$tstring = sprintf("%s-%02d-01", $year, intval($month));
$data = pg_execute($dbconn, "MYSELECT", Array($tstring, $wfo));

$TITLE = "IEM | NWS COOP Obs per month per WFO";
include("$rootpath/include/header.php");
?>

<h3>NWS COOP Observation Counts by Month by WFO</h3>

<p>This application prints out a summary of COOP reports received by the IEM 
on a per month and per WFO basis.  Errors do occur and perhaps the IEM's ingestor
is "missing" data from sites.  Please <a href="../info/contacts.php">let us know</a> of any errors you may suspect!

<form method="GET" name="changeme">
<table cellpadding="2" border="1" cellspacing="0">
<tr>
<td><strong>Select WFO:</strong><?php echo wfoSelect($wfo); ?></td>
<td><strong>Select Year:</strong><?php echo yearSelect("2010", $year); ?></td>
<td><strong>Select Month:</strong><?php echo monthSelect($month); ?></td>
</tr>
</table>
<input type="submit" value="View Report" />
</form>

<h3>COOP Report for wfo: <?php echo $wfo; ?>, month: <?php echo $month; ?>, year: <?php echo $year; ?></h3>

<table cellpadding="2" border="1" cellspacing="0">
<tr><th>NWSLI</th><th>Name</th><th>Possible</th>
<th>Precip Obs</th><th>Temperature Obs</th></tr>
<?php 
for($i=0;$row=@pg_fetch_assoc($data,$i);$i++){
	echo sprintf("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>", $row["id"], 
	$row["name"], $row["total"], $row["pobs"], $row["tobs"]);
}

?>
</table>

<?php 
include("$rootpath/include/footer.php");
?>