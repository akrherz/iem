<?php 
/*
 * functions that generate stuff
 */
include_once dirname(__FILE__) ."/database.inc.php";
function gen_feature($t){
	$s = '';
	
	$connection = iemdb("mesosite", TRUE, TRUE);
	$query1 = "SELECT oid, *, to_char(valid, 'YYYY/MM/YYMMDD') as imageref,
                to_char(valid, 'DD Mon YYYY HH:MI AM') as webdate,
                to_char(valid, 'YYYY-MM-DD') as permalink from feature
                ORDER by valid DESC LIMIT 1";
	$result = pg_exec($connection, $query1);
	$row = pg_fetch_assoc($result,0);
	$foid = $row["oid"];
	$good = intval($row["good"]);
	$bad = intval($row["bad"]);
	$abstain = intval($row["abstain"]);
	$tags = ($row["tags"] != null) ? explode(",", $row["tags"]): Array();
	$fbid = $row["fbid"];
	$fburl = "http://www.facebook.com/pages/IEM/157789644737?v=wall&story_fbid=".$fbid;
	/* Hehe, check for a IEM vote! */
	$voted = FALSE;

	if (array_key_exists('foid', $_COOKIE) && $_COOKIE["foid"] == $foid)
	{
		$voted = TRUE;
	} elseif (getenv("REMOTE_ADDR") == "129.186.142.22" || getenv("REMOTE_ADDR") == "129.186.142.37")
	{
	
	} elseif (isset($_GET["feature_good"]))
	{
		setcookie("foid", $foid, time()+100600);
		$voted = TRUE;
	
		$isql = "UPDATE feature SET good = good + 1 WHERE oid = $foid";
		$good += 1;
		pg_exec($connection, $isql);
	} elseif (isset($_GET["feature_bad"]))
	{
		setcookie("foid", $foid, time()+100600);
		$voted = TRUE;
	
		$isql = "UPDATE feature SET bad = bad + 1 WHERE oid = $foid";
		$bad += 1;
		pg_exec($connection, $isql);
	} elseif (isset($_GET["feature_abstain"]))
	{
		setcookie("foid", $foid, time()+100600);
		$voted = TRUE;
	
		$isql = "UPDATE feature SET abstain = abstain + 1 WHERE oid = $foid";
		$abstain += 1;
		pg_exec($connection, $isql);
	}
	
	
	$fref = "/mesonet/share/features/". $row["imageref"] ."_s.png";
	$width = 320;
	$height = 240;
	if (is_file($fref)){
		list($width, $height, $type, $attr) = @getimagesize($fref);
	}
	$imghref = sprintf("/onsite/features/%s_s.png", $row["imageref"]);
	$bigimghref = sprintf("/onsite/features/%s.png", $row["imageref"]);
	
	$s .= <<<EOF
	<div class="panel panel-default top-buffer">
	  <div class="panel-heading">
	  <b>IEM Daily Feature</b> &nbsp; <a href="/feature_rss.php"><img src="/images/rss.gif" /></a>
	  <div class="btn-group pull-right">
	<a class="btn btn-default" href="{$fburl}">Facebook</a>
	<a class="btn btn-default" href="/onsite/features/cat.php?day={$row["permalink"]}">Permalink</a>
	<a class="btn btn-default" href="/onsite/features/past.php">Past Features</a>
	<a class="btn btn-default" href="/onsite/features/tags/">Tags</a>
		</div>
		<div class="clearfix"></div>
	  </div>
	  <div class="panel-body">
	
	  <h4 style="display: inline;">{$row["title"]}</h4>
 
	<div class="pull-left">
EOF;
	$s .= "<small>Posted: ". $row["webdate"] ."</small>";
	$s .= "<a href=\"$bigimghref\"><img src=\"$imghref\" alt=\"Feature\" class=\"pull-right\" /></a>";
	if (sizeof($tags) > 0){
		$s .= "<br /><small>Tags: &nbsp; ";
		while (list($k,$v) = each($tags))
		{
			$s .= sprintf("<a href=\"/onsite/features/tags/%s.html\">%s</a> &nbsp; ", $v, $v);
		}
		$s .= "</small>";
	}
	$s .= "<br />". $row["story"] ;
	
	/* Rate Feature and Past ones too! */
	if ($row["voting"] == "f"){
	
	} else {
		$s .= "<div style='clear:both;'>";
		if ($voted){
			$goodurl = "#";
			$badurl = "#";
			$abstainurl = "#";
			$msg = "Thanks for voting!";
		} else {
			$goodurl = "/?feature_good";
			$badurl = "/?feature_bad";
			$abstainurl = "/?feature_abstain";
			$msg = "Rate Feature";
		}
	
		$s .= "<strong>$msg</strong> 
		<a class=\"btn btn-success\" href=\"$goodurl\">Good ($good votes)</a>
		<a class=\"btn btn-danger\" href=\"$badurl\">Bad ($bad votes)</a>
		<a class=\"btn btn-warning\" href=\"$abstainurl\">Abstain ($abstain votes)</a>
		</div>";
		
		$t->jsextra = "<script src=\"http://connect.facebook.net/en_US/all.js#appId=196492870363354&amp;xfbml=1\"></script>";
		$s .= "<div class=\"container\" style=\"margin-top: 5px\"><div id=\"fb-root\"></div>
		<fb:comments send_notification_uid=\"16922938\" callback=\"/fbcb.php\" title=\"". $row["title"] ."\" \" href=\"http://mesonet.agron.iastate.edu/onsite/features/cat.php?day=". $row["permalink"] ."\" xid=\"$fbid\" numposts=\"6\" width=\"520\"></fb:comments>";
	
		$s .= "</div></div>";
	}
	/* Now, lets look for older features! */
	$s .= "<br /><strong>Previous Years' Features</strong>";
	$sql = "select *, extract(year from valid) as yr from feature 
			WHERE extract(month from valid) = extract(month from now()) 
			and extract(day from valid) = extract(day from now()) and 
			extract(year from valid) != extract(year from now()) ORDER by yr DESC";
	$result = pg_exec($connection, $sql);
	for($i=0;$row=@pg_fetch_array($result,$i);$i++)
	{
		// Start a new row
		if ($i % 2 == 0){ $s .= "\n<div class=\"row\">"; }
		$s .= "\n<div class=\"col-md-6\">". $row["yr"] .": <a href=\"onsite/features/cat.php?day=". substr($row["valid"], 0, 10) ."\">". $row["title"] ."</a></div>";
		// End the row
		if ($i % 2 != 0){ $s .= "\n</div>\n"; }
	}
	
	if ($i % 2 != 0){ $s .= "\n<div class=\"col-md-6\">&nbsp;</div>\n</div>"; }
		
	$s .= "</div><!--  end of panel body -->";
	$s .= "</div>";
	
	return $s;
}

?>