<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$pgconn = iemdb('mos');

$times = Array();
$data = Array();
$ftimes = Array();
$fdata = Array();

$vint = "pwater";
$vdivid = 25.4;

$rs = pg_query($pgconn, "select ftime, $vint from model_gridpoint_2010 
  where station = 'KAMW' and 
    ftime = runtime and model = 'RUC' 
  ORDER by ftime ASC");
for($i=0;$row=@pg_fetch_array($rs,$i);$i++){
  $data[] = $row[$vint] / $vdivid;
  $times[] = strtotime($row["ftime"]);
  $ltime = $row["ftime"];
}

$rs = pg_query($pgconn, "select ftime, $vint from model_gridpoint_2010 
  where station = 'KAMW' and 
    runtime = '$ltime' and ftime != runtime and model = 'RUC' 
  ORDER by ftime ASC");
for($i=0;$row=@pg_fetch_array($rs,$i);$i++){
  $fdata[] = $row[$vint] / $vdivid;
  $ftimes[] = strtotime($row["ftime"]);
}


include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_bar.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");


// Create the graph. These two calls are always required
$graph = new Graph(640,500,"example1");
$graph->SetScale("datlin");
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

$graph->img->SetMargin(60,10,25,80);

$graph->xaxis->SetLabelAngle(90);
//$graph->xaxis->SetLabelFormatString("M d", true);
$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");
$graph->xaxis->HideTicks();
//$graph->xaxis->SetTickLabels($years);
//$graph->xaxis->SetTextTickInterval(10);

//$graph->y2axis->title->SetFont(FF_FONT2,FS_BOLD,16);
$graph->xaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
//$graph->xaxis->SetTitle("Valid Local Time");
$graph->yaxis->SetTitle("Precipitable Water [inch]");
$graph->yaxis->title->SetFont(FF_ARIAL,FS_BOLD,12);
$graph->yaxis->SetTitleMargin(30);
//$graph->y2axis->SetTitle("Temperature [F]");
$graph->tabtitle->Set('RUC Model Data for Ames');

  $graph->tabtitle->SetFont(FF_FONT1,FS_BOLD,16);

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->SetPos(0.2,0.1, 'right', 'top');
//$graph->legend->SetLineSpacing(3);



// Create the linear plot
$lineplot=new BarPlot($data, $times);
$lineplot->SetLegend("Analysis");
$lineplot->SetFillColor("green");
$lineplot->SetWidth(3);
$graph->Add($lineplot);

$lineplot2=new BarPlot($fdata, $ftimes);
$lineplot2->SetLegend("Forecast");
$lineplot2->SetFillColor("red");
$lineplot2->SetWidth(3);
$graph->Add($lineplot2);


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
