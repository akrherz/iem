<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/mlib.php");


$t1 = Array(); $d1 = Array();
$t2 = Array(); $d2 = Array();
$t3 = Array(); $d3 = Array();

$dbconn = iemdb('access');
$sql = "SELECT extract(EPOCH from valid) as epoch, tmpf, dwpf, sknt, vsby
  , wind_chill(tmpf, sknt) as wcht, drct from current_log WHERE 
  station = 'TNU' and dwpf > -99 and valid > '2010-07-14' and 
  valid < '2010-07-15 00:00' ORDER by valid ASC";
$rs = pg_query($dbconn, $sql);
for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $t1[] = $row["epoch"];
  $d1[] = $row["dwpf"];
}

$sql = "SELECT extract(EPOCH from valid) as epoch, tmpf, dwpf, sknt, vsby
  , wind_chill(tmpf, sknt) as wcht, drct from current_log WHERE 
  station = 'DSM' and dwpf > -99 and valid > '2010-07-14' and 
  valid < '2010-07-15 00:00' ORDER by valid ASC";
$rs = pg_query($dbconn, $sql);
for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $t2[] = $row["epoch"];
  $d2[] = $row["dwpf"];
}

$sql = "SELECT extract(EPOCH from valid) as epoch, tmpf, dwpf, sknt, vsby
  , wind_chill(tmpf, sknt) as wcht, drct from current_log WHERE 
  station = 'PEA' and dwpf > -99 and valid > '2010-07-14' and 
  valid < '2010-07-15 00:00' ORDER by valid ASC";
$rs = pg_query($dbconn, $sql);
for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $t3[] = $row["epoch"];
  $d3[] = $row["dwpf"];
}

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_scatter.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");


// Create the graph. These two calls are always required
$graph = new Graph(640,480,"example1");
$graph->SetScale("datlin");
//$graph->SetY2Scale("lin");
$graph->img->SetMargin(45,45,30,50);
$graph->SetMarginColor('white');
$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("M d", true);
//$graph->xaxis->scale->SetDateFormat("h A");
$graph->xaxis->SetPos("min");

//$graph->y2axis->SetTitleMargin(20);
//$graph->y2axis->SetColor("blue");
//$graph->y2axis->title->SetColor("blue");
//$graph->y2axis->title->SetFont(FF_FONT2,FS_BOLD,16);
//$graph->y2axis->SetTitle("Dew Point [F]");

//$graph->yaxis->SetTitleMargin(30);

$graph->xaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
//$graph->xaxis->SetTitle("Valid Local Time");
$graph->yaxis->SetTitle("Temperature [F]");
//$graph->yaxis->SetTitle("Wind Direction [N=0, E=90, S=180, W=270]");
//$graph->tabtitle->Set('Recent Comparison');
$graph->yaxis->scale->ticks->Set(90,15);
$graph->yaxis->scale->ticks->SetLabelFormat("%5.0f");
$graph->title->Set("Ames ASOS [KAMW] \nMay 2010 Time Series");

  $graph->yaxis->title->SetFont(FF_ARIAL,FS_BOLD,12);
  $graph->SetColor('wheat');

  $graph->legend->SetLayout(LEGEND_HOR);
  $graph->legend->SetPos(0.12,0.13, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();



$lineplot=new LinePlot($d1, $t1);
$lineplot->SetLegend("Newton");
$lineplot->SetColor("red");
$lineplot->SetWeight(3);
$graph->Add($lineplot);

$lineplot2=new LinePlot($d2, $t2);
$lineplot2->SetLegend("DSM");
$lineplot2->SetColor("red");
$lineplot2->SetWeight(3);
$graph->Add($lineplot2);

$lineplot3=new LinePlot($d3, $t3);
$lineplot3->SetLegend("PEA");
$lineplot3->SetColor("green");
$lineplot3->SetWeight(3);
$graph->Add($lineplot3);


//$graph->AddLine(new PlotLine(HORIZONTAL,32,"blue",2));


// Add the plot to the graph

// Display the graph
$graph->Stroke();
?>
