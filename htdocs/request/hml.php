<?php
require_once "../../config/settings.inc.php";
require_once "../../include/myview.php";
require_once "../../include/forms.php";
require_once "../../include/iemprop.php";
require_once "../../include/database.inc.php";

define("IEM_APPID", 164);
$t = new MyView();
$t->iemss = True;
$t->title = "Hydrological Markup Language (HML) Processed Data Download";

$bogus = 0;
$y1select = yearSelect(2012, date("Y"), "year1");
$m1select = monthSelect(1, "month1");
$d1select = daySelect(1, "day1");

$y2select = yearSelect(2012, date("Y"), "year2");
$m2select = monthSelect(date("m"), "month2");
$d2select = daySelect(date("d"), "day2");

$t->content = <<<EOM
<nav aria-label="breadcrumb">
  <ol class="breadcrumb">
    <li class="breadcrumb-item"><a href="/nws/">NWS Mainpage</a></li>
    <li class="breadcrumb-item active" aria-current="page">Download HML Processed Data</li>
  </ol>
</nav>

<header class="mb-4">
  <h1 class="h3 mb-3">Hydrological Markup Language Processed Data Download</h1>
  <p class="mb-2">The IEM attempts a high-fidelity processing and archival of river gauge observations and forecasts found within NWS HML products.</p>
  <p class="mb-3">The HML archive dates back to 2012.</p>
  <p class="mb-0">
    <a href="/cgi-bin/request/hml.py?help" class="btn btn-outline-primary"><i class="bi bi-file-text" aria-hidden="true"></i> Backend documentation</a>
  </p>
</header>

<div class="alert alert-info" role="status">
  Download results open in a new tab. Forecast requests are limited to a single UTC year at a time.
</div>

<form method="GET" action="/cgi-bin/request/hml.py" name="dl" target="_blank" class="mb-4">
  <div class="form2url mb-3"></div>

  <div class="row g-4">
    <div class="col-lg-6">
      <section class="card h-100 shadow-sm">
        <div class="card-body">
          <h2 class="h5 card-title">1. Select Station(s)</h2>
          <p class="text-body-secondary small">Choose one or more stations from the HML network for download.</p>
          <div id="iemss" data-network="HAS_HML" data-name="station" data-supports-all="0"></div>

          <fieldset class="mt-4">
            <legend class="h5">2. Select Data Type</legend>
            <div class="form-check">
              <input class="form-check-input" type="radio" name="kind" value="obs" checked id="obs">
              <label class="form-check-label" for="obs">Observations</label>
            </div>
            <div class="form-check">
              <input class="form-check-input" type="radio" name="kind" value="forecasts" id="forecasts">
              <label class="form-check-label" for="forecasts">Forecasts</label>
            </div>
          </fieldset>
        </div>
      </section>
    </div>
    <div class="col-lg-6">
      <section class="card h-100 shadow-sm">
        <div class="card-body">
          <div class="mb-4">
            <label for="tz" class="form-label h5 d-block mb-2">3. Timezone of Observations</label>
            <p class="form-text mt-0">Timestamps in the downloaded file will be converted to the timezone you select.</p>
            <select name="tz" id="tz" class="form-select">
              <option value="UTC">UTC Time</option>
              <option value="America/New_York">Eastern Time</option>
              <option value="America/Chicago">Central Time</option>
              <option value="America/Denver">Mountain Time</option>
              <option value="America/Los_Angeles">Western Time</option>
            </select>
          </div>

          <fieldset class="mb-4">
            <legend class="h5 mb-2">4. Select Start and End Time</legend>
            <p class="form-text mt-0">The start date is inclusive. The end date is not inclusive.</p>
            <div class="table-responsive">
              <table class="table table-sm align-middle mb-0">
                <thead>
                  <tr>
                    <th scope="col"></th>
                    <th scope="col">Year</th>
                    <th scope="col">Month</th>
                    <th scope="col">Day</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <th scope="row">Start</th>
                    <td>{$y1select}</td>
                    <td>{$m1select}</td>
                    <td>{$d1select}</td>
                  </tr>
                  <tr>
                    <th scope="row">End</th>
                    <td>{$y2select}</td>
                    <td>{$m2select}</td>
                    <td>{$d2select}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </fieldset>

          <div class="mb-4">
            <label for="fmt" class="form-label h5 d-block mb-2">5. Data Format</label>
            <select name="fmt" id="fmt" class="form-select">
              <option value="csv">Comma</option>
              <option value="excel">Excel</option>
            </select>
          </div>

          <div class="d-flex gap-2 flex-wrap">
            <button type="submit" class="btn btn-primary">Process Data Request</button>
            <button type="reset" class="btn btn-outline-secondary">Reset</button>
          </div>
        </div>
      </section>
    </div>
  </div>
</form>

<div class="row g-4">
  <div class="col-lg-6">
    <section class="card shadow-sm h-100">
      <div class="card-body">
        <h2 class="h5 card-title">Observation Data Columns</h2>
        <div class="table-responsive">
          <table class="table table-striped table-sm mb-0">
            <thead>
              <tr><th scope="col">Name</th><th scope="col">Description</th></tr>
            </thead>
            <tbody>
              <tr><th scope="row">station</th><td>5 character station identifier</td></tr>
              <tr><th scope="row">valid[timezone]</th><td>Timestamp of observation</td></tr>
              <tr><th scope="row"><code>Label for Values</code></th><td>Primary</td></tr>
              <tr><th scope="row"><code>Label for Values</code></th><td>Secondary</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>
  </div>
  <div class="col-lg-6">
    <section class="card shadow-sm h-100">
      <div class="card-body">
        <h2 class="h5 card-title">Forecast Data Columns</h2>
        <div class="table-responsive">
          <table class="table table-striped table-sm mb-0">
            <thead>
              <tr><th scope="col">Name</th><th scope="col">Description</th></tr>
            </thead>
            <tbody>
              <tr><th scope="row">station</th><td>5 character station identifier</td></tr>
              <tr><th scope="row">issued[timezone]</th><td>Timestamp of forecast issuance</td></tr>
              <tr><th scope="row">primaryname</th><td>Label for the primary forecast value</td></tr>
              <tr><th scope="row">primaryunits</th><td>Units for the primary forecast value</td></tr>
              <tr><th scope="row">secondaryname</th><td>Label for the secondary forecast value</td></tr>
              <tr><th scope="row">secondaryunits</th><td>Units for the secondary forecast value</td></tr>
              <tr><th scope="row">forecast_valid[timezone]</th><td>Timestamp of forecast valid</td></tr>
              <tr><th scope="row">primary_value</th><td>Primary forecast value</td></tr>
              <tr><th scope="row">secondary_value</th><td>Secondary forecast value</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>
  </div>
</div>
EOM;
$t->render('full.phtml');
