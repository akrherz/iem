<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/mlib.php");


$times = Array();
$sknt = Array();
$tmpf = Array();
$pres = Array();

$dbconn = iemdb('access');
$sql = "SELECT extract(EPOCH from valid) as epoch, tmpf, dwpf, sknt, pres, vsby
  from current_log WHERE station = 'SBOI4' and valid BETWEEN '2009-07-14 2:00' and '2009-07-14 6:00' ORDER by valid ASC";
$rs = pg_query($dbconn, $sql);

for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $times[] = $row["epoch"];
  $tmpf[] = $row["tmpf"];
  $sknt[] = $row["sknt"] * 1.15;
  $pres[] = $row["pres"]  * 33.8639;
}

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");


// Create the graph. These two calls are always required
$graph = new Graph(320,280,"example1");
$graph->SetScale("datlin");
$graph->SetY2Scale("lin");
$graph->img->SetMargin(40,50,40,70);

$graph->xaxis->SetLabelAngle(90);
$graph->y2axis->SetLabelFormat('%.0f');
$graph->xaxis->SetLabelFormatString("h:i A", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");

$graph->y2axis->SetTitleMargin(30);
$graph->y2axis->SetColor("blue");
$graph->y2axis->title->SetColor("blue");
$graph->xaxis->SetTitleMargin(40);

$graph->yaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
$graph->y2axis->title->SetFont(FF_FONT2,FS_BOLD,16);
$graph->xaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
$graph->xaxis->SetTitle("2009 July 14");
$graph->yaxis->SetTitle("Minute Averaged Wind [MPH]");
$graph->y2axis->SetTitle("Pressure [mb]");
//$graph->tabtitle->Set('Recent Comparison');
$graph->title->Set('Boone SchoolNet Time Series');

  $graph->tabtitle->SetFont(FF_FONT1,FS_BOLD,16);
  $graph->SetColor('wheat');

  $graph->legend->SetLayout(LEGEND_HOR);
  $graph->legend->SetPos(0.2,0.07, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();


// Create the linear plot
$lineplot=new LinePlot($pres, $times);
$lineplot->SetLegend("Pressure");
$lineplot->SetColor("blue");
$graph->AddY2($lineplot);

$lineplot3=new LinePlot($sknt,$times);
$lineplot3->SetLegend("Wind Speed");
$lineplot3->SetColor("black");
$graph->Add($lineplot3);

// Add the plot to the graph

// Display the graph
$graph->Stroke();
?>
