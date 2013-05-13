<?php
date_default_timezone_set('UTC');

include("../../include/wfoLocs.php");
include("../../include/cow.php");
include("../../include/database.inc.php");


echo "WFO,AREA_V,SIZE_R\n";
//while (list($key,$val) = each($wfos)){
 $cow = new Cow( iemdb("postgis") );
 $cow->setLimitTime( mktime(6,0,0,10,1,2007),  mktime(0,0,0,1,1,2012) );
 $cow->setHailSize(0.75);
 $cow->setLimitType( Array("TO") );
 $cow->setLimitLSRType( Array("TO") );
 $cow->setLimitWFO( Array("OAX") );
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
//}

?>
