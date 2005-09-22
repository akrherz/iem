<?php
// Library for plot functions!

function mkclrbar($map, $imgObj, $c, $i) {
  $layer = $map->getLayerByName("singlebox");
  $white = $map->addColor(255, 255, 255); // 

  $p = ms_newRectObj();
  $p->setextent(10, 460, 50, 450);
  $c0 = $layer->getClass(0);
  $c0->set("color", $white);
  $p->draw($map, $layer, $imgObj, 0, "0");
  $p->free();

  
  $x = 10;
  $width = 40;
  for ($k=0;$k<9;$k++){
    $x = $x + $width;
    $p = ms_newRectObj();
    $p->setextent($x, 460, $x + $width, 450);
    $c0 = $layer->getClass(0);
    $c0->set("color", $c[$k]);
    $p->draw($map, $layer, $imgObj, 0, $i[$k]);
    $p->free();
  }
}


?>
