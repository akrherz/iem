<?php 
include("../../../config/settings.inc.php");
$TITLE = "IEM | COOP High/Low Scatterplot";
$THISPAGE = "climatology-today";
include("$rootpath/include/header.php");
include("$rootpath/include/imagemaps.php");
include("$rootpath/include/forms.php");
$station = isset($_GET["station"]) ? $_GET["station"] : "IA0200"; 
$month = isset($_GET["month"]) ? intval($_GET["month"]): date("m");
$day = isset($_GET["day"]) ? intval($_GET["day"]): date("d");
?>

<p>This application generates a scatter plot of daily 
high versus low temperature for a NWS COOP site for a given date.  The resulting
plot gives an indication of the spread of temperatures given a high or
low temperature.

<form method="GET" action="highlow_scatter.php">

<table>
<tr>
  <th class="subtitle">Station:</th>
  <th class="subtitle">Month:</th>
  <th class="subtitle">Day:</th>
  <td></td>
</tr>

<tr>
<td><?php echo networkSelect("IACLIMATE", $station); ?>
</td>
<td><?php echo monthSelect($month, "month"); ?></td>
<td><?php echo daySelect($day, "day"); ?></td>
<td><input type="SUBMIT" value="Make Plot"></td>
</tr></table>
</form>
<?php echo "<img src=\"highs_v_lows.php?month=${month}&station=${station}&day=${day}\">\n";
?></div>

<?php include("$rootpath/include/footer.php"); ?>
