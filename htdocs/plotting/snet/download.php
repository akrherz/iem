<?php
header("Content-type: application/octet-stream");
header("Content-Disposition: attachment; filename=changeme.txt");
// 1 minute schoolnet data plotter
// Cool.....

$year = isset( $_GET["year"] ) ? $_GET["year"] : date("Y");
$month = isset( $_GET["month"] ) ? $_GET["month"] : date("m");
$day = isset( $_GET["day"] ) ? $_GET["day"] : date("d");
$station = isset($_GET['station']) ? $_GET["station"]: "";

include ("../../../include/snet_locs.php");

if (strlen($station) > 3){
    $station = $SconvBack[$station];
}

$station = intval($station);


if (strlen($year) == 4 && strlen($month) > 0 && strlen(day) > 0 ){
  $myTime = strtotime($year."-".$month."-".$day);
} else {
  $myTime = strtotime(date("Y-m-d"));
}


$dirRef = strftime("%Y_%m/%d", $myTime);
$titleDate = strftime("%b %d, %Y", $myTime);
$dRef = strftime("%Y%m%d", $myTime);

header("Content-Disposition: attachment; filename=". $dRef ."_". $station .".dat");

$fcontents = file('/mesonet/ARCHIVE/raw/snet/'.$dirRef.'/'.$station.'.dat');

while (list ($line_num, $line) = each ($fcontents)) {
    echo $line ;
}

?>
