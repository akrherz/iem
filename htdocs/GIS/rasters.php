<?php
require_once "../../config/settings.inc.php";
define("IEM_APPID", 82);
require_once "../../include/database.inc.php";
require_once "../../include/myview.php";
require_once "../../include/forms.php";
$t = new MyView();
$mesosite = iemdb("mesosite");

$t->title = "GIS RASTER Documentation";

$rid = get_int404("rid", 1);

$table = "";
$rs = pg_query($mesosite, "SELECT * from iemrasters ORDER by name ASC");

$rname = "";
$runits = "";
$urltemplate = "";
while ($row = pg_fetch_assoc($rs)) {
    if ($rid == intval($row["id"])) {
        $rname = $row["name"];
        $runits = $row["units"];
        $urltemplate = str_replace(
            "/mesonet/ARCHIVE",
            "{$EXTERNAL_BASEURL}/archive",
            is_null($row["filename_template"]) ? "": $row["filename_template"]
        );
        $t->title = sprintf("RASTER info for %s", $rname);
    }
    $table .= sprintf(
        "<tr><td><a href=\"?rid=%s\">%s</a></td>"
            . "<td>%s</td><td>%s</td></tr>\n",
        $row["id"],
        $row["name"],
        $row["description"],
        $row["units"]
    );
}

function rgb2html($r, $g, $b)
{
    if (is_array($r) && sizeof($r) == 3)
        list($r, $g, $b) = $r;

    $r = intval($r);
    $g = intval($g);
    $b = intval($b);

    $r = dechex($r < 0 ? 0 : ($r > 255 ? 255 : $r));
    $g = dechex($g < 0 ? 0 : ($g > 255 ? 255 : $g));
    $b = dechex($b < 0 ? 0 : ($b > 255 ? 255 : $b));

    $color = (strlen($r) < 2 ? '0' : '') . $r;
    $color .= (strlen($g) < 2 ? '0' : '') . $g;
    $color .= (strlen($b) < 2 ? '0' : '') . $b;
    return '#' . $color;
}

$table2 = "";
if ($rid > 0) {
    $stname = iem_pg_prepare($mesosite, "SELECT * from iemrasters_lookup"
        . " WHERE iemraster_id = $1 ORDER by coloridx ASC");
    $rs = pg_execute($mesosite, $stname, array($rid));
    while ($row = pg_fetch_assoc($rs)) {
        $table2 .= sprintf(
            "<tr><td>%s</td><td>%s</td><td>%s</td>"
                . "<td>%s</td><td>%s</td><td>%s</td></tr>\n",
            $row["coloridx"],
            (is_null($row["value"])) ? 'Missing' : $row["value"],
            $row["r"],
            $row["g"],
            $row["b"],
            rgb2html($row["r"], $row["g"], $row["b"])
        );
    }
}

$t->content = <<<EOM
<nav aria-label="breadcrumb">
    <ol class="breadcrumb">
        <li class="breadcrumb-item"><a href="/GIS/">GIS Mainpage</a></li>
        <li class="breadcrumb-item active" aria-current="page">IEM RASTER Information</li>
    </ol>
</nav>

<p>The IEM produces a number of RASTER images meant for GIS use. These RASTERs
are typically provided on the IEM website as 8 bit PNG images. This means there
are 256 slots available for a binned value to be placed. This page documents
these RASTER images and provides the lookup table of PNG index to an actual
value. Click on the item in the "Label" column to get the lookup table below.</p>

<div class="table-responsive">
<table class="table table-sm table-striped">
    <thead>
        <tr><th>Label</th><th>Description</th><th>Units</th></tr>
    </thead>
    <tbody>
        {$table}
    </tbody>
</table>
</div>

<h3>Programmatic access to this RASTER source</h3>

<p>The IEM generated RASTERs are stored in a programmatic way that should allow
for easy scripted download of the archive. This section documents the URL
template used with the time shown in UTC. The string format modifiers below
are <a href="https://docs.python.org/2/library/time.html#time.strftime">pythonic strftime values</a>.</p>

<pre class="p-2 bg-light border">{$urltemplate}</pre>

<p>A general web service also exists to convert these RASTERs to netCDF "on-the-fly".
The URL format is like so:</p>

<pre class="p-2 bg-light border">{$EXTERNAL_BASEURL}/cgi-bin/request/raster2netcdf.py?dstr=%Y%m%d%H%M&amp;prod={$rname}</pre>

<h4>Try the netCDF conversion</h4>
<form method="GET" name="try" action="/cgi-bin/request/raster2netcdf.py" class="row g-2 align-items-end">
    <input type="hidden" name="prod" value="{$rname}">
    <div class="col-auto">
        <label for="ts" class="form-label">UTC Timestamp (%Y%m%d%H%M)</label>
        <input id="ts" type="text" name="dstr" value="201710250000" class="form-control">
    </div>
    <div class="col-auto">
        <button type="submit" class="btn btn-primary">Generate</button>
    </div>
</form>

<h3 class="mt-4">Lookup Table for {$rname}</h3>

<div class="alert alert-info">Would it help you to have the information below
in a different format? Please <a class="alert-link" href="/info/contacts.php">contact us <i class="bi bi-chat-left-text" aria-hidden="true"></i></a>
if so!</div>

<div class="table-responsive">
<table class="table table-sm table-striped">
    <thead>
        <tr><th>Color Index</th><th>Value ({$runits})</th><th>Red</th><th>Green</th>
        <th>Blue</th><th>HEX</th></tr>
    </thead>
    <tbody>
        {$table2}
    </tbody>
</table>
</div>

EOM;
$t->render('single.phtml');
