<?php
// Create a table of soil temperature probabilities based on obs?
require_once "../../config/settings.inc.php";
define("IEM_APPID", 88);
require_once "../../include/myview.php";
require_once "../../include/database.inc.php";
require_once "../../include/forms.php";
$t = new MyView();

$station = get_str404("station", "A130209");
$tstr = get_str404("tstr", "50,45,40,35,32,28,23");

$conn = iemdb("isuag");
$stname1 = iem_pg_prepare($conn, "SELECT extract(year from valid) as yr,
      max(extract(doy from valid)) as v from daily WHERE station = $1 and c30 < $2 and
      extract(month from valid) < 7 and c30_f != 'e' GROUP by yr");
$stname2 = iem_pg_prepare($conn, "SELECT extract(year from valid) as yr,
      min(extract(doy from valid)) as v from daily WHERE station = $1 and c30 < $2 and
      extract(month from valid) > 6 and c30_f != 'e' GROUP by yr");

$thresholds = explode(",", $tstr);
$tblrows = array();

$row1 = '<tr><th scope="col">Date</th>';
foreach ($thresholds as $k => $thres) {
    if (!is_numeric($thres)){
        die405();
    }
    $row1 .= sprintf('<th scope="col">%s</th>', $thres);
    $rs = pg_execute($conn, $stname1, array($station, $thres));
    $cnts = array();
    $yrs = pg_num_rows($rs);
    while ($row = pg_fetch_assoc($rs)) {
        if (!array_key_exists($row["v"], $cnts)) {
            $cnts[$row["v"]] = 0;
        }
        $cnts[$row["v"]] += 1;
    }
    $probs = array();
    $running = $yrs;
    for ($i = 0; $i < 182; $i++) {
        if (array_key_exists($i, $cnts)) {
            $running -= $cnts[$i];
        }
        $probs[$i] = $running;
    }
    /* Day Sampler */
    for ($i = 0; $i < 182; $i = $i + 5) {
        $ts = mktime(0, 0, 0, 1, 1, 2000) + ($i * 86400);
        $val = array_key_exists($i, $probs) ? $probs[$i] : 0;
        if (!array_key_exists($i, $tblrows)) {
            $tblrows[$i] = "";
        }
        if ($yrs == 0) {
            $tblrows[$i] .= "<td>0</td>";
        } else {
            $tblrows[$i] .= sprintf("<td>%.0f</td>", $val / $yrs * 100);
        }
    }
}
$spring = '<table class="table table-sm table-striped table-bordered '
    . 'table-hover align-middle mb-0">'
    . '<thead class="table-light sticky-top">'
    . $row1
    . '</tr></thead><tbody>';
/* Print webpage */
for ($i = 0; $i < 182; $i = $i + 5) {
    $ts = mktime(0, 0, 0, 1, 1, 2000) + ($i * 86400);
    $spring .= sprintf(
        '<tr><th scope="row">%s</th>%s</tr>',
        date("M d", $ts),
        $tblrows[$i]
    );
}
$spring .= '</tbody></table>';

/* ________________________FALL ______________ */
$tblrows = array();
foreach ($thresholds as $k => $thres) {
    $rs = pg_execute($conn, $stname2, array($station, $thres));
    $cnts = array();
    $yrs = pg_num_rows($rs);
    for ($i = 0; $row = pg_fetch_assoc($rs); $i++) {
        if (!array_key_exists($row["v"], $cnts)) {
            $cnts[$row["v"]] = 0;
        }
        $cnts[$row["v"]] += 1;
    }
    $probs = array();
    $running = 0;
    for ($i = 182; $i < 366; $i++) {
        if (array_key_exists($i, $cnts)) {
            $running += $cnts[$i];
        }
        $probs[$i] = $running;
    }
    /* Day Sampler */
    for ($i = 182; $i < 366; $i = $i + 5) {
        $ts = mktime(0, 0, 0, 1, 1, 2000) + ($i * 86400);
        $val = array_key_exists($i, $probs) ? $probs[$i] : 0;
        if (!array_key_exists($i, $tblrows)) {
            $tblrows[$i] = "";
        }
        if ($yrs == 0) {
            $tblrows[$i] .= "<td>0</td>";
        } else {
            $tblrows[$i] .= sprintf("<td>%.0f</td>", $val / $yrs * 100);
        }
    }
}
$fall = '<table class="table table-sm table-striped table-bordered '
    . 'table-hover align-middle mb-0">'
    . '<thead class="table-light sticky-top">'
    . $row1
    . '</tr></thead><tbody>';
/* Print webpage */
for ($i = 182; $i < 366; $i = $i + 5) {
    $ts = mktime(0, 0, 0, 1, 1, 2000) + ($i * 86400);
    $fall .= sprintf(
        '<tr><th scope="row">%s</th>%s</tr>',
        date("M d", $ts),
        $tblrows[$i]
    );
}
$fall .= '</tbody></table>';

$sselect = networkSelect("ISUAG", $station);

$t->title = "ISUSM - Soil Temperature Probabilities";
$t->content = <<<EOM
<nav aria-label="breadcrumb">
    <ol class="breadcrumb mb-4">
        <li class="breadcrumb-item"><a href="/agclimate/">ISU Soil Moisture Network</a></li>
        <li class="breadcrumb-item active" aria-current="page">Soil Temperature Probabilities</li>
    </ol>
</nav>

<div class="mb-4">
    <h1 class="h3 mb-3">4 inch Soil Temperature Probabilities</h1>

    <p class="mb-3">This application computes soil temperature exceedance based on the
    observation record of an ISU Ag Climate site. The average daily 4 inch
    soil temperature is used in this calculation.</p>

    <ul class="mb-3">
        <li>Spring: The values represent the percentage of years that a temperature
        below the given threshold was observed <strong>after</strong> a given date.</li>
        <li>Fall: The values represent the percentage of years that a temperature
        below the given threshold was observed <strong>before</strong> a given date.</li>
    </ul>
</div>

<div class="alert alert-info mb-4" role="alert">This application uses the legacy ISU Ag Climate
network for its computations.  Data from the newer ISU Soil Moisture Network
is not considered.</div>

<form method="GET" name="soil" class="card mb-4">
    <div class="card-body">
        <div class="row g-3 align-items-end">
            <div class="col-md-6">
                <label for="station" class="form-label fw-semibold">Select Station</label>
                {$sselect}
            </div>
            <div class="col-md-6">
                <label for="tstr" class="form-label fw-semibold">Thresholds</label>
                <input type="text" value="{$tstr}" name="tstr" id="tstr" class="form-control">
                <div class="form-text">Comma separated thresholds.</div>
            </div>
            <div class="col-12">
                <button type="submit" class="btn btn-primary">Request</button>
            </div>
        </div>
    </div>
</form>

<div class="row g-4">
    <div class="col-lg-6">
        <div class="card h-100">
            <div class="card-header">
                <h2 class="h5 mb-0">Spring Probabilities</h2>
                <div class="small text-muted">Given date to July 1</div>
            </div>
            <div class="card-body p-0">
                <div class="table-responsive">
                    {$spring}
                </div>
            </div>
        </div>
    </div>
    <div class="col-lg-6">
        <div class="card h-100">
            <div class="card-header">
                <h2 class="h5 mb-0">Fall Probabilities</h2>
                <div class="small text-muted">July 1 to given date</div>
            </div>
            <div class="card-body p-0">
                <div class="table-responsive">
                    {$fall}
                </div>
            </div>
        </div>
    </div>
</div>
EOM;
$t->render('single.phtml');
