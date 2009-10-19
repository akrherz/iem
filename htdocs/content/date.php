<?
	$width = 87;
	$height = 60;
	$Font = '/mesonet/data/gis/static/fonts/handgotn.ttf';
    $year = isset($_GET["year"]) ? $_GET["year"] : date("Y");
    $month = isset($_GET["month"]) ? $_GET["month"] : date("m");
    $day = isset($_GET["day"]) ? $_GET["day"] : date("d");


	$gif = ImageCreate($width,$height);

	$black = ImageColorAllocate($gif,0,0,0);
	$white = ImageColorAllocate($gif,250,250,250);
	$green = ImageColorAllocate($gif, 0, 255, 0);
	$red = ImageColorAllocate($gif, 255, 0, 0);
	$grey = ImageColorAllocate($gif, 110, 110, 110);
	
	ImageFilledRectangle($gif,2,2, $width, $height, $grey);
	ImageFilledRectangle($gif,1,1, $width -2 , $height -2, $white);
	
	$size = imagettfbbox(12, 0, $Font, $month);
	$dx = abs($size[2] - $size[0]);
	$dy = abs($size[5] - $size[3]);
	$x_pad = ($width - $dx) / 2 ;
	ImageTTFText($gif, 12, 0, $x_pad , 15, $black, $Font, $month);

	$size = imagettfbbox(20, 0, $Font, $day);
	$dx = abs($size[2] - $size[0]);
	$dy = abs($size[5] - $size[3]);
	$x_pad = ($width - $dx) / 2 ;
	ImageTTFText($gif, 18, 0, $x_pad , 35, $red, $Font, $day);

	$size = imagettfbbox(15, 0, $Font, $year);
	$dx = abs($size[2] - $size[0]);
	$dy = abs($size[5] - $size[3]);
	$x_pad = ($width - $dx) / 2 ;
	ImageTTFText($gif, 14, 0, $x_pad , 55, $black, $Font, $year);

	
#	ImageString($gif, 3, 5, 5, $month ,$black);
#	ImageString($gif, 3, 5, 20, $day ,$black);
#	ImageString($gif, 3, 5, 35, $year ,$black);

	header("content-type: image/png");
	ImagePng($gif);
	ImageDestroy($gif);
?>
