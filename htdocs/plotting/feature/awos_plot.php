<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/mlib.php");


$times = Array();
$tmpf = Array();
$dwpf = Array();
$wcht = Array();
$sknt = Array();
$vsby = Array();
$alti = Array();

$dbconn = iemdb('awos');
$sql = "SELECT extract(EPOCH from valid) as epoch, tmpf, dwpf, sknt, alti
  from t2009_08 WHERE station = 'MXO' 
  and valid > '2009-08-03 03:00' and valid < '2009-08-03 09:00' 
  ORDER by valid ASC";
$rs = pg_query($dbconn, $sql);
for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $times[] = $row["epoch"];
  $tmpf[] = $row["tmpf"];
  $dwpf[] = $row["dwpf"];
  $alti[] = $row["alti"];
  $sknt[] = $row["sknt"] * 1.15;
}



include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");


// Create the graph. These two calls are always required
$graph = new Graph(640,480,"example1");
$graph->SetScale("datlin");
$graph->SetY2Scale("lin");
$graph->img->SetMargin(40,40,55,70);
$graph->SetMarginColor('white');
$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("h:i", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");

$graph->y2axis->SetTitleMargin(20);
$graph->y2axis->SetColor("blue");
$graph->y2axis->title->SetColor("blue");
$graph->y2axis->title->SetFont(FF_FONT2,FS_BOLD,16);
$graph->y2axis->SetTitle("Wind Speed [mph]");

$graph->xaxis->SetTitleMargin(30);

$graph->yaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
$graph->xaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
$graph->xaxis->SetTitle("Morning of 3 August 2009");
//$graph->yaxis->SetTitle("Temp [F] or Wind [MPH]");
$graph->yaxis->SetTitle("Temp [F]");
//$graph->yaxis->SetColor("red");
//$graph->yaxis->title->SetColor("red");
//$graph->tabtitle->Set('Recent Comparison');
$graph->title->Set('Monticello [KMXO] Time Series');

  $graph->tabtitle->SetFont(FF_FONT1,FS_BOLD,16);
  $graph->SetColor('wheat');

  $graph->legend->SetLayout(LEGEND_HOR);
  $graph->legend->SetPos(0.01,0.05, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();


// Create the linear plot
$lineplot2=new LinePlot($tmpf,$times);
$lineplot2->SetLegend("Temperature");
$lineplot2->SetColor("red");
$graph->Add($lineplot2);

// Create the linear plot
$lineplot20=new LinePlot($dwpf,$times);
$lineplot20->SetLegend("Dew Point");
$lineplot20->SetColor("green");
$graph->Add($lineplot20);


$lineplot3=new LinePlot($sknt,$times);
$lineplot3->SetLegend("Wind Speed");
$lineplot3->SetColor("blue");
$graph->AddY2($lineplot3);


//$graph->AddLine(new PlotLine(HORIZONTAL,32,"blue",2));


// Add the plot to the graph

// Display the graph
$graph->Stroke();
?>
