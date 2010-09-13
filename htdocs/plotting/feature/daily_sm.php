<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$pgconn = iemdb('wepp');

$times = Array();
$s01m = Array();

$rs = pg_query($pgconn, "SELECT valid, avg(vsm) from waterbalance_by_twp where valid >= '2010-06-01' GROUP by valid ORDER by valid ASC");
for($i=0;$row=@pg_fetch_array($rs,$i);$i++){
  $times[] = strtotime($row["valid"]);
  $s01m[] = $row["avg"];
}

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_bar.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");


// Create the graph. These two calls are always required
$graph = new Graph(320,300,"example1");
$graph->SetScale("datlin",0,40);

$graph->SetBackgroundGradient('white','green',GRAD_HOR,BGRAD_PLOT);
$graph->SetMarginColor('white');
//$graph->SetColor('white');
//$graph->SetBackgroundGradient('navy','white',GRAD_HOR,BGRAD_MARGIN);
$graph->SetFrame(true,'white');

$graph->ygrid->Show();
$graph->xgrid->Show();
$graph->ygrid->SetColor('gray@0.5');
$graph->xgrid->SetColor('gray@0.5');

$graph->img->SetMargin(40,40,25,80);

$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("M d", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");
//$graph->xaxis->SetTickLabels($years);
//$graph->xaxis->SetTextTickInterval(10);
//$graph->xaxis->SetTitleMargin(70);

$graph->yaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
//$graph->y2axis->title->SetFont(FF_FONT2,FS_BOLD,16);
$graph->xaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
//$graph->xaxis->SetTitle("Valid Local Time");
$graph->yaxis->SetTitle("# of Years [1893-2008]");
//$graph->y2axis->SetTitle("Temperature [F]");
//$graph->tabtitle->Set('Ames Daily High Temp & Average Low');

  $graph->tabtitle->SetFont(FF_FONT1,FS_BOLD,16);

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->SetPos(0.0,0.9, 'right', 'top');
//$graph->legend->SetLineSpacing(3);



// Create the linear plot
$lineplot=new BarPlot($s01m, $times);
$lineplot->SetLegend("# (High < Avg Low)");
$lineplot->SetFillColor("blue");
//$lineplot->SetWidth(1);
$graph->Add($lineplot);

/*
$lineplot2=new LinePlot($min_high, $times);
$lineplot2->SetLegend("Min High");
$lineplot2->SetColor("red");
$lineplot2->SetWeight(2);
$graph->AddY2($lineplot2);

$lineplot3=new LinePlot($highs, $times);
$lineplot3->SetLegend("Avg Low");
$lineplot3->SetColor("black");
$lineplot3->SetWeight(2);
$graph->AddY2($lineplot3);
*/


// Display the graph
$graph->Stroke();
?>
