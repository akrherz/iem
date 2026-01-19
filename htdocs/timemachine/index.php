<?php
define("IEM_APPID", 148);
require_once "../../config/settings.inc.php";

require_once "../../include/myview.php";
$t = new MyView();
$t->title = "Time Machine";
$t->headextra = <<<EOM
<link rel="stylesheet" href="index.css">
EOM;
$t->jsextra = <<<EOM
<script src="/vendor/moment/2.13.0/moment.min.js"></script>
<script type="text/javascript" src="index.js?v=2"></script>
EOM;

$t->content = <<<EOM
<p style="margin-bottom: 5px;"><strong>IEM Time Machine:</strong> Select
the product of interest and use the time controls below to
navigate the archive.</p>

<form name="app">
<div class="row align-items-center" style="margin-bottom: 15px;">
    <div class="col-lg-4 col-md-6 order-md-2" style="margin-bottom: 10px;">
        <div class="time-display" style="flex-direction: column; gap: 10px;">
            <div class="time-card" style="padding: 5px 10px;">
                <div class="icon">🕒</div>
                <h4 style="font-size: 0.9rem; margin: 0 5px 0 0;">Local</h4>
                <p id="localtime" class="time-text" style="font-size: 0.9rem;"></p>
            </div>
            <div class="time-card" style="padding: 5px 10px;">
                <div class="icon">🌍</div>
                <h4 style="font-size: 0.9rem; margin: 0 5px 0 0;">UTC</h4>
                <p id="utctime" class="time-text" style="font-size: 0.9rem;"></p>
            </div>
        </div>
    </div>
    <div class="col-lg-8 col-md-6 order-md-1" style="margin-bottom: 10px;">
        <select name="products" id="products" class="form-select" style="margin-bottom: 10px;"></select>
        <div style="display: flex; justify-content: center; gap: 10px; flex-wrap: wrap;">
            <button class="btn btn-secondary btn-sm" data-offset="-1" data-unit="minute"><i class="bi bi-arrow-left" aria-hidden="true"></i> Previous</button>
            <button class="btn btn-secondary btn-sm" id="realtime">Show Latest</button>
            <button class="btn btn-secondary btn-sm" data-offset="1" data-unit="minute">Next <i class="bi bi-arrow-right" aria-hidden="true"></i></button>
        </div>
    </div>
</div>

<div class="row" style="margin-top: 20px;">
    <div class="col-lg col-md-4 col-sm-6" style="margin-bottom: 15px;">
        <div class="time-control">
            <button data-offset="-1" data-unit="year" class="btn btn-secondary btn-sm" aria-label="Previous year"><i class="bi bi-arrow-left" aria-hidden="true"></i></button>
            <span class="time-label">Year: <span id="year-value" class="time-value"></span></span>
            <button data-offset="1" data-unit="year" class="btn btn-secondary btn-sm" aria-label="Next year"><i class="bi bi-arrow-right" aria-hidden="true"></i></button>
        </div>
    </div>
    <div class="col-lg col-md-4 col-sm-6" style="margin-bottom: 15px;" id="month-control">
        <div class="time-control">
            <button data-offset="-1" data-unit="month" class="btn btn-secondary btn-sm" aria-label="Previous month"><i class="bi bi-arrow-left" aria-hidden="true"></i></button>
            <span class="time-label">Month: <span id="month-value" class="time-value"></span></span>
            <button data-offset="1" data-unit="month" class="btn btn-secondary btn-sm" aria-label="Next month"><i class="bi bi-arrow-right" aria-hidden="true"></i></button>
        </div>
    </div>
    <div class="col-lg col-md-4 col-sm-6" style="margin-bottom: 15px;" id="day-control">
        <div class="time-control">
            <button data-offset="-1" data-unit="day" class="btn btn-secondary btn-sm" aria-label="Previous day"><i class="bi bi-arrow-left" aria-hidden="true"></i></button>
            <span class="time-label">Day: <span id="day-value" class="time-value"></span></span>
            <button data-offset="1" data-unit="day" class="btn btn-secondary btn-sm" aria-label="Next day"><i class="bi bi-arrow-right" aria-hidden="true"></i></button>
        </div>
    </div>
    <div class="col-lg col-md-4 col-sm-6" style="margin-bottom: 15px;" id="hour-control">
        <div class="time-control">
            <button data-offset="-1" data-unit="hour" class="btn btn-secondary btn-sm" aria-label="Previous hour"><i class="bi bi-arrow-left" aria-hidden="true"></i></button>
            <span class="time-label">Hour: <span id="hour-value" class="time-value"></span></span>
            <button data-offset="1" data-unit="hour" class="btn btn-secondary btn-sm" aria-label="Next hour"><i class="bi bi-arrow-right" aria-hidden="true"></i></button>
        </div>
    </div>
    <div class="col-lg col-md-4 col-sm-6" style="margin-bottom: 15px;" id="minute-control">
        <div class="time-control">
            <button data-offset="-1" data-unit="minute" class="btn btn-secondary btn-sm" aria-label="Previous minute"><i class="bi bi-arrow-left" aria-hidden="true"></i></button>
            <span class="time-label">Minute: <span id="minute-value" class="time-value"></span></span>
            <button data-offset="1" data-unit="minute" class="btn btn-secondary btn-sm" aria-label="Next minute"><i class="bi bi-arrow-right" aria-hidden="true"></i></button>
        </div>
    </div>
</div>

<div class="row"><div class="col-md-12">
    <img id="imagedisplay" src="timemachine.png" class="img-fluid"/>
</div></div>

<!-- Loading indicator -->
<div id="loading-indicator" style="display: none;">Loading...</div>

</form>

EOM;
$t->render('full.phtml');
