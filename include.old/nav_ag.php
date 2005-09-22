<?php

  $temperature='<LI><a class="whlink" href="/sites/agriculture/temperature.php">Temperature</a></LI>';
  $precipitation='<LI><a class="whlink" href="/sites/agriculture/precipitation.php">Precipitation</a></LI>';
  $solar='<LI><a class="whlink" href="/sites/agriculture/solar.php">Solar/Degree Days/Winds</a></LI>';

  echo '<UL class="nav">';
  switch($current){
   case "temperature":
    $temperature='<LI><a class="alink">Temperature</a></LI>';
    break;
   case "precipitation":
    $precipitation='<LI><a class="alink">Precipitation</a></LI>';
    break;
   case "solar":
    $solar='<LI><a class="alink">Solar/Degree Days/Winds</a></LI>';
    break;
}  
    echo $temperature;
    echo $precipitation;
    echo $solar;
    echo '</UL>';
?>
