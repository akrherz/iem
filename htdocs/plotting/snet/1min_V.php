<?php
/* Generate a 1 minute plot of wind, and peak gust */
include_once("../../../config/settings.inc.php");
include_once("../../../include/network.php");
include_once("../../../include/mlib.php");
include_once("../../../include/database.inc.php");
include ("../../../include/jpgraph/jpgraph.php");
include ("../../../include/jpgraph/jpgraph_line.php");
include ("../../../include/jpgraph/jpgraph_scatter.php");
include ("../../../include/jpgraph/jpgraph_date.php");
include ("../../../include/jpgraph/jpgraph_led.php");

$nt = new NetworkTable( Array("KCCI","KIMT","KELO") );
$cities = $nt->table;

$station = isset($_GET["station"]) ? $_GET["station"]: "SKCI4";
$year = isset( $_GET["year"] ) ? $_GET["year"] : date("Y");
$month = isset( $_GET["month"] ) ? $_GET["month"] : date("m");
$day = isset( $_GET["day"] ) ? $_GET["day"] : date("d");
$myTime = mktime(0,0,0,$month,$day,$year);
$yesterday = mktime(0,0,0,date("m"), date("d"), date("Y")) - 96400;

if ($myTime >= $yesterday)
{
  /* Look in IEM Access! */
  $dbconn = iemdb("iem");
  $tbl = "current_log";
  $pcol = ", pres as alti";
  $rs = pg_prepare($dbconn, "SELECT", "SELECT * $pcol from $tbl c JOIN stations s ON (s.iemid = c.iemid)
                 WHERE id = $1 and date(valid) = $2 ORDER by valid ASC");
} else 
{
/* Dig in the archive for our data! */
  $dbconn = iemdb("snet");
  $tbl = sprintf("t%s", date("Y_m", $myTime) );
  $pcol = "";
  $rs = pg_prepare($dbconn, "SELECT", "SELECT * $pcol from $tbl 
                 WHERE station = $1 and date(valid) = $2 ORDER by valid ASC");
}

$rs = pg_execute($dbconn, "SELECT", Array($station, date("Y-m-d", $myTime)));
if (pg_num_rows($rs) == 0) { 
 $led = new DigitalLED74();
 $led->StrokeNumber('NO DATA FOR THIS DATE',LEDC_GREEN);
 die();
}

$titleDate = strftime("%b %d, %Y", $myTime);
$cityname = $cities[$station]['name'];
$wA = mktime(0,0,0, 8, 4, 2002);
$wLabel = "1min avg Wind Speed";
if ($wA > $myTime){
 $wLabel = "Instant Wind Speed";
}

/* BEGIN GOOD WORK HERE */
$times = Array();
$drct = Array();
$smph = Array();
$gust  = Array();

for($i=0;$row = @pg_fetch_array($rs,$i); $i++)
{
  $ts = strtotime( substr($row["valid"],0,16) );
  $times[] = $ts;
  $drct[] = ($row["drct"] > 0 && $row["drct"] <= 360 && $i % 10 == 0) ? $row["drct"] : -199;
  $smph[] = ($row["sknt"] >= 0) ? $row["sknt"] * 1.15 : "";
  $gust[] = ($row["gust"] >= 0) ? $row["gust"] * 1.15 : "";
}

// Create the graph. These two calls are always required
$graph = new Graph(640,480);

$graph->SetScale("datelin",0, 360);
$graph->SetY2Scale("lin");
$graph->y2axis->SetColor("red");
$graph->y2axis->SetTitle("Wind Speed [MPH]");
$graph->xaxis->SetTitle("Valid Local Time");
$graph->tabtitle->Set(' '. $cityname ." on ". $titleDate .' ');

  $tcolor = array(230,230,0);
  /* Common for all our plots */
  $graph->img->SetMargin(80,60,40,80);
  //$graph->img->SetAntiAliasing();
  $graph->xaxis->SetTextTickInterval(120);
  $graph->xaxis->SetPos("min");

  $graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,14);
  $graph->xaxis->SetFont(FF_FONT1,FS_BOLD,12);
  //$graph->xaxis->title->SetBox( array(150,150,150), $tcolor, true);
  //$graph->xaxis->title->SetColor( $tcolor );
  $graph->xaxis->SetTitleMargin(15);
  $graph->xaxis->SetLabelFormatString("h A", true);
  $graph->xaxis->SetLabelAngle(90);
  $graph->xaxis->SetTitleMargin(50);

  $graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,14);
  $graph->yaxis->SetFont(FF_FONT1,FS_BOLD,12);
  //$graph->yaxis->title->SetBox( array(150,150,150), $tcolor, true);
  //$graph->yaxis->title->SetColor( $tcolor );
  $graph->yaxis->SetTitleMargin(50);
  $graph->yscale->SetGrace(10);

  $graph->y2axis->title->SetFont(FF_FONT1,FS_BOLD,14);
  $graph->y2axis->SetFont(FF_FONT1,FS_BOLD,12);
  //$graph->y2axis->title->SetBox( array(150,150,150), $tcolor, true);
  //$graph->y2axis->title->SetColor( $tcolor );
  $graph->y2axis->SetTitleMargin(40);

  $graph->tabtitle->SetFont(FF_FONT1,FS_BOLD,16);
  $graph->SetColor('wheat');

  $graph->legend->SetLayout(LEGEND_HOR);
  $graph->legend->SetPos(0.01,0.94, 'left', 'top');
  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();

$graph->yaxis->scale->ticks->SetLabelFormat("%5.1f");
$graph->yaxis->scale->ticks->Set(90,15);
$graph->yaxis->scale->ticks->SetLabelFormat("%5.0f");
$graph->yaxis->scale->ticks->SetLabelFormat("%5.0f");
$graph->yaxis->SetColor("blue");
$graph->yaxis->SetTitle("Wind Direction [N=0, E=90, S=180, W=270]");

// Create the linear plot
$lineplot=new LinePlot($smph, $times);
$lineplot->SetLegend($wLabel);
$lineplot->SetColor("red");

$lp1=new LinePlot($gust, $times);
$lp1->SetLegend("Peak Wind Gust");
$lp1->SetColor("black");

// Create the linear plot
$sp1=new ScatterPlot($drct, $times);
$sp1->mark->SetType(MARK_FILLEDCIRCLE);
$sp1->mark->SetFillColor("blue");
$sp1->mark->SetWidth(3);
$sp1->SetLegend("Wind Direction");

$graph->Add($sp1);
$graph->AddY2($lineplot);
$graph->AddY2($lp1);

$graph->Stroke();

?>
