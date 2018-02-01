<?php
 $station = isset($_GET['station']) ? substr($_GET['station'],0,5): 'SJEI4';
 include("../../config/settings.inc.php");
 include("../../include/mlib.php");
   $jdata = file_get_contents("http://iem.local/api/1/currents.json?station=$station");
   $jobj = json_decode($jdata, $assoc=TRUE);
   $ob = $jobj["data"][0];
 header('Content-type: text/plain');

 echo $ob["tmpf"] ."\n";
 echo $ob["dwpf"] ."\n";
 echo $ob["sknt"] ."\n";
 echo drct2txt($ob["drct"]) ."\n";
 echo round($ob["gust"],0) ."\n";
 echo $ob["pday"] ."\n";
 echo $ob["relh"] ."\n";
 echo $ob["pres"] ."\n";
 echo intval($ob["feel"]) ."\n";

?>
