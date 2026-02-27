<?php
// An audit of how the sausage gets made in the CLI
require_once "../../../config/settings.inc.php";
define("IEM_APPID", "169");
require_once "../../../include/myview.php";
require_once "../../../include/forms.php";

$t = new MyView();
$t->iemselect2 = TRUE;
$t->title = "Audit of NWS CLI Data";
$t->headextra = <<<EOM
<link rel="stylesheet" href="index.css">
EOM;
$t->jsextra = <<<EOM
<script type="module" src="index.module.js"></script>
EOM;

$sselect = networkSelect("NWSCLI", "");

$t->content = <<<EOM

<nav aria-label="breadcrumb">
<ol class="breadcrumb">
    <li class="breadcrumb-item"><a href="/nws/">NWS Mainpage</a></li>
    <li class="breadcrumb-item active" aria-current="page">Audit of NWS CLI Data</li>
</ol>
</nav>

<p>
Due to the ongoing "fun" associated with <a href="/onsite/news.phtml?id=1469">
wagering on ASOS temperatures</a>, this page attempts to show an audit path on
which products go into figuring out a given airport station's daily high
and low temperature.  This page only works for stations having NWS CLI product
coverage. This audit path includes raw METARs, METAR 6 Hour max/min
values, Daily Summary Messages (DSM)s, CLImate Reports (CLI), and CF6 Reports.
This is all <strong>unofficial data</strong> and is not intended for
gambling purposes!
</p>

<div class="card mb-3">
    <div class="card-body">
        <form id="query-form" class="row g-3 align-items-end">
            <div class="col-md-4">
                <label class="form-label fw-bold">Select Station:</label>
                        {$sselect}

            </div>
            <div class="col-md-4">
                <label class="form-label" for="date">Date</label>
                <input id="date" name="date" type="date" class="form-control"
                         required>
            </div>
            <div class="col-md-4">
                <button type="submit" class="btn btn-primary">Load Audit</button>
            </div>
        </form>
    </div>
</div>

<div id="status" class="alert alert-secondary" role="status" aria-live="polite">
    Select a station/date and load audit data.
</div>

<div id="service-meta" class="alert alert-light" role="note" aria-live="polite">
    JSON service metadata will appear here after loading data.
</div>

<div class="row g-3">
    <div class="col-lg-6">
        <div class="card h-100">
            <div class="card-header">Daily High Temperature Events</div>
            <div class="card-body p-0">
                <div id="high-events" class="table-responsive"></div>
            </div>
        </div>
    </div>
    <div class="col-lg-6">
        <div class="card h-100">
            <div class="card-header">Daily Low Temperature Events</div>
            <div class="card-body p-0">
                <div id="low-events" class="table-responsive"></div>
            </div>
        </div>
    </div>
</div>

<h3>Application Notes</h3>

<ol>
 <li>"High Frequency" MADIS data is not used due to
 <a href="/onsite/news.phtml?id=1290">reporting in whole degree C</a> and
 not using standard two minute averaging.</li>
 <li>The NWS computes this over a local standard day, so 1 AM till 1 AM
 local during daylight saving time. This app attempts to account for that.</li>
 <li>It is sometimes vague what happens with the METAR report that occurs
 just before midnight local for the start of the period.  This app considers
 the temperature report, but not the 6 hour max/min reported at this time.</li>
</ol>

EOM;

$t->render('full.phtml');
