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
$t->iemselect2 = true;
$t->refresh = 300;
$t->title = "Terminal Aerodome Forecasts";
$t->sites_current = "taf";
$t->jsextra = <<<EOM
<script src="taf.module.js" type="module"></script>
EOM;

$t->content = <<<EOM
<div class="row">
<div class="col-md-12">

<div class="card mb-4">
<div class="card-header">
<h3 class="card-title mb-0">Terminal Aerodrome Forecasts</h3>
</div>
<div class="card-body">
<p class="card-text">The IEM processes the feed of Terminal Aerodrome Forecasts from the NWS. This
page presents some of the options available for this dataset. A
<a href="/request/taf.php" class="btn btn-sm btn-outline-primary">download option</a> exists as well.</p>
</div>
</div>

</div>
</div>

<div class="row">
<div class="col-md-12 mb-4">

<div class="card">
<div class="card-header">
<h4 class="card-title mb-0">Recent METARs</h4>
</div>
<div class="card-body">
<div id="metars" data-station4="{$station4}">
<div class="d-flex justify-content-center">
<div class="spinner-border text-primary" role="status" aria-label="Loading METAR data">
<span class="visually-hidden">Loading...</span>
</div>
</div>
</div>
</div>
</div>

</div>
</div>

<div class="row">
<div class="col-lg-6 col-md-12 mb-4">

<div class="card h-100">
<div class="card-header">
<h4 class="card-title mb-0">Raw TAF Text</h4>
</div>
<div class="card-body">
<div id="rawtext" data-station3="{$station3}">
<div class="d-flex justify-content-center">
<div class="spinner-border text-primary" role="status" aria-label="Loading TAF data">
<span class="visually-hidden">Loading...</span>
</div>
</div>
</div>
</div>
</div>

</div>
<div class="col-lg-6 col-md-12 mb-4">

<div class="card h-100">
<div class="card-header">
<h4 class="card-title mb-0">Current NWS Aviation AFD</h4>
</div>
<div class="card-body">
<div id="afd" data-wfo="{$metadata['wfo']}">
<div class="d-flex justify-content-center">
<div class="spinner-border text-primary" role="status" aria-label="Loading AFD data">
<span class="visually-hidden">Loading...</span>
</div>
</div>
</div>
</div>
</div>

</div>
</div>

<div class="row">
<div class="col-md-12">

<div class="card">
<div class="card-header">
<h4 class="card-title mb-0">IEM TAF Visualization</h4>
</div>
<div class="card-body">
<p class="card-text">IEM <a href="/plotting/auto/?q=219&station={$station4}" class="btn btn-sm btn-outline-secondary">Autoplot 219</a> produced
this visualization:</p>
<div class="text-center">
<img src="/plotting/auto/plot/219/station:{$station4}.png" class="img-fluid rounded shadow-sm" alt="TAF Visualization for {$station4}">
</div>
</div>
</div>

</div>
</div>


EOM;
$t->render('sites.phtml');
