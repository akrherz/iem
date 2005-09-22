<?php

include('../include/currentOb.php');

$stData = currentOb("BNW");

$width = 150;
$height =100;
$Font = './kcci.ttf';

$gif = ImageCreate($width,$height);

$back = @imagecreatefromgif ("back1.gif");
imagecopy($gif, $back, 0, 0, 0, 0, 150, 100);

// Colors
$black = ImageColorAllocate($gif,0,0,0);
$blue = ImageColorAllocate($gif,0,0,255);
$white = ImageColorAllocate($gif,255,255,255);

$border = 5;
imagefilledrectangle($gif, $border, $border, $width - $border , $height - $border, $white);

$back = @imagecreatefromgif ("dotlogo.gif");
imagecopy($gif, $back, 30, $height - 28, 0, 2, 124, 30);

ImageTTFText($gif, 16, 0, 5, 20,
  $black, $Font, "Temp: ". intval($stData["tmpf"]) ." °F");

ImageTTFText($gif, 16, 0, 5, 40,
  $blue, $Font, "D.P. ". intval($stData["dwpf"]) ." °F");



header("content-type: image/png");
ImagePng($gif);
ImageDestroy($gif);
?>
