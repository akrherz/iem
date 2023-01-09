<?php
require_once "../../../config/settings.inc.php";
require_once "../../../include/mlib.php";
require_once "../../../include/jpgraph/jpgraph.php";
require_once "../../../include/jpgraph/jpgraph_line.php";
require_once "../../../include/jpgraph/jpgraph_date.php";
//  1 minute data plotter 

$year = isset($_GET["year"]) ? $_GET["year"] : date("Y");
$month = isset($_GET["month"]) ? $_GET["month"] : date("m");
$day = isset($_GET["day"]) ? $_GET["day"] : date("d");
$station = isset($_REQUEST['station']) ? $_REQUEST['station']: null;

if (strlen($year) == 4 && strlen($month) > 0 && strlen($day) > 0 ){
  $myTime = strtotime($year."-".$month."-".$day);
} else {
  $myTime = strtotime(date("Y-m-d"));
}

$titleDate = date("M d, Y", $myTime);
$dirRef = date("Y/m/d", $myTime);
$tmpf = array();
$dwpf = array();
$relh = array();
$valid = array();

if ($station == null){
    $fcontents = file("/mesonet/ARCHIVE/data/$dirRef/text/ot/ot0002.dat");
    foreach($fcontents as $line_num => $line){
        $parts = preg_split ("/\s+/", $line);
        $v = strtotime( substr($line, 0, 26) );
        if ($v < $myTime){
            continue;
        }
        $tval = round (substr($line, 36, 6),2);
        if ($tval < -40 || $tval > 120){
          continue;
        }
        $valid[] = $v;
        $tmpf[] = $tval;
        $rh = intval($parts[8]);

        $d = dwpf(round (substr($line, 36, 6),2), $rh);
        $dwpf[] = ($d > -40 && $d < 90 && $rh > 1 && $rh < 100)? $d : "";
        $relh[] = ($rh > 1 && $rh < 100)? $rh : "";
     } // End of while
} else {
    $fcontents = file("/mesonet/ARCHIVE/data/$dirRef/text/ot/ot0010.dat");
    /*
     * month, day, year, hour, minute, outside temp, hi outside temp, lo outside
       temp, outside humidity, wind speed, wind direction, wind gust speed, time
         of gust, pressure, daily_precip, monthly_rain, yearly_rain, inside
         temp, inside humidity, solar radiation, UV index
     */
    foreach($fcontents as $line_num => $line){
        $tokens = explode(' ', $line);
        if (sizeof($tokens) != 21){
            continue;
        }
          $tstring = sprintf("%s %s %s %s", $tokens[0], $tokens[1], $tokens[2], 
                  $tokens[3]);
          $v = strtotime($tstring);
          
        if ($v < $myTime || trim($tstring) == ""){
            continue;
        }
        $tval = floatval($tokens[5]);
        if ($tval < -40 || $tval > 120){
          continue;
        }
        $valid[] = $v;
          $tmpf[] = $tval;
        $rh = floatval($tokens[8]);
        $relh[] = $rh;
        $d = dwpf($tokens[5], $rh);
        $dwpf[] = ($rh > 1 && $rh < 101) ? $d: "";
     } // End of while
}	

// Create the graph. These two calls are always required
$graph = new Graph(600,400,"example1");
$graph->SetScale("datlin");
if (isset($_REQUEST["rh"])){
    $graph->SetY2Scale("lin",0,100);
    $graph->y2axis->SetTitle("Relative Humidity [%]");
    $graph->y2axis->title->SetFont(FF_FONT1,FS_BOLD,12);
    $graph->title->Set("$titleDate Outside Temperature & Relative Humidity");
} else {
    $graph->title->Set("$titleDate Outside Temperature");
}
$graph->img->SetMargin(65,40,55,80);
//$graph->xaxis->SetFont(FONT1,FS_BOLD);

$graph->xaxis->SetLabelAngle(90);
$graph->xaxis->SetLabelFormatString("h:i A", true);
//$graph->yaxis->scale->ticks->SetPrecision(1);
$graph->yaxis->scale->ticks->Set(1,0.5);
//$graph->yscale->SetGrace(10);

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.2,0.09);


$graph->title->SetFont(FF_FONT1,FS_BOLD,14);
$graph->yaxis->SetTitle("Temperature [F]");

$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Valid Local Time");
$graph->xaxis->SetTitleMargin(50);
//$graph->yaxis->SetTitleMargin(48);
$graph->yaxis->SetTitleMargin(40);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetPos("min");

// Create the linear plot
$lineplot=new LinePlot($tmpf, $valid);
$lineplot->SetLegend("Temperature");
$lineplot->SetColor("red");
$lineplot->SetWeight(3.0);

// Create the linear plot
$lineplot2=new LinePlot($dwpf, $valid);
$lineplot2->SetLegend("Dew Point");
$lineplot2->SetColor("blue");
$lineplot2->SetWeight(3.0);

// Create the linear plot
$lineplot3=new LinePlot($relh, $valid);
$lineplot3->SetLegend("Rel Humid");
$lineplot3->SetColor("black");
$lineplot3->SetWeight(3.0);

// Box for error notations
//[DMF]$t1 = new Text("Dups: ".$dups ." Missing: ".$missing );
//[DMF]$t1->SetPos(0.4,0.95);
//[DMF]$t1->SetOrientation("h");
//[DMF]$t1->SetFont(FF_FONT1,FS_BOLD);
//$t1->SetBox("white","black",true);
//[DMF]$t1->SetColor("black");
//[DMF]$graph->AddText($t1);

$graph->Add($lineplot);
if (isset($_REQUEST["rh"])){
    $graph->AddY2($lineplot3);
} else {
    $graph->Add($lineplot2);
}
    
$graph->Stroke();

?>
