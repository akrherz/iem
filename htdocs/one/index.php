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
            Warnings &amp; Advisories
        </label>
        <div id="warnings-toggles" class="phenomena-toggles">
            <button class="phenomena-toggle active" data-key="TO.W" title="Tornado Warning" style="background: #FF0000;">TO.W</button>
            <button class="phenomena-toggle active" data-key="SV.W" title="Severe Thunderstorm Warning" style="background: #FFA500;">SV.W</button>
            <button class="phenomena-toggle active" data-key="FF.W" title="Flash Flood Warning" style="background: #8B0000;">FF.W</button>
            <button class="phenomena-toggle active" data-key="FL.W" title="Flood Warning" style="background: #00FF00;">FL.W</button>
            <button class="phenomena-toggle active" data-key="FL.A" title="Flood Watch" style="background: #2E8B57;">FL.A</button>
            <button class="phenomena-toggle active" data-key="FL.Y" title="Flood Advisory" style="background: #00FF7F;">FL.Y</button>
            <button class="phenomena-toggle active" data-key="DS.W" title="Dust Storm Warning" style="background: #FFE4C4;">DS.W</button>
            <button class="phenomena-toggle active" data-key="DS.Y" title="Dust Storm Advisory" style="background: #BDB76B;">DS.Y</button>
            <button class="phenomena-toggle active" data-key="SQ.W" title="Squall Warning" style="background: #C71585;">SQ.W</button>
            <button class="phenomena-toggle active" data-key="FA.W" title="Areal Flood Warning" style="background: #00FF00;">FA.W</button>
            <button class="phenomena-toggle active" data-key="FA.A" title="Areal Flood Watch" style="background: #2E8B57;">FA.A</button>
            <button class="phenomena-toggle active" data-key="FA.Y" title="Areal Flood Advisory" style="background: #00FF7F;">FA.Y</button>
            <button class="phenomena-toggle active" data-key="MA.W" title="Marine Warning" style="background: #FFA500;">MA.W</button>
        </div>
    </div>
</div>
<div id="warnings-modal">
    <div id="warnings-modal-header">
        Warnings
        <button id="close-warnings">✖</button>
    </div>
    <div id="warnings-modal-content">
        <input type="text" id="warnings-search" placeholder="Search warnings..." style="width: 100%; margin-bottom: 10px; padding: 5px; border: 1px solid #ccc; border-radius: 3px;">
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
