<?php
header("Content-type: text/plain");
 // Generate placefiles, whatever
 // Inspiration: http://grlevel3.tornadocentral.com/metars.php?state=IA

echo 'Title: KCCI SchoolNet8
Refresh: 20 
Color: 200 200 255
IconFile: 1, 18, 32, 2, 31, "http://www.tornadocentral.com/grlevel3/windbarbs.png" 
IconFile: 2, 15, 15, 8, 8, "http://www.tornadocentral.com/grlevel3/cloudcover.png" 
Font: 1, 11, 1, "Courier New"

';
include("../../../config/settings.inc.php");
include("$rootpath/include/iemaccess.php");
include("$rootpath/include/iemaccessob.php");
include("$rootpath/include/mlib.php");
include("$rootpath/include/snet_locs.php");
$iem = new IEMAccess();
$snet = $iem->getNetwork("KCCI");

function s2icon($s)
{
  if ($s < 2.5) return "1,20";
  if ($s < 5) return "1,1";
  if ($s < 7.5) return "1,2";
  if ($s < 10) return "1,3";
  if ($s < 12.5) return "1,4";
  if ($s < 15) return "1,5";
  if ($s < 17.5) return "1,6";
  if ($s < 20) return "1,7";

  if ($s < 22.5) return "1,8";
  if ($s < 25) return "1,9";
  if ($s < 27.5) return "1,10";
  if ($s < 30) return "1,11";
  if ($s < 32.5) return "1,12";
  if ($s < 35) return "1,13";
  if ($s < 37.5) return "1,14";

  if ($s < 40) return "1,15";
  if ($s < 42.5) return "1,16";
  if ($s < 45) return "1,17";
  if ($s < 47.5) return "1,18";
  if ($s < 50) return "1,19";
  return "1,20";

}

$now = time();

while (list($key, $iemob) = each($snet) ){
    $mydata = $iemob->db;
    $meta = $cities["KCCI"][$key];
    $tdiff = $now - $mydata["ts"];
    if ($tdiff > 3600) continue;


echo "Object: ".$meta["lat"].",".$meta["lon"]."
  Threshold: 999 
  Icon: 0,0,". $mydata["drct"] .",". s2icon( floatval($mydata["sknt"]) ) ."
  Icon: 0,0,000,2,5,\"".$meta["city"]." @ ". strftime("%d %b %I:%M %p", $mydata['ts']) ."\\nTemp: ".$mydata["tmpf"]."F (Dew: ".$mydata["dwpf"]."F)\\nWind: ". drct2txt($mydata["drct"]) ." @ ". intval($mydata["sknt"]) ."kt\\n\" 
  Threshold: 150
  Text:  -17, 13, 1, \" ".$mydata["tmpf"]." \" 
  Text:  -17, -13, 1, \" ".$mydata["dwpf"]." \" 
 End: 

";
}

?>
