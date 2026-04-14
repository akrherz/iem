<?php
require_once "../config/settings.inc.php";
require_once "../include/myview.php";
$t = new MyView();
define("IEM_APPID", 61);
$t->title = "Information Mainpage";

$t->content = <<<EOM
<div class="container-fluid py-3">
  <h2 class="h3 mb-4">Information/Documents</h2>

  <div class="row g-4">
    <div class="col-12 col-md-6">
      <div class="card h-100">
        <div class="card-body">
          <h3 class="h5 card-title">Quick Links</h3>
          <ul class="list-group list-group-flush mb-3">
            <li class="list-group-item"><a href="/info/iem.php">IEM Info/Background</a></li>
            <li class="list-group-item">
            <i class="bi bi-book"></i> "Mastering the Mesonet" documentation kindly written by Jonathan Sailor, March 2026.
            <a href="/pickup/mastering_mesonet/Mastering-the-Mesonet.pdf">PDF</a> or
            <a href="/pickup/mastering_mesonet/Mastering-the-Mesonet.epub">ePub</a>
            </li>
            <li class="list-group-item"><a href="/info/links.php">Links</a></li>
            <li class="list-group-item"><a href="/info/variables.phtml">Variables Collected</a></li>
          </ul>

          <p class="mb-0">Information about requesting a <a href="/request/ldm.php">real-time data feed</a>.</p>
        </div>
      </div>
    </div>

    <div class="col-12 col-md-6">
      <div class="card h-100">
        <div class="card-body">
          <h3 class="h5 card-title">Station Locations (graphical)</h3>
          <ul class="list-group list-group-flush">
            <li class="list-group-item"><a href="/sites/locate.php?network=IA_ASOS">ASOS Locations</a></li>
            <li class="list-group-item"><a href="/sites/locate.php?network=IA_RWIS">RWIS Locations</a></li>
            <li class="list-group-item"><a href="/sites/locate.php?network=IA_COOP">COOP Locations</a></li>
            <li class="list-group-item"><a href="/sites/locate.php?network=ISUSM">ISU Soil Moisture Locations</a></li>
          </ul>
        </div>
      </div>
    </div>

    <div class="col-12 col-md-6">
      <div class="card h-100">
        <div class="card-body">
          <h3 class="h5 card-title">IEM Server Information</h3>
          <ul class="list-group list-group-flush">
            <li class="list-group-item"><a href="/usage/">Webfarm Statistics</a></li>
          </ul>
        </div>
      </div>
    </div>

    <div class="col-12 col-md-6">
      <div class="card h-100">
        <div class="card-body">
          <h3 class="h5 card-title">Papers/Presentations</h3>
          <ul class="list-group list-group-flush">
            <li class="list-group-item"><a href="/present/">IEM Presentation Archive</a></li>
            <li class="list-group-item"><a href="/docs/unidata2006/">2006 Unidata Equipment Grant Report</a></li>
            <li class="list-group-item"><a href="/docs/unidata2021/">2021 Unidata Equipment Grant Report</a></li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</div>
EOM;
$t->render('single.phtml');
