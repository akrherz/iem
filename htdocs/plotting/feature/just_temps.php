<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/mlib.php");


$times = Array();
$tmpf = Array();
$wcht = Array();
$sknt = Array();
$vsby = Array();

$dbconn = iemdb('asos');
$sql = "SELECT extract(EPOCH from valid) as epoch, tmpf, dwpf, sknt, vsby
  , wind_chill(tmpf, sknt) as wcht from t2008 WHERE station = 'DSM' 
  and dwpf > -99 and sknt >= 0 ORDER by valid ASC";
$rs = pg_query($dbconn, $sql);
for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $times[] = $row["epoch"];
  $tmpf[] = $row["dwpf"];
  $wcht[] = $row["wcht"];
  $sknt[] = $row["sknt"] * 1.15;
  $vsby[] = $row["vsby"];
}


$mtimes = Array();
$mtmpf = Array();
$dbconn = iemdb('mos');
$sql = "SELECT extract(epoch from ftime) as epoch, dpt from t2009 
        WHERE station = 'KDSM' and model = 'GFS' and 
        runtime = '2009-03-19 7:00' ORDER by ftime ASC";
$rs = pg_query($dbconn, $sql);
for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $mtimes[] = $row["epoch"];
  $mtmpf[] = $row["dpt"];
}

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");


// Create the graph. These two calls are always required
$graph = new Graph(620,600,"example1");
$graph->SetScale("datlin");
//$graph->SetY2Scale("lin");
$graph->img->SetMargin(40,5,50,85);

$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("Md h A", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");

//$graph->y2axis->SetTitleMargin(20);
//$graph->y2axis->SetColor("blue");
//$graph->y2axis->title->SetColor("blue");
//$graph->y2axis->title->SetFont(FF_FONT2,FS_BOLD,16);
//$graph->y2axis->SetTitle("Visibility [mile]");

$graph->xaxis->SetTitleMargin(70);

$graph->yaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
$graph->xaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
//$graph->xaxis->SetTitle("Valid Local Time");
//$graph->yaxis->SetTitle("Temp [F] or Wind [MPH]");
$graph->yaxis->SetTitle("Temp [F]");
//$graph->tabtitle->Set('Recent Comparison');
$graph->title->Set('Waterloo [KALO] Time Series');

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
$lineplot->SetLegend("Visibility");
$lineplot->SetColor("blue");
//$graph->AddY2($lineplot);

// Create the linear plot
$lineplot2=new LinePlot($tmpf,$times);
$lineplot2->SetLegend("Air Temp");
$lineplot2->SetColor("red");
$graph->Add($lineplot2);

$lineplot5=new LinePlot($mtmpf,$mtimes);
$lineplot5->SetLegend("GFS Model Forecast");
$lineplot5->SetColor("black");
$graph->Add($lineplot5);

// Create the linear plot
$lineplot4=new LinePlot($wcht,$times);
$lineplot4->SetLegend("Wind Chill");
$lineplot4->SetColor("blue");
//$graph->Add($lineplot4);

$lineplot3=new LinePlot($sknt,$times);
$lineplot3->SetLegend("Wind Speed");
$lineplot3->SetColor("black");
//$graph->Add($lineplot3);

$graph->AddLine(new PlotLine(HORIZONTAL,32,"blue",2));


// Add the plot to the graph

// Display the graph
$graph->Stroke();
?>
