<?php
date_default_timezone_set('UTC');

include("../../include/cow.php");
include("../../include/database.inc.php");
include_once "../../include/network.php";

$nt = new NetworkTable("WFO");

$wfp = fopen("warnings.csv", "w");
$lfp = fopen("lsrs.csv", "w");
fwrite($lfp, "WFO,UTC_VALID,UTC_HOUR,WARNED,LON,LAT\n");

while (list($key,$val) = each($nt->table)){
 $cow = new Cow(pg_connect("dbname=postgis host=localhost port=5555 user=nobody"));
 $cow->setLimitTime( mktime(6,0,0,1,1,2008),  mktime(6,0,0,12,31,2010) );
 $cow->setHailSize(0.75);
 $cow->setLimitType( Array("TO") );
 $cow->setLimitLSRType( Array("TO") );
 $cow->setLimitWFO( Array($key) );
 $cow->milk();

 //Iterate over the warnings
 reset($cow->warnings);
 while( list($k, $warn) = each($cow->warnings)){
 	fwrite($wfp, sprintf("%s,%s,%s,%s,%.2f,%.2f,%.3f\n", $warn["wfo"],
 			date("Y-m-d H:i", $warn["sts"]), date("H", $warn["sts"]),
 			$warn["verify"] ? "Y": "N", $warn["lon0"],
 			$warn["lat0"], $warn["parea"]));
 }

 reset($cow->lsrs);
 while(list($k, $lsr) = each($cow->lsrs)){
 	fwrite($lfp, sprintf("%s,%s,%s,%s,%.2f,%.2f\n", $lsr["wfo"],
 			date("Y-m-d H:i", $lsr["ts"]),
 			date("H", $lsr["ts"]),
 			$lsr["warned"] ? "Y": "N", $lsr["lon0"],
 			$lsr["lat0"]));
 }
}

fclose($wfp);
fclose($lfp);
?>