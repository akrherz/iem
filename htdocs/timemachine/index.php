<?php
include("../../config/settings.inc.php");
include("../../include/myview.php");
$t = new MyView();
$t->title = "Time Machine";
define("IEM_APPID", 148);
$t->thispage="archive-tm";
$t->headextra = <<<EOF
<link rel="stylesheet" type="text/css" href="https://extjs.cachefly.net/ext/gpl/5.1.0/build/packages/ext-theme-neptune/build/resources/ext-theme-neptune-all.css"/>
<script type="text/javascript" src="https://extjs.cachefly.net/ext/gpl/5.1.0/build/ext-all.js"></script>
<script type="text/javascript" src="https://extjs.cachefly.net/ext/gpl/5.1.0/build/packages/ext-theme-neptune/build/ext-theme-neptune.js"></script>
<script type="text/javascript" src="static.js?v=18"></script>
EOF;

$t->content = <<<EOF
<style>
		.x-body{
		background-color: #fff;
		}
</style>
<p style="margin-bottom: 5px;"><strong>IEM Time Machine:</strong> Adjust sliders 
to select a product of your choice from the archive.</p>

<div class="row">
	<div class="col-sm-4" id="product_select"></div>
	<div class="col-sm-4" id="year_select"></div>
	<div class="col-sm-2" id="hour_select"></div>
	<div class="col-sm-2" id="minute_select"></div>
</div>
<div class="row" style="margin-bottom: 5px;">
	<div class="col-sm-12" id="day_select"></div>
</div>
<div class="row" style="margin-bottom: 5px;">
	<div class="col-xs-1" id="realtime"></div>
	<div class="col-xs-1" id="pyear"></div>
	<div class="col-xs-1" id="pday"></div>
	<div class="col-xs-1" id="phour"></div>
	<div class="col-xs-1" id="prev"></div>
	<div class="col-xs-3" id="displaydt"></div>
	<div class="col-xs-1" id="next"></div>
	<div class="col-xs-1" id="nhour"></div>
	<div class="col-xs-1" id="nday"></div>
	<div class="col-xs-1" id="nyear"></div>
</div>

<img id="imagedisplay" src="timemachine.png" class="img img-responsive"/>
EOF;
$t->render('single.phtml');
?>