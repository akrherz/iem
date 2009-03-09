<?php
/* Generate a 1 minute plot of precip and pressure */
include_once("../../../config/settings.inc.php");
include_once("$rootpath/include/network.php");
include_once("$rootpath/include/mlib.php");
include_once("$rootpath/include/database.inc.php");
include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_scatter.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");
include ("$rootpath/include/jpgraph/jpgraph_led.php");

$nt = new NetworkTable( Array("KCCI","KIMT","KELO") );
$cities = $nt->table;

$station = isset($_GET["station"]) ? $_GET["station"]: "SKCI4";
$year = isset( $_GET["year"] ) ? $_GET["year"] : date("Y");
$month = isset( $_GET["month"] ) ? $_GET["month"] : date("m");
$day = isset( $_GET["day"] ) ? $_GET["day"] : date("d");
$myTime = mktime(0,0,0,$month,$day,$year);
$today = mktime(0,0,0,date("m"), date("d"), date("Y"));

if ($myTime == $today)
{
  /* Look in IEM Access! */
  $dbconn = iemdb("access");
  $tbl = "current_log";
  $pcol = ", pres as alti";
} else 
{
/* Dig in the archive for our data! */
  $dbconn = iemdb("snet");
  $tbl = sprintf("t%s", date("Y_m", $myTime) );
  $pcol = "";
}
$rs = pg_prepare($dbconn, "SELECT", "SELECT * $pcol from $tbl 
                 WHERE station = $1 and date(valid) = $2 ORDER by valid ASC");
$rs = pg_execute($dbconn, "SELECT", Array($station, date("Y-m-d", $myTime)));
if (pg_num_rows($rs) == 0) { 
 $led = new DigitalLED74();
 $led->StrokeNumber('NO DATA FOR THIS DATE',LEDC_GREEN);
 die();
}

$titleDate = strftime("%b %d, %Y", $myTime);
$cityname = $cities[$station]['name'];

/* BEGIN GOOD WORK HERE */
$times = Array();
$pcpn = Array();
$pres = Array();

for($i=0;$row = @pg_fetch_array($rs,$i); $i++)
{
  $ts = strtotime( substr($row["valid"],0,16) );
  $times[] = $ts;
  $pcpn[] = ($row["pday"] >= 0) ? $row["pday"] : "";
  $pres[] = ($row["alti"] > 20) ? $row["alti"] * 33.8639 : "";
}

$graph = new Graph(640, 480);
$graph->SetScale("datelin");
$graph->SetY2Scale("lin",0, intval((max($pcpn)+1)));

$graph->tabtitle->Set(' '. $cityname ." on ". $titleDate .' ');
$graph->xaxis->SetTitle("Valid Local Time");
$graph->y2axis->SetTitle("Accumulated Precipitation [inches]");
$graph->yaxis->SetTitle("Pressure [millibars]");

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



$graph->yaxis->SetTitleMargin(60);

$graph->y2axis->scale->ticks->Set(0.5,0.25);
$graph->y2axis->scale->ticks->SetLabelFormat("%4.2f");
$graph->y2axis->SetColor("blue");

$graph->yaxis->scale->ticks->SetLabelFormat("%4.1f");
$graph->yaxis->scale->ticks->Set(1,0.1);
$graph->yaxis->SetColor("black");
$graph->yscale->SetGrace(10);
//$graph->yscale->SetAutoTicks();

// Create the linear plot
$lineplot=new LinePlot($pres, $times);
$lineplot->SetLegend("Pressure");
$lineplot->SetColor("black");
//$lineplot->SetWeight(2);

// Create the linear plot
$lineplot2=new LinePlot($pcpn, $times);
$lineplot2->SetLegend("Precipitation");
$lineplot2->SetFillColor("blue@0.1");
$lineplot2->SetColor("blue");
$lineplot2->SetWeight(2);
//$lineplot2->SetFilled();
//$lineplot2->SetFillColor("blue");

// Box for error notations
//$t1 = new Text("Dups: ".$dups ." Missing: ".$missing );
//$t1->SetPos(0.4,0.95);
//$t1->SetOrientation("h");
//$t1->SetFont(FF_FONT1,FS_BOLD);
//$t1->SetBox("white","black",true);
//$t1->SetColor("black");
//$graph->AddText($t1);

$graph->AddY2($lineplot2);
$graph->Add($lineplot);

$graph->Stroke();

?>
