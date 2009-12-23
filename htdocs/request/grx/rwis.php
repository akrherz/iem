<?php
header("Content-type: text/plain");
 // Generate placefiles, whatever
 // Inspiration: http://grlevel3.tornadocentral.com/metars.php?state=IA

echo 'Title: Iowa DOT RWIS
Refresh: 5
Color: 200 200 255
IconFile: 1, 18, 32, 2, 31, "http://www.tornadocentral.com/grlevel3/windbarbs.png" 
IconFile: 2, 15, 15, 8, 8, "http://www.tornadocentral.com/grlevel3/cloudcover.png" 
IconFile: 3, 25, 25, 12, 12, "http://mesonet.agron.iastate.edu/request/grx/rwis_cr.png" 
Font: 1, 11, 1, "Courier New"

';
include("../../../config/settings.inc.php");
include("$rootpath/include/iemaccess.php");
include("$rootpath/include/iemaccessob.php");
include("$rootpath/include/mlib.php");
include("$rootpath/include/network.php");
$nt = new NetworkTable("IA_RWIS");
$cities = $nt->table;
$iem = new IEMAccess();
$snet = $iem->getNetwork("IA_RWIS");

function pcolor($tmpf)
{
  if ($tmpf >= 35) return "2";
  if ($tmpf >= 34) return "3";
  if ($tmpf >= 33) return "4";
  if ($tmpf >= 32) return "5";
  if ($tmpf >= 31) return "6";
  if ($tmpf >= 30) return "7";
  if ($tmpf < 30) return "8";
  return "1";

}

function s2icon($s)
{
  if ($s < 2.5) return "1,21";
  if ($s < 5) return "1,1";
  if ($s < 10) return "1,2";
  if ($s < 15) return "1,3";
  if ($s < 20) return "1,4";
  if ($s < 25) return "1,5";
  if ($s < 30) return "1,6";
  if ($s < 35) return "1,7";

  if ($s < 40) return "1,8";
  if ($s < 45) return "1,9";
  if ($s < 50) return "1,10";
  if ($s < 55) return "1,11";
  if ($s < 60) return "1,12";
  if ($s < 65) return "1,13";
  if ($s < 70) return "1,14";

  if ($s < 75) return "1,15";
  if ($s < 80) return "1,16";
  if ($s < 85) return "1,17";
  if ($s < 80) return "1,18";
  if ($s < 100) return "1,19";
  return "1,20";

}

$now = time();

while (list($key, $iemob) = each($snet) ){
    $mydata = $iemob->db;
    $meta = $cities[$key];
    $tdiff = $now - $mydata["ts"];
    if ($tdiff > 3600) continue;
    if ($mydata["sknt"] < 2.5) $mydata["drct"] = 0;

    /* Compute average pavement temperature */
    $total = 0;
    $cnt = 0;
    for($i=0;$i<4;$i++){
      if ($mydata["tsf$i"] > -30 && $mydata["tsf$i"] < 150){
         $cnt += 1;
         $total += $mydata["tsf$i"];
      }
    }
    if ($cnt == 0){ $mydata["pave_avg"] = "M"; }
    else{ $mydata["pave_avg"] = $total / floatval($cnt);}

    /* Condition Text */
    $condTxt = sprintf("Sensor 1: [%.1f F] %s\\nSensor 2: [%.1f F] %s\\nSensor 3: [%.1f F] %s\\nSensor 4: [%.1f F] %s\\nAvg: [%s F]", 
       $mydata["tsf0"], $mydata["scond0"],
       $mydata["tsf1"], $mydata["scond1"],
       $mydata["tsf2"], $mydata["scond2"],
       $mydata["tsf3"], $mydata["scond3"], $mydata["pave_avg"]
    );

    echo "Object: ".$meta["lat"].",".$meta["lon"]."
  Threshold: 999 
  Icon: 0,0,000,3,". pcolor($mydata["pave_avg"]) ."
  Icon: 0,0,". $mydata["drct"] .",". s2icon( floatval($mydata["sknt"]) ) ."
  Icon: 0,0,000,2,13,\"".$meta["name"]." @ ". strftime("%d %b %I:%M %p", $mydata['ts']) ."\\nTemp: ".$mydata["tmpf"]."F (Dew: ".$mydata["dwpf"]."F)\\nWind: ". drct2txt($mydata["drct"]) ." @ ". intval($mydata["sknt"]) ."kt\\n${condTxt}\" 
  Threshold: 150
  Text:  -17, 13, 1, \" ".round($mydata["tmpf"],0)." \" 
  Text:  -17, -13, 1, \" ".round($mydata["dwpf"],0)." \" 
 End: 

";
}

?>
