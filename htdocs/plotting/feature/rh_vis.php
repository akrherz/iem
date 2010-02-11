<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/mlib.php");


$times = Array();
$tmpf = Array();
$dwpf = Array();
$relh = Array();
$wcht = Array();
$sknt = Array();
$vsby = Array();

$dbconn = iemdb('asos');
$sql = "SELECT extract(EPOCH from valid) as epoch, tmpf, dwpf, sknt, vsby
  , wind_chill(tmpf, sknt) as wcht from t2010 WHERE station = 'AMW' 
  and dwpf > -99 and sknt >= 0 and valid > '2010-01-16' ORDER by valid ASC";
$rs = pg_query($dbconn, $sql);
for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $times[] = $row["epoch"];
  $tmpf[] = $row["tmpf"];
  $dwpf[] = $row["dwpf"];
  $relh[] = relh(f2c($row["tmpf"]), f2c($row["dwpf"]));
  $wcht[] = $row["wcht"];
  $sknt[] = $row["sknt"] * 1.15;
  $vsby[] = $row["vsby"];
}


$mtimes = Array();
$mtmpf = Array();
$mwsp = Array();
$dbconn = iemdb('mos');
$sql = "SELECT extract(epoch from ftime) as epoch, dpt, tmp, wsp from t2009 
        WHERE station = 'KDSM' and model = 'GFS' and 
        runtime = '2009-05-19 00:00+00' ORDER by ftime ASC";
$rs = pg_query($dbconn, $sql);
for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $mtimes[] = $row["epoch"];
  $mtmpf[] = $row["tmp"];
  $mwsp[] = $row["wsp"];
}

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_bar.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");


// Create the graph. These two calls are always required
$graph = new Graph(320,280,"example1");
$graph->SetScale("datlin",0,100);
$graph->SetY2Scale("lin",0,10);
$graph->img->SetMargin(40,40,50,70);
$graph->SetMarginColor('white');
$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("m/d hA", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");

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
$graph->yaxis->SetTitle("Relative Humidity [%]");
$graph->yaxis->SetColor("red");
$graph->yaxis->title->SetColor("red");
//$graph->tabtitle->Set('Recent Comparison');
$graph->title->Set('Ames [KAMW] Jan 2009 Time Series');

  $graph->tabtitle->SetFont(FF_FONT1,FS_BOLD,16);
  $graph->SetColor('wheat');

  $graph->legend->SetLayout(LEGEND_HOR);
  $graph->legend->SetPos(0.01,0.08, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();


// Create the linear plot
$lineplot=new LinePlot($vsby, $times);
$lineplot->SetLegend("Visibility");
$lineplot->SetFillGradient('blue','darkgreen');
$lineplot->SetStepStyle();
//$lineplot->SetColor("blue");
$graph->AddY2($lineplot);

// Create the linear plot
$lineplot2=new LinePlot($tmpf,$times);
$lineplot2->SetLegend("Temperature");
$lineplot2->SetColor("red");
$lineplot2->SetWeight(3);
//$graph->Add($lineplot2);

// Create the linear plot
$lineplot20=new LinePlot($dwpf,$times);
$lineplot20->SetLegend("Dew Point");
$lineplot20->SetColor("blue");
//$graph->Add($lineplot20);


$lineplot5=new LinePlot($relh,$times);
$lineplot5->SetLegend("Relative Humidity");
$lineplot5->SetColor("red");
$lineplot5->SetWeight(3);
//$lineplot5->SetStyle("dashed");
$graph->Add($lineplot5);

$lineplot3=new LinePlot($sknt,$times);
$lineplot3->SetLegend("Ob");
$lineplot3->SetColor("blue");
//$graph->AddY2($lineplot3);

// Create the linear plot
$lineplot4=new LinePlot($mwsp,$mtimes);
$lineplot4->SetLegend("GFS Frcst");
$lineplot4->SetColor("blue");
$lineplot4->SetStyle("dashed");
//$graph->AddY2($lineplot4);


//$graph->AddLine(new PlotLine(HORIZONTAL,32,"blue",2));


// Add the plot to the graph

// Display the graph
$graph->Stroke();
?>
