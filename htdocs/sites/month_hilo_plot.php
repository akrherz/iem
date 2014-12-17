<?php
 /* Make a nice simple plot of monthly  temperatures */
 include('../../config/settings.inc.php');
 include("../../include/database.inc.php");
 include('setup.php');

 $month = isset($_GET["month"]) ? intval($_GET["month"]): date("m");
 $year = isset($_GET["year"]) ? intval($_GET["year"]): date("Y");

 header("Location: /plotting/auto/plot/17/month:{$month}::year:{$year}::station:{$station}::network:{$network}.png");
 
?>
