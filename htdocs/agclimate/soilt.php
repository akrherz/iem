<?php
require_once "../../config/settings.inc.php";
require_once "../../include/myview.php";
$t = new MyView();
$nounce = time();
$t->title = "ISU Soil Moisture County Temperature Estimates";
$t->content = <<<EOF
<ol class="breadcrumb">
 <li><a href="/agclimate/">ISU Soil Moisture Network</a></li>
 <li class="active">Recent 4 inch Soil Temperatures</li>
</ol>

<p>The following maps are analyses of four inch depth soil temperatures.  These maps
are based on National Weather Service North American Mesoscale (NAM) forecast model
analyses and short term forecasts.  Iowa State Soil Moisture Network observations
are used to bias correct the model output after some quality control checks are made.</p>

<p><strong>Links:</strong> <a class="btn btn-default" href="/timemachine/#57.0">Archive of This Map</a>
<a class="btn btn-default" href="/agclimate/hist/daily.php">Observation Download</a>
<a class="btn btn-default" href="/agclimate/#soil04t">Real-time Map</a>
</p>

<h3>Past Three Days</h3>
<p><img src="/data/soilt_day1.png?{$nounce}" class="img img-responsive"></p>
<p><img src="/data/soilt_day2.png?{$nounce}" class="img img-responsive"></p>
<p><img src="/data/soilt_day3.png?{$nounce}" class="img img-responsive"></p>
EOF;
$t->render('single.phtml');
?>
