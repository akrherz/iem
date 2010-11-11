<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/mlib.php");


$times = Array();
$drct = Array();
$sknt = Array();
$tmpf = Array();

$dbconn = iemdb('asos');
$sql = "SELECT extract(EPOCH from valid) as epoch, tmpf, dwpf, sknt, vsby
  , wind_chill(tmpf, sknt) as wcht, drct from t2010 WHERE station = 'DSM' 
  and dwpf > -99 and drct >= 0 and valid > '2010-11-01' ORDER by valid ASC";
$rs = pg_query($dbconn, $sql);
for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $times[] = $row["epoch"];
  $drct[] = $row["drct"];
  $sknt[] = $row["sknt"] * 1.15;
  $tmpf[] = $row["tmpf"];
}


$mtimes = Array();
$mwdr = Array();
$mwsp = Array();
$dbconn = iemdb('mos');
$sql = "SELECT extract(epoch from ftime) as epoch, wdr, dpt, tmp, wsp from t2010 
        WHERE station = 'KAMW' and model = 'GFS' and 
        runtime = '2010-05-05 12:00+00' ORDER by ftime ASC";
$rs = pg_query($dbconn, $sql);
for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $mtimes[] = $row["epoch"];
  $mwdr[] = $row["wdr"];
  $mwsp[] = $row["wsp"] * 1.15;
}

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_scatter.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");


// Create the graph. These two calls are always required
$graph = new Graph(320,300,"example1");
$graph->SetScale("datlin",0,360);
$graph->SetY2Scale("lin");
$graph->img->SetMargin(45,40,55,84);
$graph->SetMarginColor('white');
$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("M d h A", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");

$graph->y2axis->SetTitleMargin(20);
$graph->y2axis->SetColor("blue");
$graph->y2axis->title->SetColor("blue");
$graph->y2axis->title->SetFont(FF_FONT2,FS_BOLD,16);
$graph->y2axis->SetTitle("Wind Speed [mph]");

$graph->yaxis->SetTitleMargin(30);

$graph->xaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
//$graph->xaxis->SetTitle("Valid Local Time");
//$graph->yaxis->SetTitle("Temp [F] or Wind [MPH]");
$graph->yaxis->SetTitle("Wind Direction [N=0, E=90, S=180, W=270]");
//$graph->tabtitle->Set('Recent Comparison');
$graph->yaxis->scale->ticks->Set(90,15);
$graph->yaxis->scale->ticks->SetLabelFormat("%5.0f");
$graph->title->Set('Des Moines [KDSM] Time Series');

  $graph->tabtitle->SetFont(FF_FONT1,FS_BOLD,16);
  $graph->SetColor('wheat');

  $graph->legend->SetLayout(LEGEND_HOR);
  $graph->legend->SetPos(0.01,0.08, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();


// Create the linear plot
$lineplot=new ScatterPlot($drct, $times);
$lineplot->SetLegend("Wind Dir");
$lineplot->SetColor("blue");
$graph->Add($lineplot);

// Create the linear plot
$lineplot4=new ScatterPlot($mwdr,$mtimes);
$lineplot4->SetLegend("GFS Forecast");
$lineplot4->mark->SetFillColor("green");
//$lineplot4->SetStyle("dashed");
//$graph->Add($lineplot4);

$lineplot2=new LinePlot($sknt, $times);
$lineplot2->SetLegend("Wind Speed");
$lineplot2->SetColor("blue");
$graph->AddY2($lineplot2);

$lineplot3=new LinePlot($mwsp, $mtimes);
$lineplot3->SetColor("green");
$lineplot3->SetLegend("GFS Forecast");
//$graph->AddY2($lineplot3);


//$graph->AddLine(new PlotLine(HORIZONTAL,32,"blue",2));


// Add the plot to the graph

// Display the graph
$graph->Stroke();
?>
