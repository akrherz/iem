<?php 
/*
 * functions that generate stuff
 */
require_once dirname(__FILE__) ."/database.inc.php";

function get_news_by_tag($tag){
    // Generate a listing of recent news items by a certain tag
    $pgconn = iemdb("mesosite", TRUE, TRUE);
    $rs = pg_prepare($pgconn, "NEWSTAGSELECT",
            "SELECT id, entered, title from news WHERE "
            ."tags @> ARRAY[$1]::varchar[] ORDER by entered DESC LIMIT 5");
    $rs = pg_execute($pgconn, "NEWSTAGSELECT", Array($tag));
    $s = "<h3>Recent News Items</h3><p>Most recent news items tagged: "
        ."{$tag}</p><ul>";
    for($i=0;$row=pg_fetch_assoc($rs);$i++){
        $s .= sprintf("<li><a href=\"/onsite/news.phtml?id=%s\">%s</a>"
                ."<br />Posted: %s</li>\n", $row["id"],
                $row["title"], date("d M Y", strtotime($row["entered"])));
    }
    $s .= "</ul>";
    return $s;
}

function get_iemapps_tags($tagname){
    // Get a html list for this tagname
    $pgconn = iemdb("mesosite", TRUE, TRUE);
    $rs = pg_prepare($pgconn, "TAGSELECT", 
            "SELECT name, description, url from iemapps WHERE "
            ."appid in (SELECT appid from iemapps_tags WHERE tag = $1) "
            ."ORDER by name ASC");
    $rs = pg_execute($pgconn, "TAGSELECT", Array($tagname));
    $s = "<ul>";
    for($i=0;$row=pg_fetch_assoc($rs);$i++){
        $s .= sprintf("<li><a href=\"%s\">%s</a><br />%s</li>\n", $row["url"],
                $row["name"], $row["description"]);	
    }
    $s .= "</ul>";
    return $s;
}

function get_website_stats(){
    $memcache = new Memcached();
    $memcache->addServer('iem-memcached', 11211);
    $val = $memcache->get("iemperf.json");
    if (! $val){
        // Fetch from nagios
        $val = @file_get_contents("http://mtadmin.local/cgi-bin/get_iemstats.py");
        if ($val) $memcache->set("iemperf.json", $val, 90);
    }
    $bcolor = "success";
    $rcolor = "success";
    $bandwidth = 0;
    $req = 0;
    if ($val){
        $jobj = json_decode($val);
    
        $bandwidth = $jobj->stats->bandwidth / 1000000.0;
        // grading of the bandwidth (MB/s)
        if ($bandwidth > 35) $bcolor = "warning";
        if ($bandwidth > 70) $bcolor = "danger";
    
        $req = $jobj->stats->apache_req_per_sec;
        if ($req > 5000) $rcolor = "warning";
        if ($req > 7500) $rcolor = "danger";
        
    }
    $label = sprintf("%.1f MB/s", $bandwidth);
    $bpercent = intval( $bandwidth / 124.0  * 100.0 );
    $rlabel = number_format($req);
    $rpercent = intval( $req / 15000.0 * 100.0);    

    $s = <<<EOF
<div class="panel panel-default">
<div class="panel-heading">Current Website Performance:</div>
  <div class="panel-body">

  <span>Bandwidth: {$label}</span>
<div class="progress">
    <div class="progress-bar progress-bar-{$bcolor}" role="progressbar" aria-valuenow="{$bpercent}" aria-valuemin="0" aria-valuemax="100" style="width: {$bpercent}%;">
    </div>
</div>

  <span>Requests/Second: {$rlabel}</span>
<div class="progress">
    <div class="progress-bar progress-bar-{$rcolor}" role="progressbar" aria-valuenow="{$rpercent}" aria-valuemin="0" aria-valuemax="100" style="width: {$rpercent}%;">
    </div>
</div>
            
  </div>
</div>
EOF;
    return $s;
}

