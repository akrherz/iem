<?php 
include("../../../config/settings.inc.php");
$TITLE = "IEM | COOP Extremes Plots";
$THISPAGE="networks-coop";
include("$rootpath/include/header.php");
include("$rootpath/include/imagemaps.php");
$station = isset($_GET["station"]) ? $_GET["station"] : ""; 
$var = isset($_GET["var"]) ? $_GET["var"]: "";
?>

<div class="text">
<B>Navigation:</B>
<a href="http://mesonet.agron.iastate.edu/">IEM</a> &nbsp;>&nbsp;
<a href="/climate/">Climatology</a> &nbsp;>&nbsp;
<B>COOP Daily Extremes</B>

<BR>
<p>Using the NWS COOP dataset, the IEM has calculated daily
temperature extremes.  You can create a annual plot of this dataset for a
station of your choice.</p> 


<form method="GET" action="extremes_fe.php">

<table>
<tr>
  <th class="subtitle">Station</th>
  <th class="subtitle">Variable</th>
  <td></td>
</tr>

<tr>
<td><?php echo networkSelect("IACLIMATE", $station); ?>
</td>
<td>
<SELECT name="var">
  <option value="high" <?php if ($var == "high") echo " SELECTED "; ?>>High Temp
  <option value="low" <?php if ($var == "low") echo " SELECTED "; ?>>Low Temp
</SELECT>
</td>
<td>
<input type="SUBMIT" value="Make Plot">

</form>
</td>

</tr></table>

<?php

  if (strlen($station) > 0 ){
    echo "<img src=\"extremes.php?var=". $var ."&station=". $station ."\">\n";
  }
?></div>

<?php include("$rootpath/include/footer.php"); ?>
