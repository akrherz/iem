<?php
define("IEM_APPID", 148);
require_once "../../config/settings.inc.php";

require_once "../../include/myview.php";
$t = new MyView();
$t->title = "Time Machine";
$t->thispage="archive-tm";

$t->headextra = <<<EOF
<link rel="stylesheet" href="/vendor/jquery-ui/1.11.4/jquery-ui.min.css">
<link rel="stylesheet" href="/vendor/jquery-ui/1.11.4/jquery-ui.theme.min.css">
<link rel="stylesheet" type="text/css" href="/vendor/select2/4.0.3/select2.min.css"/ >
EOF;
$t->jsextra = <<<EOF
<script src='/vendor/jquery-ui/1.11.4/jquery-ui.min.js'></script>
<script src="/vendor/select2/4.0.3/select2.min.js"></script>
<script src="/vendor/moment/2.13.0/moment.min.js"></script>
<script type="text/javascript" src="static.js?v=19"></script>
EOF;

$t->content = <<<EOF
<ul class="breadcrumb">
	<li><strong>IEM Time Machine</strong></li>
	<li class="active">Local: <span id="localtime"></span>, UTC: <span id="utctime"></span></li>
</ul>
<p style="margin-bottom: 5px;"><strong>IEM Time Machine:</strong> Adjust sliders 
to select a product of your choice from the archive.</p>

<form name="app">
<div class="row">
	<div class="col-sm-4" style="margin-bottom: 15px;">
	<select name="products" id="products"></select>	
	</div>
	<div class="col-sm-4" style="margin-bottom: 15px;"><div id="year_slider"><div id="year_handle" style="width: 2em;" class="ui-slider-handle"></div></div></div>
	<div class="col-sm-2" style="margin-bottom: 15px;"><div id="hour_slider"><div id="hour_handle" style="width: 3em;" class="ui-slider-handle"></div></div></div>
	<div class="col-sm-2" style="margin-bottom: 15px;"><div id="minute_slider"><div id="minute_handle" style="width: 2em;" class="ui-slider-handle"></div></div></div>
</div>
<div class="row">
	<div class="col-sm-12" style="margin-bottom: 15px;"><div id="day_slider"><div id="day_handle" style="width: 4em;" class="ui-slider-handle"></div></div></div>
</div>
<div class="row">
	<div class="col-sm-2 col-xs-3" style="margin-bottom: 15px;"><button class="btn btn-default" id="realtime">Show Latest</button></div>
	<div class="col-sm-1 col-xs-2" style="margin-bottom: 15px;">
		<button data-offset="-1" data-unit="year" class="btn btn-default" id="pyear"><i class="glyphicon glyphicon-arrow-left"></i> Year</button>
	</div>
	<div class="col-sm-1 col-xs-2" style="margin-bottom: 15px;">
		<button data-offset="-1" data-unit="day" class="btn btn-default" id="pday"><i class="glyphicon glyphicon-arrow-left"></i> Day</button>
	</div>
	<div class="col-sm-1 col-xs-2" style="margin-bottom: 15px;">
		<button data-offset="-1" data-unit="hour" class="btn btn-default" id="phour"><i class="glyphicon glyphicon-arrow-left"></i> Hour</button>
	</div>
	<div class="col-sm-2 col-xs-2" style="margin-bottom: 15px;">
		<button class="btn btn-default" id="prev"><i class="glyphicon glyphicon-arrow-left"></i> Previous</button>
	</div>
	<div class="col-sm-1 col-xs-2" style="margin-bottom: 15px;">
		<button class="btn btn-default" id="next">Next <i class="glyphicon glyphicon-arrow-right"></i></button>
	</div>
	<div class="col-sm-1 col-xs-2" style="margin-bottom: 15px;">
		<button data-offset="1" data-unit="hour" class="btn btn-default" id="nhour">Hour <i class="glyphicon glyphicon-arrow-right"></i></button>
	</div>
	<div class="col-sm-1 col-xs-2" style="margin-bottom: 15px;">
		<button data-offset="1" data-unit="day" class="btn btn-default" id="nday">Day <i class="glyphicon glyphicon-arrow-right"></i></button>
	</div>
	<div class="col-sm-1 col-xs-2" style="margin-bottom: 15px;">
		<button data-offset="1" data-unit="year" class="btn btn-default" id="nyear">Year <i class="glyphicon glyphicon-arrow-right"></i></button>
	</div>
</div>

<div class="row"><div class="col-md-12">
	<img id="imagedisplay" src="timemachine.png" class="img img-responsive"/>
</div></div>
</form>

EOF;
$t->render('single.phtml');
?>