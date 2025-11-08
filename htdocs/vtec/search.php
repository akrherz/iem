<?php
require_once "../../config/settings.inc.php";
define("IEM_APPID", 154);
require_once "../../include/mlib.php";
force_https();
require_once "../../include/myview.php";
require_once "../../include/iemprop.php";
require_once "../../include/forms.php";
$lat = get_float404('lat', 41.53);
$lon = get_float404('lon', -93.653);
$t = new MyView();
$OL = "10.6.1";
$t->jsextra = <<<EOM

<script type="text/javascript" src="wfos.js"></script>
<script src='/vendor/openlayers/{$OL}/ol.js'></script>
<script type="text/javascript" src="/js/olselect-lonlat.js?v=2"></script>
<script type="text/javascript" src="https://oss.sheetjs.com/sheetjs/xlsx.full.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/luxon@3.4.4/build/global/luxon.min.js"></script>
<script src="https://unpkg.com/tabulator-tables@6.3.1/dist/js/tabulator.min.js"></script>
<script type="text/javascript" src="search.js?v=3"></script>
EOM;
$t->headextra = <<<EOM
<link href="https://unpkg.com/tabulator-tables@6.3.1/dist/css/tabulator.min.css" rel="stylesheet">
<link rel='stylesheet' href="/vendor/openlayers/{$OL}/ol.css" type='text/css'>
<link rel="stylesheet" href="search.css" type="text/css">
EOM;
$t->title = "NWS Warning Search by Point or County/Zone";

$t->content = <<<EOM
<h1 class="h4 mb-3">NWS Watch / Warning / Advisory Search</h1>
<p>This application allows you to search for National Weather Service Watch,
Warning, and Advisories using three different search methods:</p>
<div id="vtec-search-status" class="visually-hidden" role="status" aria-live="polite"></div>

<!-- Bootstrap Navigation Tabs -->
<ul class="nav nav-tabs vtec-search-tabs" id="searchTabs" role="tablist" aria-label="Search modes">
    <li class="nav-item" role="presentation">
        <button class="nav-link" id="bypoint-tab" data-bs-toggle="tab" data-bs-target="#bypoint" type="button" role="tab" aria-controls="bypoint" aria-selected="false">
            <i class="bi bi-geo-alt-fill me-2" aria-hidden="true"></i>Storm Based Warnings by Point
        </button>
    </li>
    <li class="nav-item" role="presentation">
        <button class="nav-link" id="byugc-tab" data-bs-toggle="tab" data-bs-target="#byugc" type="button" role="tab" aria-controls="byugc" aria-selected="false">
            <i class="bi bi-map me-2" aria-hidden="true"></i>Warnings by County/Zone or Point
        </button>
    </li>
    <li class="nav-item" role="presentation">
        <button class="nav-link" id="list-tab" data-bs-toggle="tab" data-bs-target="#list" type="button" role="tab" aria-controls="list" aria-selected="false">
            <i class="bi bi-list-ul me-2" aria-hidden="true"></i>List by State/WFO
        </button>
    </li>
</ul>

