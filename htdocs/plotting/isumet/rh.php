<?php
include("../../../config/settings.inc.php");
include("../../../include/mlib.php");
require_once "../../../include/jpgraph/jpgraph.php";
require_once "../../../include/jpgraph/jpgraph_line.php";
require_once "../../../include/jpgraph/jpgraph_scatter.php";
require_once "../../../include/jpgraph/jpgraph_date.php";

$year = isset($_GET["year"]) ? $_GET["year"] : date("Y");
$month = isset($_GET["month"]) ? $_GET["month"] : date("m");
$day = isset($_GET["day"]) ? $_GET["day"] : date("d");
$station = isset($_REQUEST['station']) ? $_REQUEST['station']: null;

if (strlen($year) == 4 && strlen($month) > 0 && strlen($day) > 0 ){
  $myTime = strtotime($year."-".$month."-".$day);
} else {
  $myTime = strtotime( date("Y-m-d") );
}

$wA = mktime(0,0,0, 8, 4, 2002);
$wLabel = "1min Instantaneous Wind Speed";
if ($wA > $myTime){
 $wLabel = "Instant Wind Speed";
}

$titleDate = date("M d, Y", $myTime);
$dirRef = date("Y/m/d", $myTime);


$srad = array();
$_dwpf = array();
$irelh = array();
$orelh = array();

if ($station == null){
    $fcontents = file("/mesonet/ARCHIVE/data/$dirRef/text/ot/ot0002.dat");
    foreach($fcontents as $line_num => $line){
          $valid[] = strtotime( substr($line, 0, 26) );
          $parts = preg_split ("/\s+/", $line);
          $orelh[] = intval($parts[7]);
        $_dwpf[] = dwpf(intval($parts[6]), intval($parts[7]));
    }
} else {
    $fn = "/mesonet/ARCHIVE/data/$dirRef/text/ot/ot0010.dat";
    if (!file_exists($fn)){
        die("File not found");
    }
    $fcontents = file($fn);

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
        $rval = floatval($tokens[8]);
        if ($rval < 0 || $rval > 101){
            continue;
        }
        $valid[] = $v;
          $orelh[] = $rval;
          $irelh[] = $tokens[18];
          $_dwpf[] = dwpf(floatval($tokens[5]), floatval($tokens[8]));
     } // End of while
    
}


// Create the graph. These two calls are always required
$graph = new Graph(600, 400,"example1");
$graph->SetScale("datelin",0,100);
$graph->img->SetMargin(65,40,55,80);

//$graph->yaxis->scale->ticks->SetPrecision(1);
$graph->title->Set("$titleDate Relative Humidity");

$graph->legend->SetLayout(LEGEND_HOR);
$graph->legend->Pos(0.01,0.08);
$graph->xaxis->SetLabelAngle(90);
//$graph->yaxis->scale->ticks->Set(90,15);
//$graph->yaxis->scale->ticks->SetPrecision(0);
//$graph->yaxis->scale->ticks->SetPrecision(0);

//$graph->yaxis->SetColor("blue");

$graph->title->SetFont(FF_FONT1,FS_BOLD,14);

$graph->yaxis->SetTitle("Relative Humidity [%]");
$graph->xaxis->SetLabelFormatString("h:i A", true);
$graph->yaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetTitle("Valid Local Time");
$graph->xaxis->SetTitleMargin(50);
$graph->yaxis->SetTitleMargin(30);
//$graph->y2axis->SetTitleMargin(28);
$graph->xaxis->title->SetFont(FF_FONT1,FS_BOLD,12);
$graph->xaxis->SetPos("min");

// Create the linear plot
$lineplot=new LinePlot($orelh, $valid);
$lineplot->SetColor("blue");
$lineplot->SetLegend("Outside");
$lineplot->SetWeight(3.0);
$graph->Add($lineplot);

$lineplot2=new LinePlot($irelh, $valid);
$lineplot2->SetColor("red");
$lineplot2->SetLegend("Inside");
$lineplot2->SetWeight(3.0);
$graph->Add($lineplot2);


$graph->Stroke();
?>
