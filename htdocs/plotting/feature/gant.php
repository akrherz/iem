<?php
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/vtec.php");


$postgis = iemdb("postgis");

include ("$rootpath/include/jpgraph/jpgraph.php");
include ("$rootpath/include/jpgraph/jpgraph_gantt.php");

// Basic graph parameters
$graph = new GanttGraph(320,240);
$graph->SetMargin(5,5,40,5);
$graph->SetMarginColor('darkgreen@0.8');
$graph->SetColor('white');

// We want to display day, hour and minute scales
//$graph->ShowHeaders(GANTT_HDAY | GANTT_HHOUR );

//$graph->scale->actinfo->SetColTitles( array('Product') );

//$graph->SetDateRange('2008-12-14','2008-12-22');

$graph->scale->actinfo->vgrid->SetColor('gray');
$graph->scale->actinfo->SetColor('darkgray');
$graph->ShowHeaders(GANTT_HDAY);
// $graph ->ShowHeaders(GANTT_HHOUR);
// Setup day format
//$graph->scale->day->SetBackgroundColor('lightyellow:1.5');
//$graph->scale->day->SetFont(FF_ARIAL);
$graph->scale->day->SetStyle(DAYSTYLE_SHORTDATE4);

//$graph->scale->tableTitle->Set('Phase 1');
//$graph->scale->tableTitle->SetFont(FF_ARIAL,FS_NORMAL,12);
//$graph->scale->SetTableTitleBackground('darkgreen@0.6');
//$graph->scale->tableTitle->Show(true);

$graph->title->Set("NWS Issued Products");
$graph->subtitle->Set("for Story County [14-22 Dec 2008]");
$graph->title->SetColor('darkgray');
//$graph->title->SetFont(FF_VERDANA,FS_BOLD,14);

$graph->scale->UseWeekendBackground(false );


$rs = pg_exec($postgis, "SELECT * from
      warnings_2008 WHERE wfo = 'DMX' and issue > '2008-12-14'
      and gtype = 'C' and ugc = 'IAZ048' ORDER by issue ASC");

$ar = Array();
for($i=0;$row=@pg_fetch_array($rs,$i);$i++)
{

    $lbl = sprintf("%s %s", $vtec_phenomena[$row["phenomena"]], 
           $vtec_significance[$row["significance"]]);
    $ar[$i] = new GanttBar($i,Array($lbl),
       substr($row["issue"],0,16),substr($row["expire"],0,16));
    //if( count($data[$i])>4 )
    //$bar->title->SetFont($data[$i][4],$data[$i][5],$data[$i][6]);
    $ar[$i]->SetPattern(BAND_SOLID,"yellow");
    $ar[$i]->SetFillColor("gray");
    $graph->Add($ar[$i]);  

}

$graph->Stroke();
?>
