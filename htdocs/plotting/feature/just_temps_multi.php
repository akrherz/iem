<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/mlib.php");

$st2 = "DBQ";
$st3 = "LWD";
$times = Array(
  "AMW" => Array(),
  "$st2" => Array(),
  "$st3" => Array(),
);
$tmpf = Array(
  "AMW" => Array(),
  "$st2" => Array(),
  "$st3" => Array(),
);

$dbconn = iemdb('asos');
$sql = "SELECT extract(EPOCH from valid) as epoch, tmpf, dwpf, sknt, vsby
  , wind_chill(tmpf, sknt) as wcht, drct, station from t2010 WHERE 
  station in ('AMW','$st2','$st3') 
  and dwpf > -99 and drct >= 0 and valid > '2010-02-08' and 
  valid < '2010-02-11 14:00' ORDER by valid ASC";
$rs = pg_query($dbconn, $sql);
for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $times[$row["station"]][] = $row["epoch"];
  $tmpf[$row["station"]][] = $row["tmpf"];
}

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");


// Create the graph. These two calls are always required
$graph = new Graph(310,280,"example1");
$graph->SetScale("datlin");
$graph->img->SetMargin(45,5,30,80);
$graph->SetMarginColor('white');
$graph->xaxis->SetLabelAngle(90);
//$graph->xaxis->SetLabelFormatString("M d", true);
$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");

$graph->yaxis->SetTitleMargin(30);

$graph->xaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
//$graph->xaxis->SetTitle("Valid Local Time");
$graph->yaxis->SetTitle("Air Temperature [F]");
//$graph->yaxis->SetTitle("Wind Direction [N=0, E=90, S=180, W=270]");
//$graph->tabtitle->Set('Recent Comparison');
$graph->yaxis->scale->ticks->Set(90,15);
$graph->yaxis->scale->ticks->SetLabelFormat("%5.0f");
$graph->title->Set('Ames [KAMW] Time Series');

  $graph->tabtitle->SetFont(FF_FONT1,FS_BOLD,16);
  $graph->SetColor('wheat');

  $graph->legend->SetLayout(LEGEND_HOR);
  $graph->legend->SetPos(0.01,0.04, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();


// Create the linear plot
$lineplot=new LinePlot($tmpf["AMW"], $times["AMW"]);
//$lineplot->SetLegend("AMW");
$lineplot->SetColor("blue");
$graph->Add($lineplot);

// Create the linear plot
$lineplot2=new LinePlot($tmpf[$st2], $times[$st2]);
$lineplot2->SetLegend($st2);
$lineplot2->SetColor("red");
//$graph->Add($lineplot2);

// Create the linear plot
$lineplot3=new LinePlot($tmpf[$st3], $times[$st3]);
$lineplot3->SetLegend($st3);
$lineplot3->SetColor("black");
//$graph->Add($lineplot3);
// Display the graph
$graph->Stroke();
?>
