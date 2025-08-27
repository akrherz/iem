<?php
require_once "../../../config/settings.inc.php";
define("IEM_APPID", 55);
define("FBEXTRA", True);
require_once "../../../include/myview.php";
require_once "../../../include/database.inc.php";
require_once "../../../include/forms.php";
require_once "../../../include/mlib.php";

$t = new MyView();

try {
    $day = isset($_GET["day"]) ? new DateTime(xssafe($_GET["day"])) : null;
} catch (Exception $exp){
    xssafe("<tag>");
    die();
}
$offset = get_int404("offset", 0);
if (is_null($day)) {
    $day = new DateTime("now");
    $offset = -1;
}

$dbconn = iemdb("mesosite");
$stname1 = iem_pg_prepare($dbconn, "SELECT *, date(valid) as d,
              to_char(valid, 'YYYY/MM/YYMMDD') as imageref, 
              to_char(valid, 'DD Mon YYYY HH:MI AM') as webdate from feature
              WHERE valid < $1 ORDER by valid DESC limit 1");
$stname2 = iem_pg_prepare($dbconn, "SELECT *, date(valid) as d,
              to_char(valid, 'YYYY/MM/YYMMDD') as imageref, 
              to_char(valid, 'DD Mon YYYY HH:MI AM') as webdate from feature
              WHERE date(valid) = $1");
$stname3 = iem_pg_prepare($dbconn, "SELECT *, date(valid) as d,
              to_char(valid, 'YYYY/MM/YYMMDD') as imageref, 
              to_char(valid, 'DD Mon YYYY HH:MI AM') as webdate from feature
              WHERE valid > ($1::date + '1 day'::interval) 
              ORDER by valid ASC limit 1");

$q = $stname2;
if ($offset == "-1") {
    $q = $stname1;
} else if ($offset == "+1") {
    $q = $stname3;
}
$result = pg_execute($dbconn, $q, array($day->format("Y-m-d")));

if (pg_num_rows($result) == 0) {
    http_response_code(422);
    die("Feature Not Found");
}

$row = pg_fetch_assoc($result, 0);
$valid = strtotime($row["valid"]);

if (is_null($row["fbid"])) {
    $row["fbid"] = $valid;
}

$day = $row["d"];
$prettyday = date("l, d F Y", $valid);
$big = sprintf("/onsite/features/%s.%s", $row["imageref"], $row["mediasuffix"]);

$linktext = "";
if ($row["appurl"] != "") {
    $linktext = "<br /><a class=\"btn btn-sm btn-primary\" href=\"" . $row["appurl"] . "\"><i class=\"bi bi-signal\" aria-hidden=\"true\"></i> Generate This Chart on Website</a>";
}

$t->title = "$day Feature - " . $row["title"];
if ($row["mediasuffix"] == 'mp4') {
    // Get the video size and width
    $t->twitter_video = $big;
    $t->twitter_video_height = $row["media_height"];
    $t->twitter_video_width = $row["media_width"];
        $iso = date('c', $valid);
        $alt = htmlspecialchars($row["title"], ENT_QUOTES);
        $media = <<<EOM
    <figure class="figure">
        <video class="img-fluid" controls aria-label="Feature video for {$alt}">
            <source src="{$big}" type="video/mp4">
            Your browser does not support the video tag.
        </video>
        <figcaption class="figure-caption small">{$row["caption"]}</figcaption>
    </figure>
EOM;
} else {
        $t->twitter_image = $big;
        $iso = date('c', $valid);
        $alt = htmlspecialchars($row["title"], ENT_QUOTES);
        $media = <<<EOM
    <figure class="figure">
        <a href="{$big}"><img src="{$big}" class="img-fluid rounded" alt="{$alt}"></a>
        <figcaption class="figure-caption small"><a href="{$big}">View larger image</a> — {$row["caption"]}</figcaption>
    </figure>
EOM;
}

$content = <<<EOM

<nav class="d-flex justify-content-between align-items-center mb-3" aria-label="Feature navigation">
    <div>
        <a href="cat.php?day={$day}&offset=-1" class="btn btn-outline-secondary btn-sm" aria-label="Previous feature">&larr; Previous</a>
    </div>
    <div class="text-center flex-fill">
        <h4 class="mb-0">IEM Daily Feature<br /><small>{$prettyday}</small></h4>
    </div>
    <div class="text-end">
        <a href="cat.php?day={$day}&offset=1" class="btn btn-outline-secondary btn-sm" aria-label="Next feature">Next &rarr;</a>
    </div>
</nav>

<article>
    <header>
        <h3>{$row["title"]}</h3>
        <p><small class="text-muted">Posted: <time datetime="{$iso}">{$row["webdate"]}</time></small></p>
    </header>

    <div class="row">
        <div class="col-12 col-md-6">
            {$media}
            {$linktext}
        </div>
        <div class="col-12 col-md-6">
            <div class="card bg-light p-3 rounded">{$row["story"]}
EOM;
if ($row["voting"] == 't' && (intval($row["good"]) > 0 || intval($row["bad"]) > 0)) {
    $content .= "<br /><br /><b>Voting:</b>
            <br />Good = " . $row["good"]
        . " <br />Bad = " . $row["bad"];
    if ($row["abstain"] > 0) $content .= " <br />Abstain = " . $row["abstain"];
}
$content .= "<br />" . printTags(is_null($row["tags"]) ? Array(): explode(",", $row["tags"]));
$content .= "<br />" . printTags(is_null($row["tags"]) ? Array(): explode(",", $row["tags"]));

$content .= <<<EOM
</div>
        </div><!-- ./row -->
    </article>
    <div class="my-3" aria-hidden="true">&nbsp;</div>
EOM;
$t->content = $content;
$t->render('single.phtml');
