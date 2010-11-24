<?php
include("../../config/settings.inc.php");
 $tbl = isset($_GET["tbl"]) ? $_GET["tbl"] : "all";
 $month = isset($_GET["month"]) ? $_GET["month"] : date("m");
 $day = isset($_GET["day"]) ? $_GET["day"] : date("d");
 $valid = mktime(0,0,0,$month, $day, 2000);
 $sortcol = isset($_GET["sortcol"]) ? $_GET["sortcol"]: "station";

 if ($tbl == "all")
   $tblname = "climate";
 else
   $tblname ="climate51";

 $TITLE = "IEM | Daily Extremes";
include("$rootpath/include/header.php");
 include("$rootpath/include/forms.php");
 include("$rootpath/include/database.inc.php");
 include("$rootpath/include/network.php"); 
$nt = new NetworkTable("IACLIMATE");
$cities = $nt->table;

 $connection = iemdb("coop");

 $td = date("Y-m-d", $valid); 
 $rs = pg_prepare($connection, "SELECT", "SELECT * " .
 		"from $tblname WHERE valid = $1 " .
 		"ORDER by ". $sortcol ." DESC");
 $rs = pg_execute($connection, "SELECT", Array($td));

?> 

<h3 class="heading">COOP Extremes for <?php echo $month ."/". $day ; ?></h3>

<div class="text">
<p>This table gives a listing of <b>unofficial</b> daily records for NWS
COOP stations.  Some records may have occured on multiple years, only one
is listed here.  You may click on a column to sort it. You can pick from 
two record databases, once contains all records since 1951 and the other
contains records for sites that do and don't have data before 1951.
<b>Note:  This database does not contain data from approximately the most recent 2 months.</b>

<form method="GET" action="extremes.php">
<table cellpadding=2 cellspacing=0 border=2>
<tr>
 <td>Select Date:</td>
 <td>
  <?php echo monthSelect($month, "month"); ?>
  <?php echo daySelect($day, "day"); ?>

  </td>
 <td>Record Database:</td>
<td>
 <select name="tbl">
  <option value="all" <?php if ($tbl == "all") echo "SELECTED"; ?>>All Available
  <option value="51" <?php if ($tbl == "51") echo "SELECTED"; ?>>Since 1951
 </select>
</td></tr>

</table>

<input type="submit" value="Request"></form>

</td></tr></table>

<?php
 echo "<table cellpadding=2 rowspacing=0 cellspacing=0 width='700px'>
  <tr>
   <th rowspan='2' class='subtitle' valign='top'><a href='extremes.php?sortcol=station&day=".$day."&month=".$month."'>Station</a></th>
   <th rowspan='2' class='subtitle' valign='top'>Years</th>
   <th colspan='4' class='subtitle'>High Temperature</th>
   <th colspan='4' class='subtitle'>Low Temperature</th>
   <th colspan='2' class='subtitle'>Precipitation</th>
  </tr>
  <tr>
    <th><a href='extremes.php?sortcol=max_high&day=".$day."&month=".$month."'>Max:</a></th>
       <th><a href='extremes.php?sortcol=max_high_yr&day=".$day."&month=".$month."'>Year:</a></th>
    <th><a href='extremes.php?sortcol=min_high&day=".$day."&month=".$month."'>Min:</a></th>
       <th><a href='extremes.php?sortcol=min_high_yr&day=".$day."&month=".$month."'>Year:</a></th>
    <th><a href='extremes.php?sortcol=max_low&day=".$day."&month=".$month."'>Max:</a></th>
       <th><a href='extremes.php?sortcol=max_low_yr&day=".$day."&month=".$month."'>Year:</a></th>
    <th><a href='extremes.php?sortcol=min_low&day=".$day."&month=".$month."'>Min:</a></th>
        <th><a href='extremes.php?sortcol=min_low_yr&day=".$day."&month=".$month."'>Year:</a></th>
    <th><a href='extremes.php?sortcol=max_precip&day=".$day."&month=".$month."'>Max:</a></th>
        <th><a href='extremes.php?sortcol=max_precip_yr&day=".$day."&month=".$month."'>Year:</a></th>
  </tr>
 ";


 for( $i=0; $row = @pg_fetch_array($rs,$i); $i++)
 {
   echo "<tr ";
   if ( ($i % 2) == 0) 
     echo "class='even'";
   echo ">
     <td>". $cities[strtoupper($row["station"])]["name"] ."</td>
     <td>". $row["years"] ."</td>
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
