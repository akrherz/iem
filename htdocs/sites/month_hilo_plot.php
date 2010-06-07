<?php
 /* Make a nice simple plot of monthly  temperatures */
 include('../../config/settings.inc.php');
 include("$rootpath/include/database.inc.php");
 include('setup.php');
$st->load_station( $st->table[$station]["climate_site"]);
$cities = $st->table;

 $climate_site = $cities[$station]["climate_site"];
 $hasclimate = 1;
 if ($climate_site == ""){ $hasclimate = 0; }
 $db = iemdb("access");

 /* Call with year and month, if not, then current! */
 $month = isset($_GET["month"]) ? intval($_GET["month"]): date("m");
 $year = isset($_GET["year"]) ? intval($_GET["year"]): date("Y");
 $feature = isset($_GET["feature"]);
 $rts = mktime(0,0,0,$month,1,$year);

 /* Get high and low temps for the past 7 days */
$rs = pg_prepare($db, "SELECT", "SELECT day, max_tmpf, min_tmpf 
        from summary_$year WHERE 
        station = $1 and extract(month from day) = $2
        and day <= 'TODAY' ORDER by day ASC");
$rs = pg_execute($db, "SELECT", Array($station,$month));

$highs = Array();
$lows = Array();
$xlabels = Array();

$minVal = 100;
$maxVal = -100;

for( $i=0; $row = @pg_fetch_array($rs,$i); $i++) {
  if (intval($row["max_tmpf"]) < -50) {  $highs[] = Null; }
  else { 
    $highs[] = $row["max_tmpf"]; 
    if (intval($row["max_tmpf"]) > $maxVal) $maxVal = $row["max_tmpf"];
  }
  if (intval($row["min_tmpf"]) > 90) {  $lows[] = Null; }
  else { 
    $lows[] = $row["min_tmpf"]; 
    if (intval($row["min_tmpf"]) < $minVal) $minVal = $row["min_tmpf"];
  }
}

pg_close($db);

//$highs[] = 57;
//$highs[] = 55;
//$lows[] = 44;
//$lows[] = 41;

if ($hasclimate){
 /* Now, lets get averages */
 $db = iemdb("coop");

 $sqlDate = sprintf("2000-%s", date("m-d") );

 $rs = pg_prepare($db, "SELECT", "SELECT valid, high, low from climate 
        WHERE station = $1
        and extract(month from valid) = $2  ORDER by valid ASC");

 $rs = pg_execute($db, "SELECT", Array(strtolower($climate_site), $month));

 $ahighs = Array();
 $alows = Array();

 for( $i=0; $row = @pg_fetch_array($rs,$i); $i++) {
  $ts = strtotime($row["valid"]);
  $xlabels[] = date("m/d", $ts);
  $ahighs[] = $row["high"];
  $alows[] = $row["low"];
  if (intval($row["high"]) > $maxVal) $maxVal = $row["high"];
  if (intval($row["low"]) < $minVal) $minVal = $row["low"];
 }

 pg_close($db);
} else {
}

/* Time to plot */
include("$rootpath/include/jpgraph/jpgraph.php");
include("$rootpath/include/jpgraph/jpgraph_bar.php");
include("$rootpath/include/jpgraph/jpgraph_line.php");


$height = 360;
$width = 640;
if ($feature)
{
  $height = 200;
  $width = 320;
}
$graph = new Graph($width,$height);
$graph->SetScale("textlin", $minVal - 4, $maxVal + 4);
$graph->SetMarginColor('white');

$graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCFF@0.5');
$graph->xgrid->Show();

$graph->img->SetMargin(45,10,70,30);
$graph->title->Set( $cities[$station]["name"] ." [$station] Hi/Lo Temps for ". date("M Y", $rts) );
if ($hasclimate){
  $graph->subtitle->Set("Climate Site: ". $cities[strtoupper($climate_site)]["name"] ."[". $climate_site ."]");
}
$graph->legend->SetLayout(LEGEND_HOR);

//$graph->xaxis->SetTickLabels($xlabels);
//$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetPos("min");
$graph->xaxis->SetFont(FF_FONT1,FS_BOLD);
$graph->xaxis->SetTitle("Day of Month");

$graph->yscale->SetGrace(5);
$graph->yaxis->SetTitle("Temperature [F]");
$graph->yaxis->SetLabelFormat('%.0d');

$graph->legend->Pos(0.25, 0.11, "right", "top");

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
