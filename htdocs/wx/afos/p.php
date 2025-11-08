<?php
define("IEM_APPID", 47);

require_once "../../../config/settings.inc.php";
require_once "../../../include/database.inc.php";
require_once "../../../include/myview.php";
require_once "../../../include/forms.php";
$t = new MyView();
$t->headextra = <<<EOM
<link rel="stylesheet" type="text/css" href="/wx/afos/p.css">
EOM;
$t->jsextra = <<<EOM
<script type="module" src="/wx/afos/p.module.js"></script>
EOM;

$e = get_int404("e", null);
// Ensure e is 12 characters long
if (!is_null($e) && strlen($_GET["e"]) != 12) {
    // Naughty
    xssafe("<tag>");
}
$pil = strtoupper(substr(get_str404('pil', null), 0, 6));
$bbb = strtoupper(substr(get_str404("bbb", null), 0, 3));
$dir = get_str404('dir', null);

if (is_null($pil) || trim($pil) == "") {
    http_response_code(422);
    die("No 'pil' provided by URL, it is required.");
}

$conn = iemdb("afos");
$st_nobbb = iem_pg_prepare(
    $conn,
    "SELECT data, bbb, entered at time zone 'UTC' as mytime, source, wmo " .
        "from products WHERE pil = $1 and entered = $2"
);
$st_bbb = iem_pg_prepare(
    $conn,
    "SELECT data, bbb, entered at time zone 'UTC' as mytime, source, wmo " .
        "from products WHERE pil = $1 and entered = $2 and bbb = $3"
);

function locate_product($conn, $e, $pil, $dir)
{
    // Attempt to locate this product and redirect to stable URI if so
    $ts = gmmktime(
        intval(substr($e, 8, 2)),
        intval(substr($e, 10, 2)),
        0,
        intval(substr($e, 4, 2)),
        intval(substr($e, 6, 2)),
        intval(substr($e, 0, 4))
    );
    $sortdir = ($dir == 'next') ? "ASC" : "DESC";
    $sign = ($dir == 'next') ? ">" : "<";
    $table = sprintf(
        "products_%s_%s",
        date('Y', $ts),
        (intval(date("m", $ts)) > 6) ? "0712" : "0106"
    );
    // first attempt shortcut
    $stname = iem_pg_prepare($conn, "SELECT " .
        "entered at time zone 'UTC' as mytime from $table " .
        "WHERE pil = $1 and entered $sign $2 " .
        "ORDER by entered $sortdir LIMIT 1");
    $rs = pg_execute($conn, $stname, array(
        $pil,
        date("Y-m-d H:i", $ts)
    ));
    if (pg_num_rows($rs) == 0) {
        // widen the net
        $stname = iem_pg_prepare($conn, "SELECT " .
            "entered at time zone 'UTC' as mytime from products " .
            "WHERE pil = $1 and entered $sign $2 " .
            "ORDER by entered $sortdir LIMIT 1");
        $rs = pg_execute($conn, $stname, array(
            $pil,
            date("Y-m-d H:i", $ts)
        ));
    }
    if (pg_num_rows($rs) == 0) return $rs;

    $row = pg_fetch_assoc($rs, 0);
    $uri = sprintf(
        "p.php?pil=%s&e=%s",
        $pil,
        date("YmdHi", strtotime($row["mytime"]))
    );
    header("Location: $uri");
    die();
}

