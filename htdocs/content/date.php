<?php
require_once "../../config/settings.inc.php";
require_once "../../include/forms.php";
$width = 87;
$height = 60;
$Font = '/mesonet/data/gis/static/fonts/handgotn.ttf';
$year = get_int404("year", date("Y"));
$month = get_int404("month", date("m"));
$day = get_int404("day", date("d"));
$ts = new DateTime("{$year}-{$month}-{$day}");

$gif = ImageCreate($width, $height);

$black = ImageColorAllocate($gif, 0, 0, 0);
$white = ImageColorAllocate($gif, 250, 250, 250);
$green = ImageColorAllocate($gif, 0, 255, 0);
$red = ImageColorAllocate($gif, 255, 0, 0);
$grey = ImageColorAllocate($gif, 110, 110, 110);

ImageFilledRectangle($gif, 2, 2, $width, $height, $grey);
ImageFilledRectangle($gif, 1, 1, $width - 2, $height - 2, $white);

$size = imagettfbbox(12, 0, $Font, $ts->format("M"));
$dx = abs($size[2] - $size[0]);
$dy = abs($size[5] - $size[3]);
$x_pad = ($width - $dx) / 2;
ImageTTFText($gif, 12, 0, $x_pad, 15, $black, $Font, $ts->format("M"));

$size = imagettfbbox(20, 0, $Font, $ts->format("d"));
$dx = abs($size[2] - $size[0]);
$dy = abs($size[5] - $size[3]);
$x_pad = ($width - $dx) / 2;
ImageTTFText($gif, 18, 0, $x_pad, 35, $red, $Font, $ts->format("d"));

$size = imagettfbbox(15, 0, $Font, $ts->format("Y"));
$dx = abs($size[2] - $size[0]);
$dy = abs($size[5] - $size[3]);
$x_pad = ($width - $dx) / 2;
ImageTTFText($gif, 14, 0, $x_pad, 55, $black, $Font, $ts->format("Y"));

header("content-type: image/png");
ImagePng($gif);
ImageDestroy($gif);
