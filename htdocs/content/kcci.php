<?php
function dwp($tmpf, $relh){
  if ($relh == 0){
    return "";
  }
  $tmpk = 273.15 + ( 5.00/9.00 * ( $tmpf - 32.00) );
  $dwpk = $tmpk / (1+ 0.000425 * $tmpk * -( log10( $relh/100.0 )) );
  return round( ( $dwpk - 273.15 ) * 9.00/5.00 + 32 , 0);

}
include("../../config/settings.inc.php");
include("$rootpath/include/snet_locs.php");
include("$rootpath/include/mlib.php");
include("$rootpath/include/iemaccess.php");
include("$rootpath/include/iemaccessob.php");
$station = isset($_GET["station"]) ? substr($_GET["station"],0,5) : 'SSAS2';
$iemdb = new IEMAccess();
$myOb = $iemdb->getSingleSite($station);
//print_r($myOb);
          $tmpf = $myOb->db["tmpf"];
          $relh = $myOb->db["relh"];
          $alti = $myOb->db["alti"];
          $pday = $myOb->db["pday"];
          $drct = drct2txt($myOb->db["drct"]);
          $gust = round($myOb->db["max_gust"] * 1.15,0);
          $sped = round($myOb->db["sknt"] * 1.15,0);
          $feel = feels_like($tmpf, $relh, $sped);
          $time = "Valid: ". date("d M Y h:i a", $myOb->db["ts"]);
          $dwpf = $myOb->db["dwpf"];

          $gustDir = drct2txt($myOb->db["max_drct"]);
          $maxTemp =  $myOb->db["max_tmpf"];

          $minTemp = $myOb->db["min_tmpf"];


	$width = 320;
	$height = 240;
	$Font = '/mesonet/data/gis/static/fonts/kcci.ttf';

	$gif = ImageCreate($width,$height);

//int imagecopy ( resource dst_im, resource src_im, int dst_x, int dst_y, int src_x, int src_y, int src_w, int src_h)

	$black = ImageColorAllocate($gif,0,0,0);
	$white = ImageColorAllocate($gif,250,250,250);
	$green = ImageColorAllocate($gif, 0, 255, 0);
	$yellow = ImageColorAllocate($gif, 255, 255, 120);
	$red = ImageColorAllocate($gif, 148, 52, 53);
	$blue = ImageColorAllocate($gif, 0, 0, 255);
	$grey = ImageColorAllocate($gif, 110, 110, 110);
	
	ImageFilledRectangle($gif,2,2, $width, $height, $grey);
	ImageFilledRectangle($gif,1,1, $width -2 , $height -2, $white);

        $kcci_logo = @imagecreatefromgif ("Ames320.gif");
        imagecopy($gif, $kcci_logo, 0, 0, 0, 0, 320, 320);

        $wlogo = @imagecreatefromgif ("dirs/Wind_". strtolower($drct) .".gif");
        imagecolortransparent( $wlogo, $black);
        imagecopy($gif, $wlogo, 96, 23, 0, 0, 139, 139);

//imagettftext ( resource image, int size, int angle, int x, int y, int col, string fontfile, string text)

// imagefilledrectangle ( $gif, 167, 25, 264, 36, $black);
 ImageTTFText($gif, 10, 0, 169 , 34, $white, $Font, strtoupper(substr($cities['KCCI'][$station]["short"], 0, 16)) );

 // Box to hold current dew Point!
// imagerectangle ( $gif, 10, 40, 40, 60, $black);
// imagefilledrectangle ( $gif, 11, 41, 39, 59, $blue);
// ImageTTFText($gif, 12, 0, 11 , 55, $white, "./kcci.ttf", $dwpf );
 
// RelHumidity
 $size = imagettfbbox(22, 0, $Font, $relh ." %");
 $dx = abs($size[2] - $size[0]);
 $x0 = 206;
 $width = 74;
 $x_pad = ($width - $dx) / 2 ;
if ($relh > 0){
 ImageTTFText($gif, 20, 0, $x0 + $x_pad, 125, $white, $Font, $relh ." %");
}

// Dew Point
 $size = imagettfbbox(22, 0, $Font, $dwpf);
 $dx = abs($size[2] - $size[0]);
 $x0 = 204;
 $width = 74;
 $x_pad = ($width - $dx) / 2 ;
if ($dwpf > -99){
 ImageTTFText($gif, 22, 0, $x0 + $x_pad, 165, $white, $Font, $dwpf );
}

// Feels Like
 $size = imagettfbbox(22, 0, $Font, $feel );
 $dx = abs($size[2] - $size[0]);
 $x0 = 204;
 $width = 74;
 $x_pad = ($width - $dx) / 2 ;
if ($feel > -99){
 ImageTTFText($gif, 22, 0, $x0 + $x_pad, 205, $white, $Font, $feel );
}
// Precip
 $size = imagettfbbox(22, 0, $Font, $pday );
 $dx = abs($size[2] - $size[0]);
 $x0 = 106;
 $width = 76;
 $x_pad = ($width - $dx) / 2 ;
 ImageTTFText($gif, 22, 0, $x0 + $x_pad , 205, $white, $Font, $pday );

