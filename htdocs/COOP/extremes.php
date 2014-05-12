<?php
/*
 * List out COOP extremes table
 */
 include("../../config/settings.inc.php");
 include("../../include/myview.php");
 $t = new MyView();
 
 define("IEM_APPID", 2);
 include("../../include/forms.php");
 include("../../include/database.inc.php");
 include("../../include/network.php"); 

 $tbl = isset($_GET["tbl"]) ? substr($_GET["tbl"],0,10) : "climate";
 $month = isset($_GET["month"]) ? intval($_GET["month"]) : date("m");
 $day = isset($_GET["day"]) ? intval($_GET["day"]) : date("d");
 $valid = mktime(0,0,0,$month, $day, 2000);
 $sortcol = isset($_GET["sortcol"]) ? $_GET["sortcol"]: "station";
 $network = isset($_GET['network']) ? substr($_GET['network'],0,9): 'IACLIMATE';
 $station = isset($_GET["station"]) ? $_GET["station"] : null;
 $sortdir = isset($_GET["sortdir"]) ? $_GET['sortdir'] : 'ASC';

 
 $t->title = "NWS COOP Daily Climatology";
 $t->thispage = "climatology-extremes";


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
 	$h3 = "<h3 class=\"heading\">NWS COOP Climatology for ". $cities[strtoupper($station)]["name"] ." (ID: ". $station .")</h3>";
 } else {
 	$rs = pg_prepare($connection, "SELECT", "SELECT * " .
 		"from $tbl WHERE valid = $1 and substr(station,0,3) = $2" .
 		"ORDER by ". $sortcol ." ". $sortdir);
 	$rs = pg_execute($connection, "SELECT", Array($td, strtoupper(substr($network,0,2))));
 	$h3 = "<h3 class=\"heading\">NWS COOP Climatology for ". date("d F", $valid) ."</h3>";
 	
 }

 $ar = Array("ILCLIMATE" => "Illinois",
 		"INCLIMATE" => "Indiana",
   		"IACLIMATE" => "Iowa",
   	"KSCLIMATE" => "Kansas",
   	"KYCLIMATE" => "Kentucky",
   	"MICLIMATE" => "Michigan",
   	"MNCLIMATE" => "Minnesota",
   	"MOCLIMATE" => "Missouri",
   	"NECLIMATE" => "Nebraska",
   	"NDCLIMATE" => "North Dakota",
   	"OHCLIMATE" => "Ohio",
   	"SDCLIMATE" => "South Dakota",
   	"WICLIMATE" => "Wisconsin"
);
  $netselect = make_select("network", $network, $ar);
 $mselect = monthSelect($month, "month");
 $dselect = daySelect($day, "day");
 
 $ar = Array(
 "climate" => "All Available",
 "climate51" => "Since 1951",
 "climate71" => "1971-2000",
 "climate81" => "1981-2010");
  $tblselect = make_select("tbl", $tbl, $ar);
 
  
  if ($station != null){
  	$uribase = sprintf("&station=%s&network=%s&tbl=%s", $station, $network, $tbl);
  	$h4 = "<a href='extremes.php?sortcol=valid". $uribase ."'>Date</a>";
  }  else {
  	$uribase = sprintf("&day=%s&month=%s&network=%s&tbl=%s", $day, $month, $network, $tbl);
  	$h4 = "<a href='extremes.php?sortcol=station&day=".$day."&month=".$month."'>Station</a>";
  }
  
  $table = "";
  for( $i=0; $row = @pg_fetch_array($rs,$i); $i++)
  {
  if (!array_key_exists(strtoupper($row["station"]), $cities)){
  continue;
  }
  $table .= "<tr ";
  if ( ($i % 2) == 0)
  $table .= "class='even'";
  $table .= ">";
   if ($station != null){
  $table .= "<td><a href=\"extremes.php?month=". $row["month"] . "&day=". $row["day"] ."&network=". $network ."\">". date("F d", strtotime($row["valid"])) ."</a></td>";
  } else {
  		$table .= "<td><a href=\"extremes.php?station=". $row["station"] . $uribase ."\">". $cities[strtoupper($row["station"])]["name"] ."</a></td>";
   }
  				$table .= sprintf("<td>%s</td><td>%.1f</td><td class='red'>%s</td><td>%s</td><td class='blue'>%s</td><td>%s</td><td>&nbsp;</td><td>%.1f</td>
     <td class='red'>%s</td><td>%s</td><td class='blue'>%s</td><td>%s</td><td>&nbsp;</td><td>%.2f</td><td>%s</td><td>%s</td></tr>\n", $row["years"],
     $row["high"], $row["max_high"], $row["max_high_yr"], $row["min_high"], $row["min_high_yr"],
       $row["low"], $row["max_low"] , $row["max_low_yr"] , $row["min_low"], $row["min_low_yr"] ,
       $row["precip"], $row["max_precip"] , $row["max_precip_yr"] );
  
 }
  
 $t->content = <<<EOF
 
 {$h3}
 
