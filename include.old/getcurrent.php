<?php
 /**
  * getcurrent.php
  *  - Library for retreiving current data for a station
  */

function getdata($station, $network)
{
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
   "smph" => "Wind Speed [MPH]", "srad" => "Solar Radiation",
   "alti" => "Altimeter [inches]", "pday" => "Daily Precipitation [inches]",
   "pmonth" => "Monthly Precipitation [inches]", "prat" => "Precipitation Rate [in/hr]",
   "gmph" => "Wind Gust [MPH]", "20gu" => "20 Minute Gust [MPH]",
   "gtim" => "Time of Peak Gust", "gmt_ts" => "Observation Time [GMT]",
   "pmsl" => "Barometer [mb]");

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
