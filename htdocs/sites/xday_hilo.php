<?php
 /* Make a nice simple plot of 7 day temperatures */
 include('../../config/settings.inc.php');
 include("$rootpath/include/database.inc.php");
 include("setup.php");
$days = isset($_GET["days"]) ? intval($_GET["days"]) : 21;
$st->load_station( $st->table[$station]["climate_site"]);
$cities = $st->table;

$climate_site = $cities[$station]["climate_site"];
$hasclimate = 1;
if ($climate_site == ""){ $hasclimate = 0;}
$db = iemdb("access");
$coopdb = iemdb("coop");

$rs = pg_prepare($coopdb, "SELECT", "SELECT valid, high, low from climate 
	   WHERE station = $1 and valid = $2");

$rs = pg_prepare($db, "SELECT", "SELECT day, max_tmpf, min_tmpf from summary 
       WHERE station = $1 and 
       day BETWEEN ('TODAY'::date - '$days days'::interval) and 'TODAY' 
       ORDER by day ASC");

$rs = pg_execute($db, "SELECT", Array($station));

$highs = Array();
$lows = Array();
$xlabels = Array();
$ahighs = Array();
$alows = Array();

for( $i=0; $row = @pg_fetch_array($rs,$i); $i++) {
  $ts = strtotime($row["day"]);
  $xlabels[] = date("m/d", $ts);
  $highs[] = $row["max_tmpf"];
  $lows[] = $row["min_tmpf"];

  if ($hasclimate){
    $sqlDate = "2000-". date("m-d", $ts );
    $rs2 = pg_execute($coopdb, "SELECT", 
                     Array(strtolower($climate_site), $sqlDate));
    $row2 = pg_fetch_array($rs2,0);
    $ahighs[] = $row2["high"];
    $alows[] = $row2["low"];
  }
}

pg_close($db);
pg_close($coopdb);


/* Time to plot */
include("$rootpath/include/jpgraph/jpgraph.php");
include("$rootpath/include/jpgraph/jpgraph_bar.php");
include("$rootpath/include/jpgraph/jpgraph_line.php");

$a0 = min($lows);
$a2 = max($highs);

$graph = new Graph(335,330);
$graph->SetScale("textlin");
$graph->SetMarginColor('white');

$graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCFF@0.5');
$graph->xgrid->Show();

$graph->title->Set("Past $days Days Hi/Lo Temps for ". $metadata["name"]);
$graph->SetMargin(40,5,20,65);

$graph->xaxis->SetTickLabels($xlabels);
$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetPos("min");

$graph->yscale->SetGrace(5);
$graph->yaxis->SetTitle("Temperature [F]");

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.01,0.99,"left","bottom");

$bplot1 = new BarPlot($highs);
$bplot1->SetFillColor('red');
$bplot1->SetLegend("High T");
//$bplot1->value->Show();
//$bplot1->value->SetFormat('%d');
//$bplot1->value->SetColor('white');
//$bplot1->value->SetAngle(90);
//$bplot1->value->SetFont(FF_FONT1,FS_BOLD);
//$bplot1->SetValuePos('bottom');
$bplot1->SetWidth(0.7);

$bplot2 = new BarPlot($lows);
$bplot2->SetFillColor('blue');
$bplot2->SetLegend("Low T");
//$bplot2->value->Show();
//$bplot2->value->SetFormat('%d');
//$bplot2->value->SetColor('white');
//$bplot2->value->SetAngle(90);
//$bplot2->value->SetFont(FF_FONT1,FS_BOLD);
//$bplot2->SetValuePos('bottom');
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
?>
