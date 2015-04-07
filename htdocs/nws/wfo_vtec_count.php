<?php
 include("../../config/settings.inc.php");
 include("../../include/myview.php");
 $t = new MyView();
 define("IEM_APPID", 144);
 $phenomena = isset($_GET["phenomena"]) ? $_GET["phenomena"] : "TO";
 $significance = isset($_GET["significance"]) ? $_GET["significance"] : "W";
 $phenomena2 = isset($_GET["phenomena2"]) ? $_GET["phenomena2"] : "TO";
 $significance2 = isset($_GET["significance2"]) ? $_GET["significance2"] : "W";
 $enabled2 = isset($_REQUEST['enabled2']);
 $phenomena3 = isset($_GET["phenomena3"]) ? $_GET["phenomena3"] : "TO";
 $significance3 = isset($_GET["significance3"]) ? $_GET["significance3"] : "W";
 $enabled3 = isset($_REQUEST['enabled3']);
 $phenomena4 = isset($_GET["phenomena4"]) ? $_GET["phenomena4"] : "TO";
 $significance4 = isset($_GET["significance4"]) ? $_GET["significance4"] : "W";
 $enabled4 = isset($_REQUEST['enabled4']);
 
 $year1 = isset($_REQUEST["year1"])? intval($_REQUEST["year1"]): date("Y");
 $year2 = isset($_REQUEST["year2"])? intval($_REQUEST["year2"]): date("Y");
 $month1 = isset($_REQUEST["month1"])? intval($_REQUEST["month1"]): 1;
 $month2 = isset($_REQUEST["month2"])? intval($_REQUEST["month2"]): date("m");
 $day1 = isset($_REQUEST["day1"])? intval($_REQUEST["day1"]): 1;
 $day2 = isset($_REQUEST["day2"])? intval($_REQUEST["day2"]): date("d");
 $hour1 = isset($_REQUEST["hour1"])? intval($_REQUEST["hour1"]): 0;
 $hour2 = isset($_REQUEST["hour2"])? intval($_REQUEST["hour2"]): 0;
 
 $ts1 = gmmktime($hour1,0,0, $month1, $day1, $year1);
 $ts2 = gmmktime($hour2,0,0, $month2, $day2, $year2);
 
 $imgurl = sprintf("wfo_vtec_count_plot.py?phenomena=%s&significance=%s&",
 	$phenomena, $significance);
 if ($enabled2)
 	$imgurl .= sprintf("phenomena2=%s&significance2=%s&",
 		$phenomena2, $significance2);
 if ($enabled3)
 	$imgurl .= sprintf("phenomena3=%s&significance3=%s&",
 		$phenomena3, $significance3);
  if ($enabled4)
 	$imgurl .= sprintf("phenomena4=%s&significance4=%s&",
	 	$phenomena4, $significance4);

  $imgurl .= sprintf("sts=%s&ets=%s", gmdate("YmdH", $ts1), 
  		gmdate("YmdH", $ts2));
  
 $t->title = "NWS WWA Product Counts";

 include("../../include/vtec.php"); 
 include("../../include/forms.php");

 $p1 = make_select("phenomena", $phenomena, $vtec_phenomena);
 $s1 = make_select("significance", $significance, $vtec_significance);
 $p2 = make_select("phenomena2", $phenomena2, $vtec_phenomena);
 $s2 = make_select("significance2", $significance2, $vtec_significance);
 $p3 = make_select("phenomena3", $phenomena3, $vtec_phenomena);
 $s3 = make_select("significance3", $significance3, $vtec_significance);
 $p4 = make_select("phenomena4", $phenomena4, $vtec_phenomena);
 $s4 = make_select("significance4", $significance4, $vtec_significance);
 
 $e2 = sprintf("<input type='checkbox' name='enabled2'%s>Include</input>",
 		($enabled2) ? " checked='checked'": "");
 $e3 = sprintf("<input type='checkbox' name='enabled3'%s>Include</input>",
 		($enabled3) ? " checked='checked'": "");
 $e4 = sprintf("<input type='checkbox' name='enabled4'%s>Include</input>",
 		($enabled4) ? " checked='checked'": "");
 
 $y1 = yearSelect2(2005, $year1, 'year1');
 $m1 = monthSelect2($month1, 'month1');
 $d1 = daySelect2($day1, 'day1');
 $h1 = gmtHourSelect($hour1, 'hour1');
 $y2 = yearSelect2(2005, $year2, 'year2');
 $m2 = monthSelect2($month2, 'month2');
 $d2 = daySelect2($day2, 'day2');
 $h2 = gmtHourSelect($hour2, 'hour2');
 
 
 $t->content = <<<EOF
 <ol class="breadcrumb">
 <li><a href="/nws/">NWS Resources</a></li>
 <li>WWA Product Counts by WFO</li>
 </ol>
 <h3>WWA Product Counts by WFO</h3>
 
 <p>This application generates a map of the number of VTEC encoded Watch, Warning, 
 and Advisory (WWA) events by NWS Forecast Office for a time period of your choice.  
 The archive of products goes back to October 2005.  Note: Not all VTEC products go back to
 2005.  You can optionally plot up to 4 different VTEC phenomena and significance 
 types.
 
 <div class="alert alert-warning">Please be patient, this app may take 10-30 seconds to
 generate the image!</div>
 
<form method="GET" name="theform">

<table class="table table-striped table-bordered">
<thead>
<tr><th>Enabled:?</th><th>Phenomena</th><th>Significance</th></tr>
</thead>

<tr>
<td></td>
<td>{$p1}</td>
<td>{$s1}</td>
</tr>

<tr>
<td>{$e2}</td>
<td>{$p2}</td>
<td>{$s2}</td>
</tr>

<tr>
<td>{$e3}</td>
<td>{$p3}</td>
<td>{$s3}</td>
</tr>

<tr>
<td>{$e4}</td>
<td>{$p4}</td>
<td>{$s4}</td>
</tr>

<tr><th colspan='3'>Time Period (UTC Timestamps)</th></tr>
<tr><td colspan='3'><strong>Start Time:</strong>
  {$y1} {$m1} {$d1} {$h1}
  </td></tr>
<tr><td colspan='3'><strong>End Time:</strong>
  {$y2} {$m2} {$d2} {$h2}
</td></tr>
  </table>

<p><input type="submit" value="Generate Map" />
</form>

<p>Once generated, the map will appear below...
<p><img src="{$imgurl}" alt="The Map" class="img img-responsive"/>
EOF;
 $t->render('single.phtml');
 ?>
