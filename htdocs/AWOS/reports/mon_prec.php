<?php
require_once "../../../config/settings.inc.php";
define("IEM_APPID", 38);
require_once "../../../include/myview.php";
require_once "../../../include/database.inc.php";
require_once "../../../include/network.php";
require_once "../../../include/forms.php";

$year = isset($_GET["year"]) ? intval($_GET["year"]): date("Y");

$yselect = yearSelect2(2004, $year, "year");

$t = new MyView();
$t->thispage = "networks-awos";
$t->title = "Iowa AWOS Monthly Precipitation";

$pgconn = iemdb("iem");
$nt = new NetworkTable("AWOS");
$cities = $nt->table;


$rs = pg_query($pgconn, "SELECT 
 id,
 sum(pday) as precip,
 extract(month from day) as month
FROM summary_${year} s JOIN stations t ON (t.iemid = s.iemid)
WHERE
 network = 'AWOS'
 and pday >= 0
GROUP by id, month");
$data = Array();
for($i=0;$row=@pg_fetch_assoc($rs,$i);$i++)
{
  if (!array_key_exists($row['id'], $data))
  { 
    $data[$row['id']] = Array(null,null,null,null,null,null,null,
      null,null,null,null,null);
  }
  $data[$row["id"]][intval($row["month"])-1] = $row["precip"];
}
$t->headextra = '
<link rel="stylesheet" type="text/css" href="/vendor/ext/3.4.1/resources/css/ext-all.css"/>
<script type="text/javascript" src="/vendor/ext/3.4.1/adapter/ext/ext-base.js"></script>
<script type="text/javascript" src="/vendor/ext/3.4.1/ext-all.js"></script>
<script type="text/javascript" src="/ext/ux/TableGrid.js"></script>
<script>
Ext.onReady(function(){
    var btn = Ext.get("create-grid");
    btn.on("click", function(){
        btn.dom.disabled = true;
        
        // create the grid
        var grid = new Ext.ux.grid.TableGrid("datagrid", {
            stripeRows: true // stripe alternate rows
        });
        grid.render();
    }, false, {
        single: true
    }); // run once

});
</script>
';

reset($data);
function friendly($val){
	if ($val == null) return "M";
	return sprintf("%.2f", $val);
}
$table = "";
while (list($key,$val) = each($data)){
	$table .= sprintf("<tr><td>%s</td><td>%s</td>
  <td>%s</td><td>%s</td><td>%s</td>
  <td>%s</td><td>%s</td><td>%s</td>
  <td>%s</td><td>%s</td><td>%s</td>
  <td>%s</td><td>%s</td><td>%s</td>
  <td>%.2f</td><td>%.2f</td>
  </tr>", $key, $cities[$key]["name"],
			friendly($val[0]), friendly($val[1]), friendly($val[2]),
			friendly($val[3]), friendly($val[4]), friendly($val[5]),
			friendly($val[6]), friendly($val[7]), friendly($val[8]),
			friendly($val[9]), friendly($val[10]), friendly($val[11]),
			array_sum(array_slice($val,4,4)),
			array_sum($val)
	);
}

$d = date("d M Y h a");
$t->content = <<<EOF
<ol class="breadcrumb">
	<li><a href="/AWOS/">AWOS Mainpage</a></li>
	<li>{$year} Iowa AWOS Precipitation Report</li>
</ol>

<p>This table was generated at {$d} and is based
on available AWOS data.  
<strong>No attempt was made to estimate missing data.</strong></p>

<form name="change">
<p>{$yselect}
<input type="submit" value="Change Year" />
</form>

<p><button id="create-grid" type="button">Interactive Grid</button>

<TABLE border="1" cellpadding="2" cellspacing="0" width="100%" id="datagrid">
<thead>
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
EOF;
$t->render('single.phtml');
?>
