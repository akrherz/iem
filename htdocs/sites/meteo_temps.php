<?php
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/mlib.php");
include("setup.php");
include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_scatter.php");
include ("$rootpath/include/jpgraph/jpgraph_line.php");
include ("$rootpath/include/jpgraph/jpgraph_date.php");
include ("$rootpath/include/jpgraph/jpgraph_led.php");

$times = Array();
$dwpf = Array();
$tmpf = Array();
$srad = Array();

$dbconn = iemdb('access');
$rs = pg_prepare($dbconn, "SELECT", "SELECT c.*, 
	valid at time zone s.tzname as lvalid 
	from current_log c, stations s WHERE
    s.id = $1 and s.network = $2 and 
    c.iemid = s.iemid and 
    tmpf BETWEEN -90 and 140 and dwpf BETWEEN -90 and 140
      ORDER by valid ASC");
$rs = pg_execute($dbconn, "SELECT", array($station, $network) );
for ($i=0;  $row=@pg_fetch_array($rs,$i); $i++)
{
  $times[] = strtotime($row["lvalid"]);
  $dwpf[] = $row["dwpf"];
  $tmpf[] = $row["tmpf"];
  $srad[] = $row["srad"];
}
if (sizeof($tmpf) < 3){
	$led = new DigitalLED74();
 	$led->StrokeNumber('NO DATA, SORRY',LEDC_GREEN);
 	die();
}

$hasrad = (max($srad) > 10);

// Create the graph. These two calls are always required
$graph = new Graph(640,480,"example1");
$graph->SetScale("datlin");

$graph->img->SetMargin(45,45,30,110);
$graph->SetMarginColor('white');
$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("M d g A", true);
//$graph->xaxis->scale->SetDateFormat("h A");
$graph->xaxis->SetPos("min");

if ($hasrad) {
  $graph->SetY2Scale("lin");
  $graph->y2axis->SetTitleMargin(25);
  $graph->y2axis->SetColor("blue");
  $graph->y2axis->title->SetColor("blue");
  $graph->y2axis->title->SetFont(FF_FONT2,FS_BOLD,12);
  $graph->y2axis->SetTitle("Solar Radiation [w m{-2}]");
}

//$graph->yaxis->SetTitleMargin(30);

$graph->xaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
$graph->xaxis->SetTitle("Times in Timezone: ". $metadata["tzname"]);
$graph->xaxis->SetTitleMargin(65);
$graph->yaxis->SetTitle("Temperature [F]");
//$graph->yaxis->SetTitle("Wind Direction [N=0, E=90, S=180, W=270]");
//$graph->tabtitle->Set('Recent Comparison');
$graph->yaxis->scale->ticks->Set(90,15);
$graph->yaxis->scale->ticks->SetLabelFormat("%5.0f");
$graph->title->Set($metadata['name'] ." [$station] Time Series");

  $graph->yaxis->title->SetFont(FF_ARIAL,FS_BOLD,12);
  $graph->SetColor('wheat');

  $graph->legend->SetLayout(LEGEND_HOR);
  $graph->legend->SetPos(0.01,0.99, 'left', 'bottom');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();




$lineplot2=new LinePlot($tmpf, $times);
$lineplot2->SetLegend("Air Temp");
$lineplot2->SetColor("red");
$lineplot2->SetWeight(3);
$graph->Add($lineplot2);

$lineplot3=new LinePlot($dwpf, $times);
$lineplot3->SetLegend("Dew Point");
$lineplot3->SetColor("green");
$lineplot3->SetWeight(3);
$graph->Add($lineplot3);

if ($hasrad){
  $lineplot4=new LinePlot($srad, $times);
  $lineplot4->SetLegend("Solar Radiation");
  $lineplot4->SetColor("blue");
  $lineplot4->SetWeight(3);
  $graph->AddY2($lineplot4);
}


// Add the plot to the graph

// Display the graph
$graph->Stroke();
?>
