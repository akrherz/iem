<?php
 $station = isset($_GET['station']) ? substr($_GET['station'],0,5): 'SJEI4';
 include("../../config/settings.inc.php");
 include("$rootpath/include/iemaccess.php");
 include("$rootpath/include/mlib.php");
 include("$rootpath/include/iemaccessob.php");
 $iem = new IEMAccess();
 $ob = $iem->getSingleSite($station);
 header('Content-type: text/plain');

 echo $ob->db["tmpf"] ."\n";
 echo $ob->db["dwpf"] ."\n";
 echo $ob->db["sknt"] ."\n";
 echo drct2txt($ob->db["drct"]) ."\n";
 echo round($ob->db["gust"],0) ."\n";
 echo $ob->db["pday"] ."\n";
 echo $ob->db["relh"] ."\n";
 echo $ob->db["pres"] ."\n";
 echo feels_like($ob->db['tmpf'], $ob->db['relh'], $ob['sknt']) ."\n";

?>
