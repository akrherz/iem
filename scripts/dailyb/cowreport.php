<?php
/* Generate some cow statistics! */
$sts = mktime(0,0,0,date("m", time() - 86400),date("d", time() - 86400),
              date("Y", time() - 86400) );
$ets = mktime(0,0,0,date("m"),date("d"),date("Y"));

include("../../include/cow.php");
include("../../include/database.inc.php");
$cow = new Cow( iemdb("postgis") );
$cow->setLimitTime( $sts, $ets );
$cow->setHailSize(1.0);
$cow->setLimitType( Array("TO","SV") );
$cow->setLimitLSRType( Array("TO","SV") );
$cow->milk();

if (sizeof($cow->warnings) == 0){ echo "No Warnings Issued\n"; die(); }

echo sprintf("SVR+TOR Warnings Issued: %s Verified: %s  [%.1f %%]\n", 
     sizeof($cow->warnings), $cow->computeWarningsVerified(),
     $cow->computeWarningsVerifiedPercent() );
echo sprintf("Reduction of Size Versus County Based     [%.1f %%]\n",
     $cow->computeSizeReduction() );
echo sprintf("Average Perimeter Ratio                   [%.1f %%]\n",
     $cow->computeAveragePerimeterRatio() );
echo sprintf("Percentage of Warned Area Verified (15km) [%.1f %%]\n",
     $cow->computeAreaVerify() );
echo sprintf("Average Storm Based Warning Size          [%.0f sq km]\n",
     $cow->computeAverageSize() );
echo sprintf("Probability of Detection(higher is better)[%.2f]\n",
     $cow->computePOD() );
echo sprintf("False Alarm Ration (lower is better)      [%.2f]\n",
     $cow->computeFAR() );
echo sprintf("Critical Success Index (higher is better) [%.2f]\n",
     $cow->computeCSI() );

?>
