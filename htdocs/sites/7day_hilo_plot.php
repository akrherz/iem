<?php
 /* Make a nice simple plot of 7 day temperatures */
 require_once '../../config/settings.inc.php';
 require_once "../../include/database.inc.php";
 require_once "setup.php";
 require_once "../../include/jpgraph/jpgraph.php";
 require_once "../../include/jpgraph/jpgraph_bar.php";
 require_once "../../include/jpgraph/jpgraph_line.php";
 
$cnetwork = sprintf("%sCLIMATE", $st->table[$station]["state"]);
$st->load_station( $st->table[$station]["climate_site"], $cnetwork);
$cities = $st->table;

 $climate_site = $cities[$station]["climate_site"];
 $hasclimate = 1;
 if ($climate_site == ""){ $hasclimate = 0;}
 $db = iemdb("iem");

 /* Get high and low temps for the past 7 days */
$rs = pg_prepare($db, "SELECT",
		"SELECT day, max_tmpf, min_tmpf ".
		"from summary s, stations t ".
        "WHERE t.id = $1 and t.network = $2 and t.iemid = s.iemid and " .
       	"day > now() - '8 days'::interval and ".
        "day <= 'TODAY' ORDER by day DESC LIMIT 7");

$rs = pg_execute($db, "SELECT", Array($station, $network));

$highs = Array();
$lows = Array();
$xlabels = Array();

for( $i=0; $row = pg_fetch_array($rs); $i++) {
  $ts = strtotime($row["day"]);
  $xlabels[] = date("m/d", $ts);
  if ($row["max_tmpf"] < $row["min_tmpf"] || $row["max_tmpf"] < -100 || $row["min_tmpf"] < -100){
  	$highs[] = "";
  	$lows[] = "";
  } else {
  	$highs[] = $row["max_tmpf"];
  	$lows[] = $row["min_tmpf"];
  }
}
$xlabels = array_reverse($xlabels);
$highs = array_reverse($highs);
$lows = array_reverse($lows);

pg_close($db);

if ($hasclimate){
 $db = iemdb("coop");
 $sqlDate = sprintf("2000-%s", date("m-d") );
 $rs = pg_prepare(
    $db,
    "SELECT",
    "SELECT valid, high, low from ncdc_climate71 ". 
    "WHERE station = $1 and valid <= $2 ORDER by valid DESC LIMIT 7",
);

 $rs = pg_execute($db, "SELECT", Array($climate_site, $sqlDate));

 $ahighs = Array();
 $alows = Array();

 for( $i=0; $row = pg_fetch_array($rs); $i++) {
  $ahighs[] = $row["high"];
  $alows[] = $row["low"];
 }
 if (pg_num_rows($rs) < 1){
 	$hasclimate = false;
 } else {
 $ahighs = array_reverse($ahighs);
 $alows = array_reverse($alows);
 pg_close($db);
 $a1 = min($alows);
 $a3 = max($ahighs);
 }
}

if (!$hasclimate){
 $a1 = min($lows);
 $a3 = max($highs);
}

/* Time to plot */

$a0 = min($lows);
$a2 = max($highs);

$graph = new Graph(640,480);
$graph->SetScale("textlin", min($a0,$a1)-4, max($a2,$a3)+2);
$graph->SetMarginColor('white');

$graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCFF@0.5');
$graph->xgrid->Show();

$graph->title->Set("7 Day Hi/Lo Temps for ". $metadata["name"]);
$graph->SetMargin(40,5,50,45);

$graph->xaxis->SetTickLabels($xlabels);
$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetPos("min");

$graph->yscale->SetGrace(5);
$graph->yaxis->SetTitle("Temperature [F]");

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.01,0.07,"right","top");

$bplot1 = new BarPlot($highs);
$bplot1->SetFillColor('red');
$bplot1->SetLegend("High");
$bplot1->value->Show();
$bplot1->value->SetFormat('%.0f');
$bplot1->value->SetColor('white');
$bplot1->value->SetAngle(90);
$bplot1->value->SetFont(FF_FONT1,FS_BOLD);
$bplot1->SetValuePos('bottom');
$bplot1->SetWidth(0.7);

$bplot2 = new BarPlot($lows);
$bplot2->SetFillColor('blue');
$bplot2->SetLegend("Low");
$bplot2->value->Show();
$bplot2->value->SetFormat('%.0f');
$bplot2->value->SetColor('white');
$bplot2->value->SetAngle(90);
$bplot2->value->SetFont(FF_FONT1,FS_BOLD);
$bplot2->SetValuePos('bottom');
$bplot2->SetWidth(0.7);

$gbarplot = new GroupBarPlot(array($bplot1,$bplot2));
$gbarplot->SetWidth(0.6);

if ($hasclimate){
$l1plot=new LinePlot($alows);
$l1plot->SetColor("black");
$l1plot->mark->SetType(MARK_FILLEDCIRCLE);
$l1plot->mark->SetFillColor("lightblue");
$l1plot->mark->SetWidth(4);
$l1plot->SetWeight(2);
$l1plot->SetLegend("Avg Low");
$l1plot->SetBarCenter();

$l2plot=new LinePlot($ahighs);
$l2plot->SetColor("black");
$l2plot->mark->SetType(MARK_FILLEDCIRCLE);
$l2plot->mark->SetFillColor("lightred");
$l2plot->mark->SetWidth(4);
$l2plot->SetWeight(2);
$l2plot->SetLegend("Avg High");
$l2plot->SetBarCenter();
}

$graph->Add($gbarplot);
if ($hasclimate){
 $graph->Add($l2plot);
 $graph->Add($l1plot);
}
$graph->Stroke();
