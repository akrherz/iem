<?php

  $temperature='<LI><a class="hlink" href="/sites/agriculture/temperature.php">Temperature</a></td></LI>';
  $moisture='<LI><a class="hlink" href="/sites/agriculture/moisture.php">Precipitation</a></td></LI>';
  $solar='<LI><a class="hlink" href="/sites/agriculture/solar.php">Solar/Degree Days/Winds</a></td></LI>';

  echo '<UL>';
  switch($current){
   case "temperature":
    $temperature='<LI><a class="alink">Temperature</a></LI>';
    break;
   case "moisture":
    $moisture='<LI><a class="alink">Moisture</a></LI>';
    break;
   case "solar":
    $solar='<LI><a class="alink">Solar/Degree Days/Winds</a></LI>';
    break;
}  
    echo $temperature;
    echo $moisture;
    echo $solar;
    echo '</UL>';
?>
