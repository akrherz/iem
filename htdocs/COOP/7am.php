<?php
$OL = "10.6.1";
require_once "../../config/settings.inc.php";
define("IEM_APPID", 86);
require_once "../../include/mlib.php";
force_https();
require_once "../../include/myview.php";
$t = new MyView();
$t->title = "Iowa Daily COOP Reports and Comparisons";
$t->headextra = <<<EOM
<link rel="stylesheet" href="/vendor/openlayers/{$OL}/ol.css" type="text/css">
<link type="text/css" href="/vendor/openlayers/{$OL}/ol-layerswitcher.css" rel="stylesheet" />
<link rel="stylesheet" href="7am.css" type="text/css">
EOM;

$t->jsextra = <<<EOM
<script src="/vendor/openlayers/{$OL}/ol.js" type="text/javascript"></script>
<script src='/vendor/openlayers/{$OL}/ol-layerswitcher.js'></script>
<script src='7am-app.js?v=10'></script>
EOM;

$t->content = <<<EOM
<nav aria-label="Breadcrumb">
    <ol class="breadcrumb small mb-3">
        <li class="breadcrumb-item"><a href="/COOP/">NWS COOP</a></li>
        <li class="breadcrumb-item active" aria-current="page">7 AM - 24 Hour Precipitation Analysis</li>
    </ol>
</nav>

<header class="mb-3">
    <h1 class="h3 mb-2">Iowa Daily COOP Reports & Comparisons</h1>
    <p class="mb-0">Visual comparison of multiple data sources for the once-daily COOP reports. Choose a parameter and date to update the map. Data is valid for the 24-hour period ending near 7 AM local time.</p>
</header>

<form name="bah" class="mb-3" aria-labelledby="controlPanelHeading">
    <h2 id="controlPanelHeading" class="visually-hidden">Map Controls</h2>
    <div class="row g-3 align-items-end">
        <div class="col-md-6">
            <div class="mb-2">
                <label for="renderattr" class="form-label">Parameter</label>
                <select id="renderattr" class="form-select form-select-sm" aria-describedby="paramHelp">
                    <option value='pday'>Precipitation (inches)</option>
                    <option value='snow'>Snowfall (inches)</option>
                    <option value='snowd'>Snow Depth (inches)</option>
                    <option value='high'>24 Hour High Temperature (°F)</option>
                    <option value='low'>24 Hour Low Temperature (°F)</option>
                    <option value='coop_tmpf'>Temperature at Observation Time (°F)</option>
                </select>
                <div id="paramHelp" class="form-text">Select the variable to render on the map.</div>
            </div>
            <div class="d-flex align-items-center gap-2 flex-wrap">
                <div class="small fw-bold">MRMS Legend:</div>
                <img src="/images/mrms_q3_p24h.png" alt="Legend for MRMS 24 hour precipitation" class="img-fluid" style="max-height:48px" loading="lazy" decoding="async" />
            </div>
        </div>
        <div class="col-md-6">
            <fieldset class="mb-0" aria-describedby="dateHelp">
                <legend class="form-label mb-1">View Date</legend>
                <div class="input-group input-group-sm" style="max-width:320px;">
                    <button type="button" id="minusday" class="btn btn-outline-secondary" aria-label="Previous Day">-1</button>
                    <input type="date" id="datepicker" class="form-control" aria-label="Date to view" />
                    <button type="button" id="plusday" class="btn btn-outline-secondary" aria-label="Next Day">+1</button>
                </div>
                <div id="dateHelp" class="form-text">Select a date between Feb 1 2009 and today.</div>
            </fieldset>
        </div>
    </div>
</form>

<div id="status" class="visually-hidden" aria-live="polite" aria-atomic="true"></div>

<section class="mb-3" aria-labelledby="mapHeading">
    <h2 id="mapHeading" class="h5 mb-2">Interactive Map</h2>
    <p class="small text-muted mb-2">Use the layer switcher to toggle station networks or MRMS background. Click a station label for details.</p>
    <div id="map" class="map" role="region" aria-label="COOP map display"><div id="popup" aria-live="polite"></div></div>
</section>

<div id="popover-content" hidden>
    <p>This is the popover content</p>
</div>

EOM;
$t->render("full.phtml");
