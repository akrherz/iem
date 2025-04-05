<?php
require_once "../../config/settings.inc.php";
require_once "../../include/myview.php";
$OL = "10.4.0";

$t = new MyView();
$t->title = "IEM One";
$t->headextra = <<<EOM
<link rel="stylesheet" href="/vendor/openlayers/{$OL}/ol.css" type="text/css">
<link rel="stylesheet" href="app.css" type="text/css">
EOM;
$t->jsextra = <<<EOM
<script src="/vendor/openlayers/{$OL}/ol.js" type="text/javascript"></script>
<script src="geojsonLayer.js" type="text/javascript"></script>
<script src="app.js" type="text/javascript"></script>
EOM;
$t->content = <<<EOM
<div id="map" class="map"></div>
<div id="branding-overlay" data-mode="archive">IEM1: Archive</div>
<button id="warnings-toggle">☰ Warnings</button>
<div id="time-control" class="time-control">
    <div class="time-input-container">
        <input type="datetime-local" id="current-time" class="time-input">
    </div>
    <div class="time-buttons">
        <button id="time-step-backward">◀</button>
        <button id="time-play-pause">⏯</button>
        <button id="time-step-forward">▶</button>
        <button id="realtime-mode">⏱</button>
    </div>
    <div id="animation-progress" class="progress-bar"></div>
</div>
<div id="layer-control" class="side-drawer">
    <button id="layers-toggle">☰ Layers</button>
    <div class="drawer-content">
        <h3>Layers</h3>
        <label>
            <input type="checkbox" id="toggle-tms-layer" checked>
            Radar Layer
        </label>
        <label>
            Opacity: <input type="range" id="tms-opacity-slider" min="0" max="1" step="0.1" value="1">
        </label>
        <label>
            <input type="checkbox" id="toggle-warnings-layer" checked>
            Warnings
        </label>
        <div id="warnings-toggles" class="phenomena-toggles">
            <button class="phenomena-toggle active" data-phenomena="TO" title="Tornado">TO</button>
            <button class="phenomena-toggle active" data-phenomena="SV" title="Severe">SV</button>
            <button class="phenomena-toggle active" data-phenomena="FF" title="Flash Flood">FF</button>
            <button class="phenomena-toggle active" data-phenomena="EW" title="Extreme Wind">EW</button>
            <button class="phenomena-toggle active" data-phenomena="SQ" title="Squall">SQ</button>
            <button class="phenomena-toggle active" data-phenomena="DS" title="Dust Storm">DS</button>
            <button class="phenomena-toggle" data-phenomena="FL" title="Flood" style="background: #ccc;">FL</button> <!-- Default untoggled -->
        </div>
    </div>
</div>
<div id="warnings-modal">
    <div id="warnings-modal-header">
        Warnings
        <button id="close-warnings">✖</button>
    </div>
    <div id="warnings-modal-content">
        <table id="warnings-table">
            <thead>
                <tr>
                    <th>WFO</th>
                    <th>Till</th>
                    <th>Ph.Sig Event Link</th>
                </tr>
            </thead>
            <tbody>
                <!-- Additional rows will be dynamically populated -->
            </tbody>
        </table>
    </div>
    <button id="collapse-warnings" style="display: none;">Collapse</button> <!-- Collapse button -->
</div>
EOM;
$t->render("app.phtml");
