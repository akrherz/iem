<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$coopdb = iemdb("coop");

$data = Array();
$years = Array();

$rs = pg_query($coopdb, "SELECT year, sum( sdd86(high,low) ) from alldata
      WHERE stationid = 'ia0200' and sday < '0819' and year < 2009 GROUP by year 
      ORDER by year ASC");
for($i=0;$row=@pg_fetch_array($rs,$i);$i++){
  $data[] = $row["sum"];
  $years[] = $row["year"];
}
$data[] = 21;
$years[] = 2009;

include("$rootpath/include/jpgraph/jpgraph.php");
include("$rootpath/include/jpgraph/jpgraph_bar.php");

// Create the graph and setup the basic parameters 
$graph = new Graph(640,480,'auto');    
$graph->img->SetMargin(40,10,40,50);
$graph->SetScale("textint");
$graph->SetFrame(true,'red',1); 
$graph->SetColor('lightred');
$graph->SetMarginColor('lightred');

// Setup X-axis labels
$graph->xaxis->SetTickLabels($years);
$graph->xaxis->SetFont(FF_FONT1);
$graph->xaxis->SetColor('darkred','black');
$graph->xaxis->SetTextTickInterval(10);
$graph->xaxis->SetLabelAngle(90);

// Setup "hidden" y-axis by given it the same color
// as the background (this could also be done by setting the weight
// to zero)
$graph->yaxis->SetColor('lightred','darkred');
$graph->ygrid->SetColor('white');

// Setup graph title ands fonts
$graph->title->Set("Ames Stress Degree Days (base=86)\nPrior to 19 Aug");
$graph->title->SetFont(FF_FONT2,FS_BOLD);
//$graph->xaxis->SetTitle('Year','center');
$graph->xaxis->SetTitleMargin(10);
$graph->xaxis->title->SetFont(FF_FONT2,FS_BOLD);

// Add some grace to the top so that the scale doesn't
// end exactly at the max value. 
$graph->yaxis->scale->SetGrace(10);

                              
// Create a bar pot
$bplot = new BarPlot($data);
$bplot->SetFillColor('darkred');
$bplot->SetColor('darkred');
//$bplot->SetWidth(0.5);
//$bplot->SetShadow('darkgray');

// Setup the values that are displayed on top of each bar
// Must use TTF fonts if we want text at an arbitrary angle
//$bplot->value->Show();
//$bplot->value->SetFont(FF_ARIAL,FS_NORMAL,8);
//$bplot->value->SetFormat('$%d');
//$bplot->value->SetColor('darkred');
//$bplot->value->SetAngle(45);
$graph->Add($bplot);

// Create and add a new text
$txt=new Text(sprintf("Mean: %.1f\n2009: 21", array_sum($data)/sizeof($data)) );
$txt->SetPos(0.7,0.2);
$txt->SetColor('darkred');
$txt->SetFont(FF_FONT1,FS_BOLD);
$txt->SetBox('pink','white','gray@0.5');
$graph->AddText($txt);

// Finally stroke the graph
$graph->Stroke();

?>
