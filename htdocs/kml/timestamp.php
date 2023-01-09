<?php
// dynamic image generation of a timestamp
$label = isset($_REQUEST["label"]) ? substr($_GET["label"], 0, 120) : "No \$label set";
$font_size = isset($_GET["font_size"]) ? intval($_GET["font_size"]) : 15;

$Font = '/mesonet/data/gis/static/fonts/arialbd.ttf';

$size = imagettfbbox($font_size, 0, $Font, $label);
$dx = abs($size[2] - $size[0]);
$dy = abs($size[5] - $size[3]);
$x_pad = 30;
$y_pad = 10;
$width = $dx + $x_pad;
$height = $dy + $y_pad;

$gif = ImageCreate($width + 10, $height);
$white = ImageColorAllocate($gif, 250, 250, 250);
$black = ImageColorAllocate($gif, 0, 0, 0);
$red = ImageColorAllocate($gif, 250, 0, 0);
$grey = ImageColorAllocate($gif, 110, 110, 110);

ImageColorTransparent($gif, $white);

$xborder = (int) ($x_pad / 2) - 5;


//ImageTTFText($gif, $font_size, 0, (int) ($x_pad/2)+1, $dy + (int) ($y_pad/2), $grey, $Font, $label);
ImageTTFText($gif, $font_size, 0, (int) ($x_pad / 2), $dy + (int) ($y_pad / 2) - 1, $black, $Font, $label);

header("content-type: image/png");
ImagePng($gif);
ImageDestroy($gif);
