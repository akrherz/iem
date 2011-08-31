<?php
/*
 * List out COOP extremes table
 */
 include("../../config/settings.inc.php");
 include("$rootpath/include/forms.php");
 include("$rootpath/include/database.inc.php");
 include("$rootpath/include/network.php"); 

 $tbl = isset($_GET["tbl"]) ? substr($_GET["tbl"],0,10) : "climate";
 $month = isset($_GET["month"]) ? intval($_GET["month"]) : date("m");
 $day = isset($_GET["day"]) ? intval($_GET["day"]) : date("d");
 $valid = mktime(0,0,0,$month, $day, 2000);
 $sortcol = isset($_GET["sortcol"]) ? $_GET["sortcol"]: "station";
 $network = isset($_GET['network']) ? substr($_GET['network'],0,9): 'IACLIMATE';
 $station = isset($_GET["station"]) ? $_GET["station"] : null;
 $sortdir = isset($_GET["sortdir"]) ? $_GET['sortdir'] : 'ASC';

 
 $TITLE = "IEM | Daily Extremes";
 $THISPAGE = "networks-coop";
 include("$rootpath/include/header.php");


$nt = new NetworkTable($network);
$cities = $nt->table;

 $connection = iemdb("coop");

 $td = date("Y-m-d", $valid); 
 if ($station != null){
 	if ($sortcol == 'station') $sortcol = 'valid';
 	$rs = pg_prepare($connection, "SELECT", "SELECT *, extract(month from valid) as month,
 		extract(day from valid) as day " .
 		"from $tbl WHERE station = $1" .
 		"ORDER by ". $sortcol ." ". $sortdir);
 	$rs = pg_execute($connection, "SELECT", Array($station) );
 } else {
 	$rs = pg_prepare($connection, "SELECT", "SELECT * " .
 		"from $tbl WHERE valid = $1 and substr(station,0,3) = $2" .
 		"ORDER by ". $sortcol ." ". $sortdir);
 	$rs = pg_execute($connection, "SELECT", Array($td, strtolower(substr($network,0,2))));
 }
?> 

<h3 class="heading">COOP Extremes for <?php echo date("d F", $valid); ?></h3>

<div class="text">
<p>This table gives a listing of <b>unofficial</b> daily records for NWS
COOP stations.  Some records may have occured on multiple years, only one
is listed here.  You may click on a column to sort it.  You can click on the station
name to get all daily records for that station or click on the date to get all records
for that date.</p>

<form method="GET" action="extremes.php" name="myform">
<table cellpadding=2 cellspacing=0 border=2>
<tr>
 <td>Select State:</td>
 <td>
 <select name="network">
  <option value="ILCLIMATE" <?php if ($network == "ILCLIMATE") echo "SELECTED"; ?>>Illinois</option>
  <option value="INCLIMATE" <?php if ($network == "INCLIMATE") echo "SELECTED"; ?>>Indiana</option>
  <option value="IACLIMATE" <?php if ($network == "IACLIMATE") echo "SELECTED"; ?>>Iowa</option>
  <option value="KSCLIMATE" <?php if ($network == "KSCLIMATE") echo "SELECTED"; ?>>Kansas</option>
  <option value="KYCLIMATE" <?php if ($network == "KYCLIMATE") echo "SELECTED"; ?>>Kentucky</option>
  <option value="MICLIMATE" <?php if ($network == "MICLIMATE") echo "SELECTED"; ?>>Michigan</option>
  <option value="MNCLIMATE" <?php if ($network == "MNCLIMATE") echo "SELECTED"; ?>>Minnesota</option>
  <option value="MOCLIMATE" <?php if ($network == "MOCLIMATE") echo "SELECTED"; ?>>Missouri</option>
  <option value="NECLIMATE" <?php if ($network == "NECLIMATE") echo "SELECTED"; ?>>Nebraska</option>
  <option value="NDCLIMATE" <?php if ($network == "NDCLIMATE") echo "SELECTED"; ?>>North Dakota</option>
  <option value="OHCLIMATE" <?php if ($network == "OHCLIMATE") echo "SELECTED"; ?>>Ohio</option>
  <option value="SDCLIMATE" <?php if ($network == "SDCLIMATE") echo "SELECTED"; ?>>South Dakota</option>
  <option value="WICLIMATE" <?php if ($network == "WICLIMATE") echo "SELECTED"; ?>>Wisconsin</option>
 </select>
 </td>
 <td>Select Date:</td>
 <td>
  <?php echo monthSelect($month, "month"); ?>
  <?php echo daySelect($day, "day"); ?>

  </td>
 <td>Record Database:</td>