<p>This table gives a listing of <b>unofficial</b> daily records for NWS
COOP stations.  Some records may have occured on multiple years, only one
is listed here.  You may click on a column to sort it.  You can click on the station
name to get all daily records for that station or click on the date to get all records
for that date.</p>

<form method="GET" action="extremes.php" name="myform">
<table cellpadding=2 cellspacing=0 border=2>
<tr>
 <td>Select State:</td>
 <td>{$netselect}
 </td>
 <td>Select Date:</td>
 <td>{$mselect}
  {$dselect}

  </td>
 <td>Record Database:</td>
<td>{$tblselect}
</td>
<td>
<input type="submit" value="Request">
</td></tr>
</table>
</form>

<br />
<style>
.red{
 color: #f00;
}
.blue{
 color: #00f;
}
</style>

<table class="table table-condensed table-striped">
<thead>
  <tr>
   <th rowspan='2' class='subtitle' valign='top'>
{$h4}
</th>
<th rowspan='2' class='subtitle' valign='top'>Years</th>
   <th colspan='5' class='subtitle'>High Temperature [F]</th>
   <td>&nbsp;</td>
   <th colspan='5' class='subtitle'>Low Temperature [F]</th>
   <td>&nbsp;</td>
   <th colspan='3' class='subtitle'>Precipitation [inch]</th>
  </tr>
  <tr>
    <th><a href='extremes.php?sortcol=high{$uribase}'>Avg:</a></th>
    <th><a href='extremes.php?sortcol=max_high{$uribase}'>Max:</a></th>
       <th><a href='extremes.php?sortcol=max_high_yr{$uribase}'>Year:</a></th>
    <th><a href='extremes.php?sortcol=min_high{$uribase}'>Min:</a></th>
       <th><a href='extremes.php?sortcol=min_high_yr{$uribase}'>Year:</a></th>
       <td>&nbsp;</td>
	<th><a href='extremes.php?sortcol=low{$uribase}'>Avg:</a></th>
    <th><a href='extremes.php?sortcol=max_low{$uribase}'>Max:</a></th>
       <th><a href='extremes.php?sortcol=max_low_yr{$uribase}'>Year:</a></th>
    <th><a href='extremes.php?sortcol=min_low{$uribase}'>Min:</a></th>
        <th><a href='extremes.php?sortcol=min_low_yr{$uribase}'>Year:</a></th>
        <td>&nbsp;</td>
    <th><a href='extremes.php?sortcol=precip{$uribase}'>Avg:</a></th>
    <th><a href='extremes.php?sortcol=max_precip{$uribase}'>Max:</a></th>
        <th><a href='extremes.php?sortcol=max_precip_yr{$uribase}'>Year:</a></th>
  </tr>
</thead>
<tbody>
{$table}
</tbody>
</table>
EOF;
$t->render('single.phtml');
 ?>
