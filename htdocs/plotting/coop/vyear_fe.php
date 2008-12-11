<?php 
include("../../../config/settings.inc.php");
$TITLE = "IEM | COOP Data vs Year";
include("$rootpath/include/header.php"); 

$station = isset($_GET["station"]) ? $_GET["station"] : "";
$year = isset($_GET["year"]) ? $_GET["year"]: 2004;
include("$rootpath/include/imagemaps.php");     


?>

<div class="text">
<B>Navigation:</B>
<a href="http://mesonet.agron.iastate.edu/">IEM</a> &nbsp;>&nbsp;
<a href="/climate/">Climatology</a> &nbsp;>&nbsp;
<B>COOP Climate vs Year</B>

<BR>
<p class="intro">With this form, you can interactively plot one year vs 
climatology for a station.  Please note the first year of record for a 
station before entering the year you would like to plot against.</p>


<form method="GET" action="vyear_fe.php">

<table>
<tr>
  <th class="subtitle">Station (First Climate Year)</th>
  <th class="subtitle">Input Year ex) 2000</th>
  <td></td>
</tr>

<tr>
<td>
<?php echo networkSelect("IACLIMATE", $station); ?>
</td>
<td>
<input type="text" name="year" size=5 maxlength=4 value="<?php echo $year; ?>">
</td>
<td>
<input type="SUBMIT" value="Make Plot">

</form>
</td>

</tr></table>

<?php

  if (strlen($station) > 0 ){
    echo "<img src=\"vyear.php?year=". $year ."&station=". $station ."\">\n";
  }
?></div>

<?php include("$rootpath/include/footer.php"); ?>

</body>
</HTML>
