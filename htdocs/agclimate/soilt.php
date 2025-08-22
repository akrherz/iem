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
<script type="module" src="soilt.module.js"></script>
EOM;
$t->content = <<<EOM
<nav aria-label="breadcrumb">
  <ol class="breadcrumb">
    <li class="breadcrumb-item"><a href="/agclimate/">ISU Soil Moisture Network</a></li>
    <li class="breadcrumb-item active" aria-current="page">County 4 inch Soil Temperature Maps</li>
  </ol>
</nav>

<h1 class="mb-3">County 4 inch Soil Temperature Maps</h1>
<h2 class="h5">About These Maps</h2>
<p>This page presents daily soil temperature analysis maps. The left column combines ISU Soil Moisture Network observations and bias-corrected NWS NAM forecast model analyses for higher resolution. The right column shows simple GFS forecast model outputs without bias correction.</p>

<div class="mb-3">
  <strong>Links:</strong>
  <a class="btn btn-outline-secondary mb-1" href="/timemachine/?product=57">Archive of This Map</a>
  <a class="btn btn-outline-secondary mb-1" href="/agclimate/hist/daily.php">Observation Download</a>
  <a class="btn btn-outline-secondary mb-1" href="/agclimate/#soil04t">Real-time Map</a>
</div>

<!-- The Modal -->
<div id="myModal" class="modal" role="dialog" aria-modal="true" aria-labelledby="caption">
  <span class="close" aria-label="Close dialog">&times;</span>
  <img class="modal-content" id="img01" alt="Soil temperature map preview">
  <div id="caption"></div>
</div>

<div class="row g-3 clickme">
  <div class="col-12 col-md-6">
    <h2 class="h5">Past Three Day Observations</h2>
    <img src="/data/soilt_day1.png?{$nounce}" class="img-fluid mb-3" alt="Soil temperature map for day 1">
    <img src="/data/soilt_day2.png?{$nounce}" class="img-fluid mb-3" alt="Soil temperature map for day 2">
    <img src="/data/soilt_day3.png?{$nounce}" class="img-fluid mb-3" alt="Soil temperature map for day 3">
  </div>
  <div class="col-12 col-md-6">
    <h2 class="h5">GFS Forecast</h2>
    <img src="/data/forecast/gfs_soilt_day_f0.png?{$nounce}" class="img-fluid mb-3" alt="GFS soil temperature forecast day 0">
    <img src="/data/forecast/gfs_soilt_day_f1.png?{$nounce}" class="img-fluid mb-3" alt="GFS soil temperature forecast day 1">
    <img src="/data/forecast/gfs_soilt_day_f2.png?{$nounce}" class="img-fluid mb-3" alt="GFS soil temperature forecast day 2">
    <img src="/data/forecast/gfs_soilt_day_f3.png?{$nounce}" class="img-fluid mb-3" alt="GFS soil temperature forecast day 3">
    <img src="/data/forecast/gfs_soilt_day_f4.png?{$nounce}" class="img-fluid mb-3" alt="GFS soil temperature forecast day 4">
    <img src="/data/forecast/gfs_soilt_day_f5.png?{$nounce}" class="img-fluid mb-3" alt="GFS soil temperature forecast day 5">
    <img src="/data/forecast/gfs_soilt_day_f6.png?{$nounce}" class="img-fluid mb-3" alt="GFS soil temperature forecast day 6">
    <img src="/data/forecast/gfs_soilt_day_f7.png?{$nounce}" class="img-fluid mb-3" alt="GFS soil temperature forecast day 7">
    <img src="/data/forecast/gfs_soilt_day_f8.png?{$nounce}" class="img-fluid mb-3" alt="GFS soil temperature forecast day 8">
    <img src="/data/forecast/gfs_soilt_day_f9.png?{$nounce}" class="img-fluid mb-3" alt="GFS soil temperature forecast day 9">
    <img src="/data/forecast/gfs_soilt_day_f10.png?{$nounce}" class="img-fluid mb-3" alt="GFS soil temperature forecast day 10">
    <img src="/data/forecast/gfs_soilt_day_f11.png?{$nounce}" class="img-fluid mb-3" alt="GFS soil temperature forecast day 11">
    <img src="/data/forecast/gfs_soilt_day_f12.png?{$nounce}" class="img-fluid mb-3" alt="GFS soil temperature forecast day 12">
    <img src="/data/forecast/gfs_soilt_day_f13.png?{$nounce}" class="img-fluid mb-3" alt="GFS soil temperature forecast day 13">
    <img src="/data/forecast/gfs_soilt_day_f14.png?{$nounce}" class="img-fluid mb-3" alt="GFS soil temperature forecast day 14">
    <img src="/data/forecast/gfs_soilt_day_f15.png?{$nounce}" class="img-fluid mb-3" alt="GFS soil temperature forecast day 15">
  </div>
</div>

EOM;
$t->render('full.phtml');
