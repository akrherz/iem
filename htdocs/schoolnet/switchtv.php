<?php
// Rigamarole to get the $tv variable set and running...
$expiry = 60*60*24*100; // 100 days
session_start();
setcookie(session_name(), session_id(), time()+$expiry, "/");
$ntv = isset($_GET["ntv"]) ? $_GET["ntv"] : "";

if (strlen($ntv) > 0){
  $_SESSION['tv'] = strtoupper($ntv);
} else if (isset($_GET["tv"]) && strlen($_GET["tv"]) > 0){
  $_SESSION['tv'] = $_GET["tv"];
}
if (! isset($_SESSION['tv']) ) $_SESSION['tv'] = 'KCCI';

$tv = $_SESSION['tv'];

session_write_close();
?>
