<?
function dwp($tmpf, $relh){
  if ($relh == 0){
    return "";
  }
  $tmpk = 273.15 + ( 5.00/9.00 * ( $tmpf - 32.00) );
  $dwpk = $tmpk / (1+ 0.000425 * $tmpk * -( log10( $relh/100.0 )) );
  return round( ( $dwpk - 273.15 ) * 9.00/5.00 + 32 , 0);

}
include("../../config/settings.inc.php");
include("$rootpath/include/network.php");
$nt = new NetworkTable('KIMT');
$cities = $nt->table;
include("$rootpath/include/mlib.php");
include("$rootpath/include/iemaccess.php");
include("$rootpath/include/iemaccessob.php");
$station = isset($_GET["station"]) ? substr($_GET["station"],0,5) : 'SFMM5';
$iemdb = new IEMAccess();
$myOb = $iemdb->getSingleSite($station);
//print_r($myOb);
          $tmpf = $myOb->db["tmpf"];
          $relh = $myOb->db["relh"];
          $alti = $myOb->db["pres"];
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
	$Font = '/mesonet/data/gis/static/fonts/kimt.ttf';

	$gif = ImageCreateTrueColor($width,$height);

//int imagecopy ( resource dst_im, resource src_im, int dst_x, int dst_y, int src_x, int src_y, int src_w, int src_h)

	$black = ImageColorAllocate($gif,0,0,0);
	$white = ImageColorAllocate($gif,250,250,250);
	$green = ImageColorAllocate($gif, 0, 255, 0);
	$yellow = ImageColorAllocate($gif, 255, 255, 120);
	$red = ImageColorAllocate($gif, 200, 12, 13);
	$blue = ImageColorAllocate($gif, 0, 0, 255);
	$grey = ImageColorAllocate($gif, 110, 110, 110);
	
	//ImageFilledRectangle($gif,2,2, $width, $height, $grey);
	//ImageFilledRectangle($gif,1,1, $width -2 , $height -2, $white);

  $kcci_logo = @imagecreatefromjpeg("kimt320.jpg");
  imagecopy($gif, $kcci_logo, 0, 0, 0, 0, 320, 320);
  
  $wlogo = @imagecreatefromgif ("dirs/Wind_". strtolower($drct) .".gif");
  imagecolortransparent( $wlogo, $black);
  imagecopy($gif, $wlogo, 92, 130, 0, 0, 100, 100);


 //imagefilledrectangle ( $gif, 120, 22, 320, 36, $white);
 ImageTTFText($gif, 12, 0, 125 , 34, $red, $Font, strtoupper($cities[$station]["name"]) );

 // Box to hold current dew Point!
// imagerectangle ( $gif, 10, 40, 40, 60, $black);
// imagefilledrectangle ( $gif, 11, 41, 39, 59, $blue);
// ImageTTFText($gif, 12, 0, 11 , 55, $white, "./kcci.ttf", $dwpf );
 
// RelHumidity
 $size = imagettfbbox(16, 0, $Font, $relh ." %");
 $dx = abs($size[2] - $size[0]);
 $x0 = 30;
 $width = 74;
 $x_pad = ($width - $dx) / 2 ;
 ImageTTFText($gif, 16, 0, $x0 + $x_pad, 105, $black, $Font, $relh ." %");

// Dew Point
 $size = imagettfbbox(16, 0, $Font, $dwpf);
 $dx = abs($size[2] - $size[0]);
 $x0 = 30;
 $width = 74;
 $x_pad = ($width - $dx) / 2 ;
 ImageTTFText($gif, 16, 0, $x0 + $x_pad, 70, $black, $Font, $dwpf );

// Feels Like
 $size = imagettfbbox(16, 0, $Font, $feel );
 $dx = abs($size[2] - $size[0]);
 $x0 = 130;
 $width = 74;
 $x_pad = ($width - $dx) / 2 ;
 ImageTTFText($gif, 16, 0, $x0 + $x_pad, 92, $white, $Font, $feel );


// Altimeter
 $size = imagettfbbox(16, 0, $Font, $alti );
 $dx = abs($size[2] - $size[0]);
 $x0 = 30;
 $width = 74;
 $x_pad = ($width - $dx) / 2 ;
 ImageTTFText($gif, 16, 0, $x0 + $x_pad, 140, $black, $Font, $alti );

// Precip
 $size = imagettfbbox(16, 0, $Font, $pday );
 $dx = abs($size[2] - $size[0]);
 $x0 = 30;
 $width = 76;
 $x_pad = ($width - $dx) / 2 ;
 ImageTTFText($gif, 16, 0, $x0 + $x_pad , 175, $black, $Font, $pday );

// Gust
 $size = imagettfbbox(16, 0, $Font, $gustDir ."-".$gust);
 $dx = abs($size[2] - $size[0]);
 $x0 = 30;
 $width = 76;
 $x_pad = ($width - $dx) / 2 ;
 ImageTTFText($gif, 16, 0, $x0 + $x_pad, 210, $black, $Font, $gustDir ."-".$gust );

// Wind Speed
 $size = imagettfbbox(16, 0, $Font, $sped);
 $dx = abs($size[2] - $size[0]);
 $x0 = 115;
 $width = 45;
 $x_pad = ($width - $dx) / 2 ;
 ImageTTFText($gif, 16, 0, $x0 + $x_pad , 185, $white, $Font, $sped );


// Time
 ImageTTFText($gif, 12, 0, 150 , 235, $white, $Font, $time );

// TempF
 $size = imagettfbbox(22, 0, $Font, $tmpf);
 $dx = abs($size[2] - $size[0]);
 $x0 = 115;
 $width = 55;
 $x_pad = ($width - $dx) / 2 ;
 ImageTTFText($gif, 22, 0, $x0 + $x_pad, 72, $white, $Font, $tmpf );

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

 ImageTTFText($gif, 14, 0, 195, 70, $white, $Font, $maxTemp );
 ImageTTFText($gif, 14, 0, 195, 94, $white, $Font, $minTemp );

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
