<?php

  $precipitation='<LI><a class="whlink" href="/sites/hydrology/precipitation.php">Precipitation</a></LI>';
  $soils='<LI><a class="whlink" href="/sites/hydrology/soil.php">Soil</a></LI>';
  $atmosphere='<LI><a class="whlink" href="/sites/hydrology/atmophere.php">Atmosphere</a></LI>';

  echo '<UL>';
  switch($current){
   case "precipitation":
    $precipitation='<LI><a class="alink">Precipitation</a></LI>';
    break;
   case "soils":
    $soils='<LI><a class="alink">Soils</a></LI>';
    break;
   case "atmosphere":
    $atmosphere='<LI><a class="alink">Atmosphere</a></LI>';
    break;
}  
    echo $precipitation;
    echo $soils;
    echo $atmosphere;
    echo '</UL>';
?>