function last_product($conn, $pil)
{
    // Get the latest
    $stname = iem_pg_prepare($conn, "SELECT data, bbb, "
        . " entered at time zone 'UTC' as mytime, source from products"
        . " WHERE pil = $1"
        . " ORDER by entered DESC LIMIT 1");
    $rs = pg_execute($conn, $stname, array($pil));
    if (pg_num_rows($rs) == 1) {
        $row = pg_fetch_assoc($rs, 0);
        $uri = sprintf(
            "p.php?pil=%s&e=%s",
            $pil,
            date("YmdHi", strtotime($row["mytime"]))
        );
        header("Location: $uri");
        die();
    }
    return $rs;
}
function exact_product($conn, $e, $pil, $bbb)
{
    // Option 3: Explicit request
    $ts = gmmktime(
        intval(substr($e, 8, 2)),
        intval(substr($e, 10, 2)),
        0,
        intval(substr($e, 4, 2)),
        intval(substr($e, 6, 2)),
        intval(substr($e, 0, 4))
    );
    if (is_null($bbb)) {
        global $st_nobbb;
        $rs = pg_execute($conn, $st_nobbb, array(
            $pil,
            gmdate("Y-m-d H:i+00", $ts),
        ));
    } else {
        global $st_bbb;
        $rs = pg_execute($conn, $st_bbb, array(
            $pil,
            gmdate("Y-m-d H:i+00", $ts),
            $bbb,
        ));
    }
    return $rs;
}

// Okay, lets see if we can find the product we are looking for!
if (is_null($e)) {
    // Option 1: We only pil= set and no time, find the last product
    $rs = last_product($conn, $pil);
} elseif (!is_null($e) && !is_null($dir)) {
    // Option 2: We have a time set and some directionality set
    $rs = locate_product($conn, $e, $pil, $dir);
    // if the above fails, just go to last product
    $rs = last_product($conn, $pil);
} else {
    $rs = exact_product($conn, $e, $pil, $bbb);
}

$bc_pil = htmlspecialchars($pil ?? '');
$content = '<nav aria-label="breadcrumb"><ol class="breadcrumb mb-2">'
    . '<li class="breadcrumb-item"><a href="/nws/text.php">NWS Text Products</a></li>'
    . '<li class="breadcrumb-item active" aria-current="page">' . $bc_pil . '</li>'
    . '</ol></nav>'
    . '<h3 class="mb-3" aria-hidden="true">National Weather Service Text Product</h3>'
    . '<div id="afos-heading" class="visually-hidden">AFOS product ' . $bc_pil . '</div>'
    . '<div id="afos-status" class="visually-hidden" aria-live="polite" aria-atomic="true"></div>'
    . '<span id="utc-note" class="visually-hidden">Dates interpreted at 00:00 UTC</span>';

