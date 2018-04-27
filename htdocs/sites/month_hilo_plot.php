<?php
 // 27 Apr 2018: We still need this around as hist.phtml called it, wait for
 // search crawlers to stop hitting it
 require_once '../../config/settings.inc.php';
 require_once "../../include/database.inc.php";
 require_once 'setup.php';

 $month = isset($_GET["month"]) ? intval($_GET["month"]): date("m");
 $year = isset($_GET["year"]) ? intval($_GET["year"]): date("Y");

 header("Location: /plotting/auto/plot/17/month:{$month}::year:{$year}::station:{$station}::network:{$network}.png");
 
?>
