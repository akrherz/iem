<?php 
include("../../../config/settings.inc.php");
$TITLE = "IEM | COOP Climate Plots";
$station1 = isset($_GET["station1"]) ? $_GET["station1"] : "IA0000";
$station2 = isset($_GET["station2"]) ? $_GET["station2"] : null;
$mode = isset($_GET["mode"]) ? $_GET["mode"]: "";
$THISPAGE="networks-coop";
include("$rootpath/include/header.php"); 
include("$rootpath/include/imagemaps.php");     

$imgurl = sprintf("/cgi-bin/climate/daily.py?station1=%s", $station1);
if ($mode == 'c'){
	$imgurl .= sprintf("&station2=%s", $station2);
}

?>

<h3>Daily Climatology</h3>

<p>This application dynamically generates plots of the daily average high
and low temperature for climate locations tracked by the IEM.  You can optionally
plot two stations at once for a visual comparison.</p>

<div style="padding: 3px;">
     <b>Make Plot Selections:</b>
  <div style="background: white; padding: 3px;">

<form method="GET" action="climate_fe.php">

<table cellpadding='3' border='1' cellspacing='0'>
<tr>
  <th class="subtitle">Station 1</th>
  <th class="subtitle">Station 2</th>
  <td></td>
  <td></td>
</tr>

<tr>
<td>
<?php echo networkSelect("IACLIMATE", $station1, Array(), "station1"); ?>
</td>
<td>
<?php echo networkSelect("IACLIMATE", $station2, Array(), "station2"); ?>
</td>
<td>
  <select name="mode">
<?php
   echo "<option value=\"o\" ";
   if ($mode == "o") echo " SELECTED ";
   echo ">One Station\n";
   echo "<option value=\"c\" ";
   if ($mode == "c") echo " SELECTED ";
   echo ">Compare Two\n";

?>
  </select>
</td>

<td>
<input type="SUBMIT" value="Make Plot">

</form>
</td>

</tr></table>

</div></div>

<?php
echo "<img src=\"$imgurl\">\n";
?>

<?php include("$rootpath/include/footer.php"); ?>
