<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$iem = iemdb('access');
$coop = iemdb('coop');

/* load up averages */
$climate = Array();
$rs = pg_query($coop, "SELECT gdd50 from climate WHERE valid >= '2000-05-01' and valid < '2000-08-14' and station = 'ia2364' ORDER by valid ASC");
for($i=0;$row=@pg_fetch_array($rs,$i);$i++){
  $climate[] = $row["gdd50"];
}

/* load up what happened */
$diff = Array();
$days = Array();
$rs = pg_query($iem, "SELECT day, gdd50(max_tmpf, min_tmpf) from summary WHERE station = 'DBQ' and day >= '2009-05-01' and day < '2009-08-14' ORDER by day ASC");
for($i=0;$row=@pg_fetch_array($rs,$i);$i++){
  $diff[] = $row["gdd50"] - $climate[$i];
  $days[] = date("d M", strtotime($row["day"]) );
}

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_bar.php");


// Create the graph. These two calls are always required
$graph = new Graph(640,600,"example1");
$graph->SetScale("textlin",-20,20);
$graph->img->SetMargin(40,10,50,50);

$graph->xaxis->SetLabelAngle(90);
//$graph->xaxis->SetLabelFormatString("M d", true);
//$graph->xaxis->scale->SetDateFormat("M d h A");
$graph->xaxis->SetPos("min");
$graph->xaxis->SetTickLabels($days);
$graph->xaxis->SetTextTickInterval(5);
$graph->xaxis->SetTitleMargin(70);

$graph->yaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
$graph->xaxis->title->SetFont(FF_FONT2,FS_BOLD,16);
//$graph->xaxis->SetTitle("Valid Local Time");
$graph->yaxis->SetTitle("Departure from Normal");
//$graph->tabtitle->Set('Ames High Temperature');
$graph->title->Set("2009 Dubuque Daily \nGrowing Degree Day Departure");

  $graph->tabtitle->SetFont(FF_FONT1,FS_BOLD,16);
  $graph->SetColor('wheat');

//  $graph->legend->SetLayout(LEGEND_HOR);
//  $graph->legend->SetPos(0.01,0.07, 'right', 'top');
//  $graph->legend->SetLineSpacing(3);

  $graph->ygrid->SetFill(true,'#EFEFEF@0.5','#BBCCEE@0.5');
  $graph->ygrid->Show();
  $graph->xgrid->Show();


// Create the linear plot
$lineplot=new BarPlot($diff);
//$lineplot->SetLegend("When Previous Day < 32");
$lineplot->SetColor("blue");
$graph->Add($lineplot);



// Display the graph
$graph->Stroke();
?>
