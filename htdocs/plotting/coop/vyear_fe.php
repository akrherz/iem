<?php 
include("../../../config/settings.inc.php");
$TITLE = "IEM | COOP Data vs Year";
include("$rootpath/include/header.php"); 

$station = isset($_GET["station"]) ? $_GET["station"] : "";
$year = isset($_GET["year"]) ? $_GET["year"]: date("Y");
include("../../../include/forms.php");     
include("../../../include/imagemaps.php");

$imgurl = sprintf("/cgi-bin/climate/daily.py?plot=compare&station1=%s&year=%s",
		$station, $year);
?>


<p class="intro">With this form, you can interactively plot one year vs 
climatology for a station.  Please note the first year of record for a 
station before entering the year you would like to plot against.</p>


<form method="GET" action="vyear_fe.php">

<table>
<tr>
  <th class="subtitle">Station:</th>
  <th class="subtitle">Select Year:</th>
  <td></td>
</tr>

<tr>
<td>
<?php echo networkSelect("IACLIMATE", $station); ?>
</td>
<td>
<?php echo yearSelect(1893, $year); ?>
</td>
<td>
<input type="SUBMIT" value="Make Plot">

</form>
</td>

</tr></table>

<?php
    echo "<img src=\"$imgurl\">\n";
?>
<?php include("../../../include/footer.php"); ?>
