<?php 
include("../../../config/settings.inc.php");
$TITLE = "IEM | COOP Climate Plots";
include("$rootpath/include/header.php"); 

$station1 = isset($_GET["station1"]) ? $_GET["station1"] : "";
$station2 = isset($_GET["station2"]) ? $_GET["station2"] : "";
$mode = isset($_GET["mode"]) ? $_GET["mode"]: "";
$season = isset($_GET["season"]) ? $_GET["season"]: "";
?>

<div class="text">
<B>Navigation:</B>
<a href="http://mesonet.agron.iastate.edu/">IEM</a> &nbsp;>&nbsp;
<a href="/climate/">Climatology</a> &nbsp;>&nbsp;
<B>COOP Yearly Averages</B>

<p>Using the historical COOP data archive, this application plots yearly
temperature averages.  You can plot averages for a single station or compare
two stations side-by-side.</p>

<?php 
include("$rootpath/include/network.php");     
$nt = new NetworkTable("IACLIMATE");
$cities = $nt->table;

?>

<div style="padding: 3px;">
     <b>Make Plot Selections:</b>
  <div style="padding: 3px;">

<form method="GET" action="yearly_fe.php">

<table>
<tr>
  <th class="subtitle">Station 1</th>
  <th class="subtitle">Station 2</th>
  <th class="subtitle">Plot Mode</th>
  <th class="subtitle">Seasons?</th>
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
  <select name="season">
<?php
   echo "<option value=\"all\" ";
   if ( strcmp($season, 'all') == 0 ) echo " SELECTED ";
   echo ">All\n";

   echo "<option value=\"winter\" ";
   if ( strcmp($season, 'winter') == 0 ) echo " SELECTED ";
   echo ">Winter (DJF)\n";

   echo "<option value=\"spring\" ";
   if ( strcmp($season, 'spring') == 0 ) echo " SELECTED ";
   echo ">Spring (MAM)\n";

   echo "<option value=\"summer\" ";
   if ( strcmp($season, 'summer') == 0) echo " SELECTED ";
   echo ">Summer (JJA)\n";

   echo "<option value=\"fall\" ";
   if ( strcmp($season, 'fall') == 0 ) echo " SELECTED ";
   echo ">Fall (SON)\n";

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
    echo "<img src=\"yearly_diff.php?station1=".$station1."&station2=".$station2."&season=".$season."\">\n";

  }else if (strlen($station1) > 0 ){
    echo "<img src=\"yearly.php?station=". $station1 ."&season=".$season."\">\n";
  }else{
    echo "<p>Please make plot selections above.\n";
  }
?></div>

<?php include("$rootpath/include/footer.php"); ?>
