<?php 
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");

include("setup.php");

    $current="parms";
    $TITLE = "IEM | Current Data";
    include("$rootpath/include/header.php"); 
    include("$rootpath/include/nav_site.php");

?><br>
<div class="text">
<h3 class="subtitle">Parameters measured by station:</h3>
           <UL>
<?php
$paramDict = Array("tmpf" => "Temperature", "dwpf" => "Dew Point",
  "drct" => "Wind Direction", "sknt" => "Wind Speed",
  "p01i" => "Precipitation", "vsby" => "Visibility",
  "ceil" => "Cloud Ceiling and Coverage", "pmsl" => "Pressure", 
  "srad" => "Solar Radiation", "pave" => "Pavement Temperature",
  "subc" => "Sub-Pavement Temperature", "snow" => "Snowfall");

$tokens = split("," , $row["params"] );
while( list($i) = each($tokens) ){
  echo "<LI>" . $paramDict[ $tokens[$i]] . "</LI>";
}
?>
 	 </UL></div>
<?php include("$rootpath/include/footer.php"); ?>
