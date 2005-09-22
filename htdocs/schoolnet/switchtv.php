<?php
// Rigamarole to get the $tv variable set and running...
$expiry = 60*60*24*100; // 100 days
session_start();
setcookie(session_name(), session_id(), time()+$expiry, "/");
$ntv = $_GET["ntv"];

if (strlen($ntv) > 0){
  $_SESSION['tv'] = strtoupper($ntv);
} else if (strlen($tv) == 0){
  $_SESSION['tv'] = 'KCCI';
  $tv = 'KCCI';
}
?>
