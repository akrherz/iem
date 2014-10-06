<?php 
include("../../../config/settings.inc.php");
include_once "../../../include/myview.php";
$t = new MyView();
$t->title = "COOP High/Low Scatterplot";
$t->thispage = "climatology-today";
include("../../../include/imagemaps.php");
include("../../../include/forms.php");
$station = isset($_GET["station"]) ? $_GET["station"] : "IA0200"; 
$month = isset($_GET["month"]) ? intval($_GET["month"]): date("m");
$day = isset($_GET["day"]) ? intval($_GET["day"]): date("d");

$nselect = networkSelect("IACLIMATE", $station);
$ms = monthSelect($month, "month");
$ds = daySelect($day, "day");

$t->content = <<<EOF
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
<td>{$nselect}</td>
<td>{$ms}</td>
<td>{$ds}</td>
<td><input type="SUBMIT" value="Make Plot"></td>
</tr></table>
</form>
<img src="highs_v_lows.php?month=${month}&station=${station}&day=${day}">
</div>
EOF;
$t->render('single.phtml');
?>
