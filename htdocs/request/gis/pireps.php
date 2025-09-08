<?php 
require_once "../../../config/settings.inc.php";
require_once "../../../include/myview.php";
require_once "../../../include/forms.php";
define("IEM_APPID", 111);

$t = new MyView();
$t->iemss = True;
$t->iem_resource = "PIREPS";
$t->title = "Download PIREPs";
$artcc = Array(
    "ZAB"=> "[ZAB] ALBUQUERQUE",
    "ZAN"=> "[ZAN] ANCHORAGE",
    "ZAU"=> "[ZAU] CHICAGO",
    "ZBW"=> "[ZBW] BOSTON ",
    "ZDC"=> "[ZDC] WASHINGTON",
    "ZDV"=> "[ZDV] DENVER",
    "ZFW"=> "[ZFW] FORT WORTH",
    "ZHU"=> "[ZHU] HOUSTON",
    "ZID"=> "[ZID] INDIANAPOLIS",
    "ZJX"=> "[ZJX] JACKSONVILLE",
    "ZKC"=> "[ZKC] KANSAS CITY",
    "ZLA"=> "[ZLA] LOS ANGELES",
    "ZLC"=> "[ZLC] SALT LAKE CITY",
    "ZMA"=> "[ZMA] MIAMI",
    "ZME"=> "[ZME] MEMPHIS",
    "ZMP"=> "[ZMP] MINNEAPOLIS",
    "ZNY"=> "[ZNY] NEW YORK",
    "ZOA"=> "[ZOA] OAKLAND",
    "ZOB"=> "[ZOB] CLEVELAND ",
    "ZSE"=> "[ZSE] SEATTLE",
    "ZTL"=> "[ZTL] ATLANTA",
    "_ALL" => "No ARTCC Filter",
);
$artccSelect = make_select("artcc", "_ALL", $artcc);

$content = <<<EOM
<nav aria-label="breadcrumb">
    <ol class="breadcrumb">
        <li class="breadcrumb-item"><a href="/nws/">NWS Mainpage</a></li>
        <li class="breadcrumb-item active" aria-current="page">Archived Pilot Reports (PIREPs)</li>
    </ol>
</nav>

<p>The IEM attempts to process a feed of Pilot Reports (PIREPs). This
processing is done via the <a href="https://github.com/akrherz/pyIEM/blob/main/src/pyiem/nws/products/pirep.py">PyIEM Library</a>.
Sadly, there is not strict coherence to a format specification and so a 
number of reports are simply unparsable.  This archive should not be
considered 'complete'.</p>

<div class="alert alert-info">
 <i class="bi bi-exclamation-triangle" aria-hidden="true"></i> The PIREP parsing library that decodes the location information into a latitude
 and longitude is crude.  It does not properly account for magnetic north and may
 also have errors with VOR baseline locations.  This download interface provides
 the raw undecoded PIREP reports, so users that have more sophisticated location
 calculators are encouraged to process them for yourself.
</div>

<p>Due to filesize and speed, you can only request up to 120 days of data
at a time!  If you request data with the spatial filter, you can download
longer periods of data. <a href="/cgi-bin/request/gis/pireps.py?help"
class="btn btn-secondary"><i class="bi bi-file-text" aria-hidden="true"></i> Backend documentation</a>
exists for those wishing to script against this service.</p>

<p><strong>Related:</strong>
<a class="btn btn-primary" href="cwas.phtml">CWSU Center Weather Advisories</a>
<a class="btn btn-primary" href="awc_gairmets.phtml">Graphical AIRMETs</a>
<a class="btn btn-primary" href="awc_sigmets.phtml">SIGMETs</a>
<a class="btn btn-primary" href="/request/taf.php">TAFs</a>
<a class="btn btn-primary" href="/request/tempwind_aloft.php">Temp/Winds Aloft</a>
</p>

<form method="GET" action="/cgi-bin/request/gis/pireps.py">
<div class="form2url"></div>

<h4>Select time interval</h4>
<i>(Times are in UTC.)</i>
<div class="table-responsive">
<table class="table">
<thead>
    <tr>
    <th colspan="6">Time Interval</th>
    <th>Format</th>
    <th>Filters (Optional)</th>
    </tr>