// Gust
 $size = imagettfbbox(22, 0, $Font, $gustDir ."-".$gust);
 $dx = abs($size[2] - $size[0]);
 $x0 = 106;
 $width = 76;
 $x_pad = ($width - $dx) / 2 ;
 ImageTTFText($gif, 22, 0, $x0 + $x_pad, 165, $white, $Font, $gustDir ."-".$gust );

// Wind Speed
 $size = imagettfbbox(22, 0, $Font, $sped);
 $dx = abs($size[2] - $size[0]);
 $x0 = 122;
 $width = 45;
 $x_pad = ($width - $dx) / 2 ;
 ImageTTFText($gif, 22, 0, $x0 + $x_pad , 80, $white, $Font, $sped );


// Time
 ImageTTFText($gif, 12, 0, 150 , 235, $white, $Font, $time );

// TempF
 $size = imagettfbbox(22, 0, $Font, $tmpf);
 $dx = abs($size[2] - $size[0]);
 $x0 = 32;
 $width = 55;
 $x_pad = ($width - $dx) / 2 ;
if ($tmpf > -99){
 ImageTTFText($gif, 22, 0, $x0 + $x_pad, 205, $white, $Font, $tmpf );
}

// Time to do the rotation!!!
//              x   y    x   y    x   y
$windDirs = Array(
  "N" => Array(140, 50, 145, 40, 150, 50),
  "S" => Array(140, 92, 145,102, 150, 92),
  "W" => Array(124, 66, 124, 76, 114, 71),
  "E" => Array(176, 71, 166, 76, 166, 66),
  "NNE" => Array(150, 50, 157, 54, 156, 44)
   );

// imagefilledpolygon($gif, $windDirs["N"], 3, $yellow);
// imagefilledpolygon($gif, $windDirs["S"], 3, $yellow);
// imagefilledpolygon($gif, $windDirs["W"], 3, $yellow);
// imagefilledpolygon($gif, $windDirs["E"], 3, $yellow);
// imagefilledpolygon($gif, $windDirs["NNE"], 3, $yellow);

// imagepolygon($gif, $windDirs["N"], 3, $black);
// imagepolygon($gif, $windDirs["S"], 3, $black);
// imagepolygon($gif, $windDirs["W"], 3, $black);
// imagepolygon($gif, $windDirs["E"], 3, $black);
// imagepolygon($gif, $windDirs["NNE"], 3, $black);

// Time to do temperature
 $leftside = 57;
 $rightside = 61;
 $maxT_y = 47;
 $minT_y = 147;
 $maxT = 120;
 $minT = -20;

 $pixels = ($minT_y - $maxT_y);
 $x = $tmpf + 20; // Adjust for -20 start
 $height = $pixels * ($x / ($maxT - $minT) ) ;
 $maxLineHeight = $pixels * (($maxTemp + 20)/ ($maxT - $minT) ) ;
 $minLineHeight = $pixels * (($minTemp + 20)/ ($maxT - $minT) ) ;


if ($tmpf > -99){
 imagefilledrectangle ( $gif, $leftside, $minT_y - $height, $rightside, $minT_y, $red);

}
 imagefilledrectangle( $gif, $leftside -50, $minT_y - $maxLineHeight -1, 
                  $rightside +2, $minT_y - $maxLineHeight, $black);
 imagefilledrectangle( $gif, $leftside -50, $minT_y - $minLineHeight -1, 
                  $rightside +2, $minT_y - $minLineHeight, $black);
// MAX
 imagefilledrectangle($gif, $leftside - 50, $minT_y - $maxLineHeight - 1 - 20,
                  $leftside - 30, $minT_y - $maxLineHeight - 1, $red);
 ImageTTFText($gif, 16, 0, $leftside - 50 + 2 , $minT_y - $maxLineHeight -1 -2, 
     $white, $Font, $maxTemp );
 ImageTTFText($gif, 10, 0, $leftside - 50 + 1 , $minT_y - $maxLineHeight -1 -20 -2, 
     $white, $Font, "MAX");

// MIN
 imagefilledrectangle($gif, $leftside - 50, $minT_y - $minLineHeight - 1 ,
                  $leftside - 30, $minT_y - $minLineHeight - 1 + 20, $blue);
 ImageTTFText($gif, 16, 0, $leftside - 50 + 2 , $minT_y - $minLineHeight - 1 +20 -2, 
     $white, $Font, $minTemp );
 ImageTTFText($gif, 10, 0, $leftside - 50 + 1 , $minT_y - $minLineHeight -1 +20 +10, 
     $white, $Font, "MIN");

//	$size = imagettfbbox(12, 0, $Font, $Scities[$site]["city"]);
//	$dx = abs($size[2] - $size[0]);
//	$dy = abs($size[5] - $size[3]);
//	$x_pad = ($width - $dx) / 2 ;
//  ImageTTFText($gif, 8, 0, 10 , 85, $red, "./kcci.tff",$Scities[$site]["city"] );

	header("content-type: image/png");
header("Expires: Mon, 26 Jul 1997 05:00:00 GMT");    // Date in the past
header("Last-Modified: " . gmdate("D, d M Y H:i:s") . " GMT"); 
header("Cache-Control: no-store, no-cache, must-revalidate");  // HTTP/1.1
header("Cache-Control: post-check=0, pre-check=0", false);
header("Pragma: no-cache");                          // HTTP/1.0
	ImagePng($gif);
	ImageDestroy($gif);
?>
