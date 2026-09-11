<?php
require_once "../../config/settings.inc.php";
require_once "../../include/myview.php";
require_once "../../include/forms.php";
require_once "../../include/database.inc.php";

$t = new MyView();
$t->iemss = True;
define("IEM_APPID", 162);

$t->title = "WMO BUFR Surface Station Data Download";

$ys1 = yearSelect(2024, date("Y"), "year1");
$ms1 = monthSelect("1", "month1");
$ds1 = daySelect("1", "day1");
$hs1 = gmtHourSelect("0", "hour1");
$ys2 = yearSelect(2024, date("Y"), "year2");
$ms2 = monthSelect(date("m"), "month2");
$ds2 = daySelect(date("d"), "day2");
$hs2 = gmtHourSelect("0", "hour2");

$t->content = <<<EOM
<nav aria-label="breadcrumb">
  <ol class="breadcrumb">
    <li class="breadcrumb-item"><a href="/other/">Other Mainpage</a></li>
    <li class="breadcrumb-item active" aria-current="page">WMO BUFR Surface Download</li>
  </ol>
</nav>

<header class="mb-4">
  <h1 class="h3 mb-3">WMO BUFR Surface Data Download</h1>
  <p class="mb-3">Use this form to retrieve archived surface observations from the WMO BUFR network.</p>
  <a class="btn btn-outline-primary" href="/cgi-bin/request/wmo_bufr_srf.py?help"><i class="bi bi-file-text" aria-hidden="true"></i> Backend documentation</a>
</header>

<form target="_blank" method="GET" action="/cgi-bin/request/wmo_bufr_srf.py" name="iemss" class="mb-4">
  <div class="form2url mb-3"></div>
  <input type="hidden" name="network" value="WMO_BUFR_SRF">

  <div class="row g-4">
    <div class="col-lg-7">
      <section class="card h-100 shadow-sm">
        <div class="card-body">
          <h2 class="h5 card-title">1. Select station(s)</h2>
          <p class="form-text mt-0">Choose one or more stations for the download.</p>
          <div id="iemss" data-network="WMO_BUFR_SRF"></div>
        </div>
      </section>
    </div>
    <div class="col-lg-5">
      <section class="card h-100 shadow-sm">
        <div class="card-body">
          <fieldset class="mb-4">
            <legend class="h5 mb-2">2. Select start and end time</legend>
            <div class="table-responsive">
              <table class="table table-sm align-middle mb-0">
                <thead>
                  <tr>
                    <th scope="col"></th>
                    <th scope="col">Year</th><th scope="col">Month</th><th scope="col">Day</th>
                    <th scope="col">Hour</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <th scope="row">Start</th>
                    <td>{$ys1}</td><td>{$ms1}</td><td>{$ds1}</td>
                    <td>{$hs1}<input type="hidden" name="minute1" value="0"></td>
                  </tr>
                  <tr>
                    <th scope="row">End</th>
                    <td>{$ys2}</td><td>{$ms2}</td><td>{$ds2}</td>
                    <td>{$hs2}<input type="hidden" name="minute2" value="0"></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </fieldset>

          <div class="mb-4">
            <label for="what" class="form-label h5 d-block">3. How to download/view?</label>
            <select name="what" id="what" class="form-select">
              <option value="txt">Download as Delimited Text File</option>
              <option value="excel">Download as Excel</option>
              <option value="html">View as HTML webpage</option>
            </select>
          </div>

          <div class="mb-4">
            <label for="delim" class="form-label h5 d-block">3a. Data delimitation</label>
            <p class="form-text mt-0">For delimited text files, choose how values are separated.</p>
            <select name="delim" id="delim" class="form-select">
              <option value="comma">Comma</option>
              <option value="space">Space</option>
              <option value="tab">Tab</option>
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

<section class="card shadow-sm mb-4">
  <div class="card-body">
    <h2 class="h5 card-title">Returned data columns</h2>
    <pre class="mb-0"><code>
utc_valid - Observation timestamp in UTC
station - Often WIGOS or guessed WIGOS identifier
tmpf - Air temperature in F
dwpf - Dew Point Temperature in F
drct - Wind Direction (degrees North)
sknt - Wind Speed (knots)
gust - Wind Gust (knots)
relh - Relative Humidity (%)
alti - Pressure Altimeter (inch)
pcpncnt - Precipitation Counter (inch)
pday - Precip for Day (inch)
pmonth - Precip for Month (inch)
srad - Solar Radiation (W/m^2)
tsoil_4in_f - Approx Four inch depth Soil Temp (F)
tsoil_8in_f - Approx Eight inch depth Soil Temp (F)
tsoil_16in_f - Approx Sixteen inch depth Soil Temp (F)
tsoil_20in_f - Approx Twenty inch depth Soil Temp (F)
tsoil_32in_f - Approx Thirty-Two inch depth Soil Temp (F)
tsoil_40in_f - Approx Forty inch depth Soil Temp (F)
tsoil_64in_f - Approx Sixty-Four inch depth Soil Temp (F)
tsoil_128in_f - Approx One Hundred Twenty-Eight inch depth Soil Temp (F)
skyc1 - Sky Cover 1
skyc2 - Sky Cover 2
skyc3 - Sky Cover 3
skyc4 - Sky Cover 4
skyl1 - Sky Level 1 (ft)
skyl2 - Sky Level 2 (ft)
skyl3 - Sky Level 3 (ft)
skyl4 - Sky Level 4 (ft)
srad_1h_j - Solar Radiation 1 hour sum (J/m^2)
</code></pre>
  </div>
</section>
EOM;
$t->render('full.phtml');
