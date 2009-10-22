<?php
include("../../config/settings.inc.php");
include("$rootpath/include/forms.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/constants.php");
include("$rootpath/include/network.php");
$nt = new NetworkTable("COOPDB");
$cities = $nt->table;

$coopdb = iemdb("coop");
$month = isset($_GET["month"]) ? intval($_GET["month"]): date("m");
$year = isset($_GET["year"]) ? intval($_GET["year"]): date("Y");
$station = isset($_GET["station"]) ? strtolower($_GET["station"]): "ia0200";

/* Go get it */
$rs = pg_prepare($coopdb, "SELECT", "SELECT * from alldata WHERE
      stationid = $1 and year = $2 and month = $3 ORDER by day ASC");
$rs = pg_execute($coopdb, "SELECT", Array($station, $year, $month) );

$TITLE = "IEM | COOP Data by Month";
$THISPAGE="networks-coop";
include("$rootpath/include/header.php"); 
?>
<h3>IEM Provided NWS COOP Data by Month</h3>

<p>This page provides a way to view daily NWS COOP observations for a given 
month.  Values after <strong><?php echo date('d M Y', $coop_archive_end); ?>
</strong> have been <a href="<?php echo $rooturl; ?>/onsite/news.phtml?id=881">estimated</a> by the IEM.  You can download these observations <a href="<?php echo $rooturl; ?>/request/coop/fe.phtml">here</a>.</p>

<form method="GET" name="myform">
<table>
<tr><td>Select Station:</td>
<td><select name="station">
<?php
while (list($id, $meta) = each($cities)){
  $chk = (strtolower($id) == $station) ? "SELECTED": "";
  echo sprintf("<option value=\"%s\" %s>%s [%s]</option>", $id, $chk, $meta["name"], $id);
}
?>
</select></td>
<td>Year:</td><td><?php echo yearSelect(1893,$year); ?></td>
<td>Month:</td><td><?php echo monthSelect($month); ?></td>
<td><input type="submit" value="Generate Table"></td>
</tr></table>
</form>

<!-- Time for the data -->
<p>
<table cellpadding="2" cellspacing="0" border="1">
<thead><tr><th>Station ID:</th><th>Date</th><th>High</th><th>Low</th><th>Precip</th><th>Snow</th><th>Snowdepth</th></tr></thead>
<tbody>
<?php
for($i=0;$row=@pg_fetch_array($rs,$i);$i++){
  echo sprintf("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>", 
       $cities[strtoupper($station)]["name"], $row["day"], $row["high"], 
       $row["low"], $row["precip"], $row["snow"], $row["snowd"]);
}
?>
</tbody>
</table>
<?php
if (pg_num_rows($rs) == 0){
  echo "<div class=\"warning\">Sorry, no data found for your query parameters.</div>";
}

include("$rootpath/include/footer.php"); 
?>

