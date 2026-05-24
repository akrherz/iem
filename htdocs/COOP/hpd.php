<?php
// List out HPD data for a date and station of your choice
require_once "../../config/settings.inc.php";
define("IEM_APPID", 91);
require_once "../../include/myview.php";
require_once "../../include/forms.php";
require_once "../../include/database.inc.php";

$station = get_str404("station", null);
$year = get_int404("year", date("Y"));
$month = get_int404("month", date("m"));
$day = get_int404("day", date("d"));

$yselect = yearSelect(2008, $year, "year");
$mselect = monthSelect($month, "month");
$dselect = daySelect($day, "day");

$result_note = '<div class="alert alert-secondary mb-0" role="status">Please select a station and date.</div>';
$table = "";
if ($station) {
    $dbconn = iemdb('other');
    $stname = iem_pg_prepare(
        $dbconn,
        "select * from hpd_alldata WHERE station = $1 and valid >= $2 " .
            "and valid < $3 ORDER by valid ASC"
    );
    $valid = mktime(0, 0, 0, $month, $day, $year);
    $sts = date("Y-m-d 00:00", $valid);
    $ets = date("Y-m-d 23:59", $valid);
    $rs = pg_execute($dbconn, $stname, array($station, $sts, $ets));
    $rowcount = pg_num_rows($rs);
    $result_note = sprintf(
        '<div class="alert alert-info mb-3" role="status">Showing %s report(s) for <strong>%s</strong> on <strong>%s</strong>.</div>',
        $rowcount,
        htmlspecialchars($station),
        date("d M Y", $valid)
    );
    if ($rowcount === 0) {
        $table = '<div class="alert alert-warning mb-0" role="status">No HPD reports were found for the selected station and date.</div>';
    } else {
        $table = '<div class="table-responsive"><table class="table table-striped table-hover align-middle mb-0"><thead class="table-light"><tr><th scope="col">Valid</th><th scope="col">Precip</th></tr></thead><tbody>';
    while ($row = pg_fetch_assoc($rs)) {
        $table .= sprintf(
            "<tr><td>%s</td><td>%s</td></tr>",
            $row["valid"],
            $row["precip"]
        );
    }
        $table .= "</tbody></table></div>";
    }
}

$t = new MyView();
$t->title = "COOP HPD FisherPorter Precip";

$sselect = networkSelect("IA_HPD", $station);
$t->content = <<<EOM
<nav aria-label="breadcrumb">
    <ol class="breadcrumb">
        <li class="breadcrumb-item"><a href="/COOP/">COOP Data</a></li>
        <li class="breadcrumb-item active" aria-current="page">Fisher Porter Rain Gauge Data</li>
    </ol>
</nav>

<header class="mb-4">
    <h1 class="h3 mb-3">Fisher Porter Rain Gauge Data</h1>
    <p class="mb-2">The IEM maintains an archive of processed rain gauge data from Fisher Porter equipment operated at some Iowa NWS COOP locations. Availability depends on delayed source data from <a href="https://www.ncei.noaa.gov/pub/data/hpd/data/">NCEI</a>.</p>
    <p class="mb-0">The historical ingest process ran monthly and attempted to backfill the prior 3rd, 6th, and 12th month through the current date.</p>
</header>

<div class="alert alert-warning" role="status">
    <strong>Updated 3 Feb 2023:</strong> This data source no longer appears to be available from NCEI, so this archive has no data after approximately February 2021.
</div>

<section class="card shadow-sm mb-4" aria-labelledby="hpd-controls-heading">
    <div class="card-body">
        <h2 id="hpd-controls-heading" class="h5 card-title">Lookup Controls</h2>
        <form method="GET" name="st" class="row g-3 align-items-end mb-0">
            <div class="col-lg-5">
                <label for="station" class="form-label">Select Station</label>
                {$sselect}
            </div>
            <div class="col-lg-5">
                <label class="form-label d-block">Select Date</label>
                <div class="row g-2">
                    <div class="col-sm-4">{$yselect}</div>
                    <div class="col-sm-4">{$mselect}</div>
                    <div class="col-sm-4">{$dselect}</div>
                </div>
            </div>
            <div class="col-lg-2">
                <button type="submit" class="btn btn-primary w-100">Show Data</button>
            </div>
        </form>
    </div>
</section>

<section class="card shadow-sm" aria-labelledby="hpd-results-heading">
    <div class="card-body">
        <div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-3">
            <h2 id="hpd-results-heading" class="h5 mb-0">Results</h2>
            <span class="badge text-bg-light border">HPD archive</span>
        </div>
        {$result_note}
        {$table}
    </div>
</section>

EOM;
$t->render('single.phtml');
