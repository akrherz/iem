<?php
require_once "../../../config/settings.inc.php";
require_once "../../../include/database.inc.php";
require_once "../../../include/network.php";
require_once "../../../include/forms.php";
require_once "../../../include/jpgraph/jpgraph.php";
require_once "../../../include/jpgraph/jpgraph_line.php";
$nt = new NetworkTable("SCAN");

$connection = iemdb("scan");

$station = isset($_GET["station"]) ? xssafe($_GET["station"]) : "S2031";
$year = get_int404("year", date("Y", time() - 3 * 86400));
$month = get_int404("month", date("m", time() - 3 * 86400));
$day = get_int404("day", date("d", time() - 3 * 86400));

$y2label = "Temperature [C]";

$date = "$year-$month-$day";

$rs = pg_prepare($connection, "SELECT", "SELECT c1tmpf, c2tmpf, c3tmpf, 
        c4tmpf, c5tmpf, srad , tmpf,
        to_char(valid, 'mmdd/HH24') as tvalid 
        from alldata WHERE 
        station = $1 and date(valid) >= $2  
        ORDER by tvalid ASC LIMIT 96");

$result = pg_execute($connection, "SELECT", Array($station, $date));

$ydata1 = array();
$ydata2 = array();
$ydata3 = array();
$ydata4 = array();
$ydata5 = array();
$ydataA = array();
$ydataSR = array();

$xlabel= array();

for( $i=0; $row = pg_fetch_array($result); $i++) 
{ 
  $ydata1[$i]  = $row["c1tmpf"];
  $ydata2[$i]  = $row["c2tmpf"];
  $ydata3[$i] = $row["c3tmpf"];
  $ydata4[$i] = $row["c4tmpf"];
  $ydata5[$i] = $row["c5tmpf"];
  $ydataSR[$i] = $row["srad"];
  $ydataA[$i] = $row["tmpf"];
  $xlabel[$i] = $row["tvalid"];
}

pg_close($connection);


// Create the graph. These two calls are always required
$graph = new Graph(660,450,"example1");
$graph->SetScale("textlin");
$graph->SetY2Scale("lin",0,900);
$graph->img->SetMargin(40,50,55,90);
$graph->xaxis->SetFont(FF_FONT1,FS_BOLD);
$graph->xaxis->SetTickLabels($xlabel);
$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetPos("min");
$graph->title->Set("Solar Rad & Soil Temps for ".$nt->table[$station]["name"]."  SCAN Site");

$graph->y2axis->scale->ticks->Set(100,25);
//$graph->y2axis->scale->ticks->SetPrecision(0);

$graph->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->y2axis->SetTitle("Solar Radiation [Watts m**-2]");
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Local Valid Time");
$graph->yaxis->SetTitle( $y2label );
$graph->y2axis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->y2axis->SetTitleMargin(35);
$graph->xaxis->SetTitleMargin(55);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
if ($i > 72){
  $graph->xaxis->SetTextTickInterval(6);
}
//$graph->y2axis->SetColor("blue");
$graph->y2axis->SetColor("red");

// Create the linear plot
$lineplot=new LinePlot($ydataSR);
$lineplot->SetColor("red");
$lineplot->SetLegend("Solar Rad");

// Create the linear plot
$lineplot1=new LinePlot($ydata1);
$lineplot1->SetColor("green");
$lineplot1->SetLegend("2 in");

// Create the linear plot
$lineplot2=new LinePlot($ydata2);
$lineplot2->SetColor("aquamarine4");
$lineplot2->SetLegend("4 in");

// Create the linear plot
$lineplot3=new LinePlot($ydata3);
$lineplot3->SetColor("chocolate4");
$lineplot3->SetLegend("8 in");
$lineplot3->SetStyle("dashed");

// Create the linear plot
$lineplot4=new LinePlot($ydata4);
$lineplot4->SetColor("blue");
$lineplot4->SetLegend("20 in");

// Create the linear plot
$lineplotA=new LinePlot($ydataA);
$lineplotA->SetColor("black");
$lineplotA->SetLegend("2m Air");


// Create the linear plot
$lineplot5=new LinePlot($ydata5);
$lineplot5->SetColor("black");
$lineplot5->SetLegend("40 in");
$lineplot5->SetStyle("dotted");

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.10, 0.06, "right", "top");


// Add the plot to the graph
$graph->Add($lineplot1);
$graph->Add($lineplot2);
$graph->Add($lineplot3);
$graph->Add($lineplot4);
$graph->Add($lineplot5);
$graph->Add($lineplotA);
$graph->AddY2($lineplot);

// Display the graph
$graph->Stroke();
