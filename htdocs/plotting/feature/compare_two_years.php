<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/mlib.php");


$times = Array();
$times2 = Array();
$pmsl = Array();
$pmsl2 = Array();

$dbconn = iemdb('asos');
$sql = "SELECT dwpf, extract(EPOCH from valid) as epoch, alti, tmpf, p01m / 24.5 as phour
  from t2009 WHERE station = 'DSM' and valid > '2009-05-15' and 
  valid < '2009-06-15' and dwpf > 0 ORDER by valid ASC";
$rs = pg_query($dbconn, $sql);

for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $times[] = $row["epoch"];
  $pmsl[] = $row["dwpf"];
  //$feel[] = wcht_idx($row['tmpf'], $row["sknt"] * 1.15);
}

$sql = "SELECT dwpf, extract(EPOCH from (valid + '1 year'::interval)) as epoch, alti, tmpf, p01m / 24.5 as phour
  from t2008 WHERE alti > 25 and station = 'DSM' and valid > '2008-05-15' 
  and valid < '2008-06-15' and dwpf > 0 ORDER by valid ASC";
$rs = pg_query($dbconn, $sql);

for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $times2[] = $row["epoch"];
  $pmsl2[] = $row["dwpf"];
  //$feel[] = wcht_idx($row['tmpf'], $row["sknt"] * 1.15);
}

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_bar.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");


// Create the graph. These two calls are always required
$graph = new Graph(320,300,"example1");
$graph->SetScale("datlin");
//$graph->SetY2Scale("lin");
$graph->img->SetMargin(50,5,5,70);

$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("M d", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");

$graph->yaxis->SetTitleMargin(35);
$graph->xaxis->SetTitleMargin(40);


$graph->xaxis->SetTitle("Valid Local Time");
//$graph->yaxis->SetTitle("Des Moines Altimeter [inch Hg]");
$graph->yaxis->SetTitle("Des Moines Dew Point [F]");
//$graph->y2axis->SetTitle("Des Moines Precip [inch]");
//$graph->tabtitle->Set('Recent Comparison');

  $graph->tabtitle->SetFont(FF_FONT1,FS_BOLD,16);
  $graph->SetColor('wheat');

  $graph->legend->SetLayout(LEGEND_HOR);
  $graph->legend->SetPos(0.15,0.01, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();


// Create the linear plot
$lineplot=new LinePlot($pmsl, $times);
$lineplot->SetLegend("2008");
$lineplot->SetColor("red");

$lineplot2=new LinePlot($pmsl2, $times2);
$lineplot2->SetLegend("2007");
$lineplot2->SetColor("blue");

// Create the linear plot
//$lineplot2=new BarPlot($phour,$times);
//$lineplot2->SetLegend("Precipitation");
//$lineplot2->SetColor("blue");

// Add the plot to the graph
$graph->Add($lineplot);
$graph->Add($lineplot2);
//$graph->AddY2($lineplot2);

// Display the graph
$graph->Stroke();
?>
