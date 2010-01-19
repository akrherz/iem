<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$pgconn = iemdb('mos');

$times = Array();
$pop = Array();

$rs = pg_query($pgconn, "select ftime, p12 from t2009 WHERE station = 'KAMW' and ftime - runtime = '36 hours'::interval and runtime > '2009-09-01' and model = 'GFS' and p12 is not null ORDER by runtime ASC");
for($i=0;$row=@pg_fetch_array($rs,$i);$i++){
  $pop[] = $row["p12"];
  $times[] = strtotime($row["ftime"]);
}


include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_bar.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");


// Create the graph. These two calls are always required
$graph = new Graph(320,300,"example1");
$graph->SetScale("datlin",0,100);
//$graph->SetY2Scale("lin",-55,75);

$graph->SetBackgroundGradient('yellow','lightyellow',GRAD_HOR,BGRAD_PLOT);
$graph->SetMarginColor('white');
//$graph->SetColor('white');
//$graph->SetBackgroundGradient('navy','white',GRAD_HOR,BGRAD_MARGIN);
$graph->SetFrame(true,'white');

$graph->ygrid->Show();
$graph->xgrid->Show();
$graph->ygrid->SetColor('gray@0.5');
$graph->xgrid->SetColor('gray@0.5');

$graph->img->SetMargin(40,40,25,50);

$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("M d", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");
$graph->xaxis->HideTicks();
//$graph->xaxis->SetTickLabels($years);
//$graph->xaxis->SetTextTickInterval(10);

//$graph->y2axis->title->SetFont(FF_FONT2,FS_BOLD,16);
$graph->xaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
//$graph->xaxis->SetTitle("Valid Local Time");
$graph->yaxis->SetTitle("Probability of Precip [%]");
$graph->yaxis->title->SetFont(FF_ARIAL,FS_BOLD,12);
$graph->yaxis->SetTitleMargin(30);
//$graph->y2axis->SetTitle("Temperature [F]");
$graph->tabtitle->Set('GFS MOS Forecast for Ames');

  $graph->tabtitle->SetFont(FF_FONT1,FS_BOLD,16);

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->SetPos(0.0,0.9, 'right', 'top');
//$graph->legend->SetLineSpacing(3);



// Create the linear plot
$lineplot=new BarPlot($pop, $times);
//$lineplot->SetLegend("# (High < Avg Low)");
$lineplot->SetFillColor("green");
$lineplot->SetWidth(3);
$graph->Add($lineplot);

//$lineplot2=new LinePlot($min_high, $times);
//$lineplot2->SetLegend("Min High");
//$lineplot2->SetColor("red");
//$lineplot2->SetWeight(2);
//$graph->AddY2($lineplot2);

//$lineplot3=new LinePlot($highs, $times);
//$lineplot3->SetLegend("Avg Low");
//$lineplot3->SetColor("black");
//$lineplot3->SetWeight(2);
//$graph->AddY2($lineplot3);

// Display the graph
$graph->Stroke();
?>
