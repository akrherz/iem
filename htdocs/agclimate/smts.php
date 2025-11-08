<?php
define("IEM_APPID", 114);
require_once "../../config/settings.inc.php";
require_once "../../include/forms.php";
require_once "../../include/myview.php";

$t = new MyView();
$t->title = "ISU Soil Moisture Plots";

$now = time();
$d2 = time() - 5 * 86400;
$station = get_str404("station", "BOOI4");
$opt = get_str404("opt", "1");

if (array_key_exists("sts", $_GET)) {
    $sts = new DateTime(get_str404("sts", null));
    $ets = new DateTime(get_str404("ets", null));
} else {
    // Legacy CGI parameters
    $year1 = get_int404('year1', date("Y", $d2));
    $month1 = get_int404('month1', date("m", $d2));
    $day1 = get_int404('day1', date("d", $d2));
    $hour1 = get_int404('hour1', 0);

    $year2 = get_int404('year2', date("Y", $now));
    $month2 = get_int404('month2', date("m", $now));
    $day2 = get_int404('day2', date("d", $now));
    $hour2 = get_int404('hour2', 23);
    $sts = new DateTime();
    $sts->setDate($year1, $month1, $day1);
    $sts->setTime($hour1, 0);
    $ets = new DateTime();
    $ets->setDate($year2, $month2, $day2);
    $ets->setTime($hour2, 0);
}

$errmsg = "";
if ($ets <= $sts) {
    $errmsg = "<div class=\"alert alert-warning\">Error, your requested" .
        " End Time is before the Start Time.  Please adjust your selection" .
        " and try once again.</div>";
}

$sselect = networkSelect("ISUSM", $station, array(), "station", FALSE, 'form-select w-100');
$y1 = yearSelect(2012, $sts->format("Y"), "year1");
$m1 = monthSelect($sts->format("m"), "month1");
$d1 = daySelect($sts->format("d"), "day1");
$h1 = hourSelect($sts->format("H"), "hour1");
$y2 = yearSelect(2012, $ets->format("Y"), "year2");
$m2 = monthSelect($ets->format("m"), "month2");
$d2 = daySelect($ets->format("d"), "day2");
$h2 = hourSelect($ets->format("H"), "hour2");

// Retreive the autoplot description JSON
$content = file_get_contents($INTERNAL_BASEURL . "/plotting/auto/meta/177.json");
$meta = json_decode($content, $assoc=TRUE);
$dd = "This plot is a time series graph of
observations from a time period and ISU Soil Moisture station of your choice.";
$desc = array();
foreach ($meta["arguments"] as $arg) {
    if ($arg["name"] == "opt") {
        $ar = $arg["options"];
        $keys = array_keys($ar);
        foreach ($keys as $key) {
            $desc[$key] = $dd;
        }
        break;
    }
}

$desc["m"] = <<<EOM
This plot presents a Meteogram, which is just a time series of common weather
variables including temperature, dew point, wind speed, and wind direction. If
the plot covers more than five days, an hourly interval dataset is used,
otherwise the values are plotted at one minute interval.
EOM;
$desc["6"] = <<<EOM
This plot presents a histogram of hourly volumetric soil moisture observations.
The y-axis is expressed in logarithmic to better show the low frequency obs
within the distribution.
EOM;
$desc["7"] = <<<EOM
This plot computes the daily change in soil water approximately between
the depths of 6 to 30 inches.  This is using only two measurements at
12, and 24 inch depths.  The 12 inch depth is assumed to cover the
6-18 inch layer and the 24 inch depth to cover 18-30 layer.  If you select a
period of less than 60 days, the daily rainfall will be plotted as well.
EOM;
$desc["10"] = <<<EOM
This plot provides a diagnostic of the data being provided by the inversion
sensors.  These temperature sensors are installed at 1.5 and 10 feet above the
ground, which then can sense if temperature increases with height.  This
sensor package was installed in 2021 and only found at three sites BOOI4 - Ames
AEA, CRFI4 - Crawfordsville, and CAMI4 - Sutherland.
EOM;
$desc["encrh"] = <<<EOM
Many of the stations track the humidity within the logger enclosure to ensure
that desiccant packs are working as intended.  Elevated humidity leads to
damage of wiring.
EOM;

$thedescription = $desc[$opt];
$oselect = make_select("opt", $opt, $ar, '', 'form-select w-100');

$img = sprintf(
    "<img src=\"/plotting/auto/plot/177/network:ISUSM::" .
        "station:%s::opt:%s::sts:%s::" .
        "ets:%s.png" .
        "\" class=\"img-fluid\">",
    $station,
    $opt,
    $sts->format("Y-m-d Hi"),  // lame format, but alas
    $ets->format("Y-m-d Hi")
);
if ($errmsg != "") {
    $img = $errmsg;
}

$t->content = <<<EOM
    <nav aria-label="breadcrumb">
        <ol class="breadcrumb">
            <li class="breadcrumb-item"><a href="/agclimate/">ISU Soil Moisture Network</a></li>
            <li class="breadcrumb-item active" aria-current="page">Soil Moisture Plots</li>
        </ol>
    </nav>

    <h1 class="mb-3">Soil Moisture and Precipitation Timeseries</h1>
    <h2 class="h5">Plot Selection</h2>
    <p>This application plots a timeseries of soil moisture and precipitation from
        an ISU Soil Moisture station of your choice. Please select a start and end time
        and click the 'Make Plot' button below.</p>

        <form name="selector" method="GET" autocomplete="off">
            <div class="row g-3 align-items-end">
                <div class="col-12 col-md-4">
                    <label for="station" class="form-label">Station</label>
                    {$sselect}
                </div>
                <div class="col-12 col-md-4">
                    <label for="opt" class="form-label">Plot Option</label>
                    {$oselect}
                </div>
                <div class="col-12 col-md-2">
                    <label for="sts" class="form-label">Start Time (US Central)</label>
                    <input type="datetime-local" id="sts" name="sts" class="form-control" value="{$sts->format('Y-m-d\TH:i')}" />
                </div>
                <div class="col-12 col-md-2">
                    <label for="ets" class="form-label">End Time (US Central)</label>
                    <input type="datetime-local" id="ets" name="ets" class="form-control" value="{$ets->format('Y-m-d\TH:i')}" />
                </div>
                <div class="col-12 mt-2 d-flex justify-content-center">
                    <button type="submit" class="btn btn-primary w-auto">Make Plot</button>
                </div>
            </div>
        </form>

    <div aria-live="polite">
        {$img}
    </div>

    <section class="mt-4">
        <h2 class="h5">Plot Description</h2>
        <p>{$thedescription}</p>
    </section>
EOM;
$t->render('single.phtml');
