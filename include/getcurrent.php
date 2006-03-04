<?php
 /**
  * getcurrent.php
  *  - Library for retreiving current data for a station
  */

function getdata($station, $network)
{
    global $rootpath;
	include ('iemaccess.php');
	include ('iemaccessob.php');
	$iem = new IEMAccess();
	$iemob = $iem->getSingleSite($station);
	return $iemob->db;
}

function printTable($station, $network){

 // $rs = getdata("MCW", "ASOS");
 $rs = getdata($station, $network);

 $vardict = Array("valid" => "Observation Time", "tmpf" => "Air Temp [F]",
   "dwpf" => "Dew Point [F]", "relh" => "Relative Humidity [%]",
   "drct" => "Wind Direction", "sknt" => "Wind Speed [knots]",
   "srad" => "Solar Radiation",
   "alti" => "Altimeter [inches]", "pday" => "Daily Precipitation [inches]",
   "pmonth" => "Monthly Precipitation [inches]",
   "gust" => "Wind Gust [knots]");

 foreach ( $vardict as $key => $value ) { 
   if ($rs[$key] != "")
    {
     if ($key == "gmt_ts" || $key == "gtim")
      {
       $time = strftime("%c", $rs[$key]);
       echo '<tr><td class="subtitle"><b>'. $value .'</b></td><td>'. $time .' GMT</td></tr>';
      }
     else
      {
       echo '<tr><td class="subtitle"><b>'. $value .'</b></td><td>'. $rs[$key] .'</td></tr>';
      } // End if
    } // End if
} // End of for
} // End of printTable

?>
