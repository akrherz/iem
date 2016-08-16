<?php
include("../../config/settings.inc.php");
include_once "../../include/myview.php";
$t = new MyView();
$t->thispage = "networks-agclimate";
$nounce = time();
$t->title = "ISU Soil Moisture County Temperature Estimates";
$t->content = <<<EOF
<ol class="breadcrumb">
 <li><a href="/agclimate/">ISU Soil Moisture Network</a></li>
 <li class="active">Recent 4 inch Soil Temperatures</li>
</ol>

<p>The following images are an interpolated analysis of county-by-county
average soil temperature at a four inch depth.</p>

<p><strong>Links:</strong> <a class="btn btn-default" href="/timemachine/#57.0">Archive of This Map</a>
<a class="btn btn-default" href="/agclimate/hist/daily.php">Observation Download</a></p>

<h3>Past Three Days</h3>
<p><img src="/data/soilt_day1.png?{$nounce}" class="img img-responsive"></p>
<p><img src="/data/soilt_day2.png?{$nounce}" class="img img-responsive"></p>
<p><img src="/data/soilt_day3.png?{$nounce}" class="img img-responsive"></p>
EOF;
$t->render('single.phtml');
?>
