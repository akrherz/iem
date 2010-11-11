<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$dbconn = iemdb("access");

$times = Array("DSM" => Array(), "LWD" => Array(), "AMW" => Array());
$precip = Array("DSM" => Array(), "LWD" => Array(), "AMW" => Array());
$total = Array("DSM" => 0, "LWD" => 0, "AMW" => 0);

$rs = pg_query($dbconn, "SELECT phour, station, valid from hourly_2010 WHERE
network = 'IA_ASOS' and station in ('AMW','DSM','LWD') and
valid >= '2010-06-01' ORDER by valid ASC");
for($i=0;$row=@pg_fetch_array($rs,$i);$i++){
  $total[ $row["station"] ] += $row["phour"];
  $times[ $row["station"] ][] = strtotime($row["valid"]);
  $precip[ $row["station"] ][] = $total[ $row["station"] ];
}

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");

$graph = new Graph(320,280,"example1");
$graph->SetScale("datlin",0,16);
//$graph->SetY2Scale("lin");
$graph->SetFrame(false);
$graph->SetBox(true);
$graph->img->SetMargin(40,25,20,30);

$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("d", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");
//$graph->xaxis->SetTickLabels($hours);
//$graph->xaxis->SetTextTickInterval(6);
//$graph->xaxis->HideTicks();
//$graph->xaxis->SetTitleMargin(15);
//$graph->yaxis->SetTitleMargin(18);

//$graph->yaxis->SetColor('blue');
//$graph->yaxis->title->SetColor('blue');

$graph->xaxis->title->SetFont(FF_ARIAL,FS_NORMAL,10);
$graph->yaxis->title->SetFont(FF_ARIAL,FS_NORMAL,10);
$graph->xaxis->SetTitle("Date in June");
$graph->yaxis->SetTitle("Accumulated Precipitation [inch]");
//$graph->tabtitle->Set('Ames (1893-2009)');
$graph->title->Set("Three cities' quest for 12+ inches\n of rain in June 2010");
//$graph->subtitle->Set("number of severe t'storm and tornado \ncounty based warnings");

  $graph->title->SetFont(FF_ARIAL,FS_NORMAL,12);
  $graph->subtitle->SetFont(FF_ARIAL,FS_NORMAL,10);
  $graph->SetColor('wheat');

//  $graph->legend->SetLayout(LEGEND_HOR);
  $graph->legend->SetPos(0.0,0.65, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();

$lineplot=new LinePlot($precip["AMW"], $times["AMW"]);
$lineplot->SetLegend("Ames [Rock Star Late]");
$lineplot->SetColor("red");
$lineplot->SetWeight(3);
$graph->Add($lineplot);

$lineplot2=new LinePlot($precip["DSM"], $times["DSM"]);
$lineplot2->SetLegend("Des Moines [Tortoise]");
$lineplot2->SetColor("blue");
$lineplot2->SetWeight(3);
$graph->Add($lineplot2);

$lineplot3=new LinePlot($precip["LWD"], $times["LWD"]);
$lineplot3->SetLegend("Lamoni [Hare]");
$lineplot3->SetColor("green");
$lineplot3->SetWeight(3);
$graph->Add($lineplot3);


$graph->Stroke();
?>
