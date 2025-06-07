<?php
define("IEM_APPID", 148);
require_once "../../config/settings.inc.php";

require_once "../../include/myview.php";
$t = new MyView();
$t->title = "Time Machine";
$t->headextra = <<<EOM
<link rel="stylesheet" href="/vendor/nouislider/15.8.1/nouislider.min.css">
<link rel="stylesheet" href="index.css">
EOM;
$t->jsextra = <<<EOM
<script src="/vendor/nouislider/15.8.1/nouislider.min.js"></script>
<script src="/vendor/moment/2.13.0/moment.min.js"></script>
<script type="text/javascript" src="index.js"></script>
EOM;

$t->content = <<<EOM
<p style="margin-bottom: 5px;"><strong>IEM Time Machine:</strong> Select
the product of interest and adjust the time sliders or click the buttons to
navigate the archive.</p>

<div class="time-display">
    <div class="time-card">
        <div class="icon">🕒</div>
        <h4>Local Time</h4>
        <p id="localtime" class="time-text"></p>
    </div>
    <div class="time-card">
        <div class="icon">🌍</div>
        <h4>UTC Time</h4>
        <p id="utctime" class="time-text"></p>
    </div>
</div>

<form name="app">
<div class="row">
    <div class="col-sm-4" style="margin-bottom: 15px;">
    <select name="products" id="products"></select>	
    <div style="display: flex; justify-content: space-between; margin-top: 10px;">
        <button class="btn btn-default btn-sm" data-offset="-1" data-unit="minute"><i class="fa fa-arrow-left"></i> Previous</button>
        <button class="btn btn-default btn-sm" id="realtime">Show Latest</button>
        <button class="btn btn-default btn-sm" data-offset="1" data-unit="minute">Next <i class="fa fa-arrow-right"></i></button>
    </div>
    </div>
    <div class="col-sm-4" style="margin-bottom: 15px;">
        <label for="year_slider" style="display: flex; align-items: center; justify-content: space-between;">
            <button data-offset="-1" data-unit="year" class="btn btn-default btn-sm" id="pyear"><i class="fa fa-arrow-left"></i></button>
            <span class="year-label-text">Year</span>
            <button data-offset="1" data-unit="year" class="btn btn-default btn-sm" id="nyear"><i class="fa fa-arrow-right"></i></button>
        </label>
        <div id="year_slider"></div>
    </div>
    <div class="col-sm-2" style="margin-bottom: 15px;">
        <label for="hour_slider" style="display: flex; align-items: center; justify-content: space-between;">
            <button data-offset="-1" data-unit="hour" class="btn btn-default btn-sm" id="phour"><i class="fa fa-arrow-left"></i></button>
            <span class="hour-label-text">Hour</span>
            <button data-offset="1" data-unit="hour" class="btn btn-default btn-sm" id="nhour"><i class="fa fa-arrow-right"></i></button>
        </label>
        <div id="hour_slider"></div>
    </div>
    <div class="col-sm-2" style="margin-bottom: 15px;">
        <label for="minute_slider" style="display: flex; align-items: center; justify-content: space-between;">
            <button data-offset="-1" data-unit="minute" class="btn btn-default btn-sm" id="pminute"><i class="fa fa-arrow-left"></i></button>
            <span class="minute-label-text">Minute</span>
            <button data-offset="1" data-unit="minute" class="btn btn-default btn-sm" id="nminute"><i class="fa fa-arrow-right"></i></button>
        </label>
        <div id="minute_slider"></div>
    </div>
</div>
<div class="row">
    <div class="col-sm-12" style="margin-bottom: 15px;">
        <label for="day_slider" style="display: flex; align-items: center; justify-content: space-between;">
            <button data-offset="-1" data-unit="day" class="btn btn-default btn-sm" id="pday"><i class="fa fa-arrow-left"></i></button>
            <span class="day-label-text">Day</span>
            <button data-offset="1" data-unit="day" class="btn btn-default btn-sm" id="nday"><i class="fa fa-arrow-right"></i></button>
        </label>
        <div id="day_slider"></div>
    </div>
</div>

<div class="row"><div class="col-md-12">
    <img id="imagedisplay" src="timemachine.png" class="img img-responsive"/>
</div></div>

<!-- Loading indicator -->
<div id="loading-indicator" style="display: none;">Loading...</div>

</form>

EOM;
$t->render('single.phtml');
