<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/mlib.php");


$times = Array();
$drct = Array();
$srad = Array();
$tmpf = Array();

$dbconn = iemdb('access');
$sql = "SELECT extract(EPOCH from valid) as epoch, tmpf, dwpf, sknt, vsby
  , wind_chill(tmpf, sknt) as wcht, drct, srad from current_log WHERE 
  station = 'SAKI4' ORDER by valid ASC";
$rs = pg_query($dbconn, $sql);
for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $times[] = $row["epoch"];
  $drct[] = $row["drct"];
  $srad[] = $row["srad"];
  $tmpf[] = $row["tmpf"];
}


include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_scatter.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");


// Create the graph. These two calls are always required
$graph = new Graph(330,300,"example1");
$graph->SetScale("datlin",0,360);
$graph->SetYScale(0,'int');
$graph->SetYScale(1,'int');
$graph->img->SetMargin(45,100,50,60);
$graph->SetMarginColor('white');
$graph->xaxis->SetLabelAngle(90);
//$graph->xaxis->SetLabelFormatString("M d", true);
$graph->xaxis->scale->SetDateFormat("d h A");
$graph->xaxis->SetPos("min");

//$graph->ynaxis[0]->SetTitleMargin(20);
$graph->ynaxis[0]->SetColor("red");
$graph->ynaxis[0]->title->SetColor("red");
$graph->ynaxis[0]->title->SetFont(FF_FONT2,FS_BOLD,16);
$graph->ynaxis[0]->SetTitle("Temperature [F]");

//$graph->ynaxis[0]->SetTitleMargin(20);
$graph->ynaxis[1]->SetColor("green");
$graph->ynaxis[1]->title->SetColor("green");
$graph->ynaxis[1]->title->SetFont(FF_FONT2,FS_BOLD,16);
$graph->ynaxis[1]->SetTitle("Solar Radiation [W m{-2}]");

$graph->yaxis->SetTitleMargin(30);

$graph->xaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
//$graph->xaxis->SetTitle("Valid Local Time");
//$graph->yaxis->SetTitle("Temp [F] or Wind [MPH]");
$graph->yaxis->SetTitle("Wind Direction [N=0, E=90, S=180, W=270]");
//$graph->tabtitle->Set('Recent Comparison');
$graph->yaxis->scale->ticks->Set(90,15);
$graph->yaxis->scale->ticks->SetLabelFormat("%5.0f");
$graph->title->Set('Ankeny SchoolNet [26-28 Feb 2010]');

  $graph->tabtitle->SetFont(FF_FONT1,FS_BOLD,16);
  $graph->SetColor('wheat');

  $graph->legend->SetLayout(LEGEND_HOR);
  $graph->legend->SetPos(0.,0.07, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();


// Create the linear plot
$lineplot=new ScatterPlot($drct, $times);
$lineplot->SetLegend("Wind Dir");
$lineplot->SetColor("blue");
$graph->Add($lineplot);

$lineplot2=new LinePlot($tmpf, $times);
$lineplot2->SetLegend("Temp [F]");
$lineplot2->SetColor("red");
$lineplot2->SetWeight(3);
$graph->AddY(0, $lineplot2);

$lineplot3=new LinePlot($srad, $times);
$lineplot3->SetLegend("Solar Rad [W m{-2}]");
$lineplot3->SetColor("green");
$lineplot3->SetWeight(3);
$graph->AddY(1, $lineplot3);


//$graph->AddLine(new PlotLine(HORIZONTAL,32,"blue",2));


// Add the plot to the graph

// Display the graph
$graph->Stroke();
?>
