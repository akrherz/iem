<?php
/*
 * Generate an image used for the COW output
 */
$ae = isset($_GET["ae"])? $_GET["ae"] : "AAA";
$aw = isset($_GET["aw"])? $_GET["aw"] : "AAA";
$b = isset($_GET["b"])? $_GET["b"] : "BBB";
$c = isset($_GET["c"])? $_GET["c"] : "CCC";
$d = isset($_GET["d"])? $_GET["d"] : "DDD";

function ImageRectangleWithRoundedCorners(&$im, $x1, $y1, $x2, $y2, $radius, $color) {
	// draw rectangle without corners
	imagefilledrectangle($im, $x1+$radius, $y1, $x2-$radius, $y2, $color);
	imagefilledrectangle($im, $x1, $y1+$radius, $x2, $y2-$radius, $color);
	// draw circled corners
	imagefilledellipse($im, $x1+$radius, $y1+$radius, $radius*2, $radius*2, $color);
	imagefilledellipse($im, $x2-$radius, $y1+$radius, $radius*2, $radius*2, $color);
	imagefilledellipse($im, $x1+$radius, $y2-$radius, $radius*2, $radius*2, $color);
	imagefilledellipse($im, $x2-$radius, $y2-$radius, $radius*2, $radius*2, $color);
}
function imagettftextalign($image, $size, $angle, $x, $y, $color, $font, $text, $alignment='L') {
  
   //check width of the text
   $bbox = imagettfbbox ($size, $angle, $font, $text);
   $textWidth = $bbox[2] - $bbox[0];
   switch ($alignment) {
       case "R":
           $x -= $textWidth;
           break;
       case "C":
           $x -= $textWidth / 2;
           break;
   }
      
   //write text
   imagettftext ($image, $size, $angle, $x, $y, $color, $font, $text);

}

/* Make fancy chart! */
$width = 130;
$height = 122;
$font = "/usr/share/fonts/liberation-serif/LiberationSerif-Bold.ttf";

$png = ImageCreate($width,$height);

$white = ImageColorAllocate($png,255,255,255);
$black = ImageColorAllocate($png,0,0,0);
$green = ImageColorAllocate($png, 0, 255, 0);
$blue = ImageColorAllocate($png, 0,0,255);
$red = ImageColorAllocate($png, 255,0,0);
$grey = ImageColorAllocate($png, 220, 220, 220);

/* Draw the box! */
$margin_left = 40;
$margin_right = 4;
$margin_top = 40;
$margin_bottom = 4;
ImageRectangleWithRoundedCorners($png, $margin_left,$margin_top,$width-$margin_right,$height-$margin_bottom,10,$black);
ImageRectangleWithRoundedCorners($png, $margin_left+4,$margin_top+4,$width-$margin_right-4,$height-$margin_bottom-4,10,$white);

$boxcenterx = $margin_left + (($width-$margin_right-$margin_left)/2);
$boxcentery = $margin_top + (($height-$margin_top-$margin_bottom)/2);
$boxwidth = $width-$margin_left-$margin_right;
$boxheight = $height-$margin_top-$margin_bottom;

ImageLine($png, $boxcenterx, $margin_top, $boxcenterx, $height-$margin_bottom,$black);
ImageLine($png,$margin_left, $boxcentery, $width-$margin_right, $boxcentery,$black);


ImageTTFText($png, 12, 90, 14 , $height-2, $blue, $font, "Observation");
ImageTTFText($png, 14, 0, 25 , $boxcentery-10, $black, $font, "Y");
ImageTTFText($png, 14, 0, 25 , $boxcentery+25, $black, $font, "N");

ImageTTFText($png, 12, 0, $width-75 , 14, $red, $font, "Warning");
ImageTTFText($png, 14, 0, $boxcenterx-20 , 34, $black, $font, "Y");
ImageTTFText($png, 14, 0, $boxcenterx+10 , 34, $black, $font, "N");

/* Now we get fancy! */
ImageTTFTextAlign($png, 28, 0, $boxcenterx - ($boxwidth/4) , $boxcentery - 2, $grey, $font, "A", "C");
ImageTTFTextAlign($png, 28, 0, $boxcenterx + ($boxwidth/4) , $boxcentery - 2, $grey, $font, "B", 'C');
ImageTTFTextAlign($png, 28, 0, $boxcenterx - ($boxwidth/4) , $boxcentery + 30, $grey, $font, "C", 'C');
ImageTTFTextAlign($png, 28, 0, $boxcenterx + ($boxwidth/4) , $boxcentery + 30, $grey, $font, "D", 'C');

/* Finally plot! */
ImageTTFTextAlign($png, 14, 0, $boxcenterx - ($boxwidth/4) , $boxcentery - ($boxheight/4) + 2, $red, $font, $aw, 'C');
ImageTTFTextAlign($png, 14, 0, $boxcenterx - ($boxwidth/4) , $boxcentery - ($boxheight/4) + 18, $blue, $font, $ae, 'C');
ImageTTFTextAlign($png, 14, 0, $boxcenterx + ($boxwidth/4) , $boxcentery - ($boxheight/4) + 7, $black, $font, $b, 'C');
ImageTTFTextAlign($png, 14, 0, $boxcenterx - ($boxwidth/4) , $boxcentery + ($boxheight/4) + 7, $black, $font, $c, 'C');
ImageTTFTextAlign($png, 14, 0, $boxcenterx + ($boxwidth/4) , $boxcentery + ($boxheight/4) + 7, $black, $font, $d, 'C');


header("Content-type: image/png");
ImagePng($png);
ImageDestroy($png);
?>
