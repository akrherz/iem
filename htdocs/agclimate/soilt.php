<?php
include("../../config/settings.inc.php");
include_once "../../include/myview.php";
$t = new MyView();
$t->thispage = "networks-agclimate";
$nounce = time();
$t->title = "ISU Soil Moisture County Temperature Estimates";
$t->content = <<<EOF
<h3>Recent 4 inch Soil Temperatures</h3>

<p>The following images are an interpolated analysis of county-by-county
average soil temperature at a four inch depth. You can find an archive
of these maps <a href="/timemachine/#57.0">here</a>.</p>

<p><img src="/data/soilt_day1.png?{$nounce}" class="img img-responsive"></p>
<p><img src="/data/soilt_day2.png?{$nounce}" class="img img-responsive"></p>
<p><img src="/data/soilt_day3.png?{$nounce}" class="img img-responsive"></p>
EOF;
$t->render('single.phtml');
?>
