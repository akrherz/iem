<?php
$OL = "10.9.0";
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
<script src='7am-app.js?v=1'></script>
EOM;

$t->content = <<<EOM
<nav aria-label="Breadcrumb">
    <ol class="breadcrumb small mb-3">
        <li class="breadcrumb-item"><a href="/COOP/">NWS COOP</a></li>
        <li class="breadcrumb-item active" aria-current="page">7 AM - 24 Hour Precipitation Analysis</li>
    </ol>
</nav>

<header class="mb-3">
    <h1 class="h3 mb-2">Daily COOP Reports & Comparisons</h1>
    <p class="mb-0">Visual comparison of multiple data sources for the once-daily COOP reports. Choose a parameter and date to update the map. Data is valid for the 24-hour period ending near 7 AM local time.</p>
</header>

<section class="card shadow-sm mb-3" aria-labelledby="controlPanelHeading">
    <div class="card-body">
        <div class="row g-4">
            <div class="col-lg-7">
                <form class="mb-0">
                    <h2 id="controlPanelHeading" class="h5 mb-3">Map Controls</h2>
                    <div class="row g-3 align-items-end">
                        <div class="col-md-6">
                            <label for="renderattr" class="form-label">Parameter</label>
                            <select id="renderattr" class="form-select" aria-describedby="paramHelp">
                                <option value='pday'>Precipitation (inches)</option>
                                <option value='snow'>Snowfall (inches)</option>
                                <option value='snowd'>Snow Depth (inches)</option>
                                <option value='high'>24 Hour High Temperature (°F)</option>
                                <option value='low'>24 Hour Low Temperature (°F)</option>
                                <option value='coop_tmpf'>Temperature at Observation Time (°F)</option>
                            </select>
                            <div id="paramHelp" class="form-text">Select the station variable to render on the map.</div>
                        </div>
                        <div class="col-md-6">
                            <fieldset class="mb-0" aria-describedby="dateHelp">
                                <legend class="form-label mb-1">View Date</legend>
                                <div class="input-group">
                                    <button type="button" id="minusday" class="btn btn-outline-secondary" aria-label="Previous Day">-1</button>
                                    <input type="date" id="datepicker" class="form-control" aria-label="Date to view" />
                                    <button type="button" id="plusday" class="btn btn-outline-secondary" aria-label="Next Day">+1</button>
                                </div>
                                <div id="dateHelp" class="form-text">Select a date between Feb 1 2009 and today.</div>
                            </fieldset>
                        </div>
                    </div>
                </form>

                <div id="legend-panel" class="legend-panel mt-4 p-3 rounded border bg-light-subtle" aria-live="polite">
                    <div class="d-flex align-items-center justify-content-between gap-3 flex-wrap mb-2">
                        <h3 class="h6 mb-0">Parameter Guide</h3>
                        <span id="legend-badge" class="badge text-bg-secondary">Precipitation</span>
                    </div>
                    <p id="legend-text" class="small text-muted mb-2">MRMS 24-hour precipitation is shown as the background raster for comparison against station reports.</p>
                    <div id="legend-media" class="legend-media d-flex align-items-center gap-2 flex-wrap">
                        <img src="/images/mrms_q3_p24h.png" alt="Legend for MRMS 24 hour precipitation" class="img-fluid" loading="lazy" decoding="async" />
                    </div>
                </div>
            </div>
            <div class="col-lg-5">
                <div class="h-100 rounded border bg-body-tertiary p-3">
                    <h2 class="h5 mb-3">How To Read This Map</h2>
                    <p class="small text-muted">Use the layer switcher to toggle station networks and the MRMS precipitation background. Click a station label on the map for its full 7 AM report summary.</p>
                    <h3 class="h6 mt-3">Data Sources</h3>
                    <ul class="small mb-0 ps-3">
                        <li><strong>NWS COOP:</strong> once-daily cooperative observer reports.</li>
                        <li><strong>CoCoRaHS:</strong> volunteer precipitation and snowfall observations.</li>
                        <li><strong>ASOS/AWOS:</strong> automated airport observations when available.</li>
                        <li><strong>MRMS:</strong> gridded precipitation estimate used as a background comparison layer.</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
</section>

<section class="card shadow-sm mb-3" aria-labelledby="mapHeading">
    <div class="card-body">
        <div id="status" class="alert alert-secondary py-2 px-3 small mb-3 d-none" role="status" aria-live="polite" aria-atomic="true"></div>
        <h2 id="mapHeading" class="h5 mb-2">Interactive Map</h2>
        <p id="map-help" class="small text-muted mb-3">Use the layer switcher to toggle station networks or MRMS background. Click a station label for details.</p>
        <div id="map" class="map" role="region" aria-label="COOP map display">
            <div id="popup" aria-live="polite"></div>
        </div>
    </div>
</section>

EOM;
$t->render("full.phtml");
