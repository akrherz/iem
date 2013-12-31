<?php 
/* Generate Cheezy PIL image
 * 
 */
$pil = isset($_REQUEST["pil"]) ? substr($_REQUEST["pil"],0,6): 'AFDDMX';

// Try to get it from memcached
$memcache = new Memcache;
$memcache->connect('iem-memcached', 11211);
$val = $memcache->get("pil_${pil}.png");
if ($val){
	header("Content-type: image/png");
	die($val);
}
// Need to buffer the output so that we can save it to memcached later
ob_start();

$img = ImageCreate(85, 65);
$white = ImageColorAllocate($img,255,255,255);
$black = ImageColorAllocate($img,0,0,0);
ImageFilledRectangle($img,0,0, 85, 65, $white);
//$logo = imagecreatefrompng("../images/logo_small.png");
//imagecopy($img, $logo, 0, 0, 0, 0, 85, 65);
imagettftext($img, 24, 0, 5, 30, $black, 
	"/usr/share/fonts/liberation/LiberationMono-Bold.ttf", substr($pil,0,3));
imagettftext($img, 24, 0, 5, 60, $black,
"/usr/share/fonts/liberation/LiberationMono-Bold.ttf", substr($pil,3,3));

header("content-type: image/png");
ImagePng($img);
ImageDestroy($img);

$memcache->set("pil_${pil}.png", ob_get_contents(), false, 0);
ob_end_flush();

?>