<?php 
include("../../config/settings.inc.php");
define("IEM_APPID", 101);
include("../../include/myview.php");
$t = new MyView();
$t->title = "Quality Control, Sites Offline";
$t->thispage = "iem-qc";

include("../../include/iemaccess.php");
$iem = new IEMAccess();
$rs = pg_prepare($iem->dbconn, "SELECT", "SELECT *,
                 to_char(valid, 'Mon DD YYYY HH:MI AM') as v from offline
                 WHERE network = $1 ORDER by valid ASC");

function aSortBySecondIndex($multiArray, $secondIndex) {
	while (list($firstIndex, ) = each($multiArray))
		$indexMap[$firstIndex] = $multiArray[$firstIndex][$secondIndex];        asort($indexMap);
	while (list($firstIndex, ) = each($indexMap))
	if (is_numeric($firstIndex))
		$sortedArray[] = $multiArray[$firstIndex];
	else $sortedArray[$firstIndex] = $multiArray[$firstIndex];
	return $sortedArray;
}

include ("../../include/network.php");
$nt = new NetworkTable("IA_ASOS");
function networkOffline($network)
{
	global $iem, $nt;
	$nt->load_network($network);
	$cities = $nt->table;
	$s = "";
	$rs = pg_execute($iem->dbconn, "SELECT", Array($network) );

	$q = 0;
	for( $i=0; $row = @pg_fetch_array($rs,$i); $i++)
	{
		$valid = $row["v"];
		$tracker_id = $row["trackerid"];
		$station = $row["station"];
		if (! isset($cities[$station]))  continue;
		$name = $cities[$station]['name'];
		$s .= "<tr><td>$station</td><td>$name</td><td>$valid</td></tr>\n";
		$q = 1;
	}
	if ($q == 0){ $s .= "<tr><td colspan=3>All Sites Online!!!</td></tr>\n"; }

	return $s;
}
$kcci = networkOffline("KCCI");
$kelo = networkOffline("KELO");
$kimt = networkOffline("KIMT");
$rwis = networkOffline("IA_RWIS");
$awos = networkOffline("AWOS");
$isusm = networkOffline("ISUSM");
$t->content = <<< EOF
<ol class="breadcrumb">
 <li><a href="/QC/">Quality Control</a></li>
 <li class="active">Sites Offline</li>
</ol>

<P>Unfortunately, automated observing sites occasionally go offline due
to a wide range of factors.  Here is a listing of sites currently offline.
</p>


<table class="table table-striped">
<thead>
<tr>
 <th align="left">Site ID:</th>
 <th align="left">Name</th>
 <th align="left">Flagged Offline At</th></tr>
</thead>
<tr><td colspan="3" style="background: #CCCCCC;"><b>ISU Soil Moisture Network</b>
  (3 hour tolerance)</td></tr>
{$isusm}

<tr><td colspan="3" style="background: #CCCCCC;"><b>KCCI School Network</b>
  (30 minute tolerance)</td></tr>
{$kcci}

<tr><td colspan=3 style="background: #CCCCCC;"><b>KELO School Network</b>
  (3 hour tolerance)</td></tr>
{$kelo}

<tr><td colspan=3 style="background: #CCCCCC;"><b>KIMT School Network</b>
  (30 minute tolerance)</td></tr>
{$kimt}

<tr>
 <td colspan=3 style="background: #CCCCCC;"><b>RWIS Network</b>
  (1 hour tolerance)</td>
</tr>
{$rwis}

<tr>
 <td colspan=3 style="background: #CCCCCC;"><b>AWOS Network</b>
  (90 minute tolerance)</td>
</tr>
{$awos}

</table>

<p>

<p></div>
EOF;
$t->render('single.phtml');
?>
