<?php
include("../../config/settings.inc.php");
function dwp($tmpf, $relh){
  if ($relh == 0){
    return "";
  }
  $tmpk = 273.15 + ( 5.00/9.00 * ( $tmpf - 32.00) );
  $dwpk = $tmpk / (1+ 0.000425 * $tmpk * -( log10( $relh/100.0 )) );
  return round( ( $dwpk - 273.15 ) * 9.00/5.00 + 32 , 0);

}
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

        $kelo_logo = imagecreatefromgif ("kelo_back.gif");
        imagecopy($gif, $kelo_logo, 0, 0, 0, 0, 320, 320);

        $wlogo = imagecreatefromgif ("dirs/Wind_". strtolower($drct) .".gif");
        imagecolortransparent( $wlogo, $black);
        imagecopy($gif, $wlogo, 102, 41, 0, 0, 139, 139);

//imagettftext ( resource image, int size, int angle, int x, int y, int col, string fontfile, string text)

// imagefilledrectangle ( $gif, 167, 25, 264, 36, $black);
 ImageTTFText($gif, 12, 0, 67, 32, $white, $Font, $myOb->db["sname"] );

// RelHumidity
if ($relh == 0) $relh = "--";
else $relh += " %";
 $size = imagettfbbox(22, 0, $Font, $relh );
 $dx = abs($size[2] - $size[0]);
 $x0 = 215;
 $width = 74;
 $x_pad = ($width - $dx) / 2 ;
 ImageTTFText($gif, 20, 0, $x0 + $x_pad, 120, $white, $Font, $relh );

// Dew Point
if ($dwpf == "") $dwpf = "--";
 $size = imagettfbbox(22, 0, $Font, $dwpf);
 $dx = abs($size[2] - $size[0]);
 $x0 = 215;
 $width = 74;
 $x_pad = ($width - $dx) / 2 ;
 ImageTTFText($gif, 22, 0, $x0 + $x_pad, 165, $white, $Font, $dwpf );

// Feels Like
 $size = imagettfbbox(22, 0, $Font, $feel );
 $dx = abs($size[2] - $size[0]);
 $x0 = 215;
 $width = 74;
 $x_pad = ($width - $dx) / 2 ;
 ImageTTFText($gif, 22, 0, $x0 + $x_pad, 208, $white, $Font, $feel );

// Precip
 $size = imagettfbbox(22, 0, $Font, $pday );
 $dx = abs($size[2] - $size[0]);
 $x0 = 109;
 $width = 76;
 $x_pad = ($width - $dx) / 2 ;
 ImageTTFText($gif, 22, 0, $x0 + $x_pad , 210, $white, $Font, $pday );

// Gust
 $size = imagettfbbox(22, 0, $Font, $gustDir ."-".$gust);
 $dx = abs($size[2] - $size[0]);
 $x0 = 109;
 $width = 76;
 $x_pad = ($width - $dx) / 2 ;
 ImageTTFText($gif, 22, 0, $x0 + $x_pad, 172, $white, $Font, $gustDir ."-".$gust );

// Wind Speed
 $size = imagettfbbox(22, 0, $Font, $sped);
 $dx = abs($size[2] - $size[0]);
 $x0 = 125;
 $width = 45;
 $x_pad = ($width - $dx) / 2 ;
 ImageTTFText($gif, 22, 0, $x0 + $x_pad , 95, $white, $Font, $sped );


// Time
 ImageTTFText($gif, 13, 0, 150 , 237, $black, $Font, $time );

// TempF
 $size = imagettfbbox(22, 0, $Font, $tmpf);
 $dx = abs($size[2] - $size[0]);
 $x0 = 28;
 $width = 55;
 $x_pad = ($width - $dx) / 2 ;
 ImageTTFText($gif, 22, 0, $x0 + $x_pad, 205, $white, $Font, $tmpf );

// Max Tmpf
 $size = imagettfbbox(22, 0, $Font, $maxTemp);
 $dx = abs($size[2] - $size[0]);
 $x0 = 28;
 $width = 55;
 $x_pad = ($width - $dx) / 2 ;
 ImageTTFText($gif, 22, 0, $x0 + $x_pad, 95, $white, $Font, $maxTemp );

// Min Tmpf
 $size = imagettfbbox(22, 0, $Font, $minTemp);
 $dx = abs($size[2] - $size[0]);
 $x0 = 28;
 $width = 55;
 $x_pad = ($width - $dx) / 2 ;
 ImageTTFText($gif, 22, 0, $x0 + $x_pad, 145, $white, $Font, $minTemp );


header("content-type: image/png");
header("Expires: Mon, 26 Jul 1997 05:00:00 GMT");    // Date in the past
header("Last-Modified: " . gmdate("D, d M Y H:i:s") . " GMT"); 
header("Cache-Control: no-store, no-cache, must-revalidate");  // HTTP/1.1
header("Cache-Control: post-check=0, pre-check=0", false);
header("Pragma: no-cache");                          // HTTP/1.0
ImagePng($gif);
ImageDestroy($gif);
?>
