<?php
 include("../../config/settings.inc.php");
 define("IEM_APPID", 77);
 putenv("TZ=UTC");
 date_default_timezone_set('UTC');
 include("../../include/myview.php");
 include("../../include/vtec.php"); 
 include("../../include/forms.php");
 include("../../include/imagemaps.php");
  
 $t = new MyView();
 
 $year = isset($_REQUEST["year"])? intval($_REQUEST["year"]): date("Y");
 $wfo = isset($_REQUEST["wfo"])? $_REQUEST["wfo"]: "DMX";
 
 $jsonuri = sprintf("http://iem.local/json/ibw_tags.py?wfo=%s&year=%s",
 		$wfo, $year);
 $publicjsonuri = sprintf("http://mesonet.agron.iastate.edu/json/ibw_tags.py?wfo=%s&amp;year=%s",
 		$wfo, $year);
 
 $t->title = "NWS $wfo issued SVR+TOR Warning Tags for $year";
 $t->headextra = '
<link rel="stylesheet" type="text/css" href="https://extjs.cachefly.net/ext/gpl/3.4.1.1/resources/css/ext-all.css"/>
<script type="text/javascript" src="https://extjs.cachefly.net/ext/gpl/3.4.1.1/adapter/ext/ext-base.js"></script>
<script type="text/javascript" src="https://extjs.cachefly.net/ext/gpl/3.4.1.1/ext-all.js"></script>
<script type="text/javascript" src="/ext/ux/TableGrid.js"></script>
<script>
Ext.onReady(function(){
    var btn = Ext.get("create-grid1");
    btn.on("click", function(){
        btn.dom.disabled = true;
 
        // create the grid
        var grid = new Ext.ux.grid.TableGrid("svr", {
            stripeRows: true // stripe alternate rows
        });
        grid.render();
    }, false, {
        single: true
    }); // run once

 	var btn2 = Ext.get("create-grid2");
    btn2.on("click", function(){
        btn2.dom.disabled = true;
 
        // create the grid
        var grid = new Ext.ux.grid.TableGrid("tor", {
            stripeRows: true // stripe alternate rows
        });
        grid.render();
    }, false, {
        single: true
    }); // run once
 		
});
</script>
';
 

function do_col1($row){
	$ts = strtotime($row["issue"]);
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
		return date("Y/m/d Hi", strtotime($row["issue"]));
	}
	return date("Y/m/d Hi", strtotime($row["polygon_begin"]));
}
function do_col3($row){
	if ($row["status"] == 'NEW'){
		return date("Hi", strtotime($row["expire"]));
	}
		return date("Hi", strtotime($row["polygon_end"]));
}
function do_row($row){
	return sprintf("<tr><td>%s</td><td nowrap>%s</td><td>%s</td><td>%s</td>"
 			."<td>%02.0f</td><td>%4.2f</td><td>%s</td><td>%s</td><td>%02.0f</td></tr>", do_col1($row), do_col2($row),
 			do_col3($row),
 			$row["locations"], $row["windtag"], $row["hailtag"],
 			$row["tornadotag"], $row["tornadodamagetag"], $row["tml_sknt"]);
}
 
 $svrtable = <<<EOF
 <table id='svr' class="table table-condensed table-striped table-bordered">
 <thead><tr><th>Eventid</th><th>Start (UTC)</th><th>End</th>
 <th>Counties/Parishes</th>
 <th>Wind Tag</th><th>Hail Tag</th><th>Tornado Tag</th><th>Tornado Damage Tag</th>
 <th>Storm Speed (kts)</th></tr></thead>
 <tbody>
EOF;
 $tortable = str_replace('svr', 'tor', $svrtable);

 $data = file_get_contents($jsonuri);
 $json = json_decode($data);
 
 while(list($key, $val)=each($json['results'])){
 	if ($val["phenomena"] == 'SV'){
 		$svrtable .= do_row($val);
 	} else {
 		$tortable .= do_row($val);
 	}
 	
 }

$svrtable .= "</tbody></table>";
$tortable .= "</tbody></table>";


$yselect = yearSelect2(2002, $year, 'year');
$wselect = networkSelect("WFO", $wfo, array(), "wfo");
 
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
 these tables into Microsoft Excel prior to making the table sortable!</p>
 
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
 
 <div class="alert alert-success">There is a <a href="/json/">JSON-P webservice</a>
 that provides the data found in this table.  The direct URL is:<br />
 <code>{$publicjsonuri}</code></div>
 
 
 <h3>Tornado Warnings</h3>
 <button id="create-grid2" class="btn btn-info" type="button">Make Table Sortable</button>
 {$tortable}
 
 <h3>Severe Thunderstorm Warnings</h3>
<button id="create-grid1" class="btn btn-info" type="button">Make Table Sortable</button>
 		{$svrtable}
 
 
EOF;
 $t->render('single.phtml');
 ?>
