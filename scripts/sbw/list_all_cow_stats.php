<?php
date_default_timezone_set('UTC');

include("../../include/wfoLocs.php");
include("../../include/cow.php");
include("../../include/database.inc.php");

$lt = Array("F" => "Flash Flood", "T" => "Tornado", "D" => "Tstm Wnd Dmg", "H" => "Hail","G" => "Wind Gust", "W" => "Waterspout", "M" => "Marine Tstm Wnd");


while (list($key,$val) = each($wfos)){
	echo "Running for $key\n";

	$output = fopen("data/${key}.csv", 'w');

  fwrite($output, "WFO,YEAR,WARN_ID,ISSUE,EXPIRE,SBW_AREA,CNTY_AREA,PERIM_RATIO,AREAL_VERIF,LSR1_VALID,LSR1_TYPE,LSR1_MAG,LSR2_VALID,LSR2_TYPE,LSR2_MAG,LSR3_VALID,LSR3_TYPE,LSR3_MAG,LSR4_VALID,LSR4_TYPE,LSR4_MAG,LSR5_VALID,LSR5_TYPE,LSR5_MAG,\n");
  $cow = new Cow( iemdb("postgis") );
  $cow->setLimitTime( mktime(12,0,0,1,1,2005),  mktime(12,0,0,1,1,2013) );
  $cow->setHailSize(0.75);
  $cow->setLimitType( Array("TO","SV") );
  $cow->setLimitLSRType( Array("TO","SV") );
  $cow->setLimitWFO( Array($key) );
  $cow->milk();

  reset($cow->warnings);
  while( list($k, $warn) = each($cow->warnings)){
  	$carea = 0;
  	reset($warn["ugc"]);
  	while ( list($k,$v) = each($warn["ugc"])){
  		$carea += $cow->ugcCache[$v]["area"];
  	}
  	$bratio = "0";
  	if ($warn["perimeter"] > 0){
  		$bratio = $warn["sharedborder"] / $warn["perimeter"] * 100.0;
  	}
  	fwrite($output, sprintf("%s,%s,%s.%s,%s,%s,%.2f,%.2f,%.2f,%.2f,", $key, 
  	  gmdate("Y", $warn["sts"]), $warn["phenomena"], $warn["eventid"],
  	  date("m/d/Y H:i", $warn["sts"]),
  	  date("m/d/Y H:i", $warn["expire"]),
  	   $warn["parea"], $carea,
  	  $bratio, $warn["buffered"] / $warn["parea"] * 100.0));
  	// LSRs
  	reset($warn["lsrs"]);
  	while ( list($k,$lsrid) = each($warn["lsrs"])){
  		$lsr = $cow->lsrs[$lsrid];
  		fwrite($output, sprintf("%s,%s,%s,", gmdate("m/d/Y H:i", $lsr["ts"]),
  			$lt[$lsr["type"]], $lsr["magnitude"]));
  	}
  	fwrite($output, "\n");
  	
  }
  
   fclose($output);

   $output = fopen("data/${key}-LSR.csv", 'w');
   
   fwrite($output, "WFO,LSR_VALID,LSR_TYPE,LSR_MAG,\n");
   reset($cow->lsrs);
   while ( list($k,$lsr) = each($cow->lsrs)){
   		if ($lsr["warned"]) continue;

   	fwrite($output, sprintf("%s,%s,%s,%s,\n", $key, gmdate("m/d/Y H:i", $lsr["ts"]),
  			$lt[$lsr["type"]], $lsr["magnitude"]));
   }
   fclose($output);
   
   die();
}

?>
