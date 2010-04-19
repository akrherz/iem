<?php
include("../../../config/settings.inc.php");
$year = isset($_GET["year"]) ? intval($_GET["year"]): date("Y");
include("$rootpath/include/database.inc.php");
$pgconn = iemdb("access");
include("$rootpath/include/network.php");
$nt = new NetworkTable("AWOS");
$cities = $nt->table;


$rs = pg_query($pgconn, "SELECT 
 station,
 sum(pday) as precip,
 extract(month from day) as month
FROM summary_${year}
WHERE
 network = 'AWOS'
 and pday >= 0
GROUP by station, month");
$data = Array();
for($i=0;$row=@pg_fetch_array($rs,$i);$i++)
{
  if (!array_key_exists($row['station'], $data))
  { 
    $data[$row['station']] = Array(null,null,null,null,null,null,null,
      null,null,null,null,null);
  }
  $data[$row["station"]][intval($row["month"])-1] = $row["precip"];
}
$HEADEXTRA = '<link rel="stylesheet" type="text/css" href="http://extjs.cachefly.net/ext-3.2.0/resources/css/ext-all.css"/>
<script type="text/javascript" src="http://extjs.cachefly.net/ext-3.2.0/adapter/ext/ext-base.js"></script>
<script type="text/javascript" src="http://extjs.cachefly.net/ext-3.2.0/ext-all.js"></script>
<script type="text/javascript" src="../../ext/ux/TableGrid.js"></script>
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
$THISPAGE = "networks-awos";
$TITLE = "IEM Iowa AWOS Monthly Precipitation";
include("$rootpath/include/header.php"); 
?>

<h3 class="heading"><?php echo $year; ?> Iowa AWOS Precipitation Report</h3>

<p>This table was generated at <?php echo date("d M Y h a"); ?> and is based
on AWOS minute by minute data.  No attempt was made to estimate missing data.</p>

<button id="create-grid" type="button">Interactive Grid</button>

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
<?php
reset($data);
function friendly($val){
 if ($val == null) return "M";
 return sprintf("%.2f", $val); 
}
while (list($key,$val) = each($data)){
  echo sprintf("<tr><td>%s</td><td>%s</td>
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
?>
</tbody>
</table>

<?php include("$rootpath/include/footer.php"); ?>
