<?php
 include("../../config/settings.inc.php");
 include("../../include/myview.php");
 include("../../include/vtec.php"); 
 include("../../include/forms.php");
 include("../../include/database.inc.php");
 include("../../include/imagemaps.php");
 
 $pgconn = iemdb('postgis');
 
 $t = new MyView();
 define("IEM_APPID", 77);

 $year = isset($_REQUEST["year"])? intval($_REQUEST["year"]): date("Y");
 $wfo = isset($_REQUEST["wfo"])? $_REQUEST["wfo"]: "DMX";
 
 $sql = <<<EOF
 WITH stormbased as (
 	SELECT eventid, phenomena, issue at time zone 'UTC' as utc_issue, 
 	expire at time zone 'UTC' as utc_expire, 
 	polygon_begin at time zone 'UTC' as utc_polygon_begin,
 	polygon_end at time zone 'UTC' as utc_polygon_end,
 	status, windtag, hailtag, tornadotag, tml_sknt, tornadodamagetag, wfo
 	from sbw_$year WHERE wfo = $1 and phenomena = $2
 	and significance = 'W'	and status != 'EXP' and status != 'CAN'
 ),
 		
 countybased as (
 	select string_agg( u.name || ' ['||u.state||']', ', ') as locations, 
 	eventid from warnings_$year w JOIN ugcs u
    ON (u.gid = w.gid) WHERE w.wfo = $1 and
    significance = 'W' and phenomena = $2
    and eventid is not null GROUP by eventid 
 )
 		
 SELECT c.eventid, c.locations, s.utc_issue, s.utc_expire, 
 s.utc_polygon_begin, s.utc_polygon_end, s.status, s.windtag, s.hailtag,
 s.tornadotag, s.tml_sknt, s.tornadodamagetag, s.wfo, s.phenomena
 from countybased c JOIN stormbased s on (c.eventid = s.eventid)
 ORDER by eventid ASC, utc_polygon_begin ASC
 
EOF;
 $rs = pg_prepare($pgconn, "MYSELECT", $sql);
 
 $t->title = "List Tags used in NWS Warnings";

function do_col1($row){
	$ts = strtotime($row["utc_issue"]);
	$uri = sprintf("/vtec/#%s-O-%s-K%s-%s-%s-%04d", date("Y", $ts),
			'NEW', $row["wfo"], $row["phenomena"],
			'W', $row["eventid"]);
	
	if ($row["status"] == 'NEW'){
		return sprintf("<a href=\"%s\">%s</a>", $uri, $row["eventid"]);
	}
	return sprintf("<a href=\"%s\">%s</a>", $uri, 'SVS');
	
}
function do_col2($row){
	if ($row["status"] == 'NEW'){
		return date("d M Y Hi", strtotime($row["utc_issue"]));
	}
	return date("d M Y Hi", strtotime($row["utc_polygon_begin"]));
}
function do_col3($row){
	if ($row["status"] == 'NEW'){
		return date("Hi", strtotime($row["utc_expire"]));
	}
		return date("Hi", strtotime($row["utc_polygon_end"]));
}
function do_row($row){
	return sprintf("<tr><th>%s</th><td nowrap>%s</td><td>%s</td><td>%s</td>"
 			."<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>", do_col1($row), do_col2($row),
 			do_col3($row),
 			$row["locations"], $row["windtag"], $row["hailtag"],
 			$row["tornadotag"], $row["tornadodamagetag"], $row["tml_sknt"]);
}
 
 $svrtable = <<<EOF
 <table class="table table-condensed table-striped table-bordered">
 <thead><tr><th>Eventid</th><th>Start (UTC)</th><th>End</th>
 <th>Counties/Parishes</th>
 <th>Wind Tag</th><th>Hail Tag</th><th>Tornado Tag</th><th>Tornado Damage Tag</th>
 <th>Storm Speed (kts)</th></tr></thead>
 <tbody>
EOF;
 $tortable = $svrtable;

 $rs = pg_execute($pgconn, "MYSELECT", array($wfo, 'SV'));
 for($i=0;$row=@pg_fetch_assoc($rs,$i);$i++){
 	$svrtable .= do_row($row);
 }
$svrtable .= "</tbody></table>";

$rs = pg_execute($pgconn, "MYSELECT", array($wfo, 'TO'));
for($i=0;$row=@pg_fetch_assoc($rs,$i);$i++){
	$tortable .= do_row($row);
}
$tortable .= "</tbody></table>";


$yselect = yearSelect2(2002, $year, 'year');
$wselect = networkSelect("WFO", $wfo);
 
 $t->content = <<<EOF
 <ol class="breadcrumb">
 <li><a href="/nws/">NWS Resources</a></li>
 <li>List Warning Tags Issued</li>
 </ol>
 
 <p>This application lists out Severe Thunderstorm and Tornado Warnings
 issued by a National Weather Service office for a given year.  The listing
 includes metadata tags included in the initial warning or SVS update. 
 <strong>IMPORTANT: Not all offices include these tags in their warnings!</strong>
 For convience, this application lists out warnings back to 2002 eventhough
 these tags did not start until recent years. You should be able to copy/paste
 these tables into Microsoft Excel.</p>
 
 <form method="GET" name="one">
 <div class="row well">
 <div class="col-sm-6"> 
 <b>Select WFO:</b> {$wselect}
 </div>
 <div class="col-sm-4">
 <b>Select Year:</b> {$yselect}
 </div>
 <div class="col-sm-2">
 <input type="submit" value="Generate Table">
 </div>
 </div>
 </form>
 
 <h3>Tornado Warnings</h3>
 		
 		{$tortable}
 
 <h3>Severe Thunderstorm Warnings</h3>

 		{$svrtable}
 
 
EOF;
 $t->render('single.phtml');
 ?>
