<?php 
include("../../config/settings.inc.php");
include("../../include/database.inc.php");
include("../../include/forms.php");
include("setup.php");
include("../../include/myview.php");
$t = new MyView();
$t->thispage = "iem-sites";
$t->title = "Site Meteorograms";
$t->sites_current="meteo"; 

$uri = sprintf("meteo_temps.php?network=%s&station=%s",   $network, $station);
$t->content = <<<EOF
 <br /><img src="{$uri}">
EOF;
$t->render('sites.phtml');
?>
