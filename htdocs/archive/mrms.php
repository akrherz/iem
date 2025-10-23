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
  <li><strong>30 Sep 2025</strong>: Document the "Path Forward" for the MRMS hourly zip
  files.</li>
  <li><strong>24 Sep 2025</strong>: Attempting to consolidate documentation on this
  page and start to document an upcoming archive data removal of hourly zip files
  per Iowa State cloud storage changes.</li>
</ul>

<div class="row g-4">
  <div class="col-md-12">
    <div class="card h-100">
      <div class="card-header">
        <h5 class="card-title mb-0"><i class="bi bi-arrow-right-circle"></i> "Path Forward" for MRMS hourly zip archive</h5>
      </div>
      <div class="card-body">

<p class="card-text">The IEM has been providing an
archive of <a href="https://mrms.agron.iastate.edu">hourly MRMS zip files</a> since September
2019.  This archive consisted of some modest local storage caching recent data
and then the rest being made available via cloud storage.  Due to a quota change
with the cloud storage, this archive is no longer viable in its entirety. So here
is a listing of the path forward for this archive.</p>

<p class="card-text"><strong>27 Sep 2019 - 30 Oct 2020</strong>:  This portion of the archive is not
available via the NOAA AWS OpenData MRMS archive.  The data also represents a period
prior to a <a
href="https://mesonet.agron.iastate.edu/wx/afos/p.php?pil=PNSWSH&e=202009101318">major MRMS upgrade</a>
that happened, which makes it not as seemlessly comparable with MRMS data after.  NOAA
made a decision to not backfill this data to AWS OpenData for this reason.  There
is space locally to continue to host this data and it will be kept around until
perhaps better things are made available from NOAA...</p>

<p class="card-text"><strong>Nov 2020 - Present</strong>: This portion of the archive should be
available via the <a href="https://registry.opendata.aws/noaa-mrms-pds/">NOAA AWS
OpenData MRMS archive</a>.  There is limited utility for it to be kept around, but
some folks may have a usage for the convience factor of having everything zipped up
in one file.  So going forward, a very limited cache will be kept around, which should
be a month or two of data.  Presently, a cross checking process is running to ensure
the AWS archive contains everything found within this archive.  So you will notice
files start being removed once the cross check completes.</p>

</div></div></div>


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
