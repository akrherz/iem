<?php 
require_once "../../config/settings.inc.php";
define("IEM_APPID", 101);
require_once "../../include/myview.php";
$t = new MyView();
$t->title = "Quality Control, Sites Offline";

require_once "../../include/database.inc.php";
require_once "../../include/network.php";
require_once "../../include/mlib.php";
$pgconn = iemdb("iem");
$rs = pg_prepare(
    $pgconn,
    "SELECT",
    "SELECT *, to_char(valid, 'Mon DD YYYY HH:MI AM') as v from offline ".
    "WHERE network = $1 ORDER by valid ASC",
);

$nt = new NetworkTable("IA_ASOS");
function networkOffline($network)
{
    global $pgconn, $nt;
    $nt->loadNetwork($network);
    $cities = $nt->table;
    $s = "";
    $rs = pg_execute($pgconn, "SELECT", Array($network) );

    $q = 0;
    for( $i=0; $row = pg_fetch_array($rs); $i++)
    {
        $valid = $row["v"];
        $station = $row["station"];
        if (! isset($cities[$station]))  continue;
        $name = $cities[$station]['name'];
        $s .= "<tr><td>$station</td><td>$name</td><td>$valid</td></tr>\n";
        $q = 1;
    }
    if ($q == 0){ $s .= "<tr><td colspan=3>All Sites Online!!!</td></tr>\n"; }

    return $s;
}
$rwis = networkOffline("IA_RWIS");
$awos = networkOffline("IA_ASOS");
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

<tr>
 <td colspan=3 style="background: #CCCCCC;"><b>Iowa RWIS Network</b>
  (1 hour tolerance)</td>
</tr>
{$rwis}

<tr>
 <td colspan=3 style="background: #CCCCCC;"><b>Iowa AWOS Network</b>
  (90 minute tolerance)</td>
</tr>
{$awos}

</table>

<p>

<p></div>
EOF;
$t->render('single.phtml');