if (is_null($rs) || pg_num_rows($rs) < 1) {
    if (!is_null($e)) {
        // Archived AFOS data suffers from some rectification problems, so we try
        // to be helpful here and look around for nearby products.
        $offsets = array(-1, 1, -2, 2, -3, 3, -4, 4, -5, 5);
        foreach ($offsets as $_idx => $offset) {
            $rs = exact_product($conn, $e + $offset, $pil, $bbb);
            if (!is_null($rs) && pg_num_rows($rs) > 0) {
                $row = pg_fetch_assoc($rs, 0);
                $uri = sprintf(
                    "p.php?pil=%s&e=%s",
                    $pil,
                    date("YmdHi", strtotime($row["mytime"]))
                );
                header("Location: $uri");
                die();
            }
        }
        // Try to be even more helpful
        $rs = locate_product($conn, $e, $pil, "prev");
    }
}
if (is_null($rs) || pg_num_rows($rs) < 1) {
    $content .= '<div class="alert alert-warning" role="alert">Sorry, could not find product.</div>';
}
if (pg_num_rows($rs) > 1) {
    $rows = pg_num_rows($rs);
    $content .= '<div class="alert alert-danger"><i class="bi bi-file-earmark-text" aria-hidden="true"></i> ' .
        "Found {$rows} products at the given pil and timestamp. Scroll down to see them all.</div>";
}
$extratools = "";
$img = "";
for ($i = 0; $row = pg_fetch_assoc($rs); $i++) {
    if ($i == 0) {
        $basets = strtotime($row["mytime"]);
        if (substr($pil, 0, 3) == "CLI" || substr($pil, 0, 3) == "CF6") {
            $station = sprintf("%s%s", substr($row["source"], 0, 1), substr($pil, 3, 3));
            $year = date("Y", $basets);
            $ccc = substr($pil, 0, 3);
            $cc = strtolower($ccc);
            $extratools = <<<EOM
            <p><a class="btn btn-success" href="/nws/{$cc}table.php?station={$station}&opt=bystation&year={$year}">
                <i class="bi bi-list-ul" aria-hidden="true"></i> Daily {$ccc} Table for {$station}</a></p>
EOM;
        }
        $newe = date("YmdHi", $basets);
        $rawtext = sprintf(
            "/api/1/nwstext/%s-%s-%s-%s",
            $newe,
            $row["source"],
            $row["wmo"],
            $pil,
        );
        if ($row["bbb"] != "") {
            $rawtext .= "-" . $row["bbb"];
        }
        $isodt = date("Y-m-d\\TH:i", $basets);
        $t->title = sprintf(
            "%s from NWS %s",
            substr($pil, 0, 3),
            substr(is_null($row["source"]) ? "" : $row["source"], 1, 3)
        );
        $product_id = sprintf(
            "%s-%s-%s-%s",
            $newe,
            $row["source"],
            $row["wmo"],
            $pil
        );
        if (!is_null($row["bbb"])) {
            $product_id .= sprintf("-%s", $row["bbb"]);
        }
        $t->twitter_description = sprintf(
            "%s issued by NWS %s at %s UTC",
            substr($pil, 0, 3),
            substr($pil, 3, 3),
            date("d M Y H:i", $basets)
        );
        if (substr($pil, 0, 3) == "CWA") {
            $pconn = iemdb("postgis");
            $stname = iem_pg_prepare(
                $pconn,
                "SELECT num, issue, center from cwas WHERE " .
                    "issue > $1 and issue < $2 and product_id = $3"
            );
            $rs2 = pg_execute(
                $pconn,
                $stname,
                array(
                    date("Y-m-d H:i+00", $basets - 3600),
                    date("Y-m-d H:i+00", $basets + 3600),
                    $product_id,
                )
            );
            if (pg_num_rows($rs2) > 0) {
                $row2 = pg_fetch_assoc($rs2, 0);
                $t->twitter_image = sprintf(
                    "/plotting/auto/plot/226/network:CWSU::cwsu:%s::num:%s::" .
                        "issue:%s%%20%s.png",
                    $row2["center"],
                    $row2["num"],
                    date("Y-m-d", strtotime($row2["issue"])),
                    date("Hi", strtotime($row2["issue"])),
                );
                $img = sprintf(
                    '<p><img src="%s" class="img-fluid"></p>',
                    $t->twitter_image,
                );
            }
        }
        if (substr($pil, 0, 3) == "FRW" && strpos($row["data"], "LAT...LON") !== false) {
            $t->twitter_image = "/plotting/auto/plot/227/pid:{$product_id}.png";
            $img = <<<EOM
<p><a class="btn btn-primary"
 href="/plotting/auto/?q=227&pid={$product_id}"><i class="bi bi-bar-chart" aria-hidden="true"></i> Autoplot 227</a>
generated the following image below.  You may find more customization options
for this image by visiting that autoplot.</p>
<p><img src="/plotting/auto/plot/227/pid:{$product_id}.png"
 class="img-fluid"></p>
EOM;
        } else if (substr($pil, 0, 3) == "SPS") {
            // Account for multi-segment SPS by counting $$ occurrences
            $segments = substr_count($row["data"], "$$");
            // Can only do one, so this is the best we can do
            $t->twitter_image = "/plotting/auto/plot/217/pid:{$product_id}.png";
            $img = <<<EOM
<p><a class="btn btn-primary"
 href="/plotting/auto/?q=217&pid={$product_id}"><i class="bi bi-bar-chart" aria-hidden="true"></i> Autoplot 217</a>
generated the following image below.  You may find more customization options
, like removal of RADAR, for this image by visiting that autoplot.</p>
<p><img src="/plotting/auto/plot/217/pid:{$product_id}::segnum:0.png"
 class="img-fluid"></p>
EOM;
            for ($segnum = 1; $segnum < $segments; $segnum++) {
                $img .= sprintf(
                    '<p><img src="/plotting/auto/plot/217/pid:%s::segnum:%s.png" ' .
                        'class="img-fluid"></p>',
                    $product_id,
                    $segnum,
                );
            }
        } else if ((substr($pil, 0, 3) == "LSR") && (intval(substr($product_id, 0, 4)) > 1985)) {
            // Can only do one, so this is the best we can do
            $t->twitter_image = "/plotting/auto/plot/242/pid:{$product_id}.png";
            $img = sprintf(
                '<p><img src="/plotting/auto/plot/242/pid:%s.png" ' .
                    'class="img-fluid"></p>',
                $product_id,
            );
        } else {
            $t->twitter_image = "/wx/afos/{$newe}_{$pil}.png";
        }
        $t->twitter_card = "summary_large_image";
        $dstamp = date("Y-m-d H:i", $basets);
        $listlink = sprintf(
            "/wx/afos/list.phtml?source=%s&amp;day=%s&amp;month=%s&amp;year=%s",
            $row["source"],
            date("d", $basets),
            date("m", $basets),
            date("Y", $basets)
        );
        $pil3 = substr($pil, 0, 3);
        $pil_listlink = sprintf(
            "/wx/afos/list.phtml?by=pil&pil=%s&amp;day=%s&amp;month=%s&amp;year=%s",
            $pil3,
            date("d", $basets),
            date("m", $basets),
            date("Y", $basets)
        );
        $date2 =  date("d M Y", $basets);
        $year = date("Y", $basets);
        $year2 = intval($year) + 1;
                $content .= <<<EOM
<div class="row g-4 align-items-start">
    <div class="col-md-7 col-lg-8">
        <p class="mb-1">Displaying AFOS PIL: <strong>$pil</strong><br>
        Product Timestamp: <strong>{$dstamp} UTC</strong></p>
        <div class="btn-group my-2 flex-wrap" role="group" aria-label="Product navigation">
            <a class="btn btn-outline-primary btn-sm" aria-label="Previous product in time" href="p.php?dir=prev&pil=$pil&e=$newe"><i class="bi bi-arrow-left" aria-hidden="true"></i> Previous</a>
            <a class="btn btn-outline-primary btn-sm" aria-label="Latest product" href="p.php?pil=$pil">Latest</a>
            <a class="btn btn-outline-primary btn-sm" aria-label="Next product in time" href="p.php?dir=next&pil=$pil&e=$newe">Next <i class="bi bi-arrow-right" aria-hidden="true"></i></a>
        </div>
        <div class="d-flex flex-wrap gap-2 my-2">
            <a class="btn btn-primary btn-sm" href="{$listlink}">All {$row["source"]} Products ({$date2})</a>
            <a class="btn btn-primary btn-sm" href="{$pil_listlink}">All {$pil3} Products ({$date2})</a>
            <a class="btn btn-secondary btn-sm" href="{$t->twitter_image}">Text as Image</a>
            <a class="btn btn-secondary btn-sm" href="{$rawtext}">Download Text</a>
        </div>
        {$extratools}
    </div>
    <div class="col-md-5 col-lg-4">
        <div class="border rounded p-2 bg-light afos-bulk-wrapper">
            <form method="GET" action="/cgi-bin/afos/retrieve.py" name="bulk" aria-label="Bulk AFOS download" class="d-flex flex-wrap align-items-end gap-2 w-100 m-0 afos-bulk-form">
                <input type="hidden" name="dl" value="1">
                <input type="hidden" name="limit" value="9999">
                <div class="d-flex flex-column afos-field">
                    <label for="bulkPil" class="form-label small mb-0">3-6 Char PIL / AFOS ID</label>
                    <input id="bulkPil" type="text" maxlength="6" class="form-control form-control-sm" name="pil" value="{$pil}" autocomplete="off">
                </div>
                <div class="d-flex flex-column afos-field">
                    <label for="bulkFmt" class="form-label small mb-0">Format</label>
                    <select id="bulkFmt" name="fmt" class="form-select form-select-sm">
                        <option value="text">Text (^C delimited)</option>
                        <option value="zip">Zip</option>
                    </select>
                </div>
                <fieldset class="d-flex flex-wrap gap-2 m-0 p-0 border-0 afos-field">
                    <legend class="visually-hidden">Download date range (UTC midnight)</legend>
                    <div class="d-flex flex-column">
                        <label for="bulkSdate" class="form-label small mb-0">Start</label>
                        <input id="bulkSdate" type="date" min="1980-01-01" value="{$year}-01-01" name="sdate" class="form-control form-control-sm" aria-describedby="utc-note">
                    </div>
                    <div class="d-flex flex-column">
                        <label for="bulkEdate" class="form-label small mb-0">End</label>
                        <input id="bulkEdate" type="date" min="1980-01-01" value="{$year2}-01-01" name="edate" class="form-control form-control-sm" aria-describedby="utc-note">
                    </div>
                </fieldset>
                <div class="d-flex flex-column">
                    <button type="submit" class="btn btn-success btn-sm">Download</button>
                </div>
            </form>
            <div class="d-flex justify-content-between align-items-center afos-bulk-heading mt-1" id="bulk-download-note" role="heading" aria-level="4">
                <span class="afos-bulk-title"><i class="bi bi-download" aria-hidden="true"></i> Bulk Download</span>
                <button type="button" class="btn btn-link btn-sm p-0 afos-bulk-help-toggle" aria-expanded="false" aria-controls="bulk-help">Help</button>
            </div>
            <div id="bulk-help" class="mt-1" hidden>
                <p class="mb-1"><strong>Bulk Download Help</strong></p>
                <p class="mb-1">This bulk download tool provides the NWS text
                in a raw form, hopefully directly usable by your processing system.
                You can either provide a complete 6-character PIL/AFOS ID or provide
                the 3-character base ID (e.g., <code>AFD</code>). The start and end
                dates represent 00 UTC for those dates.  The Zip format is useful as
                the filenames will have the product timestamp, which is useful for
                when the product format has ambiguous timestamps.
                </p>
                <p class="mb-1"><a href="/cgi-bin/afos/retrieve.py?help">Backend Documentation</a></p>
            </div>
        </div>
    </div>
</div>

EOM;
    }
    if (strtotime($row["mytime"]) != $basets) {
        continue;
    }
    // Look for <?xml in the data and if found, pretty print it
    if (preg_match("/<\?xml/", $row["data"])) {
        $pos = strpos($row["data"], "<?xml");
        // data could have multiple XML messages, so we need to
        // parse each one
        $tokens = explode("<?xml", substr($row["data"], $pos));
    $content .= sprintf('<div class="afos-block" role="region" aria-label="Product XML segment"><div class="afos-toolbar"><button type="button" aria-label="Copy product text" class="btn btn-sm btn-outline-secondary afos-copy" data-copy-target="next">Copy</button></div><pre class="afos-pre">%s',
            htmlentities(substr($row["data"], 0, $pos))
        );
        foreach ($tokens as $token) {
            if (trim($token) == "") {
                continue;
            }
            $rawxml = "<?xml" . $token;
            try {
                $xml = new SimpleXMLElement($rawxml);
                $dom = dom_import_simplexml($xml)->ownerDocument;
                $dom->formatOutput = true;
                $content .= htmlentities($dom->saveXML());
            } catch (Exception $e) {
                $content .= htmlentities($rawxml);
            }
        }
    $content .= "</pre></div>";
        continue;
    }
    $repr = htmlentities(preg_replace(
        "/\1/",
        "",
        preg_replace("/\r\r\n/", "\n", $row["data"])
    ));
    $content .= '<div class="afos-block" role="region" aria-label="Product text" ><div class="afos-toolbar"><button type="button" aria-label="Copy product text" class="btn btn-sm btn-outline-secondary afos-copy" data-copy-target="next">Copy</button></div><pre class="afos-pre">' . $repr . "</pre></div>\n";
}

$content .= $img;

$t->content = $content;
$t->render('single.phtml');
