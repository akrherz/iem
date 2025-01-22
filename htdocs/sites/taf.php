<?php
require_once "../../config/settings.inc.php";
require_once "../../include/database.inc.php";
require_once "../../include/sites.php";
require_once "../../include/myview.php";

$ctx = get_sites_context();
$station = $ctx->station;
$network = $ctx->network;
$metadata = $ctx->metadata;

$station4 = (strlen($station) == 3) ? sprintf("K%s", $station) : $station;
$station3 = substr($station4, 1, 3);

$t = new MyView();
$t->refresh = 300;
$t->title = "Terminal Aerodome Forecasts";
$t->sites_current = "taf";
$t->jsextra = <<<EOM
<script src="taf.js" type="text/javascript"></script>
EOM;

$t->content = <<<EOM
<h3>Terminal Aerodome Forecasts</h3>

<p>The IEM processes the feed of Terminal Aerodome Forecasts from the NWS.  This
page presents some of the options available for this dataset. A
<a href="/request/taf.php">download option</a> exists as well.</p>

<h4>Recent METARs</h4>

<div id="metars" data-station4="{$station4}"></div>

<h4>Raw TAF Text</h4>

<div id="rawtext" data-station3="{$station3}"></div>

<h4>Current NWS Aviation AFD</h4>

<div id="afd" data-wfo="{$metadata['wfo']}"></div>


<h4>IEM TAF Visualization</h4>

<p>IEM <a href="/plotting/auto/?q=219&station={$station4}">Autoplot 219</a> produced
this visualization:</p>

<p><img src="/plotting/auto/plot/219/station:{$station4}.png" class="img img-responsive"></p>


EOM;
$t->render('sites.phtml');
