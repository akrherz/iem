<?php 
require_once "../../config/settings.inc.php";
require_once "../../include/database.inc.php";
require_once "setup.php";
require_once "../../include/myview.php";

$t = new MyView();
$t->title = "Terminal Aerodome Forecasts";
$t->sites_current = "taf"; 

$station4 = (sizeof($station) == 3) ? sprintf("K%s", $station): $station;
$station3 = substr($station4, 1, 3);
$t->content = <<<EOF
<h3>Terminal Aerodome Forecasts</h3>

<p>The IEM processes the feed of Terminal Aerodome Forecasts from the NWS.  This
page presents some of the options available for this dataset. A
<a href="/request/taf.php">download option</a> exists as well.</p>

<p><a href="/wx/afos/p.php?pil=TAF${station3}">Latest raw text product</a></p>

<p><img src="/plotting/auto/plot/219/station:${station4}.png" class="img img-responsive"></p>

EOF;
$t->render('sites.phtml');
