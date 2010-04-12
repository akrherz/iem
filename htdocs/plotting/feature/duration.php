<?php
include("../../../config/settings.inc.php");


$years = Array();
$ts0 = Array();
$ts1 = Array();


$fc = file('yearly.txt');
while (list ($line_num, $line) = each ($fc)) {
      $tokens = split ("\|", $line);
   $ts0[] = "2000-".substr(trim($tokens[1]),5,5) ;
   $ts1[] = "2000-".substr(trim($tokens[2]),5,5) ;
   $years[] = $tokens[0];
 }

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_gantt.php");

$graph = new GanttGraph();
//$graph->SetMargin(3,3,25,3);

//$graph->SetVMarginFactor(0.02);

$graph->title->Set("First+Last NWS Warning in Iowa\nSevere T'Storm and Tornado");

// Setup some "very" nonstandard colors
$graph->SetMarginColor('lightgreen@0.8');
$graph->SetBox(true,'yellow:0.6',2);
$graph->SetFrame(true,'darkgreen',4);
$graph->scale->divider->SetColor('yellow:0.6');
$graph->scale->dividerh->SetColor('yellow:0.6');

// Explicitely set the date range 
// (Autoscaling will of course also work)
$graph->SetDateRange('2000-01-01','2000-12-31');

// Display month and year scale with the gridlines
$graph->ShowHeaders(GANTT_HMONTH );
$graph->scale->month->grid->SetColor('gray');
$graph->scale->month->grid->Show(true);
//$graph->scale->month->SetFont(FF_ARIAL,FS_NORMAL,7);
$graph->scale->year->grid->SetColor('gray');
$graph->scale->year->grid->Show(true);

// Setup a horizontal grid
$graph->hgrid->Show();
$graph->hgrid->SetRowFillColor('darkblue@0.9');

// Setup activity info

// For the titles we also add a minimum width of 100 pixels for the Task name column
$graph->scale->actinfo->SetColTitles(array('Year'),array(30));
$graph->scale->actinfo->SetBackgroundColor('white:0.5@0.5');
//$graph->scale->actinfo->SetFont(FF_ARIAL,FS_NORMAL,10);
$graph->scale->actinfo->vgrid->SetStyle('solid');
$graph->scale->actinfo->vgrid->SetColor('gray');

    
// Create the bars and add them to the gantt chart
for($i=0; $i<count($years); $i++) {
    $bar = new GanttBar($i,array($years[$i]),$ts0[$i],$ts1[$i],"", 8);
    $bar->SetPattern(BAND_RDIAG,"yellow");
    $bar->SetFillColor("gray");
    //$bar->progress->Set(0.5);
    //$bar->progress->SetPattern(GANTT_SOLID,"darkgreen");
    $graph->Add($bar);
}

// Output the chart
$graph->stroke();

?>
