<?php
date_default_timezone_set('UTC');

include("../../include/cow.php");
include("../../include/database.inc.php");
include_once "../../include/network.php";

$nt = new NetworkTable("WFO");


echo "WFO,AREA_V,SIZE_R\n";
while (list($key,$val) = each($nt->table)){
 $cow = new Cow(pg_connect("dbname=postgis host=iemdb user=nobody") );
 $cow->setLimitTime( mktime(6,0,0,1,1,2008),  mktime(6,0,0,12,31,2010) );
 $cow->setHailSize(0.75);
 $cow->setLimitType( Array("TO") );
 $cow->setLimitLSRType( Array("TO") );
 $cow->setLimitWFO( Array($key) );
 $cow->milk();

 echo sprintf("%s,%.1f,%.1f,", $key, $cow->computeAreaVerify(),
	$cow->computeSizeReduction() );
 echo $cow->computeAveragePerimeterRatio();
 echo ",";
 echo $cow->computePOD();
 echo ",";
 echo $cow->computeFAR();
 echo ",";
 echo $cow->computeCSI();
 echo ",";
 echo $cow->computeSharedBorder();
 echo ",";
 echo $cow->computeAverageSize();
 echo ",";
 echo $cow->computeWarningsVerified();
 echo ",";
 echo $cow->computeWarnedEvents();
 echo ",";
 echo $cow->computeUnwarnedEvents();
 echo ",";
 echo $cow->computeWarningsUnverified();
 echo "\n";
}

?>