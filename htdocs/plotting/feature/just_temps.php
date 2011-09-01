<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/mlib.php");


$times = Array();
$wcht = Array();
$dwpf = Array();
$tmpf = Array();
$sknt = Array();

$dbconn = iemdb('iem');
$sql = "SELECT extract(EPOCH from valid) as epoch, 
  case when gust > sknt then gust else sknt end as wind, tmpf, dwpf, sknt, vsby
  , wind_chill(tmpf, sknt) as wcht, drct from current_log WHERE 
  station = 'AMW' 
  and dwpf > -99 and sknt >= 0 and valid > '2011-08-22 00:00' and 
  valid < '2011-08-29 20:00' ORDER by valid ASC";
$rs = pg_query($dbconn, $sql);
for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $times[] = $row["epoch"];
  if ($row["wcht"] > $row["tmpf"]){ $row["wcht"] = $row["tmpf"]; }
  $wcht[] = $row["wcht"];
  $dwpf[] = $row["dwpf"];
  $tmpf[] = $row["tmpf"];
  $sknt[] = $row["wind"] * 1.15;

  $relh[] = relh($row["tmpf"], $row["dwpf"]);
}



include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_scatter.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");
include ("$rootpath/include/jpgraph/jpgraph_bar.php");


// Create the graph. These two calls are always required
$graph = new Graph(640,500,"example1");
$graph->SetScale("datlin");
//$graph->SetY2Scale("lin");
$graph->img->SetMargin(45,5,60,90);
$graph->SetMarginColor('white');
$graph->xaxis->SetLabelAngle(90);
//$graph->xaxis->SetLabelFormatString("d M", true);
$graph->xaxis->scale->SetDateFormat("m/d h:i A");
$graph->xaxis->SetPos("min");

//$graph->y2axis->SetTitleMargin(20);
//$graph->y2axis->SetColor("blue");
//$graph->y2axis->title->SetColor("blue");
//$graph->y2axis->title->SetFont(FF_FONT2,FS_BOLD,16);
//$graph->yaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
//$graph->y2axis->SetTitle("Wind Speed [mph]");

//$graph->yaxis->SetTitleMargin(30);

$graph->xaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
//$graph->xaxis->SetTitle("Valid Local Time");
$graph->yaxis->SetTitle("Temperature [F]");
//$graph->yaxis->SetTitle("Wind Direction [N=0, E=90, S=180, W=270]");
//$graph->tabtitle->Set('Recent Comparison');
$graph->yaxis->scale->ticks->Set(90,15);
$graph->yaxis->scale->ticks->SetLabelFormat("%5.0f");
$graph->title->Set("23-24 Aug 2011 Ames, Iowa ASOS [KAMW]");

  $graph->title->SetFont(FF_ARIAL,FS_BOLD,10);
  $graph->SetColor('wheat');

  $graph->legend->SetLayout(LEGEND_HOR);
  $graph->legend->SetPos(0.01,0.08, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();



$lineplot=new LinePlot($tmpf, $times);
$lineplot->SetLegend("Temperature");
$lineplot->SetColor("red");
$lineplot->SetWeight(3);
$graph->Add($lineplot);

$lineplot2=new LinePlot($dwpf, $times);
$lineplot2->SetLegend("Dew Point");
$lineplot2->SetColor("darkgreen");
$lineplot2->SetWeight(3);
$graph->Add($lineplot2);

$lineplot3=new BarPlot($sknt, $times);
$lineplot3->SetLegend("Peak Wind");
$lineplot3->SetFillColor("blue");
$lineplot3->SetColor("blue");
$lineplot3->SetWeight(3);
//$graph->AddY2($lineplot3);


//$graph->AddLine(new PlotLine(HORIZONTAL,32,"blue",2));


// Add the plot to the graph

// Display the graph
$graph->Stroke();
?>
