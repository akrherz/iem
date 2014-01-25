<?php
/* Allow direct fetching of webcam images from the webcam network.  A 15 
 * second lifetime of the image in memcached hopefully prevents the website
 * from sucking all bandwidth from a webcam's site
 */
require_once("../../config/settings.inc.php");
require_once("../../include/cameras.inc.php");

$id = isset($_GET["id"]) ? $_GET["id"] : "KCCI-001";

function fail_image(){
	header("Content-type: image/png");
	$im = imagecreate(640, 480);
	$background_color = imagecolorallocate($im, 0, 0, 0);
	$text_color = imagecolorallocate($im, 233, 14, 91);
	imagestring($im, 5, 150, 240,  "Sorry, image unavailable.", $text_color);
	imagepng($im);
	imagedestroy($im);
	die();
}
	
// Offline webcams and scraped webcams don't emit images :)
if (! $cameras[$id]["active"] || $cameras[$id]['scrape_url'] != null){
	fail_image();
}

// Try to get it from memcached
$memcache = new Memcache;
$memcache->connect('iem-memcached', 11211);
$val = $memcache->get("live_". $id);
if ($val){
	header("Content-type: image/jpeg");
	die($val);
}

// Need to buffer the output so that we can save it to memcached later
ob_start();
$ip = $cameras[$id]["ip"];

$u = $camera_user[ $cameras[$id]['network'] ];
$p = $camera_pass[ $cameras[$id]['network'] ];
$port = $cameras[$id]['port'];
if ($cameras[$id]["is_vapix"]){
	$im = @imagecreatefromjpeg("http://${u}:${p}@$ip:${port}/axis-cgi/jpg/image.cgi?resolution=640x480");
} else {
	$im = @imagecreatefromjpeg("http://${u}:${p}@$ip:${port}/-wvhttp-01-/GetOneShot");
}
if (! $im ){
	fail_image();
}

$white = imagecolorallocate($im, 250, 250, 250);
$black = imagecolorallocate($im, 0, 0, 0);
imagefilledrectangle($im, 3, 465, 637, 480, $black);
imagestring($im, 5, 15, 465, date("d M Y h:i:s A, ") . $cameras[$id]["name"] ." Live Shot!", $white);

header("Content-type: image/jpeg");
imagejpeg($im);
$memcache->set("live_". $id, ob_get_contents(), false, 15);
ob_end_flush();
?>
