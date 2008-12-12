<?php 
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("setup.php");

$THISPAGE="iem-sites";
	$TITLE = "IEM | Current Data";
	include("$rootpath/include/header.php"); 
?>
<?php $current = "current"; include("sidebar.php"); ?>
<?php 
  include ("$rootpath/include/iemaccess.php");
  include ("$rootpath/include/iemaccessob.php");
  $iem = new IEMAccess();
  $iemob = $iem->getSingleSite($station);
  $rs = $iemob->db;

 $vardict = Array("valid" => "Observation Time", "tmpf" => "Air Temp [F]",
   "dwpf" => "Dew Point [F]", "relh" => "Relative Humidity [%]",
   "drct" => "Wind Direction", "sknt" => "Wind Speed [knots]",
   "srad" => "Solar Radiation",
   "alti" => "Altimeter [inches]", "pday" => "Daily Precipitation [inches]",
   "pmonth" => "Monthly Precipitation [inches]",
   "gust" => "Wind Gust [knots]");
?>
<p>This application displays the last observation received by the IEM 
from this site.</p>
<table>
<?php
  foreach ( $vardict as $key => $value ) {
    if ($rs[$key] != "") {
      if ($key == "gmt_ts" || $key == "gtim") {
        $time = strftime("%c", $rs[$key]);
        echo '<tr><td><b>'. $value .'</b></td><td>'. $time .' GMT</td></tr>';
      } else {
        echo '<tr><td><b>'. $value .'</b></td><td>'. $rs[$key] .'</td></tr>';
      } // End if
    } // End if
  } 
?>
</table>
<?php include("$rootpath/include/footer.php"); ?>
