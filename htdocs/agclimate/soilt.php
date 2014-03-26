<?php
include("../../config/settings.inc.php");
include_once "../../include/myview.php";
$t = new MyView();
$t->thispage = "networks-agclimate";
$nounce = time();
$t->content = <<<EOF
<h3>Recent 4 inch Soil Temperatures</h3>

<p>The following images are an interpolated analysis of county-by-county
average soil temperature at a four inch depth.</p>

<p><img src="/data/soilt_day1.png?{$nounce}"></p>
<p><img src="/data/soilt_day2.png?{$nounce}"></p>
<p><img src="/data/soilt_day3.png?{$nounce}"></p>
EOF;
$t->render('single.phtml');
?>
