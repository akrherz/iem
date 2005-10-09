<?php

 /** 
  * Something simple to enable click interface on a PHP mapcript
  * application
  */
function click2geo($oextents, $click_x, $click_y, $imgsz_x, $imgsz_y, $zoom) {

  $arExtents = explode(",", $oextents);
  $ll_x = $arExtents[0];
  $ll_y = $arExtents[1];
  $ur_x = $arExtents[2];
  $ur_y = $arExtents[3];
//  print_r($arExtents);

  $dy = ($ur_y - $ll_y) / floatval($imgsz_y);
  $dx = ($ur_x - $ll_x) / floatval($imgsz_x);

  $centerX = ($click_x * $dx) + $ll_x ; 
  $centerY = $ur_y - ($click_y * $dy) ;

  if (intval($zoom) < 0)
    $zoom = -1 / intval($zoom) ; 

  $n_ll_x = $centerX - (($dx * $zoom) * ($imgsz_x / 2.00));
  $n_ur_x = $centerX + (($dx * $zoom) * ($imgsz_x / 2.00));
  $n_ll_y = $centerY - (($dy * $zoom) * ($imgsz_y / 2.00));
  $n_ur_y = $centerY + (($dy * $zoom) * ($imgsz_y / 2.00));

  return $n_ll_x .",". $n_ll_y .",". $n_ur_x .",". $n_ur_y ;
}
?>
