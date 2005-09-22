<?php

include('../include/mlib.php');
include('../include/currentOb.php');
include('../include/awosLoc.php');

$station = "BNW";
$stData = currentOb($station);

$width = 175;
$height =100;
$Font = './arial.ttf';
$FontB = './arialbd.ttf';

$gif = ImageCreate($width,$height);

$back = @imagecreatefromgif ("back1.gif");
imagecopy($gif, $back, 0, 0, 0, 0, 150, 100);

// Colors
$black = ImageColorAllocate($gif,0,0,0);
$blue = ImageColorAllocate($gif,0,0,255);
$white = ImageColorAllocate($gif,255,255,255);
$red = ImageColorAllocate($gif,255,0,0);

$border = 5;
imagefilledrectangle($gif, $border, $border, $width - $border , $height - $border, $white);

$back = @imagecreatefromgif ("dotlogo.gif");
imagecopy($gif, $back, $width - 124, $height - 28, 0, 2, 124, 30);

ImageTTFText($gif, 12, 0, 5, 20,
  $blue, $Font, $Wcities[$station]["city"]);

ImageTTFText($gif, 12, 0, 5 + 1, $height - $border - 1,
  $red, $FontB, $station);

ImageTTFText($gif, 12, 0, 5, 35,
  $black, $Font, "Temp: ". intval($stData["tmpf"]) ." °F");

ImageTTFText($gif, 12, 0, 5, 50,
  $blue, $Font, "Dew P: ". intval($stData["dwpf"]) ." °F");

ImageTTFText($gif, 10, 0, 5, 70,
  $blue, $Font, "Wind is ". $stData["sknt"] ." knots from ". $stData["drct"]);


header("content-type: image/png");
ImagePng($gif);
ImageDestroy($gif);
?>
