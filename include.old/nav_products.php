<?php

  echo '<tr><td class="prodnav"><TABLE class="nav">';
  echo '<tr><td class="hlink"><br /><a class="whlink" href="/sites/products/products.php">IEM Products</a></td></tr>';

  $agriculture='<tr><td class="llink"><br /><a class="whlink" href="/sites/agriculture/temperature.php">Agriculture</a><br /></td></tr>';
  $aviation='<tr><td class="llink"><br /><a class="whlink" href="/sites/aviation/temperature.php">Aviation</a><br /></td></tr>';
  $hydrology='<tr><td class="llink"><br /><a class="whlink" href="/sites/hydrology/precipitation.php">Hydrology</a><br /></td></tr>';
  $severe='<tr><td class="llink"><br /><a class="whlink" href="/sites/severe/temperature.php">Severe Storms</a><br /><br /></td></tr>';

  switch($product){
   case "top":
    echo $agriculture;
    echo $aviation;
    echo $hydrology;
    echo $severe;
    break;
   case "agriculture":
    $agriculture='<tr><td class="llink"><br /><a class="whlink">Agriculture</a>';
    echo $agriculture;
    include("../../include/nav_ag.php");
    echo '</td></tr>';
    echo $aviation;
    echo $hydrology;
    echo $severe;
    break;
   case "aviation":
    echo $agriculture;
    $aviation='<tr><td class="llink"><br /><a class="whlink">Aviation</a>';
    echo $aviation;
    include("../../include/nav_aviation.php");
    echo '</td></tr>';
    echo $hydrology;
    echo $severe;
    break;
   case "hydrology":
    echo $agriculture;
    echo $aviation;
    $hydrology='<tr><td class="llink"><br /><a class="whlink">Hydrology</a>';
    echo $hydrology;
    include("../../include/nav_hydro.php");
    echo '</td></tr>';
    echo $severe;
    break;
   case "severe":
    echo $agriculture;
    echo $aviation;
    echo $hydrology;
    $severe='<tr><td class="llink"><a class="whlink">Severe Storms</a>';
    echo $severe;
    include("../../include/nav_severe.php");
    echo '</td></tr>';
    break;

}  
    echo '</TABLE></TD>';
?>
