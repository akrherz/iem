<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/mlib.php");


$otimes = Array();
$odata = Array();
$ftimes = Array();
$fdata = Array();

/* Extract Obs */
$dbconn = iemdb('asos');
$sql = "SELECT extract(EPOCH from valid) as epoch, tmpf, dwpf, sknt, vsby
  , wind_chill(tmpf, sknt) as wcht, alti from t2010 WHERE station = 'AMW' 
  and dwpf > -99 and sknt >= 0 and valid > '2010-11-05' ORDER by valid ASC";
$rs = pg_query($dbconn, $sql);
for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $otimes[] = $row["epoch"];
  $odata[] = $row["tmpf"];
}

$dbconn = iemdb('mos');
$sql = "SELECT extract(epoch from ftime) as epoch, dpt, tmp, wsp from t2010
        WHERE station = 'KAMW' and model = 'GFS' and 
        runtime = '2010-11-10 00:00+00' ORDER by ftime ASC";
$rs = pg_query($dbconn, $sql);
for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $ftimes[] = $row["epoch"];
  $fdata[] = $row["tmp"];
}

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_plotline.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");


// Create the graph. These two calls are always required
$graph = new Graph(320,300,"example1");
$graph->SetScale("datlin");
//$graph->SetY2Scale("lin",0,50);
$graph->img->SetMargin(40,10,50,80);
$graph->SetMarginColor('white');
$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("M d h A", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");

//$graph->y2axis->SetTitleMargin(20);
//$graph->y2axis->SetColor("blue");
//$graph->y2axis->title->SetColor("blue");
//$graph->y2axis->title->SetFont(FF_FONT2,FS_BOLD,16);
//$graph->y2axis->SetTitle("Wind Speed [kt]");

$graph->xaxis->SetTitleMargin(70);

$graph->yaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
$graph->xaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
//$graph->xaxis->SetTitle("Valid Local Time");
//$graph->yaxis->SetTitle("Temp [F] or Wind [MPH]");
$graph->yaxis->SetTitle("Air Temperature [F]");
//$graph->yaxis->SetColor("red");
//$graph->yaxis->title->SetColor("red");
//$graph->tabtitle->Set('Recent Comparison');
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
$lineplot=new LinePlot($odata, $otimes);
$lineplot->SetLegend("Temperature");
$lineplot->SetColor("red");
$graph->Add($lineplot);

// Create the linear plot
$lineplot4=new LinePlot($fdata,$ftimes);
$lineplot4->SetLegend("GFS Frcst");
$lineplot4->SetColor("red");
$lineplot4->SetStyle("dashed");
$graph->Add($lineplot4);


//$graph->AddLine(new PlotLine(HORIZONTAL,60,"blue",2));


// Add the plot to the graph

// Display the graph
$graph->Stroke();
?>
