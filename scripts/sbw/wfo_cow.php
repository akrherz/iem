<?php
date_default_timezone_set('UTC');

include("../../include/cow.php");
include("../../include/database.inc.php");


echo "WFO,AREA_V,SIZE_R\n";
//while (list($key,$val) = each($wfos)){
 $cow = new Cow(pg_connect("dbname=postgis host=localhost port=5555 user=nobody") );
 $cow->setLimitTime( mktime(6,0,0,10,1,2007),  mktime(0,0,0,5,23,2016) );
 $cow->setHailSize(0.75);
 $cow->setLimitType( Array("TO") );
 $cow->setLimitLSRType( Array("TO") );
 $cow->setLimitWFO( Array("IND") );
 $cow->milk();

 echo sprintf("%s,%.1f,%.1f\n", $key, $cow->computeAreaVerify(),
	$cow->computeSizeReduction() );
 echo $cow->computeAveragePerimeterRatio();
 echo "\n";
 echo $cow->computePOD();
 echo "\n";
 echo $cow->computeFAR();
 echo "\n";
 echo $cow->computeCSI();
 echo "\n";
 echo $cow->computeSharedBorder();
 echo "\n";
 echo $cow->computeAverageSize();
 echo "\n";
 //}

?>