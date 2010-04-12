<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/mlib.php");


$times = Array();
$tmpf = Array();
$dwpf = Array();
$wcht = Array();
$sknt = Array();
$pres = Array();
$vsby = Array();

$dbconn = iemdb('asos');
$sql = "SELECT extract(EPOCH from valid) as epoch, tmpf, dwpf, sknt, vsby
  , wind_chill(tmpf, sknt) as wcht, alti from t2010 WHERE station = 'AMW' 
  and dwpf > -99 and sknt >= 0 and valid > '2010-03-05' ORDER by valid ASC";
$rs = pg_query($dbconn, $sql);
for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $times[] = $row["epoch"];
  $tmpf[] = $row["tmpf"];
  $dwpf[] = $row["dwpf"];
  $wcht[] = $row["wcht"];
  $sknt[] = $row["sknt"] * 1.15;
  $vsby[] = $row["vsby"];
  $pres[] = $row["alti"] * 33.863;
}



include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");


// Create the graph. These two calls are always required
$graph = new Graph(600,450,"example1");
$graph->SetScale("datlin");
$graph->SetY2Scale("lin",0,10);
//$graph->SetYScale(0,'lin');
//$graph->SetYScale(1,'lin');
//$graph->SetYScale(2,'lin');
$graph->img->SetMargin(50,45,30,80);
$graph->SetMarginColor('white');
$graph->xaxis->SetLabelAngle(90);
//$graph->xaxis->SetLabelFormatString("M d", true);
$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");

$graph->yaxis->SetTitleMargin(35);
$graph->y2axis->SetTitleMargin(20);
$graph->y2axis->SetColor("blue");
$graph->y2axis->title->SetColor("blue");
$graph->y2axis->title->SetFont(FF_FONT2,FS_BOLD,16);
$graph->y2axis->SetTitle("Visibility [mile]");

$graph->xaxis->SetTitleMargin(70);

$graph->yaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
$graph->xaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
//$graph->xaxis->SetTitle("Valid Local Time");
//$graph->yaxis->SetTitle("Temp [F] or Wind [MPH]");
$graph->yaxis->SetTitle("Temperature [F]");
$graph->yaxis->SetColor("red");
$graph->yaxis->title->SetColor("red");
//$graph->subtitle->Set('34 mb pressure drop in 24 hours 1024 to 990 mb');
$graph->title->Set('Ames [KAMW] Time Series');

  $graph->tabtitle->SetFont(FF_FONT1,FS_BOLD,16);
  $graph->SetColor('wheat');

  $graph->legend->SetLayout(LEGEND_HOR);
  $graph->legend->SetPos(0.01,0.07, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();


// Create the linear plot
$lineplot=new LinePlot($vsby, $times);
//$lineplot->SetLegend("Visibility");
$lineplot->SetColor("blue");
$graph->AddY2($lineplot);


// Create the linear plot
$lineplot2=new LinePlot($pres,$times);
//$lineplot2->SetLegend("Pressure");
$lineplot2->SetColor("red");
//$graph->Add($lineplot2);

// Create the linear plot
$lineplot20=new LinePlot($tmpf,$times);
//$lineplot20->SetLegend("Dew Point");
$lineplot20->SetColor("red");
$graph->Add($lineplot20);


$lineplot3=new LinePlot($sknt,$times);
//$lineplot3->SetLegend("Wind Speed");
$lineplot3->SetColor("blue");
//$graph->AddY2($lineplot3);

//$graph->AddLine(new PlotLine(HORIZONTAL,32,"blue",2));


// Add the plot to the graph

// Display the graph
$graph->Stroke();
?>