<td>
 <select name="tbl">
  <option value="climate" <?php if ($tbl == "climate") echo "SELECTED"; ?>>All Available
  <option value="climate51" <?php if ($tbl == "climate51") echo "SELECTED"; ?>>Since 1951
  <option value="climate71" <?php if ($tbl == "climate71") echo "SELECTED"; ?>>1971-2000
  <option value="climate81" <?php if ($tbl == "climate81") echo "SELECTED"; ?>>1981-2010
 </select>
</td>
<td>
<input type="submit" value="Request">
</td></tr>
</table>
</form>

<br />

<?php

 echo "<table cellpadding=2 rowspacing=0 cellspacing=0 width='700px'>
  <tr>
   <th rowspan='2' class='subtitle' valign='top'>";
 	if ($station != null){
 		$uribase = sprintf("&station=%s&network=%s&tbl=%s", $station, $network, $tbl);
 		echo "<a href='extremes.php?sortcol=valid". $uribase ."'>Date</a></th>";
 	}  else {
		$uribase = sprintf("&day=%s&month=%s&network=%s&tbl=%s", $day, $month, $network, $tbl);
 		echo "<a href='extremes.php?sortcol=station&day=".$day."&month=".$month."'>Station</a></th>";
 	}
   echo "<th rowspan='2' class='subtitle' valign='top'>Years</th>
   <th colspan='4' class='subtitle'>High Temperature</th>
   <th colspan='4' class='subtitle'>Low Temperature</th>
   <th colspan='2' class='subtitle'>Precipitation</th>
  </tr>
  <tr>
    <th><a href='extremes.php?sortcol=max_high".$uribase."'>Max:</a></th>
       <th><a href='extremes.php?sortcol=max_high_yr".$uribase."'>Year:</a></th>
    <th><a href='extremes.php?sortcol=min_high".$uribase."'>Min:</a></th>
       <th><a href='extremes.php?sortcol=min_high_yr".$uribase."'>Year:</a></th>
    <th><a href='extremes.php?sortcol=max_low".$uribase."'>Max:</a></th>
       <th><a href='extremes.php?sortcol=max_low_yr".$uribase."'>Year:</a></th>
    <th><a href='extremes.php?sortcol=min_low".$uribase."'>Min:</a></th>
        <th><a href='extremes.php?sortcol=min_low_yr".$uribase."'>Year:</a></th>
    <th><a href='extremes.php?sortcol=max_precip".$uribase."'>Max:</a></th>
        <th><a href='extremes.php?sortcol=max_precip_yr".$uribase."'>Year:</a></th>
  </tr>
 ";


 for( $i=0; $row = @pg_fetch_array($rs,$i); $i++)
 {
 	if (!array_key_exists(strtoupper($row["station"]), $cities)){
 		continue;
 	}
   echo "<tr ";
   if ( ($i % 2) == 0) 
     echo "class='even'";
   echo ">";
   if ($station != null){
     echo "<td><a href=\"extremes.php?month=". $row["month"] . "&day=". $row["day"] ."&network=". $network ."\">". date("F d", strtotime($row["valid"])) ."</a></td>";
   } else {
     echo "<td><a href=\"extremes.php?station=". $row["station"] . $uribase ."\">". $cities[strtoupper($row["station"])]["name"] ."</a></td>";
   }
     echo "<td>". $row["years"] ."</td>
     <td>". $row["max_high"] ."</td>
     <td>". $row["max_high_yr"] ."</td>
     <td>". $row["min_high"] ."</td>
     <td>". $row["min_high_yr"] ."</td>
     <td>". $row["max_low"] ."</td>
     <td>". $row["max_low_yr"] ."</td>
     <td>". $row["min_low"] ."</td>
     <td>". $row["min_low_yr"] ."</td>
     <td>". $row["max_precip"] ."</td>
     <td>". $row["max_precip_yr"] ."</td>

   </tr>";

 }
 pg_close($connection);
 echo "</table>\n";
?></div>
<?php include("$rootpath/include/footer.php"); ?>
