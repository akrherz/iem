<?php
/*
 * functions that generate stuff
 */
require_once dirname(__FILE__) . "/database.inc.php";
require_once dirname(__FILE__) . "/memcache.php";

/**
 * Generate a listing of recent citations for a given IEM resource
 * 
 * Result is cached for 1 hour
 * 
 * @param string $label The IEM resource label
 * @return string HTML
 */
$get_website_citations = cacheable('citations')(function ($label){
    $conn = iemdb("mesosite");
    $stname = iem_pg_prepare(
        $conn,
        "SELECT * from website_citations WHERE iem_resource = $1 ".
        "ORDER by publication_date DESC LIMIT 10");
    $rs = pg_execute($conn, $stname, array($label));
    $s = <<<EOM
<h3>Publications Citing IEM Data (<a href="/info/refs.php">View All</a>)</h3>
<p>These are the most recent 10 publications that have cited the usage of data
from this page. This
list is not exhaustive, so please <a href="/info/contacts.php">let us know</a>
if you have a publication that should be added.</p>
<ul>
EOM;
    for ($i=0; $row = pg_fetch_assoc($rs); $i++){
        $s .= sprintf(
            "<li>%s <a href=\"%s\">%s</a></li>",
            $row["title"], $row["link"], $row["link"]);
    }
    $s .= "</ul>";
    return $s;
});


$get_news_by_tag = cacheable("newsbytag")(function($tag)
{
    // Generate a listing of recent news items by a certain tag
    $pgconn = iemdb("mesosite");
    $stname = iem_pg_prepare(
        $pgconn,
        "SELECT id, entered, title from news WHERE "
            . "tags @> ARRAY[$1]::varchar[] ORDER by entered DESC LIMIT 5"
    );
    $rs = pg_execute($pgconn, $stname, array($tag));
    $s = "<h3>Recent News Items</h3><p>Most recent news items tagged: "
        . "{$tag}</p><ul>";
    for ($i = 0; $row = pg_fetch_assoc($rs); $i++) {
        $s .= sprintf(
            "<li><a href=\"/onsite/news.phtml?id=%s\">%s</a>"
                . "<br />Posted: %s</li>\n",
            $row["id"],
            $row["title"],
            date("d M Y", strtotime($row["entered"]))
        );
    }
    $s .= "</ul>";
    return $s;
});

$get_iemapps_tags = cacheable("iemappstags")(function($tagname)
{
    // Get a html list for this tagname
    $pgconn = iemdb("mesosite");
    $stname = iem_pg_prepare(
        $pgconn,
        "SELECT name, description, url from iemapps WHERE "
            . "appid in (SELECT appid from iemapps_tags WHERE tag = $1) "
            . "ORDER by name ASC"
    );
    $rs = pg_execute($pgconn, $stname, array($tagname));
    $s = "<ul>";
    while ($row = pg_fetch_assoc($rs)) {
        $s .= sprintf(
            "<li><a href=\"%s\">%s</a><br />%s</li>\n",
            $row["url"],
            $row["name"],
            $row["description"]
        );
    }
    $s .= "</ul>";
    return $s;
});

$get_website_stats = cacheable("websitestats", 120)(function ()
{
    // Fetch from nagios
    $val = file_get_contents("https://nagios.agron.iastate.edu/cgi-bin/get_iemstats.py");  // skipcq
    $bcolor = "success";
    $rcolor = "success";
    $ocolor = "success";
    $acolor = "success";
    $bandwidth = 0;
    $req = 0;
    $ok = 0;
    $apirate = 0;
    if ($val) {
        $jobj = json_decode($val);

        $ok = $jobj->stats->telemetry_ok;
        if ($ok < 90) $ocolor = "warning";
        if ($ok < 80) $ocolor = "danger";

        $apirate = $jobj->stats->telemetry_rate;
        if ($apirate < 10) $acolor = "warning";
        if ($apirate < 5) $acolor = "danger";

        $bandwidth = $jobj->stats->bandwidth / 1000000.0;
        // grading of the bandwidth (MB/s)
        if ($bandwidth > 35) $bcolor = "warning";
        if ($bandwidth > 70) $bcolor = "danger";

        $req = $jobj->stats->apache_req_per_sec;
        if ($req > 5000) $rcolor = "warning";
        if ($req > 7500) $rcolor = "danger";
    }
    $label = sprintf("%.1f MB/s", $bandwidth);
    $bpercent = intval($bandwidth / 124.0  * 100.0);
    $rlabel = sprintf("%s req/s", number_format($req));
    $rpercent = intval($req / 15000.0 * 100.0);
    $olabel = sprintf("%.0f%%", $ok);
    $opercent = intval($ok);
    $alabel = sprintf("%.1f req/s", $apirate);
    $apercent = intval($apirate / 100.0 * 100.0);

    $s = <<<EOF
<div class="card mb-3">
<div class="card-header">Current Website Performance:</div>
  <div class="card-body">

  <div class="mb-2">
    <span class="fw-bold">Bandwidth: {$label}</span>
    <div class="progress">
        <div class="progress-bar bg-{$bcolor}" role="progressbar" aria-valuenow="{$bpercent}" aria-valuemin="0" aria-valuemax="100" style="width: {$bpercent}%;">
        </div>
    </div>
  </div>

  <div class="mb-2">
    <span class="fw-bold">Total Website: {$rlabel}</span>
    <div class="progress">
        <div class="progress-bar bg-{$rcolor}" role="progressbar" aria-valuenow="{$rpercent}" aria-valuemin="0" aria-valuemax="100" style="width: {$rpercent}%;">
        </div>
    </div>
  </div>

  <div class="mb-2">
    <span class="fw-bold">API/Data Services: {$alabel}</span>
    <div class="progress">
        <div class="progress-bar bg-{$acolor}" role="progressbar" aria-valuenow="{$apercent}" aria-valuemin="0" aria-valuemax="100" style="width: {$apercent}%;">
        </div>
    </div>
  </div>

  <div class="mb-2">
    <span class="fw-bold">API Success: {$olabel}</span>
    <div class="progress">
        <div class="progress-bar bg-{$ocolor}" role="progressbar"
        aria-valuenow="{$opercent}" aria-valuemin="0" aria-valuemax="100"
        style="width: {$opercent}%;">
        </div>
    </div>
  </div>

  </div>
</div>
EOF;
    return $s;
});

