<?php
require_once "../../config/settings.inc.php";
require_once "../../include/myview.php";
$t = new MyView();
$nounce = time();
$t->title = "ISU Soil Moisture County Temperature Estimates";
$t->headextra = <<<EOM
<link rel="stylesheet" href="soilt.css" />
EOM;
$t->jsextra = <<<EOM
<script type="text/javascript" src="soilt.js"></script>
EOM;
$t->content = <<<EOF
<ol class="breadcrumb">
 <li><a href="/agclimate/">ISU Soil Moisture Network</a></li>
 <li class="active">County 4 inch Soil Temperature Maps</li>
</ol>

<p>This page presents daily soil temperature analysis maps.  The left hand
column plots combine ISU Soil Moisture Network observations and bias corrected
NWS NAM forecast model analyses to produce a higher resolution plot.  The right
hand plots are simple GFS forecast model outputs without any bias correction.</p>

<p><strong>Links:</strong> <a class="btn btn-default" href="/timemachine/#57.0">Archive of This Map</a>
<a class="btn btn-default" href="/agclimate/hist/daily.php">Observation Download</a>
<a class="btn btn-default" href="/agclimate/#soil04t">Real-time Map</a>
</p>

<!-- The Modal -->
<div id="myModal" class="modal">

  <!-- The Close Button -->
  <span class="close">&times;</span>

  <!-- Modal Content (The Image) -->
  <img class="modal-content" id="img01">

  <!-- Modal Caption (Image Text) -->
  <div id="caption"></div>
</div>

<div class="row clickme">
<div class="col-md-6">
    <h3>Past Three Day Observations</h3>
    <p><img src="/data/soilt_day1.png?{$nounce}" class="img img-responsive"></p>
    <p><img src="/data/soilt_day2.png?{$nounce}" class="img img-responsive"></p>
    <p><img src="/data/soilt_day3.png?{$nounce}" class="img img-responsive"></p>
</div>
<div class="col-md-6">
    <h3>GFS Forecast</h3>
    <p><img src="/data/forecast/gfs_soilt_day_f0.png?{$nounce}" class="img img-responsive"></p>
    <p><img src="/data/forecast/gfs_soilt_day_f1.png?{$nounce}" class="img img-responsive"></p>
    <p><img src="/data/forecast/gfs_soilt_day_f2.png?{$nounce}" class="img img-responsive"></p>
    <p><img src="/data/forecast/gfs_soilt_day_f3.png?{$nounce}" class="img img-responsive"></p>
    <p><img src="/data/forecast/gfs_soilt_day_f4.png?{$nounce}" class="img img-responsive"></p>
    <p><img src="/data/forecast/gfs_soilt_day_f5.png?{$nounce}" class="img img-responsive"></p>
    <p><img src="/data/forecast/gfs_soilt_day_f6.png?{$nounce}" class="img img-responsive"></p>
    <p><img src="/data/forecast/gfs_soilt_day_f7.png?{$nounce}" class="img img-responsive"></p>
    <p><img src="/data/forecast/gfs_soilt_day_f8.png?{$nounce}" class="img img-responsive"></p>
    <p><img src="/data/forecast/gfs_soilt_day_f9.png?{$nounce}" class="img img-responsive"></p>
    <p><img src="/data/forecast/gfs_soilt_day_f10.png?{$nounce}" class="img img-responsive"></p>
    <p><img src="/data/forecast/gfs_soilt_day_f11.png?{$nounce}" class="img img-responsive"></p>
    <p><img src="/data/forecast/gfs_soilt_day_f12.png?{$nounce}" class="img img-responsive"></p>
    <p><img src="/data/forecast/gfs_soilt_day_f13.png?{$nounce}" class="img img-responsive"></p>
    <p><img src="/data/forecast/gfs_soilt_day_f14.png?{$nounce}" class="img img-responsive"></p>
    <p><img src="/data/forecast/gfs_soilt_day_f15.png?{$nounce}" class="img img-responsive"></p>
</div>
</div>

EOF;
$t->render('full.phtml');
