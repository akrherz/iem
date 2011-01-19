<?php
// Actually, my first PHP script not running as apache!
// Daryl Herzmann 17 Oct 2002

include('../../config/settings.inc.php');
include("$rootpath/include/mlib.php");
include("$rootpath/include/network.php");
$nt = new NetworkTable(Array("KCCI","IA_RWIS"));
$cities = $nt->table;
include("$rootpath/include/iemaccess.php");
include("$rootpath/include/iemaccessob.php");

$iem = new IEMAccess();
pg_exec($iem->dbconn, "SET TIME ZONE 'GMT'");
$rwis = $iem->getNetwork("IA_RWIS");
$rwisf = fopen('rwis.dat', 'w');

$mydata = Array();
while (list($key, $iemob) = each($rwis) ){
  $mydata[$key] = $iemob->db;
  fwrite($rwisf,  $key .",". date('Y-m-d H:i', $mydata[$key]['ts']) .",". 
    $cities[$key]['lat'] .":". $cities[$key]['lon'] .",". 
    $mydata[$key]['sknt'] .",".
    $mydata[$key]['drct'] .",". $mydata[$key]['gust'] .",".
    $mydata[$key]['relh'] .",".
    $mydata[$key]['tmpf'] .",". $mydata[$key]['dwpf'] ."\n");
} // End of while


###############################################################
###############################################################


$rwis = $iem->getNetwork("KCCI");
$snetf = fopen('snet.dat', 'w');


$mydata = Array();
while (list($key, $iemob) = each($rwis) ){
  $mydata[$key] = $iemob->db;

  fwrite($snetf, $key .",". date('Y-m-d H:i', $mydata[$key]['ts']) .",". 
    $cities[$key]['lat'] .":". $cities[$key]['lon'] .",". 
    $mydata[$key]['sknt'] .",".
    $mydata[$key]['drct'] .",0,".
    $mydata[$key]['relh'] .",".
    $mydata[$key]['tmpf'] .",". $mydata[$key]['dwpf'] .",".
    $mydata[$key]['pday'] ."\n");
} // End of while


#########
###########
#############

copy('rwis.dat', '/mesonet/share/pickup/spider/rwis-v0.dat');
copy('snet.dat', '/mesonet/share/pickup/spider/snet-v0.dat');
unlink('rwis.dat');
unlink('snet.dat');

?>
