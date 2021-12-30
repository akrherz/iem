<?php 
 require_once "../../config/settings.inc.php";
 require_once "../../include/database.inc.php";
 require_once "setup.php";
 require_once "../../include/myview.php";
 require_once "../../include/mlib.php";

 $t = new MyView();
 $t->refresh = 60;
 $t->title = "Latest Observation";
 $t->sites_current = "current";
 $SPECIAL = Array(
	 'OT0013' => 'MCFC-001',
	 'OT0014' => 'MCFC-002',
	 'OT0015' => 'MCFC-003');
$LOOKUP = Array(
	'OT0013' => 'scranton',
	'OT0014' => 'carroll',
	'OT0015' => 'jefferson'
);
function fmt($val, $varname){
	if ($varname == 'altimeter[in]'){
		return sprintf("%.2f", $val); 
	}
	return $val;
}

 if (strpos($network, "_DCP") || strpos($network, "_COOP") ){
 	$table = '<p>This station reports observations in SHEF format.  The following
 			is a table of the most recent reports from this site identifier for
 			each reported SHEF variable';
 	$mesosite = iemdb('mesosite');
 	$shefcodes = Array();
 	$rs = pg_query($mesosite, "SELECT * from shef_physical_codes");
 	for($i=0;$row=pg_fetch_assoc($rs);$i++){
 		$shefcodes[ $row['code'] ] = $row['name'];
 	}
 	$durationcodes = Array();
 	$rs = pg_query($mesosite, "SELECT * from shef_duration_codes");
 	for($i=0;$row=pg_fetch_assoc($rs);$i++){
 		$durationcodes[ $row['code'] ] = $row['name'];
 	}
 	$extremumcodes = Array();
 	$rs = pg_query($mesosite, "SELECT * from shef_extremum_codes");
 	for($i=0;$row=pg_fetch_assoc($rs);$i++){
 		$extremumcodes[ $row['code'] ] = $row['name'];
 	}
    $arr = Array(
        "station" => $station,
    );
 	$jobj = iemws_json("last_shef.json", $arr);
     $exturi = sprintf(
         "https://mesonet.agron.iastate.edu/api/1/last_shef.json?".
         "station=%s",
         $station,
     );
	$table .= <<<EOM
<table class="table table-striped">
<thead>
    <tr><th>Physical Code</th><th>Duration</th><th>Type</th>
	<th>Source</th><th>Extrenum</th><th>Valid</th><th>Value</th>
    <th>Product</th></tr>
</thead>
EOM;
     $localtz = new DateTimeZone($metadata["tzname"]);
     $utctz = new DateTimeZone("UTC");
    $baseprodvalid = new DateTime("now", $utctz);
    $baseprodvalid->modify("-5 days");
 	foreach($jobj["data"] as $bogus => $row){
 		$depth = "";
 		if ($row["depth"] > 0){
 			$depth = sprintf("%d inch", $row["depth"]);
 		}
         $valid = new DateTime($row["utc_valid"], $utctz);
         $valid->setTimeZone($localtz);
        $plink = "N/A";
        if ($valid > $baseprodvalid){
            if (! is_null($row["product_id"])){
                $plink = sprintf(
                    '<a href="/p.php?pid=%s">Source Text</a>',
                    $row["product_id"]
                );
            }
        }
 		$table .= sprintf(
            "<tr><td>[%s] %s %s</td><td>[%s] %s</td><td>%s</td>".
            "<td>%s</td><td>[%s] %s</td><td>%s</td><td>%s</td><td>%s</td></tr>", 
 			$row["physical_code"], $shefcodes[$row["physical_code"]], $depth,
 			$row["duration"], $durationcodes[ $row["duration"] ],
            $row["type"], $row["source"], 
 			$row["extremum"] == 'Z'? '-': $row['extremum'] , $extremumcodes[ $row["extremum"] ],
 			$valid->format("M j, Y h:i A"), $row["value"], $plink);
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
 foreach($vardict as $key => $label){
    if (!array_key_exists("last_ob", $json) ||
            !array_key_exists($key, $json["last_ob"])){
		continue;
	}
 	if ($key == "local_valid") {
 		$t2 = date("d M Y, g:i A", strtotime($json["last_ob"][$key]));
 		$table .= '<tr><td><b>'. $label .'</b></td><td>'. $t2 .'</td></tr>';
 	}
 	else if ($key == "winddirection[deg]") {
		$table .= sprintf("<tr><td><b>%s</b></td><td>%s (%.0f degrees)</td></tr>",
			$label, drct2txt($json["last_ob"][$key]), $json["last_ob"][$key]);
	}
	else {
		 if (is_null($json["last_ob"][$key])) continue;
		 $table .= '<tr><td><b>'. $label .'</b></td>'.
		 '<td>'. fmt($json["last_ob"][$key], $key).'</td></tr>';
 	} // End if
 } // End if
 $table .= "</table>";
}

$table .= sprintf("<p>This data was provided by a ".
"<a href=\"%s\">JSON(P) webservice</a>. You can find ".
"<a href=\"/json/\">more JSON services</a>.</p>", $exturi);

$interface = $table;
if (array_key_exists($station, $SPECIAL)){
	$interface = <<<EOM
<h4>New Way Weather Network</h4>

<a class="btn btn-default" href="/sites/current.php?station=OT0013&network=OT">Scranton</a>
&nbsp;
<a class="btn btn-default" href="/sites/current.php?station=OT0014&network=OT">Carroll</a>
&nbsp;
<a class="btn btn-default" href="/sites/current.php?station=OT0015&network=OT">Jefferson</a>

<div class="row">
  <div class="col-md-6">
	{$table}
  </div>
  <div class="col-md-6">
	<h3>Latest Webcam Image</h3>
	<img src="/data/camera/stills/{$SPECIAL[$station]}.jpg"
	 class="img img-responsive">
	<br />View Recent Time Lapses:<br />
	<a href="/current/camlapse/#{$LOOKUP[$station]}_sunrise">Sunrise</a>,
	<a href="/current/camlapse/#{$LOOKUP[$station]}_morning">Morning</a>,
	<a href="/current/camlapse/#{$LOOKUP[$station]}_afternoon">Afternoon</a>,
	<a href="/current/camlapse/#{$LOOKUP[$station]}_sunset">Sunset</a>, and
	<a href="/current/camlapse/#{$LOOKUP[$station]}_day">All Day</a>
  </div>
</div>

EOM;
}

$t->content = <<<EOF

<h3>Most Recent Observation</h3>

<p>This application displays the last observation received by the IEM
 from this site. The time stamp is in 
 <strong>{$metadata["tzname"]}</strong> timezone.</p>

{$interface}

EOF;
$t->render('sites.phtml');
?>