/**
 * Generate the HTML for the most recent feature
 * With 2 minutes of caching
 * param object $t Template object
 * return string HTML
 */
function gen_feature($t)
{
    global $EXTERNAL_BASEURL;
    $s = '';

    $connection = iemdb("mesosite");
    $query1 = "SELECT *, to_char(valid, 'YYYY/MM/YYMMDD') as imageref,
                to_char(valid, 'DD Mon YYYY HH:MI AM') as webdate,
                to_char(valid, 'YYYY-MM-DD') as permalink from feature
                WHERE valid < now() ORDER by valid DESC LIMIT 1";
    $result = pg_exec($connection, $query1);
    $row = pg_fetch_assoc($result, 0);
    $good = intval($row["good"]);
    $bad = intval($row["bad"]);
    $abstain = intval($row["abstain"]);
    $tags = ($row["tags"] != null) ? explode(",", $row["tags"]) : array();
    $fbid = $row["fbid"];
    $fburl = sprintf("https://www.facebook.com/permalink.php?" .
        "story_fbid=%s&id=157789644737", $fbid);

    $imghref = sprintf(
        "/onsite/features/%s.%s",
        $row["imageref"],
        $row["mediasuffix"]
    );

    $linktext = "";
    if ($row["appurl"] != "") {
        $linktext = "<br /><a class=\"btn btn-sm btn-primary\" href=\"" . $row["appurl"] . "\"><i class=\"bi bi-bar-chart\"></i> Generate This Chart on Website</a>";
    }

    $tagtext = "";
    if (sizeof($tags) > 0) {
        $tagtext .= "<br /><small>Tags: &nbsp; ";
        foreach ($tags as $k => $v) {
            $tagtext .= sprintf("<a href=\"/onsite/features/tags/%s.html\">%s</a> &nbsp; ", $v, $v);
        }
        $tagtext .= "</small>";
    }
    $jsextra = "";
    if ($row["mediasuffix"] == 'mp4') {
        $imgiface = <<<EOM
<video class="img img-fluid" controls>
    <source src="{$imghref}" type="video/mp4">
    Your browser does not support the video tag.
</video>
EOM;
    } else {
        $imgiface = "<a href=\"$imghref\"><img src=\"$imghref\" alt=\"Feature\" class=\"img img-fluid\" /></a>";
    }
    if ($row["javascripturl"]) {
        $imgiface = <<<EOF
<div class="d-none d-md-block">
<div id="ap_container" style="width:100%;height:400px;"></div>
</div>
<div class="d-md-none">
<a href="$imghref"><img src="$imghref" alt="Feature" class="img img-fluid" /></a>
</div>
EOF;
        $HC = "8.2.0";
        $jsextra = <<<EOM
<script src="/vendor/highcharts/{$HC}/highcharts.js"></script>
<script src="/vendor/highcharts/{$HC}/highcharts-more.js"></script>
<script src="/vendor/highcharts/{$HC}/modules/exporting.js"></script>
<script src="{$row["javascripturl"]}"></script>
EOM;
    }

    $s .= <<<EOF
<div class="card mb-3">
    <div class="card-header">
    
<div class='row'>
    <div class='col-12 col-sm-4'><b>IEM Daily Feature</b>
        <a href="/feature_rss.php"><img src="/images/rss.gif" /></a></div>
    <div class='col-12 col-sm-8'>
        <div class='d-flex flex-wrap gap-1'>
            <a class="btn btn-outline-secondary btn-sm" href="{$fburl}">Facebook</a>
            <a class="btn btn-outline-secondary btn-sm" href="/onsite/features/cat.php?day={$row["permalink"]}">Permalink</a>
            <a class="btn btn-outline-secondary btn-sm" href="/onsite/features/past.php">Past Features</a>
            <a class="btn btn-outline-secondary btn-sm" href="/onsite/features/tags/">Tags</a>
         </div>
    </div>
</div>
    
    </div>
    <div class="card-body">

    
        <div class="col-12 col-sm-7 float-end">
            <div class="card">
                <div class="card-img-top">
                    {$imgiface}
                </div>
                <div class="card-body"><span>{$row["caption"]}</span>{$linktext}</div>
            </div>
        </div>

        <h4 style="display: inline;">{$row["title"]}</h4>
        
            <br /><small>Posted: {$row["webdate"]}, Views: {$row["views"]}</small>
            {$tagtext}
            <br />{$row["story"]}

        <div class="clearfix"></div>

EOF;

    /* Rate Feature and Past ones too! */
    if ($row["voting"] == "f") {
        $fbtext = "";
        $vtext = "";
    } else {
        $vtext = <<<EOM
        <div class="mt-3">
        <div class="row g-2">
        <div class="col-12 col-sm-3 d-flex align-items-center"><strong><span id="feature_msg">Rate Feature</span></strong></div>
        <div class="col-12 col-sm-3"> 
<button class="btn btn-success w-100 feature_btn" type="button" data-voting="good">Good (<span id="feature_good_votes">$good</span> votes)</button>
        </div>
        <div class="col-12 col-sm-3"> 
<button class="btn btn-danger w-100 feature_btn" type="button" data-voting="bad">Bad (<span id="feature_bad_votes">$bad</span> votes)</button>
        </div>
        <div class="col-12 col-sm-3"> 
<button class="btn btn-warning w-100 feature_btn" type="button" data-voting="abstain">Abstain (<span id="feature_abstain_votes">$abstain</span> votes)</button>
        </div>
        </div>
    </div>
EOM;

        $t->jsextra = <<<EOF
<script src="index.js"></script>
{$jsextra}
EOF;
        $huri = "{$EXTERNAL_BASEURL}/onsite/features/cat.php?day=" . $row["permalink"];
        $fbtext = <<<EOF
<div class="fb-comments" data-href="{$huri}" data-numposts="5" data-colorscheme="light"></div>
EOF;
    }
    $s .= <<<EOF
        $vtext
        $fbtext
            
        <br /><strong>Previous Years' Features</strong>
            
EOF;
    /* Now, lets look for older features! */
    $sql = "select *, extract(year from valid) as yr from feature 
            WHERE extract(month from valid) = extract(month from now()) 
            and extract(day from valid) = extract(day from now()) and 
            extract(year from valid) != extract(year from now()) ORDER by yr DESC";
    $result = pg_exec($connection, $sql);

    for ($i = 0; $row = pg_fetch_assoc($result); $i++) {
        // Start a new row
        if ($i % 2 == 0) {
            $s .= "\n<div class=\"row\">";
        }
        $s .= sprintf(
            "\n<div class=\"col-6\">%s: %s" .
                "<a href=\"onsite/features/cat.php?day=%s\">" .
                "%s</a></div>",
            $row["yr"],
            $row["appurl"] ? "<i class=\"bi bi-bar-chart\"></i> " : "",
            substr($row["valid"], 0, 10),
            $row["title"]
        );
        // End the row
        if ($i % 2 != 0) {
            $s .= "\n</div>\n";
        }
    }

    if ($i > 0 && $i % 2 != 0) {
        $s .= "\n<div class=\"col-6\">&nbsp;</div>\n</div>";
    }

    $s .= "</div><!--  end of card body -->";
    $s .= "</div><!-- end of card -->";

    return $s;
};

/**
 * Get recent news items
 */
$get_recent_news = cacheable("recentnews", 120)(function(){
    $pgconn = iemdb("mesosite");
    $rs = pg_query($pgconn, "SELECT * from news ORDER by entered DESC LIMIT 5");
    
    $today = new DateTime();
    
    $news = "";
    while ($row = pg_fetch_assoc($rs)){
        $ts = new DateTime(substr($row["entered"],0,16));
        if ($ts > $today) $sts = $ts->format("g:i A");
        $sts = $ts->format("j M g:i A");
        $news .= sprintf("<p><a href=\"/onsite/news.phtml?id=%s\">%s</a>".
            "<br /><i>Posted:</i> %s</li>\n", $row["id"], $row["title"], $sts);
    }
    return $news;
});