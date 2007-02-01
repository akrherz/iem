<?php
 /* Make a nice simple plot of monthly  temperatures */
 include('../../config/settings.inc.php');
 include("$rootpath/include/database.inc.php");
 include("$rootpath/include/all_locs.php");
 include('setup.php');
 $climate_site = $cities[$station]["climate_site"];
 if ($climate_site == "none"){  die("App does not work outside of Iowa"); }
 $db = iemdb("access");

 /* Call with year and month, if not, then current! */
 $month = isset($_GET["month"]) ? intval($_GET["month"]): date("m");
 $year = isset($_GET["year"]) ? intval($_GET["year"]): date("Y");
$feature = isset($_GET["feature"]);

 /* Get high and low temps for the past 7 days */
$sql = "SELECT day, max_tmpf, min_tmpf from summary_$year WHERE 
        station = '$station' and extract(month from day) = $month
        and day < 'TODAY' ORDER by day ASC";

$rs = pg_query($db, $sql);

$highs = Array();
$lows = Array();
$xlabels = Array();

for( $i=0; $row = @pg_fetch_array($rs,$i); $i++) {
  $highs[] = $row["max_tmpf"];
  $lows[] = $row["min_tmpf"];
}

pg_close($db);

/* Now, lets get averages */
$db = iemdb("coop");

$sqlDate = sprintf("2000-%s", date("m-d") );

$sql = "SELECT valid, high, low from climate WHERE station = '$climate_site'
        and extract(month from valid) = $month  ORDER by valid ASC";

$rs = pg_query($db, $sql);

$ahighs = Array();
$alows = Array();

for( $i=0; $row = @pg_fetch_array($rs,$i); $i++) {
  $ts = strtotime($row["valid"]);
  $xlabels[] = date("m/d", $ts);
  $ahighs[] = $row["high"];
  $alows[] = $row["low"];
}

pg_close($db);

/* Time to plot */
include("$rootpath/include/jpgraph/jpgraph.php");
include("$rootpath/include/jpgraph/jpgraph_bar.php");
include("$rootpath/include/jpgraph/jpgraph_line.php");

$a0 = min($lows);
$a1 = min($alows);
$a2 = max($highs);
$a3 = max($ahighs);

$height = 360;
$width = 640;
if ($feature)
{
  $height = 200;
  $width = 320;
}
$graph = new Graph($width,$height);

$graph->SetScale("textlin", min($a0,$a1)-4, max($a2,$a3)+2);
$graph->SetMarginColor('white');

$graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCFF@0.5');
$graph->xgrid->Show();

$dstr = date("M", $ts);
$graph->title->Set("$dstr $year Hi/Lo Temps for ". $metadata["city"]);
$graph->SetMargin(40,5,50,40);

$graph->xaxis->SetTickLabels($xlabels);
$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetPos("min");

$graph->yscale->SetGrace(5);
$graph->yaxis->SetTitle("Temperature [F]");

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.01,0.09,"left","top");

$bplot1 = new BarPlot($highs);
$bplot1->SetFillColor('red');
$bplot1->SetLegend("High");
$bplot1->value->Show(! $feature);
$bplot1->value->SetFormat('%d');
$bplot1->value->SetColor('black');
$bplot1->value->SetAngle(0);
$bplot1->value->SetFont(FF_FONT1,FS_BOLD);
$bplot1->SetValuePos('top');
$bplot1->SetWidth(0.7);

$bplot2 = new BarPlot($lows);
$bplot2->SetFillColor('blue');
$bplot2->SetLegend("Low");
$bplot2->value->Show(! $feature);
$bplot2->value->SetFormat('%d');
$bplot2->value->SetColor('black');
$bplot2->value->SetAngle(0);
$bplot2->value->SetFont(FF_FONT1,FS_BOLD);
$bplot2->SetValuePos('top');
$bplot2->SetWidth(0.7);

$gbarplot = new GroupBarPlot(array($bplot1,$bplot2));
$gbarplot->SetWidth(0.6);

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

$graph->Add($gbarplot);
$graph->Add($l2plot);
$graph->Add($l1plot);

$graph->Stroke();
?>
