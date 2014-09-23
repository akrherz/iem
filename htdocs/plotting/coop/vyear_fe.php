<?php 
include("../../../config/settings.inc.php");
include_once "../../../include/myview.php";
include("../../../include/forms.php");
include("../../../include/imagemaps.php");

$t = new MyView();
$t->title = "COOP Data vs Year";

$station = isset($_GET["station"]) ? $_GET["station"] : "";
$year = isset($_GET["year"]) ? $_GET["year"]: date("Y");

$imgurl = sprintf("/cgi-bin/climate/daily.py?plot=compare&station1=%s&year=%s",
		$station, $year);

$nselect = networkSelect("IACLIMATE", $station);
$yselect = yearSelect(1893, $year);

$t->content = <<<EOF

<p>With this form, you can interactively plot one year vs 
climatology for a station.</p>


<form method="GET" action="vyear_fe.php">

<table>
<tr>
  <th class="subtitle">Station:</th>
  <th class="subtitle">Select Year:</th>
  <td></td>
</tr>

<tr>
<td>
{$nselect}
</td>
<td>
{$yselect}
</td>
<td>
<input type="SUBMIT" value="Make Plot">

</form>
</td>

</tr></table>

<img src="{$imgurl}">

EOF;
$t->render('single.phtml');
?>