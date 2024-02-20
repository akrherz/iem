<?php
define("IEM_APPID", 47);

require_once "../../../config/settings.inc.php";
require_once "../../../include/database.inc.php";
require_once "../../../include/myview.php";
require_once "../../../include/forms.php";
$t = new MyView();

$e = get_int404("e", null);
$pil = isset($_GET['pil']) ? strtoupper(substr(xssafe($_GET['pil']), 0, 6)) : null;
$bbb = isset($_GET["bbb"]) ? strtoupper(substr(xssafe($_GET["bbb"]), 0, 3)) : null;
$dir = isset($_REQUEST['dir']) ? xssafe($_REQUEST['dir']) : null;

if (is_null($pil) || trim($pil) == "") {
    die("No 'pil' provided by URL, it is required.");
}

$conn = iemdb("afos");
$rs = pg_prepare(
    $conn,
    "_LSELECT",
    "SELECT data, bbb, entered at time zone 'UTC' as mytime, source, wmo ".
    "from products WHERE pil = $1 and entered = $2");
$rs = pg_prepare(
    $conn,
    "_LSELECT_BBB",
    "SELECT data, bbb, entered at time zone 'UTC' as mytime, source, wmo ".
    "from products WHERE pil = $1 and entered = $2 and bbb = $3");
    
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
    $rs = pg_prepare($conn, "_LSELECT22", "SELECT " .
        "entered at time zone 'UTC' as mytime from $table " .
        "WHERE pil = $1 and entered $sign $2 " .
        "ORDER by entered $sortdir LIMIT 1");
    $rs = pg_execute($conn, "_LSELECT22", array(
        $pil,
        date("Y-m-d H:i", $ts)
    ));
    if (pg_num_rows($rs) == 0) {
        // widen the net
        $rs = pg_prepare($conn, "_LSELECT2", "SELECT " .
            "entered at time zone 'UTC' as mytime from products " .
            "WHERE pil = $1 and entered $sign $2 " .
            "ORDER by entered $sortdir LIMIT 1");
        $rs = pg_execute($conn, "_LSELECT2", array(
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
    $rs = pg_prepare($conn, "_LSELECT3", "SELECT data, bbb, "
        . " entered at time zone 'UTC' as mytime, source from products"
        . " WHERE pil = $1"
        . " ORDER by entered DESC LIMIT 1");
    $rs = pg_execute($conn, "_LSELECT3", array($pil));
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
function exact_product($conn, $e, $pil, $bbb){
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
        $rs = pg_execute($conn, "_LSELECT", array(
            $pil,
            gmdate("Y-m-d H:i+00", $ts),
        ));
    } else {
        $rs = pg_execute($conn, "_LSELECT_BBB", array(
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

$content = "<h3>National Weather Service Raw Text Product</h3>";

if (is_null($rs) || pg_num_rows($rs) < 1) {
    if (!is_null($e)){
        // Archived AFOS data suffers from some rectification problems, so we try
        // to be helpful here and look around for nearby products.
        $offsets = Array(-1, 1, -2, 2, -3, 3, -4, 4, -5, 5);
        foreach($offsets as $_idx => $offset){
            $rs = exact_product($conn, $e + $offset, $pil, $bbb);
            if (!is_null($rs) && pg_num_rows($rs) > 0){
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
    }
    $content .= "<div class=\"alert alert-warning\">Sorry, could not find product.</div>";
}
if (pg_num_rows($rs) > 1) {
    $rows = pg_num_rows($rs);
    $content .= '<div class="alert alert-danger"><i class="fa fa-file"></i> ' .
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
            <i class="fa fa-list"></i> Daily {$ccc} Table for {$station}</a></p>
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
            substr(is_null($row["source"]) ? "": $row["source"], 1, 3)
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
            $rs2 = pg_prepare(
                $pconn,
                "_SELECT", "SELECT num, issue, center from cwas WHERE ".
                "issue > $1 and issue < $2 and product_id = $3");
            $rs2 = pg_execute(
                $pconn, "_SELECT", array(
                    date("Y-m-d H:i+00", $basets - 3600),
                    date("Y-m-d H:i+00", $basets + 3600),
                    $product_id,
                )
            );
            if (pg_num_rows($rs2) > 0) {
                $row2 = pg_fetch_assoc($rs2, 0);
                $t->twitter_image = sprintf(
                    "/plotting/auto/plot/226/network:CWSU::cwsu:%s::num:%s::".
                    "issue:%s%%20%s.png",
                    $row2["center"],
                    $row2["num"],
                    date("Y-m-d", strtotime($row2["issue"])),
                    date("Hi", strtotime($row2["issue"])),
                );
                $img = sprintf(
                    '<p><img src="%s" class="img img-responsive"></p>',
                    $t->twitter_image,
                );
            }
            pg_close($pconn);
        }
        if (substr($pil, 0, 3) == "SPS") {
            // Account for multi-segment SPS by counting $$ occurrences
            $segments = substr_count($row["data"], "$$");
            // Can only do one, so this is the best we can do
            $t->twitter_image = "/plotting/auto/plot/217/pid:{$product_id}.png";
            $img = sprintf(
                '<p><img src="/plotting/auto/plot/217/pid:%s::segnum:0.png" ' .
                    'class="img img-responsive"></p>',
                $product_id,
            );
            for ($segnum = 1; $segnum < $segments; $segnum++) {
                $img .= sprintf(
                    '<p><img src="/plotting/auto/plot/217/pid:%s::segnum:%s.png" ' .
                        'class="img img-responsive"></p>',
                    $product_id,
                    $segnum,
                );
            }
        } else if ((substr($pil, 0, 3) == "LSR") && (intval(substr($product_id, 0, 4)) > 1985)) {
            // Can only do one, so this is the best we can do
            $t->twitter_image = "/plotting/auto/plot/242/pid:{$product_id}.png";
            $img = sprintf(
                '<p><img src="/plotting/auto/plot/242/pid:%s.png" ' .
                    'class="img img-responsive"></p>',
                $product_id,
            );
        } else {
            $t->twitter_image = "/wx/afos/{$newe}_{$pil}.png";
        }
        $t->twitter_card = "summary_large_image";
        $dstamp = date("Y-m-d H:i", $basets);
        $listlink = sprintf(
            "list.phtml?source=%s&amp;day=%s&amp;month=%s&amp;year=%s",
            $row["source"],
            date("d", $basets),
            date("m", $basets),
            date("Y", $basets)
        );
        $pil3 = substr($pil, 0, 3);
        $pil_listlink = sprintf(
            "list.phtml?by=pil&pil=%s&amp;day=%s&amp;month=%s&amp;year=%s",
            $pil3,
            date("d", $basets),
            date("m", $basets),
            date("Y", $basets)
        );
        $date2 =  date("d M Y", $basets);
        $year = date("Y", $basets);
        $year2 = intval($year) + 1;
        $content .= <<<EOF
<div class="row">
<div class="col-sm-7 col-md-7">
<p>Displaying AFOS PIL: <strong>$pil</strong> 
Received: <strong>{$dstamp} UTC</strong>

<p><a class="btn btn-primary" 
 href="p.php?dir=prev&pil=$pil&e=$newe"><i class="fa fa-arrow-left"></i> 
 Previous in Time</a>
<a class="btn btn-primary" 
 href="p.php?pil=$pil">Latest Product</a>
<a class="btn btn-primary" 
 href="p.php?dir=next&pil=$pil&e=$newe">Next in Time <i class="fa fa-arrow-right"></i></a>

<p><a class="btn btn-primary" 
 href="{$listlink}">View All {$row["source"]} Products for {$date2}</a>
 <a class="btn btn-primary" 
 href="{$pil_listlink}">View All {$pil3} Products for {$date2}</a>
<a class="btn btn-primary"
 href="{$t->twitter_image}">View As Image</a>
<a class="btn btn-primary" href="{$rawtext}">Download As Text</a></p>

{$extratools}

</div>
<div class="col-sm-5 col-md-5 well">
<form method="GET" action="/cgi-bin/afos/retrieve.py" name="bulk">
<input type="hidden" name="dl" value="1">
<input type="hidden" name="limit" value="9999">
<p><i class="fa fa-download"></i> <strong>Bulk Download</strong></p>
<strong>PIL:</strong> <input type="text" size="6" name="pil" value="{$pil}">
<select name="fmt">
 <option value="text">Single Text File (\\003 Delimited)</option>
 <option value="zip">Zip File of One Product per File</option>
</select>
<br /><strong>Start UTC Date @0z:</strong> <input type="date" min="1980-01-01"
 value="{$year}-01-01" name="sdate">
 <br /><strong>End UTC Date @0z:</strong> <input type="date" min="1980-01-01"
 value="{$year2}-01-01" name="edate">
<br /><input type="submit" value="Download Please">
</form>

</div>
</div>

EOF;
    }
    if (strtotime($row["mytime"]) != $basets) {
        continue;
    }
    $d = preg_replace(
        "/\1/", "", preg_replace("/\r\r\n/", "\n", $row["data"])
    );
    $content .= "<pre>" . htmlentities($d) . "</pre>\n";
}

$content .= $img;

$t->content = $content;
$t->render('single.phtml');
