<?php
require_once "../../config/settings.inc.php";
require_once "../../include/myview.php";
$t = new MyView();
$t->title = "IEM Provided MRMS Archives";

$d = date("Y/m/d");

$t->content = <<<EOM
<nav aria-label="breadcrumb">
  <ol class="breadcrumb">
    <li class="breadcrumb-item"><a href="/archive/">Archive</a></li>
    <li class="breadcrumb-item active" aria-current="page">MRMS Archives</li>
  </ol>
</nav>

<h3>IEM Provided MRMS Archives</h3>

<h4>Archive Changelog</h4>
<ul>
  <li><strong>24 Sep 2025</strong>: Attempting to consolidate documentation on this
  page and start to document an upcoming archive data removal of hourly zip files
  per Iowa State cloud storage changes.</li>
</ul>

<h4>Archive Info</h4>

<div class="row g-4">
  <div class="col-md-6">
    <div class="card h-100">
      <div class="card-header">
        <h5 class="card-title mb-0"><i class="bi bi-info-circle"></i> MRMS Project Overview</h5>
      </div>
      <div class="card-body">
        <p class="card-text">The <a href="https://www.nssl.noaa.gov/projects/mrms/">MRMS Project</a> is
        an important part of the IEM's data curation effort. It directly drives the
        rainfall product within the <a href="https://dailyerosion.org">Daily Erosion Project</a>
        and is used in a variety of other applications. The IEM has been archiving and
        generating products from MRMS since the early days running at NSSL prior to being
        operationalized by the NWS NCEP.</p>

<p class="card-text">The NSSL MRMS website has a handy
<a href="https://www.nssl.noaa.gov/projects/mrms/operational/tables.php">Grib Table Listing</a>,
which helps with knowing what is available and grib file units.</p>
        </div>
    </div>
  </div>

  <div class="col-md-6">
    <div class="card h-100">
      <div class="card-header">
        <h5 class="card-title mb-0"><i class="bi bi-cloud"></i> AWS OpenData Archive</h5>
      </div>
      <div class="card-body">
        <p class="card-text">Starting in October 2020, MRMS started to be archived at
        <a href="https://registry.opendata.aws/noaa-mrms-pds/">AWS OpenData</a>, which
        obsoleted much of the utility of IEM's raw grib product archives. However, this
        archive does not include what the IEM archived prior to Oct 2020 back to about
        Sep 2019.</p>
      </div>
    </div>
  </div>

  <div class="col-md-6">
    <div class="card h-100">
      <div class="card-header">
        <h5 class="card-title mb-0"><i class="bi bi-archive"></i> Complete Hourly Zip Archives</h5>
      </div>
      <div class="card-body">
        <p class="card-text">Starting September 2019, the IEM started creating hourly zip file archives
        of all MRMS products distributed over LDM on the <a href="https://mrms.agron.iastate.edu">mrms.agron.iastate.edu</a>
        website. This service utilized an <i>unlimited</i> ISU campus storage option called CyBox.</p>
        <div class="alert alert-warning mt-3" role="alert">
          <i class="bi bi-exclamation-triangle"></i> <strong>Important:</strong> This service will no longer be unlimited starting
          in January 2026 and the archive is too large to host within existing infrastructure
          at ISU. So much of the archive <strong>will be deleted</strong> starting in 2026.
          Thankfully, most of this archive is already at AWS OpenData, but the IEM is
          attempting to get the archive prior to Oct 2020 uploaded there prior to deletion!
        </div>
      </div>
    </div>
  </div>

  <div class="col-md-6">
    <div class="card h-100">
      <div class="card-header">
        <h5 class="card-title mb-0"><i class="bi bi-server"></i> MTArchive Site</h5>
      </div>
      <div class="card-body">
        <p class="card-text">To support the Daily Erosion Project and other applications, the IEM
        archived a select number of MRMS grib fields at per UTC date trees on the
        <a href="https://mtarchive.geol.iastate.edu/{$d}/mrms/ncep/">MTArchive site</a>
        , which contains products back to October 2014 (NCEP implementation) and also
        a "Tile2" binary file (which covered Iowa) from the NSSL days.</p>

        <p class="card-text">The MTArchive site also contains an <a href="https://mtarchive.geol.iastate.edu/2001/11/01/mrms/reanalysis/">archive example</a>
        of the <a href="https://osf.io/9gzp2/">MRMS ReAnalysis</a>, but a more useful
        copy exists on <a href="https://registry.opendata.aws/noaa-oar-myrorss-pds/">AWS OpenData</a>.</p>
      </div>
    </div>
  </div>

  <div class="col-md-6">
    <div class="card h-100">
      <div class="card-header">
        <h5 class="card-title mb-0"><i class="bi bi-clock"></i> Real-time Files</h5>
      </div>
      <div class="card-body">
        <p class="card-text">The IEM also has a cache of near realtime grib files on
        <a href="http://metfs1.agron.iastate.edu/data/mrms/">metfs1 service</a>,
        but its utility is not as useful as what you can find at the
        official <a href="https://mrms.ncep.noaa.gov/data/">MRMS Data Website</a>.</p>
      </div>
    </div>
  </div>
</div>

EOM;
$t->render('single.phtml');
