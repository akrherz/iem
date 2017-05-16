<?php 
 include("../../config/settings.inc.php");
 include("../../include/database.inc.php");
 require_once "setup.php";

 include("../../include/myview.php");
 $t = new MyView();
 
 $t->thispage = "iem-sites";
 $t->title = "Current Data";
 $t->sites_current = "current"; 


 if (strpos($network, "_DCP") || strpos($network, "_COOP") ){
 	$table = '<p>This station reports observations in SHEF format.  The following
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
 	$rs = pg_prepare($pgconn, "SELECT", "SELECT *, ".
 			"to_char(valid at time zone $1, 'dd Mon YYYY HH:MI AM') as ts ".
 			"from current_shef ".
 			"where station = $2 ORDER by physical_code ASC");
 	$rs = pg_execute($pgconn, "SELECT", Array($metadata['tzname'], $station));
	$table .= "<table class=\"table table-striped\">
			<thead><tr><th>Physical Code</th><th>Duration</th><th>Extremum</th>
			<th>Valid</th><th>Value</th></thead>";
 	for($i=0;$row=@pg_fetch_assoc($rs,$i);$i++){
 		$depth = "";
 		if ($row["depth"] > 0){
 			$depth = sprintf("%d inch", $row["depth"]);
 		}
 		$table .= sprintf("<tr><td>[%s] %s %s</td><td>[%s] %s</td><td>[%s] %s</td><td>%s</td><td>%s</td></tr>", 
 				$row["physical_code"],$shefcodes[$row["physical_code"]], $depth,
 				$row["duration"], $durationcodes[ $row["duration"] ], 
 				$row["extremum"] == 'Z'? '-': $row['extremum'] , $extremumcodes[ $row["extremum"] ],
 				$row["ts"], $row["value"]);
 	}
 	$table .= "</table>";
} else {
	$wsuri = sprintf("http://iem.local/json/current.py?network=%s&station=%s",
			$network, $station);
	$exturi = sprintf("https://mesonet.agron.iastate.edu/".
			"json/current.py?network=%s&station=%s",
			$network, $station);
	$data = file_get_contents($wsuri);
	$json = json_decode($data, $assoc=TRUE);
	
 	$vardict = Array(
 		"local_valid" => "Observation Local Time",
 		"utc_valid" => "Observation UTC Time",
 		"airtemp[F]" => "Air Temp [F]",
 		"max_dayairtemp[F]" => "Maximum Air Temperature [F]", 
 		"min_dayairtemp[F]" => "Minimum Air Temperature [F]",
   		"dewpointtemp[F]" => "Dew Point [F]",
 		"relh" => "Relative Humidity [%]",
   		"winddirection[deg]" => "Wind Direction",
 		"windspeed[kt]" => "Wind Speed [knots]",
   		"srad" => "Solar Radiation",
   		"altimeter[in]" => "Altimeter [inches]",
 		"pday" => "Daily Precipitation [inches]",
   		"pmonth" => "Monthly Precipitation [inches]",
   		"gust" => "Wind Gust [knots]", 
 		"c1tmpf" => "Soil Temperature [F]",	
 		"c2tmpf" => "Soil Temperature [F]",	
 		"c3tmpf" => "Soil Temperature [F]",
 		"c4tmpf" => "Soil Temperature [F]",
 		"c5tmpf" => "Soil Temperature [F]",
 		"c1smv" => "Soil Moisture [%]",
 		"c2smv" => "Soil Moisture [%]",
 		"c3smv" => "Soil Moisture [%]",
 		"c4smv" => "Soil Moisture [%]",
 		"c5smv" => "Soil Moisture [%]",		
 		"raw" => "Raw Observation/Product");

 	if ($network == 'ISUSM'){
 		$vardict["c1tmpf"] = "4 inch Soil Temperature [F]";
 		$vardict["c2tmpf"] = "12 inch Soil Temperature [F]";
 		$vardict["c3tmpf"] = "24 inch Soil Temperature [F]";
 		$vardict["c4tmpf"] = "50 inch Soil Temperature [F]";
 		$vardict["c2smv"] = "12 inch Soil Moisture [%]";
 		$vardict["c3smv"] = "24 inch Soil Moisture [%]";
 		$vardict["c4smv"] = "50 inch Soil Moisture [%]";
 	}
 
 $table = "<table class=\"table table-striped\">";
 while (list($key, $label) = each($vardict)){
	if (! array_key_exists($key, $json["last_ob"])){
		continue;
	}
 	if ($key == "local_valid") {
 		$t2 = date("d M Y, g:i A", strtotime($json["last_ob"][$key]));
 		$table .= '<tr><td><b>'. $label .'</b></td><td>'. $t2 .'</td></tr>';
 	}
 	else {
 		$table .= '<tr><td><b>'. $label .'</b></td><td>'. $json["last_ob"][$key].'</td></tr>';
 	} // End if
 } // End if
 $table .= "</table>";
 $table .= sprintf("<p>This data was provided by a ".
 		"<a href=\"%s\">JSON(P) webservice</a>. You can find ".
 		"<a href=\"/json/\">more JSON services</a>.</p>", $exturi);
}
 
$t->content = <<<EOF

<h3>Most Recent Observation</h3>

<p>This application displays the last observation received by the IEM
 from this site. The time stamp is in 
 <strong>{$metadata["tzname"]}</strong> timezone.</p>

{$table}

EOF;
$t->render('sites.phtml');
?>