<!-- Tab Content -->
<div class="tab-content" id="searchTabContent">
    <!-- Tab 1: Storm Based Warnings by Point -->
    <div class="tab-pane fade" id="bypoint" role="tabpanel" aria-labelledby="bypoint-tab">
        <div class="mt-3">
            <p class="section-description">The official warned area for some products the NWS issues is a polygon.
            This section allows you to specify a point on the map below by dragging the
            marker to where you are interested in. Once you stop dragging the marker, the
            grid will update and provide a listing of storm based warnings found.</p>

            <div class="row">
                <div class="col-md-4">
                    <div class="card vtec-card mb-3">
                        <div class="card-body">
                            <h6 class="card-title"><i class="bi bi-gear-fill me-2" aria-hidden="true"></i>Search Parameters</h6>

                            <div class="coordinate-section">
                                <strong>Enter coordinates manually:</strong><br />
                                <div class="mt-2">
                                    <label for="lat" class="form-label">Latitude (deg N):</label>
                                    <input id="lat" value="{$lat}" class="form-control coordinate-input">
                                </div>
                                <div class="mt-2">
                                    <label for="lon" class="form-label">Longitude (deg E):</label>
                                    <input id="lon" value="{$lon}" class="form-control coordinate-input">
                                </div>
                            </div>

                            <div class="mb-3">
                                <label for="buffer" class="form-label">Approximate Location Buffer Radius:</label>
                                <select name="buffer" class="form-select">
                                    <option value="0">0 (Exact point)</option>
                                    <option value="0.01">~1 mile (0.01 deg)</option>
                                    <option value="0.1">~10 miles (0.10 deg)</option>
                                </select>
                            </div>

                            <div class="mb-2">
                                <label for="sdate1" class="form-label">Start Date:</label>
                                <input name="sdate1" type="date" id="sdate1" class="form-control">
                            </div>
                            <div class="mb-3">
                                <label for="edate1" class="form-label">End Date:</label>
                                <input name="edate1" type="date" id="edate1" class="form-control">
                            </div>

                            <button type="button" class="btn btn-primary w-100" id="manualpt">
                                <i class="bi bi-arrow-repeat me-2" aria-hidden="true"></i>Update Results
                            </button>
                        </div>
                    </div>

                    <div class="card vtec-card">
                        <div class="card-body">
                            <h6 class="card-title"><i class="bi bi-cursor me-2" aria-hidden="true"></i>Interactive Map</h6>
                            <p class="card-text">Drag the marker to select coordinates:</p>
                            <div
                             id="map"
                             class="map"
                             data-initial-lat="{$lat}"
                             data-initial-lon="{$lon}"
                             data-lat-input="lat"
                             data-lon-input="lon"></div>
                        </div>
                    </div>
                </div>

                <div class="col-md-8">
                    <div class="card vtec-card">
                        <div class="card-body">
                            <h4 id="table1title" class="card-title"><i class="bi bi-table me-2" aria-hidden="true"></i>Search Results</h4>

                            <div class="full-dataset-export mb-3">
                                <div class="alert alert-info py-2">
                                    <div class="d-flex justify-content-between align-items-center">
                                        <div>
                                            <strong><i class="bi bi-database me-1" aria-hidden="true"></i>Full Dataset Export</strong>
                                            <small class="d-block text-muted">Download complete results (all matching records)</small>
                                        </div>
                                        <div class="btn-group">
                                            <button type="button" data-table="1" data-opt="excel" class="btn btn-outline-success btn-sm iemtool" aria-label="Download full dataset as Excel">
                                                <i class="bi bi-file-earmark-spreadsheet me-1" aria-hidden="true"></i>Excel
                                            </button>
                                            <button type="button" data-table="1" data-opt="csv" class="btn btn-outline-primary btn-sm iemtool" aria-label="Download full dataset as CSV">
                                                <i class="bi bi-file-earmark-text me-1" aria-hidden="true"></i>CSV
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="table-responsive">
                                <table id="table1" data-order='[[ 3, "desc" ]]' class="table table-striped table-hover">
                                <caption class="text-start">Storm based warnings results table. Columns list event metadata including issuance/expiration and event tags.</caption>
                                <thead class="table-dark">
                                <tr><th>Event</th><th>Phenomena</th><th>Significance</th><th>Issued</th>
                                <th>Expired</th><th>Issue Hail Tag</th><th>Issue Wind Tag</th>
                                <th>Issue Tornado Tag</th><th>Issue Damage Tag</th></tr>
                                </thead>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Tab 2: Search by County/Zone or Point -->
    <div class="tab-pane fade" id="byugc" role="tabpanel" aria-labelledby="byugc-tab">
        <div class="mt-3">
            <div class="section-description">
                <p>The NWS issues watch, warnings, and advisories (WWA) for counties/parishes. For
                some products (like winter warnings), they issue for forecast zones. In many parts of the country, these zones are exactly the
                same as the counties/parishes. When you get into regions with topography,
                then zones will start to differ to the local counties.</p>

                <p>This application allows you to search the IEM's archive of NWS WWA products.
                Our archive is not complete, but there are no known holes since 12 November 2005.
                This archive is of those products that contain VTEC codes, which are nearly all
                WWAs that the NWS issues for. There are Severe Thunderstorm, Tornado, and
                Flash Flood Warnings included in this archive for dates prior to 2005. These
                were retroactively assigned VTEC event identifiers by the IEM based on some
                hopefully intelligent logic.</p>
            </div>

            <div class="alert alert-warning">Please note: NWS forecast offices have
            changed over the years, this application may incorrectly label old warnings as coming from
            an office that did not exist at the time.

                <br /><strong>Also note:</strong> This particular search interface will return
                    <strong>false-positives</strong> for some warnings that are now fully polygon/storm based. The IEM
                    database tracks the UGC areas associated with the storm based warnings. So querying
                    by UGC (even if you query by point), will return some warnings that were not actually
                    active for that point, but were technically active for that UGC of which the point
                    falls inside of. Please use the above search for these types of warnings!
            </div>

            <form id="form2">
            <div class="row">
                <div class="col-md-4">
                    <div class="card vtec-card mb-3">
                        <div class="card-body">
                            <h6 class="card-title"><i class="bi bi-calendar me-2" aria-hidden="true"></i>Date Range</h6>
                            <p class="card-text">These dates (at 00 UTC) define the issuance of the event, please do not
                            be too tight with these dates.</p>
                            <div class="mb-2">
                                <label for="sdate" class="form-label">Start Date:</label>
                                <input name="sdate" type="date" class="form-control">
                            </div>
                            <div class="mb-2">
                                <label for="edate" class="form-label">End Date:</label>
                                <input name="edate" type="date" class="form-control">
                            </div>
                        </div>
                    </div>

                    <div class="card vtec-card mb-3">
                        <div class="card-body">
                            <h6 class="card-title"><i class="bi bi-geo-alt me-2" aria-hidden="true"></i>Manual Selection</h6>
                            <div class="mb-2">
                                <label for="state" class="form-label">Select State:</label>
                                <select name="state" id="state" class="form-select"></select>
                            </div>
                            <div class="mb-2">
                                <label for="ugc" class="form-label">Select County/Zone:</label>
                                <select name="ugc" class="form-select"></select>
                            </div>
                            <button type="button" class="btn btn-primary w-100" id="manualugc">
                                <i class="bi bi-arrow-repeat me-2" aria-hidden="true"></i>Update Results
                            </button>
                        </div>
                    </div>

                    <div class="card vtec-card mb-3">
                        <div class="card-body">
                            <h6 class="card-title"><i class="bi bi-crosshair me-2" aria-hidden="true"></i>Manual Point Selection</h6>
                            <p class="card-text">You can otherwise search by lat/lon point. The start and
                            end date set above are used with this option as well:</p>

                            <div class="coordinate-section">
                                <div class="mb-2">
                                    <label for="lat2" class="form-label">Latitude (deg N):</label>
                                    <input id="lat2" value="{$lat}" class="form-control coordinate-input">
                                </div>
                                <div class="mb-2">
                                    <label for="lon2" class="form-label">Longitude (deg E):</label>
                                    <input id="lon2" value="{$lon}" class="form-control coordinate-input">
                                </div>
                            </div>

                            <div class="mb-3">
                                <label for="buffer2" class="form-label">Approximate Location Buffer Radius:</label>
                                <select name="buffer2" class="form-select">
                                    <option value="0">0 (Exact point)</option>
                                    <option value="0.01">~1 mile (0.01 deg)</option>
                                    <option value="0.1">~10 miles (0.10 deg)</option>
                                </select>
                            </div>
                            <button type="button" class="btn btn-primary w-100" id="manualpt2">
                                <i class="bi bi-arrow-repeat me-2" aria-hidden="true"></i>Update Results
                            </button>
                        </div>
                    </div>

                    <div class="card vtec-card">
                        <div class="card-body">
                            <h6 class="card-title"><i class="bi bi-cursor me-2" aria-hidden="true"></i>Interactive Map</h6>
                            <p class="card-text">Drag the marker to select coordinates:</p>
                            <div
                             id="map2"
                             data-initial-lat="{$lat}"
                             data-initial-lon="{$lon}"
                             data-lat-input="lat2"
                             data-lon-input="lon2"
                             class="map"></div>
                        </div>
                    </div>
                </div>

                <div class="col-md-8">
                    <div class="card vtec-card">
                        <div class="card-body">
                            <h4 id="table2title" class="card-title"><i class="bi bi-table me-2" aria-hidden="true"></i>Search Results</h4>

                            <div class="full-dataset-export mb-3">
                                <div class="alert alert-info py-2">
                                    <div class="d-flex justify-content-between align-items-center">
                                        <div>
                                            <strong><i class="bi bi-database me-1" aria-hidden="true"></i>Full Dataset Export</strong>
                                            <small class="d-block text-muted">Download complete results (all matching records)</small>
                                        </div>
                                        <div class="btn-group">
                                            <button type="button" data-table="2" data-opt="excel" class="btn btn-outline-success btn-sm iemtool" aria-label="Download full dataset as Excel">
                                                <i class="bi bi-file-earmark-spreadsheet me-1" aria-hidden="true"></i>Excel
                                            </button>
                                            <button type="button" data-table="2" data-opt="csv" class="btn btn-outline-primary btn-sm iemtool" aria-label="Download full dataset as CSV">
                                                <i class="bi bi-file-earmark-text me-1" aria-hidden="true"></i>CSV
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div class="table-responsive">
                                <table id="table2" data-order='[[ 3, "desc" ]]' class="table table-striped table-hover">
                                <caption class="text-start">Events by UGC or point results table. Columns show event identifiers and timing.</caption>
                                <thead class="table-dark">
                                <tr><th>Event</th><th>Phenomena</th><th>Significance</th><th>Issued</th>
                                <th>Expired</th></tr>
                                </thead>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div><!-- ./row -->
            </form><!-- ./form2 -->
        </div>
    </div>

    <!-- Tab 3: List by State/WFO -->
    <div class="tab-pane fade" id="list" role="tabpanel" aria-labelledby="list-tab">
        <div class="mt-3">
            <p class="section-description">This section generates a simple list of NWS Watch, Warning, and Advisories
            by state and year.</p>

            <form id="form3">
            <div class="row">
                <div class="col-md-4">
                    <div class="card vtec-card">
                        <div class="card-body">
                            <h6 class="card-title"><i class="bi bi-gear-fill me-2" aria-hidden="true"></i>Search Parameters</h6>

                            <div class="radio-group mb-3">
                                <div class="form-check">
                                    <input type="radio" name="by3" value="state" checked="checked" id="bystate" class="form-check-input"/>
                                    <label for="bystate" class="form-check-label"><strong>Select By State</strong></label>
                                </div>
                                <select name="state" id="state3" class="form-select mt-2"></select>
                            </div>

                            <div class="radio-group mb-3">
                                <div class="form-check">
                                    <input type="radio" name="by3" value="wfo" id="bywfo" class="form-check-input"/>
                                    <label for="bywfo" class="form-check-label"><strong>Select By WFO</strong></label>
                                </div>
                                <select name="wfo" id="wfo3" class="form-select mt-2"></select>
                            </div>

                            <div class="radio-group mb-3">
                                <div class="form-check">
                                    <input type="radio" name="single3" value="single" id="single3" checked="checked" class="form-check-input"/>
                                    <label for="single3" class="form-check-label"><strong>Single VTEC Event</strong></label>
                                </div>
                                <div class="form-check">
                                    <input type="radio" name="single3" value="all" id="all3" class="form-check-input">
                                    <label for="all3" class="form-check-label"><strong>All VTEC Events</strong></label>
                                </div>

                                <div class="mt-2">
                                    <label for="ph3" class="form-label">Select VTEC Phenomena:</label>
                                    <select name="ph" id="ph3" class="form-select"></select>
                                </div>
                            </div>

                            <div class="mb-3">
                                <label for="sig3" class="form-label">Select VTEC Significance:</label>
                                <select name="sig" id="sig3" class="form-select"></select>
                            </div>

                            <div class="mb-3">
                                <label for="year3" class="form-label">Select Year:</label>
                                <select name="year" id="year3" class="form-select"></select>
                            </div>

                            <button type="button" class="btn btn-primary w-100" id="button3">
                                <i class="bi bi-arrow-repeat me-2" aria-hidden="true"></i>Update Table
                            </button>
                        </div>
                    </div>
                </div>

                <div class="col-md-8">
                    <div class="card vtec-card">
                        <div class="card-body">
                            <h4 id="table3title" class="card-title"><i class="bi bi-table me-2" aria-hidden="true"></i>Search Results</h4>
                            <div class="btn-group-export mb-3">
                                <button type="button" data-table="3" data-opt="excel" class="btn btn-outline-success btn-sm iemtool" aria-label="Download full dataset as Excel">
                                    <i class="bi bi-file-earmark-spreadsheet me-1" aria-hidden="true"></i>Excel
                                </button>
                                <button type="button" data-table="3" data-opt="csv" class="btn btn-outline-primary btn-sm iemtool" aria-label="Download full dataset as CSV">
                                    <i class="bi bi-file-earmark-text me-1" aria-hidden="true"></i>CSV
                                </button>
                            </div>

                            <div class="table-responsive">
                                <table id="table3" data-order='[[ 3, "desc" ]]' class="table table-striped table-hover">
                                <caption class="text-start">List by state or WFO results table. Columns include WFO, locations, and issuance/expiration.</caption>
                                <thead class="table-dark">
                                <tr>
                                <th>Event</th>
                                <th>Phenomena</th>
                                <th>Significance</th>
                                <th>WFO</th>
                                <th>Locations</th>
                                <th>Issued</th>
                                <th>Expired</th></tr>
                                </thead>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div><!-- ./row -->
            </form><!-- ./form3 -->
        </div>
    </div>
</div>
EOM;
$t->render('full.phtml');
