<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/mlib.php");


$times = Array();
$drct = Array();
$dwpf = Array();
$tmpf = Array();

$dbconn = iemdb('access');
$sql = "SELECT extract(EPOCH from valid) as epoch, tmpf, dwpf, sknt, vsby
  , wind_chill(tmpf, sknt) as wcht, drct from current_log WHERE 
  station = 'TNU' 
  and dwpf > -99 and valid > '2010-07-14' and 
  valid < '2010-07-15 00:00' ORDER by valid ASC";
$rs = pg_query($dbconn, $sql);
for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $times[] = $row["epoch"];
  $drct[] = $row["drct"];
  $dwpf[] = $row["dwpf"];
  $tmpf[] = $row["tmpf"];
  $relh[] = relh($row["tmpf"], $row["dwpf"]);
}



include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_scatter.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");


// Create the graph. These two calls are always required
$graph = new Graph(640,480,"example1");
$graph->SetScale("datlin");
$graph->SetY2Scale("lin");
$graph->img->SetMargin(45,45,30,50);
$graph->SetMarginColor('white');
$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("M d", true);
//$graph->xaxis->scale->SetDateFormat("h A");
$graph->xaxis->SetPos("min");

$graph->y2axis->SetTitleMargin(20);
$graph->y2axis->SetColor("blue");
$graph->y2axis->title->SetColor("blue");
$graph->y2axis->title->SetFont(FF_FONT2,FS_BOLD,16);
$graph->y2axis->SetTitle("Dew Point [F]");

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



$lineplot=new LinePlot($relh, $times);
$lineplot->SetLegend("Relative Humidity");
$lineplot->SetColor("red");
$lineplot->SetWeight(3);
$graph->AddY2($lineplot);

$lineplot2=new LinePlot($tmpf, $times);
$lineplot2->SetLegend("Air Temp");
$lineplot2->SetColor("red");
$lineplot2->SetWeight(3);
$graph->Add($lineplot2);

$lineplot3=new LinePlot($dwpf, $times);
$lineplot3->SetLegend("Dew Point");
$lineplot3->SetColor("green");
$lineplot3->SetWeight(3);
$graph->Add($lineplot3);


//$graph->AddLine(new PlotLine(HORIZONTAL,32,"blue",2));


// Add the plot to the graph

// Display the graph
$graph->Stroke();
?>
