<?php 
include("../../../config/settings.inc.php");
$TITLE = "IEM | COOP Climate Plots";
$station1 = isset($_GET["station1"]) ? $_GET["station1"] : "IA0000";
$station2 = isset($_GET["station2"]) ? $_GET["station2"] : "";
$mode = isset($_GET["mode"]) ? $_GET["mode"]: "";
$THISPAGE="networks-coop";
include("$rootpath/include/header.php"); 
include("$rootpath/include/network.php");     
$nt = new NetworkTable("IACLIMATE");
$cities = $nt->table;
?>

<div class="text">
<B>Navigation:</B>
<a href="http://mesonet.agron.iastate.edu/">IEM</a> &nbsp;>&nbsp;
<a href="/climate/">Climatology</a> &nbsp;>&nbsp;
<B>COOP Station Normals</B>

<BR>
<p>The IEM has a database of daily temperature averages 
based on a climatology from the COOP stations.  You can interactively generate 
a plot from this dataset.</p>


<div style="padding: 3px;">
     <b>Make Plot Selections:</b>
  <div style="background: white; padding: 3px;">

<form method="GET" action="climate_fe.php">

<table>
<tr>
  <th class="subtitle">Station 1</th>
  <th class="subtitle">Station 2</th>
  <td></td>
  <td></td>
</tr>

<tr>
<td>
<SELECT name="station1">
<?php
	for(reset($cities); $key = key($cities); next($cities))
	{
		print("<option value=\"" . $cities[$key]["id"] ."\"");
                if ($cities[$key]["id"] == $station1) print(" SELECTED ");

		print(">" . $cities[$key]["name"] . "\n");
	}
?>
</SELECT>
</td>
<td>
<SELECT name="station2">
<?php
        for(reset($cities); $key = key($cities); next($cities))
        {
                print("<option value=\"" . $cities[$key]["id"] ."\"");
                if ($cities[$key]["id"] == $station2) print(" SELECTED ");

                print(">" . $cities[$key]["name"] . "\n");
        }
?>
</SELECT>
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

  if ($mode == "c"){
    echo "<img src=\"climate.php?station1=".$station1."&station2=".$station2."\">\n";

  }else if (strlen($station1) > 0 ){
    echo "<img src=\"climate.php?station1=". $station1 ."\">\n";
  }
?></div>

<?php include("$rootpath/include/footer.php"); ?>
