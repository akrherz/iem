<?php
        include("../../../include/mlib.php");
        $site = substr($station, 0, 5);
        if (strlen($site) == 0)  $site = 'SKCI4';


	$width = 640;
	$height = 480;
	$Font = '../fancy/kcci.ttf';

        $gif = @imagecreatefromgif("images/650am.gif");
        $time = "6:50 AM";
        $dbtime = "06:50";

	$black = ImageColorAllocate($gif,0,0,0);
	$white = ImageColorAllocate($gif,250,250,250);
	$green = ImageColorAllocate($gif, 0, 255, 0);
	$yellow = ImageColorAllocate($gif, 255, 255, 120);
	$red = ImageColorAllocate($gif, 148, 52, 53);
	$blue = ImageColorAllocate($gif, 0, 0, 255);
	$grey = ImageColorAllocate($gif, 110, 110, 110);
	
//	ImageFilledRectangle($gif,2,2, $width, $height, $grey);
//	ImageFilledRectangle($gif,1,1, $width -2 , $height -2, $white);


$connect = pg_connect("localhost","5432","snet");
$query = "SELECT * from t2002_07 WHERE valid = '2002-07-10 ".$dbtime."'";
$result = pg_exec($connect, $query);

$data = Array();

for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
{
 $data[$row["station"]] = $row;
}
pg_close($connect);


$var = "sknt";
 function trans($in, $st, $data){
$dirTrans = Array(360 => 'N',
  30 =>'NNE',
  50 => 'NE',
  70 => 'ENE',
  90 => 'E',
 120 => 'ESE',
 140 => 'SE',
 160 => 'SSE',
 180 => 'S',
 210 => 'SSW',
 230 => 'SW',
 250 => 'WSW',
 270 => 'W',
 290 => 'WNW',
 310 => 'NW',
 340 => 'NNW');

  if (strlen($in) == 0) return "";
  return $dirTrans[$data[$st]["drct"]] ." @ ". round( $in * 1.15 );
 }

function trans2($in){
  return round($in, 2);
}

// Time
 ImageTTFText($gif, 20, 0, $width - 70 , $height - 20, $white, $Font, $time );

// Conn Rapids
 ImageTTFText($gif, 20, 0, 310, 335, $black, $Font, trans2($data["SCBI4"]["pday"]) );
 ImageTTFText($gif, 20, 0, 309, 335, $white, $Font, trans2($data["SCBI4"]["pday"]) );

 ImageTTFText($gif, 20, 0, 310, 365, $black, $Font, trans($data["SCBI4"][$var], "SCBI4", $data) );
 ImageTTFText($gif, 20, 0, 309, 365, $white, $Font, trans($data["SCBI4"][$var], "SCBI4", $data) );


// Jefferson
 ImageTTFText($gif, 20, 0, 503, 216, $black, $Font, trans2($data["SJEI4"]["pday"]) );
 ImageTTFText($gif, 20, 0, 502, 216, $white, $Font, trans2($data["SJEI4"]["pday"]) );

 ImageTTFText($gif, 20, 0, 503, 246, $black, $Font, trans($data["SJEI4"][$var], "SJEI4", $data) );
 ImageTTFText($gif, 20, 0, 502, 246, $white, $Font, trans($data["SJEI4"][$var], "SJEI4", $data) );


// Glidden
 ImageTTFText($gif, 20, 0, 288, 182, $black, $Font, trans2($data["SGLI4"]["pday"]) );
 ImageTTFText($gif, 20, 0, 287, 182, $white, $Font, trans2($data["SGLI4"]["pday"]) );

 ImageTTFText($gif, 20, 0, 288, 212, $black, $Font, trans($data["SGLI4"][$var], "SGLI4", $data) );
 ImageTTFText($gif, 20, 0, 287, 212, $white, $Font, trans($data["SGLI4"][$var], "SGLI4", $data) );

// Carroll
 ImageTTFText($gif, 20, 0, 185, 175, $black, $Font, trans2($data["SCAI4"]["pday"]) );
 ImageTTFText($gif, 20, 0, 184, 175, $white, $Font, trans2($data["SCAI4"]["pday"]) );

 ImageTTFText($gif, 20, 0, 185, 205, $black, $Font, trans($data["SCAI4"][$var], "SCAI4", $data) );
 ImageTTFText($gif, 20, 0, 184, 205, $white, $Font, trans($data["SCAI4"][$var], "SCAI4", $data) );


	ImageGif($gif, "/mesonet/www/html/tmp/tester.gif");
	ImageDestroy($gif);

  echo "<img src=\"/tmp/tester.gif\">\n";
?>
