<?php 
 include("../../config/settings.inc.php");
 include("$rootpath/include/database.inc.php");
 include("setup.php");

 $THISPAGE="iem-sites";
 $TITLE = "IEM | Current Data";
 include("$rootpath/include/header.php"); 
 $current = "current"; include("sidebar.php"); 

 echo '<h3 class="subtitle">Most Recent Observation</h3>
 		<p>This application displays the last observation received by the IEM
 	from this site. The time stamp is in 
 		<strong>'. $metadata["tzname"] .'</strong> timezone.</p>';
 
 if (strpos($network, "_DCP") || strpos($network, "_COOP") ){
 	echo '<p>This station reports observations in SHEF format.  The following
 			is a table of the most recent reports from this site identifier for
 			each reported SHEF variable';
 	$mesosite = iemdb('mesosite');
 	$shefcodes = Array();
 	$rs = pg_query($mesosite, "SELECT * from shef_physical_codes");
 	for($i=0;$row=@pg_fetch_assoc($rs,$i);$i++){
 		$shefcodes[ $row['code'] ] = $row['name'];
 	}
 	$durationcodes = Array();
 	$rs = pg_query($mesosite, "SELECT * from shef_duration_codes");
 	for($i=0;$row=@pg_fetch_assoc($rs,$i);$i++){
 		$durationcodes[ $row['code'] ] = $row['name'];
 	}
 	$extremumcodes = Array();
 	$rs = pg_query($mesosite, "SELECT * from shef_extremum_codes");
 	for($i=0;$row=@pg_fetch_assoc($rs,$i);$i++){
 		$extremumcodes[ $row['code'] ] = $row['name'];
 	}
 	
 	$pgconn = iemdb('access');
 	pg_query($pgconn, "SET time zone '". $metadata['tzname'] ."'");
 	$rs = pg_prepare($pgconn, "SELECT", "SELECT * from current_shef
 			where station = $1 ORDER by physical_code ASC");
 	$rs = pg_execute($pgconn, "SELECT", Array($station));
	echo "<table cellpadding='3' cellspacing='0' border='1'>
			<thead><tr><th>Physical Code</th><th>Duration</th><th>Extremum</th>
			<th>Valid</th><th>Value</th></thead>";
 	for($i=0;$row=@pg_fetch_assoc($rs,$i);$i++){
 		$ts = strtotime($row["valid"]);
 		$depth = "";
 		if ($row["depth"] > 0){
 			$depth = sprintf("%d inch", $row["depth"]);
 		}
 		echo sprintf("<tr><td>[%s] %s %s</td><td>[%s] %s</td><td>[%s] %s</td><td>%s</td><td>%s</td></tr>", 
 				$row["physical_code"],$shefcodes[$row["physical_code"]], $depth,
 				$row["duration"], $durationcodes[ $row["duration"] ], 
 				$row["extremum"] == 'Z'? '-': $row['extremum'] , $extremumcodes[ $row["extremum"] ],
 				date('d M Y g:i A', $ts), $row["value"]);
 	}
 	echo "</table>";
 } else {
  include ("$rootpath/include/iemaccess.php");
  include ("$rootpath/include/iemaccessob.php");
  $iem = new IEMAccess($metadata["tzname"]);
  $iemob = $iem->getSingleSite($station);
  $rs = $iemob->db;

 $vardict = Array("lvalid" => "Observation Time", "tmpf" => "Air Temp [F]",
 		"max_tmpf" => "Maximum Air Temperature [F]", 
 		"min_tmpf" => "Minimum Air Temperature [F]",
   "dwpf" => "Dew Point [F]", "relh" => "Relative Humidity [%]",
   "drct" => "Wind Direction", "sknt" => "Wind Speed [knots]",
   "srad" => "Solar Radiation",
   "alti" => "Altimeter [inches]", "pday" => "Daily Precipitation [inches]",
   "pmonth" => "Monthly Precipitation [inches]",
   "gust" => "Wind Gust [knots]", "raw" => "Raw Observation/Product");
?>
<table cellpadding="2" cellspacing="0" border="1">
<?php
  foreach ( $vardict as $key => $value ) {
    if (array_key_exists($key, $rs) && $rs[$key] != "" && $rs[$key] != -99) {
      if ($key == "lvalid") {
        $t = date("d M Y, g:i A", strtotime($rs[$key]));
        echo '<tr><td><b>'. $value .'</b></td><td>'. $t .'</td></tr>';
      }
      else {
        echo '<tr><td><b>'. $value .'</b></td><td>'. $rs[$key] .'</td></tr>';
      } // End if
    } // End if
  } 
  echo "</table>";
 }
?>
<?php include("$rootpath/include/footer.php"); ?>
