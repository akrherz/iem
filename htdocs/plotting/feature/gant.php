<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");

$postgis = iemdb("postgis");

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_gantt.php");

// Basic graph parameters
$graph = new GanttGraph();
$graph->SetMarginColor('darkgreen@0.8');
$graph->SetColor('white');

// We want to display day, hour and minute scales
$graph->ShowHeaders(GANTT_HDAY | GANTT_HHOUR );

$graph->scale->actinfo->SetColTitles(
    array('Phenomena','Event ID'));

$graph->SetDateRange('2008-06-20 12:00','2008-06-21 02:00');

$graph->scale->actinfo->vgrid->SetColor('gray');
$graph->scale->actinfo->SetColor('darkgray');

// Setup day format
$graph->scale->day->SetBackgroundColor('lightyellow:1.5');
$graph->scale->day->SetFont(FF_ARIAL);
$graph->scale->day->SetStyle(DAYSTYLE_SHORTDAYDATE3);

// Setup hour format
$graph->scale->hour->SetIntervall(1);
$graph->scale->hour->SetBackgroundColor('lightyellow:1.5');
$graph->scale->hour->SetFont(FF_FONT0);
$graph->scale->hour->SetStyle(HOURSTYLE_H24);
$graph->scale->hour->grid->SetColor('gray:0.8');

// Setup minute format
$graph->scale->minute->SetIntervall(30);
$graph->scale->minute->SetBackgroundColor('lightyellow:1.5');
$graph->scale->minute->SetFont(FF_FONT0);
$graph->scale->minute->SetStyle(MINUTESTYLE_MM);
$graph->scale->minute->grid->SetColor('lightgray');

$graph->scale->tableTitle->Set('Phase 1');
$graph->scale->tableTitle->SetFont(FF_ARIAL,FS_NORMAL,12);
$graph->scale->SetTableTitleBackground('darkgreen@0.6');
$graph->scale->tableTitle->Show(true);

$graph->title->Set("Example of hours & mins scale");
$graph->title->SetColor('darkgray');
$graph->title->SetFont(FF_VERDANA,FS_BOLD,14);



$rs = pg_exec($postgis, "SELECT * from
      warnings_2008 WHERE wfo = 'DMX' and date(issue) = 'TODAY'
      and gtype = 'P' ORDER by issue ASC");

for($i=0;$row=@pg_fetch_array($rs,$i);$i++)
{

    $bar = new GanttBar($i,Array($row["phenomena"], $row["eventid"]),$row["issue"],$row["expire"]);
    //if( count($data[$i])>4 )
    //$bar->title->SetFont($data[$i][4],$data[$i][5],$data[$i][6]);
    $bar->SetPattern(BAND_RDIAG,"yellow");
    $bar->SetFillColor("gray");
    $graph->Add($bar);  

}

$graph->Stroke();
?>
