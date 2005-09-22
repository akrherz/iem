<?php

  echo '<TABLE class="page" style="background-color: #DDDDDD;">
         <tr>';
  $precipitation='<td class="hlink"><a class="hlink" href="/sites/hydrology/precipitation.php">Precipitation</a></td>';
  $soils='<td class="hlink"><a class="hlink" href="/sites/hydrology/soil.php">Soil</a></td>';
  $atmosphere='<td class="hlink"><a class="hlink" href="/sites/hydrology/atmophere.php">Atmosphere</a></td>';

  switch($current){
   case "precipitation":
    $precipitation='<td class="hlink"><a class="alink">Precipitation</a></td>';
    break;
   case "soils":
    $soils='<td class="hlink"><a class="alink">Soils</a></td>';
    break;
   case "atmosphere":
    $atmosphere='<td class="hlink"><a class="alink">Atmosphere</a></td>';
    break;
}  
    echo '<td class="header">Options:</td>';
    echo $precipitation;
    echo '<th>|</th>';
    echo $soils;
    echo '<th>|</th>';
    echo $atmosphere;
    echo '</tr>';
    echo '<tr bgcolor="black"><td colspan="13"><img src="/icons/spacer.gif" height="1" border="0" width="1" ALT="Spacer"></td></tr>';
    echo '</TABLE>';
?>