</thead>
<tr>
    <th></th>
    <th>Year</th><th>Month</th><th>Day</th>
    <th>Hour</th><th>Minute</th>
    <td rowspan="3">
        <select name="fmt" class="form-select form-select-sm">
            <option value="shp">ESRI Shapefile</option>
            <option value="csv">Comma Delimited</option>
        </select>
    </td>
    <td rowspan="3">
        <div class="card border-secondary p-2">
            <div class="d-flex justify-content-between align-items-start">
                <div>
                    <h6 class="mb-1">Filters (optional)</h6>
                    <div class="form-text">Use either ARTCC, Lon/Lat, or both.</div>
                </div>
                <div id="filter-summary" class="text-end">
                    <span class="badge bg-secondary">No filters</span>
                </div>
            </div>

            <div class="mt-2">
                <div class="form-check mb-2">
                    <input class="form-check-input" type="checkbox" name="filter" value="1" id="filter">
                    <label class="form-check-label" for="filter">Enable Lon/Lat Filter</label>
                </div>

                <div id="spatialfilter" class="d-none mb-3">
                    <div class="row g-2 align-items-center">
                        <div class="col-auto">
                            <label for="degrees" class="form-label mb-0 visually-hidden">Radius (degrees)</label>
                            <div class="input-group input-group-sm">
                                <span class="input-group-text">Radius</span>
                                <input class="form-control" type="text" id="degrees" name="degrees" size="5" value="3.0" aria-label="degrees">
                                <span class="input-group-text">deg</span>
                            </div>
                            <div class="invalid-feedback">Enter a radius in degrees (&gt;=0).</div>
                        </div>

                        <div class="col-auto">
                            <label for="lon" class="form-label mb-0 visually-hidden">Longitude</label>
                            <div class="input-group input-group-sm">
                                <span class="input-group-text">Lon</span>
                                <input class="form-control" type="text" id="lon" name="lon" size="10" value="-91.99" aria-label="longitude">
                            </div>
                            <div class="invalid-feedback">Longitude must be between -180 and 180.</div>
                        </div>

                        <div class="col-auto">
                            <label for="lat" class="form-label mb-0 visually-hidden">Latitude</label>
                            <div class="input-group input-group-sm">
                                <span class="input-group-text">Lat</span>
                                <input class="form-control" type="text" id="lat" name="lat" size="10" value="41.99" aria-label="latitude">
                            </div>
                            <div class="invalid-feedback">Latitude must be between -90 and 90.</div>
                        </div>
                    </div>
                    <div class="form-text mt-2">Filter reports to a latitude/longitude circle centered at the point (Lon, Lat) with the radius in degrees.</div>
                </div>

                <div class="mb-1">
                    <label for="artcc" class="form-label mb-1">ARTCC Filter</label>
                    <div>{$artccSelect}</div>
                    <div class="form-text">Optional: pick an ARTCC to further restrict results. You may use this with or without the Lon/Lat filter.</div>
                </div>
            </div>
        </div>
    </td>
</tr>

<tr>
EOM;
$content .= "
    <th>Start:</th>
    <td>
     ". yearSelect(2000, date("Y"), "year1") ."
    </td>
    <td>
     ". monthSelect(1, "month1") ."
    </td>
    <td>
     ". daySelect(1, "day1") ."
    </td>
    <td>
     ". gmtHourSelect(0, "hour1") ."
    </td>
    <td>
     ". minuteSelect(0, "minute1") ."
    </td>
  </tr>

  <tr>
    <th>End:</th>
    <td>
     ". yearSelect(2000, date("Y"), "year2") ."
    </td>
    <td>
     ". monthSelect(date("m"), "month2") ."
    </td>
    <td>
     ". daySelect(date("d"), "day2") ."
    </td>
    <td>
     ". gmtHourSelect(23, "hour2") ."
    </td>
    <td>
     ". minuteSelect(59, "minute2") ."
    </td>
  </tr>
</table>
</div>";

$content .= <<<EOM
<p>
    <button type="submit" class="btn btn-success">Giveme data right now!</button>
</p>
</form>

<h4>Shapefile DBF schema:</h4>
<pre>
Field 0: Type=C/String, Title='VALID', Timestamp in UTC
Field 1: Type=C/String, Title='URGENT', Was this an urgent PIREP
Field 2: Type=C/String, Title='AIRCRAFT', Reported Aircraft type
Field 3: Type=C/String, Title='REPORT', The PIREP Report
Field 4: Type=C/String, Title='ICING', The icing /IC portion of the PIREP
Field 5: Type=C/String, Title='TURB', The turbulence /TB portion of the PIREP
Field 6: Type=C/String, Title='ARTCC', The ARTCC identifier, when applicable.
Field 7: Type=N/Double, Title='LAT', Latitude
Field 8: Type=N/Double, Title='LON', Longitude 
Field 9: Type=C/String, Title='PROD_ID', The IEM NWS text product identifier.
</pre>

<h4>Archive notes:</h4>
<ul>
 <li>Archive starts December 2000</li>
 <li><strong>11 Feb 2025:</strong> An issue was found with the location of
 the navaid <code>FLM</code>.  This resulted in PIREPs referencing that navaid
 being placed in Florida.  This has been corrected and the archive was
 reprocessed to fix this issue.</li>
 <li><strong>31 July 2024:</strong> Going forward, a IEM product identifier
 field has been added to allow the retrieval of the raw NWS text product that
 the report was extracted from.  Hope to backfill this, at some point.</li> 
 <li><strong>30 January 2023:</strong> Added extraction of icing and turbulence
 portions of the PIREP. Added the associated, when applicable, ARTCC
 identifier for the location of the PIREP.</li>
 <li><strong>23 September 2022</strong>: The archive was backfilled for as long
 as raw data was available from NCEI.  This backfilling covered a period between
 early March 2003 and 20 January 2015.  Confidence is not great that this backfilling
 is complete and PIREPs from Canada are mostly missing.  Again, due to reasons
 above and the poor format of this data, this archive is not the greatest, but
 is certainly unique!</li>
 <li><strong>21 April 2021</strong>: It was kindly pointed out that location
 offsets are in nautical miles and not miles.  The archive was reprocessed
 to properly use nautical miles.</li>
 <li><strong>8 January 2020</strong>: Previously, the ingest process would not
 consider PIPEPs with unknown / bad location details.  These are now included
 in the CSV option with a "None" column for the latitude and longitude.  On a
 typical day, less than five PIREPs have unknown location details.</li>
 </ul>
EOM;
$t->content = $content;
$t->jsextra = <<<EOM
<script type="module" src="pireps.module.js"></script>
EOM;

$t->render('single.phtml');
