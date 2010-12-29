<?php
include("../../../config/settings.inc.php");

$year = isset($_GET["year"]) ? $_GET["year"] : date("Y");
$month = isset($_GET["month"]) ? $_GET["month"]: date("m");
$day = isset($_GET["day"]) ? $_GET["day"] : date("d");

$myTime = mktime(0,0,0,$month,$day,$year);

$titleDate = strftime("%b %d, %Y", $myTime);

$dirRef = strftime("%Y/%m/%d", $myTime);
$fcontents = file("/mesonet/ARCHIVE/data/$dirRef/text/ot/ot0003.dat");


$oldformat = 1;
if ($myTime >= mktime(0,0,0,8,12,2005))
{
  $oldformat = 0;
}

$v1 = array();
$times = array();

$start = intval( $myTime );
$i = 0;

$new_contents = array_slice($fcontents,2);
while (list ($line_num, $line) = each ($new_contents)) {
  $parts = split (",", $line);
  if (sizeof($parts) < 3) continue;
  $hhmm = str_pad($parts[3],4,"0",STR_PAD_LEFT);
  $hh = substr($hhmm,0,2);
  if ($hh == 24){$hh = 00;}
  $mm = substr($hhmm,2,3);
  $timestamp = mktime($hh,$mm,0,$month,$day,$year);

  if ($oldformat && $parts[11] > 1)
  {
    $v1[] = round($parts[11],2);
  }
  else if ($parts[8] > 1)
  {
    $v1[] = round($parts[8],2);
  }
  else
  {
    $v1[] = "";
  }
  $times[] = $timestamp;

} // End of while


include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");

// Create the graph. These two calls are always required
$graph = new Graph(600,300);
$graph->SetScale("datlin");
//$graph->xaxis->scale->SetDateFormat("h A");
$graph->xaxis->SetLabelFormatString("h A", true);
$graph->img->SetMargin(65,40,45,60);
//$graph->xaxis->SetFont(FONT1,FS_BOLD);
//$graph->xaxis->SetTickLabels($xlabel);
//$graph->xaxis->SetTextLabelInterval(60);
$graph->xaxis->SetTextTickInterval(6);
$graph->xaxis->SetLabelAngle(90);
//$graph->yaxis->scale->ticks->SetPrecision(2);
$graph->yaxis->scale->ticks->Set(0.01,0.005);
$graph->yscale->SetGrace(20);
$graph->title->Set("Logger Battery Voltage");
$graph->subtitle->Set($titleDate );

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.01,0.075);

//[DMF]$graph->y2axis->scale->ticks->Set(100,25);
//[DMF]$graph->y2axis->scale->ticks->SetPrecision(0);

$graph->title->SetFont(FF_FONT1,FS_BOLD,14);
$graph->yaxis->SetTitle("Voltage [Volts]");

$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Valid Local Time");
$graph->xaxis->SetTitleMargin(30);
//$graph->yaxis->SetTitleMargin(48);
$graph->yaxis->SetTitleMargin(40);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetPos("min");

// Create the linear plot
$lineplot=new LinePlot($v1, $times);
$lineplot->SetLegend("Voltage");
$lineplot->SetColor("blue");

//[DMF]$graph->Add($lineplot2);
$graph->Add($lineplot);
//[DMF]$graph->AddY2($lineplot3);

$graph->Stroke();

?>