function gen_feature($t){
    $s = '';
    
    $connection = iemdb("mesosite", TRUE, TRUE);
    $query1 = "SELECT *, to_char(valid, 'YYYY/MM/YYMMDD') as imageref,
                to_char(valid, 'DD Mon YYYY HH:MI AM') as webdate,
                to_char(valid, 'YYYY-MM-DD') as permalink from feature
                WHERE valid < now() ORDER by valid DESC LIMIT 1";
    $result = pg_exec($connection, $query1);
    $row = pg_fetch_assoc($result,0);
    $good = intval($row["good"]);
    $bad = intval($row["bad"]);
    $abstain = intval($row["abstain"]);
    $tags = ($row["tags"] != null) ? explode(",", $row["tags"]): Array();
    $fbid = $row["fbid"];
    $fburl = sprintf("https://www.facebook.com/permalink.php?".
            "story_fbid=%s&id=157789644737", $fbid);
    
    $imghref = sprintf("/onsite/features/%s.%s", $row["imageref"],
        $row["mediasuffix"]);
    
    $linktext = "";
    if ($row["appurl"] != ""){
        $linktext = "<br /><a class=\"btn btn-sm btn-primary\" href=\"".$row["appurl"]."\"><i class=\"fa fa-signal\"></i> Generate This Chart on Website</a>";
    }
    
    $tagtext = "";
    if (sizeof($tags) > 0){
        $tagtext .= "<br /><small>Tags: &nbsp; ";
        foreach($tags as $k => $v)
        {
            $tagtext .= sprintf("<a href=\"/onsite/features/tags/%s.html\">%s</a> &nbsp; ", $v, $v);
        }
        $tagtext .= "</small>";
    }
    $jsextra = "";
    if ($row["mediasuffix"] == 'mp4'){
        $imgiface = <<<EOM
<video class="img img-responsive" controls>
    <source src="${imghref}" type="video/mp4">
    Your browser does not support the video tag.
</video>
EOM;
    } else {
        $imgiface = "<a href=\"$imghref\"><img src=\"$imghref\" alt=\"Feature\" class=\"img img-responsive\" /></a>";
    }
    if ($row["javascripturl"]){
        $imgiface = <<<EOF
<div class="hidden-sm hidden-xs">
<div id="ap_container" style="width:100%s;height:400px;"></div>
</div>
<div class="visible-sm visible-xs">
<a href="$imghref"><img src="$imghref" alt="Feature" class="img img-responsive" /></a>
</div>
EOF;
        $HC = "8.2.0";
        $jsextra = <<<EOF
<script src="/vendor/highcharts/{$HC}/highcharts.js"></script>
<script src="/vendor/highcharts/{$HC}/highcharts-more.js"></script>
<script src="/vendor/highcharts/{$HC}/modules/exporting.js"></script>
<script src="{$row["javascripturl"]}"></script>
EOF;
    }
    
    $s .= <<<EOF
<div class="panel panel-default top-buffer">
    <div class="panel-heading">
    
<div class='row'>
    <div class='col-xs-12 col-sm-4'><b>IEM Daily Feature</b>
        <a href="/feature_rss.php"><img src="/images/rss.gif" /></a></div>
    <div class='col-xs-12 col-sm-8'>
        <div class='btn-group row'>
            <a class="btn btn-default col-xs-6 col-sm-3" href="{$fburl}">Facebook</a>
            <a class="btn btn-default col-xs-6 col-sm-3" href="/onsite/features/cat.php?day={$row["permalink"]}">Permalink</a>
            <a class="btn btn-default col-xs-6 col-sm-4" href="/onsite/features/past.php">Past Features</a>
            <a class="btn btn-default col-xs-6 col-sm-2" href="/onsite/features/tags/">Tags</a>
         </div>
    </div>
</div>
    
        <div class="clearfix"></div>
    </div>
    <div class="panel-body">

    
        <div class="thumbnail col-xs-12 col-sm-7 pull-right">
            {$imgiface}
            <div class="caption"><span>{$row["caption"]}</span>{$linktext}</div>
        </div>
        
        <h4 style="display: inline;">{$row["title"]}</h4>
        
            <br /><small>Posted: {$row["webdate"]}, Views: {$row["views"]}</small>
            {$tagtext}
            <br />{$row["story"]}
    
            


        <div class="clearfix"></div>
            

EOF;
    
    /* Rate Feature and Past ones too! */
    if ($row["voting"] == "f"){
        $fbtext = "";
        $vtext = "";
    } else {
        $vtext = <<<EOF
        <div style="clear:both;">
        <div class="row">
        <div class="col-xs-12 col-sm-3"><strong><span id="feature_msg">Rate Feature</span></strong></div>
        <div class="col-xs-12 col-sm-3"> 
<button class="btn btn-success btn-block feature_btn" role="button" data-voting="good">Good (<span id="feature_good_votes">$good</span> votes)</button>
        </div>
        <div class="col-xs-12 col-sm-3"> 
<button class="btn btn-danger btn-block feature_btn" role="button" data-voting="bad">Bad (<span id="feature_bad_votes">$bad</span> votes)</button>
        </div>
        <div class="col-xs-12 col-sm-3"> 
<button class="btn btn-warning btn-block feature_btn" role="button" data-voting="abstain">Abstain (<span id="feature_abstain_votes">$abstain</span> votes)</button>
        </div>
        </div>
    </div>
EOF;
        
        $t->jsextra = <<<EOF
        <div id="fb-root"></div>
<script type="text/javascript">
(function(d, s, id) {
  var js, fjs = d.getElementsByTagName(s)[0];
  if (d.getElementById(id)) return;
  js = d.createElement(s); js.id = id;
  js.src = "//connect.facebook.net/en_US/all.js#xfbml=1&appId=196492870363354";
  fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));

window.fbAsyncInit = function() {
    FB.Event.subscribe('comment.create', function(response){
        $.post('/fbcomments.php', {
          "action": "comment created",
          "url_of_page_comment_leaved_on": response.href,
          "id_of_comment_object": response.commentID
        });
      });
}
function onFeatureData(data){
      $("#feature_good_votes").html(data.good);
      $("#feature_bad_votes").html(data.bad);
      $("#feature_abstain_votes").html(data.abstain);
      if (! data.can_vote){
          $("#feature_msg").html("<i class=\"fa fa-ok\"></i> Thanks for voting!");
          $("button.feature_btn").prop("disabled",true);
      }
}
$("button.feature_btn").click(function(){
  $.get("/onsite/features/vote/"+ $(this).data('voting') +".json", onFeatureData);
});
$(document).ready(function(){
  $.get("/onsite/features/vote.json", onFeatureData);
});

</script>
{$jsextra}
EOF;
        $huri = "https://mesonet.agron.iastate.edu/onsite/features/cat.php?day=". $row["permalink"] ;
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
    
    for($i=0;$row=pg_fetch_assoc($result);$i++)
    {
        // Start a new row
        if ($i % 2 == 0){ $s .= "\n<div class=\"row\">"; }
        $s .= sprintf("\n<div class=\"col-xs-6\">%s: %s".
                "<a href=\"onsite/features/cat.php?day=%s\">".
                "%s</a></div>",
                $row["yr"],
                $row["appurl"] ? "<i class=\"fa fa-signal\"></i> ": "",
                substr($row["valid"], 0, 10), $row["title"]);
        // End the row
        if ($i % 2 != 0){ $s .= "\n</div>\n"; }
    }
    
    if ($i > 0 && $i % 2 != 0){ 
        $s .= "\n<div class=\"col-xs-6\">&nbsp;</div>\n</div>"; 
    }
        
    $s .= "</div><!--  end of panel body -->";
    $s .= "</div><!-- end of panel -->";
    
    return $s;
}
