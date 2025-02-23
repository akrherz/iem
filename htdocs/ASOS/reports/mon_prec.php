<?php
require_once "../../../config/settings.inc.php";
require_once "../../../include/myview.php";
require_once "../../../include/database.inc.php";
require_once "../../../include/network.php";
require_once "../../../include/forms.php";
require_once "../../../include/imagemaps.php";

$network = isset($_GET["network"]) ? xssafe($_GET["network"]) : "IA_ASOS";
$year = get_int404("year", date("Y"));

$netselect = selectNetworkType("ASOS", $network);
$yselect = yearSelect2(2004, $year, "year");

define("IEM_APPID", 29);
$t = new MyView();
$t->title = "{$year} {$network} Monthly Precipitation";

$pgconn = iemdb("iem");
$nt = new NetworkTable($network);
$cities = $nt->table;


$rs = pg_prepare($pgconn, "NSS", "SELECT 
 id,
 sum(pday) as precip,
 extract(month from day) as month
FROM summary_{$year} s JOIN stations t ON (t.iemid = s.iemid)
WHERE
 network = $1
 and pday >= 0
GROUP by id, month");
$rs = pg_execute($pgconn, "NSS", array($network));
$data = array();
for ($i = 0; $row = pg_fetch_assoc($rs); $i++) {
    if (!array_key_exists($row['id'], $data)) {
        $data[$row['id']] = array(
            null, null, null, null, null, null, null,
            null, null, null, null, null
        );
    }
    $data[$row["id"]][intval($row["month"]) - 1] = $row["precip"];
}
$t->headextra = <<<EOM
<link rel="stylesheet" type="text/css" href="/vendor/ext/3.4.1/resources/css/ext-all.css"/>
<script type="text/javascript" src="/vendor/ext/3.4.1/adapter/ext/ext-base.js"></script>
<script type="text/javascript" src="/vendor/ext/3.4.1/ext-all.js"></script>
<script type="text/javascript" src="/vendor/ext/ux/TableGrid.js"></script>
<script type="text/javascript" src="mon_prec.js"></script>
EOM;

reset($data);
function friendly($val)
{
    if (is_null($val)) return "M";
    return sprintf("%.2f", $val);
}
$table = "";
foreach ($data as $key => $val) {
    $table .= sprintf(
        "<tr><td><a href=\"/sites/site.phtml?station=%s&network=%s\">%s</a></td><td>%s</td>
  <td>%s</td><td>%s</td><td>%s</td>
  <td>%s</td><td>%s</td><td>%s</td>
  <td>%s</td><td>%s</td><td>%s</td>
  <td>%s</td><td>%s</td><td>%s</td>
  <td>%.2f</td><td>%.2f</td>
  </tr>",
        $key,
        $network,
        $key,
        $cities[$key]["name"],
        friendly($val[0]),
        friendly($val[1]),
        friendly($val[2]),
        friendly($val[3]),
        friendly($val[4]),
        friendly($val[5]),
        friendly($val[6]),
        friendly($val[7]),
        friendly($val[8]),
        friendly($val[9]),
        friendly($val[10]),
        friendly($val[11]),
        array_sum(array_slice($val, 4, 4)),
        array_sum($val)
    );
}

$d = date("d M Y h a");
$t->content = <<<EOM
<ol class="breadcrumb">
    <li><a href="/ASOS/">ASOS Mainpage</a></li>
    <li>{$year} {$network} Precipitation Report</li>
</ol>

<p>This table was generated at {$d} and is based
on available ASOS data.  
<strong>No attempt was made to estimate missing data.</strong></p>

<form name="change">
<p>{$netselect}
<p>{$yselect}
<input type="submit" value="Change Year" />
</form>

<p><button id="create-grid" type="button">Interactive Grid</button>

<TABLE border="1" cellpadding="2" cellspacing="0" width="100%" id="datagrid">
<thead class="sticky">
<TR>
<th>ID</th>
<th>Name</th>
<TH>Jan</TH>
<TH>Feb</TH>
<TH>Mar</TH>
<TH>Apr</TH>
<TH>May</TH>
<TH>Jun </TH>
<TH>Jul</TH>
<TH>Aug</TH>
<TH>Sep</TH>
<TH>Oct</TH>
<TH>Nov</TH>
<TH>Dec</TH>
<TH><B>MJJA</B></TH>
<TH><B>Year</B></TH>
</TR>
</thead>
<tbody>
{$table}
</tbody>
</table>
EOM;
$t->render('single.phtml');
