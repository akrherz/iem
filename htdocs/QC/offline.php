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
$stname = iem_pg_prepare(
    $pgconn,
    "SELECT *, to_char(valid, 'Mon DD YYYY HH:MI AM') as v from offline ".
    "WHERE network = $1 ORDER by valid ASC",
);

function networkOffline($network)
{
    global $pgconn, $stname;
    $nt = new NetworkTable($network);
    $cities = $nt->table;
    $s = "";
    $rs = pg_execute($pgconn, $stname, Array($network) );

    $q = 0;
    while ($row = pg_fetch_assoc($rs))
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
$t->content = <<<EOM
<nav aria-label="breadcrumb">
<ol class="breadcrumb">
 <li class="breadcrumb-item"><a href="/QC/">Quality Control</a></li>
 <li class="breadcrumb-item active" aria-current="page">Sites Offline</li>
</ol>
</nav>

<p>Unfortunately, automated observing sites occasionally go offline due
to a wide range of factors.  Here is a listing of sites currently offline.</p>

<div class="table-responsive">
<table class="table table-striped table-bordered">
<thead class="table-light">
<tr>
 <th>Site ID:</th>
 <th>Name</th>
 <th>Flagged Offline At</th>
</tr>
</thead>
<tbody>
<tr><td colspan="3" class="table-secondary fw-bold">ISU Soil Moisture Network (3 hour tolerance)</td></tr>
{$isusm}

<tr><td colspan="3" class="table-secondary fw-bold">Iowa RWIS Network (1 hour tolerance)</td></tr>
{$rwis}

<tr><td colspan="3" class="table-secondary fw-bold">Iowa AWOS Network (90 minute tolerance)</td></tr>
{$awos}

</tbody>
</table>
</div>
EOM;
$t->render('single.phtml');
