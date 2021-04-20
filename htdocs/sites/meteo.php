<?php 
require_once "../../config/settings.inc.php";
require_once "../../include/database.inc.php";
require_once "../../include/forms.php";
require_once "setup.php";
require_once "../../include/myview.php";
$t = new MyView();
$t->title = "Site Meteorograms";
$t->sites_current="meteo"; 

$uri = sprintf("/plotting/auto/plot/43/station:%s::network:%s.png",  $station,
		$network);
$t->content = <<<EOF

<p>This page creates a simple plot of recent observations from this site.</p>

 <br /><img src="{$uri}" class="img img-responsive">
EOF;
$t->render('sites.phtml');
?>
