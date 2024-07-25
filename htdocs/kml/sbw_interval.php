<?php
/* Sucks to render a KML */
require_once "../../config/settings.inc.php";
require_once "../../include/database.inc.php";
require_once "../../include/vtec.php";

function nice_date($val){
    if (is_null($val)) return "not available";
    return gmdate('d M Y H:i', strtotime($val)) ." UTC";
}

$connect = iemdb("postgis");
$has_error = false;
$error_message = 'Unknown error occurred';
$mywfos = array();
if (isset($_REQUEST['location_group'])){
    $location_group = (string) $_REQUEST['location_group'];
    if($location_group === 'states'){
        if(isset($_REQUEST[$location_group])){
            $connect_meso = iemdb('mesosite');
            $mywfos = pull_wfos_in_states($connect_meso, $_REQUEST[$location_group]);
            if($mywfos === null){
                $has_error = true;
                $error_message = 'Error determine relevant list of WFO to use';
            }
            else{
                // Make sure we have at least one wfo
                if(count($mywfos) === 0){
                    $has_error = true;
                    $error_message = 'Unable to find any WFO in those states';
                }
            }
        }
        else{
            $has_error = true;
            $error_message = 'No states specified';
        }
    }
    elseif($location_group === 'wfo'){
        $wfo = isset($_GET["wfo"]) ? substr($_GET["wfo"],0,3) : "";
        $mywfos = isset($_GET["wfos"]) ? $_GET["wfos"] : Array();
        if (sizeof($mywfos) == 0 && $wfo != ""){ $mywfos[] = $wfo; }
    }
}
else{
    $has_error = true;
    $error_message = 'No location type specified';
}

if($has_error){
    echo $error_message;
    exit;
}
else{
    if (isset($_REQUEST["year1"])){
        $ts = mktime($_REQUEST["hour1"], $_REQUEST["minute1"],0, $_REQUEST["month1"], $_REQUEST["day1"], $_REQUEST["year1"]);
        $ts2 = mktime($_REQUEST["hour2"], $_REQUEST["minute2"],0, $_REQUEST["month2"], $_REQUEST["day2"], $_REQUEST["year2"]);
    } else {
        $ts = isset($_GET["ts"]) ? strtotime($_GET["ts"]) : die("APIFAIL");
        $ts2 = isset($_GET["ts2"]) ? strtotime($_GET["ts2"]) : die("APIFAIL");
    }

    $tsSQL = date("Y-m-d H:i:00+00", $ts);
    $tsSQL2 = date("Y-m-d H:i:00+00", $ts2);

    $result = pull_vtec_events_by_wfo_year(
        $connect, $mywfos, $tsSQL, $tsSQL2, $_GET);
}

header('Content-disposition: attachment; filename=sbw_interval.kml');
header("Content-Type: application/vnd.google-earth.kml+xml");
// abgr

echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<kml xmlns=\"http://earth.google.com/kml/2.2\">
 <Document>
    <Style id=\"TOstyle\">
      <LineStyle><width>1</width><color>ff000000</color></LineStyle>
      <PolyStyle><color>7d0000ff</color></PolyStyle>
    </Style>
    <Style id=\"MAstyle\">
      <LineStyle><width>1</width><color>ff000000</color></LineStyle>
      <PolyStyle><color>7d00ff00</color></PolyStyle>
    </Style>
    <Style id=\"SVstyle\">
      <LineStyle><width>1</width><color>ff000000</color></LineStyle>
      <PolyStyle><color>7d00ffff</color></PolyStyle>
    </Style>
    <Style id=\"FAstyle\">
      <LineStyle><width>1</width><color>ff000000</color></LineStyle>
      <PolyStyle><color>7d00ff00</color></PolyStyle>
    </Style>
    <Style id=\"FFstyle\">
      <LineStyle><width>1</width><color>ff000000</color></LineStyle>
      <PolyStyle><color>7d00ff00</color></PolyStyle>
    </Style>";
for ($i=0;$row=pg_fetch_array($result);$i++){
    $uri = sprintf(
        "<a href=\"%s/vtec/#%s-O-NEW-K%s-%s-%s-%04d\">%s</a>",
        "https://mesonet.agron.iastate.edu", date('Y', strtotime($row["polygon_begin"])),
        $row["wfo"], $row["phenomena"],
        $row["significance"], $row["eventid"], $row["eventid"]
    );
  echo "<Placemark>
    <description>
        <![CDATA[
  <p><font color=\"red\"><i>Polygon Size:</i></font> ". $row["psize"] ." sq km
  <br /><font color=\"red\"><i>Event ID:</i></font> $uri
  <br /><font color=\"red\"><i>Issued:</i></font> ". nice_date($row["issue"]) ."
  <br /><font color=\"red\"><i>Expires:</i></font> ". nice_date($row["expire"]) ."
  <br /><font color=\"red\"><i>Polygon Begin:</i></font> ". nice_date($row["polygon_begin"]) ."
  <br /><font color=\"red\"><i>Polygon End:</i></font> ". nice_date($row["polygon_end"]) ."
  <br /><font color=\"red\"><i>Status:</i></font> ". $vtec_status[$row["status"]] ."
  <br /><font color=\"red\"><i>Hail Tag:</i></font> {$row["hailtag"]} IN
  <br /><font color=\"red\"><i>Wind Tag:</i></font> {$row["windtag"]} MPH
  <br /><font color=\"red\"><i>Tornado Tag:</i></font> {$row["tornadotag"]}
  <br /><font color=\"red\"><i>Damage Tag:</i></font> {$row["damagetag"]}
   </p>
        ]]>
    </description>
    <styleUrl>#".$row["phenomena"]."style</styleUrl>
    <name>". $vtec_phenomena[$row["phenomena"]] ." ". $vtec_significance[$row["significance"]]  ."</name>\n";
  echo $row["kml"];
  echo "</Placemark>";
}
echo "</Document>
</kml>";

function pull_wfos_in_states($db, $state_abbreviations){
    $status = true;
    $sql = 'SELECT distinct wfo FROM stations WHERE state IN (';
    // Loop over the states just to be safe
    $in_delimiter = '';
    $valid_state_count = 0;
    $wfos = array();
    $wfo_count = 0;
    foreach($state_abbreviations as $state_abbreviation){
        if(preg_match('#^[A-Z]{2}$#', $state_abbreviation)){
            $sql .= $in_delimiter . '\'' . $state_abbreviation . '\'';
            $in_delimiter = ',';
            ++$valid_state_count;
        }
        else{
            $status = false;
            break;
        }
    }
    if($status){
        if($valid_state_count > 0 ){
            $sql .= ')';
            $result  = pg_query($db, $sql);
            for ($i=0;$row=pg_fetch_array($result);$i++){
                if($row['wfo'] !== null){
                    $wfos[$wfo_count] = $row['wfo'];
                    ++$wfo_count;
                }
            }
        }
        else{
            $status = false;
        }
    }

    if(!$status){
        $wfos = null;
    }

    return $wfos;
}

function pull_vtec_events_by_wfo_year(
        $db, $wfos, $tsSQL, $tsSQL2, $form){
    if(count($wfos) > 0 && ! in_array("ALL", $wfos)){
        $wfolimiter = 'wfo IN (\'' . implode("','", $wfos) . '\') and';
    }
    else{
        $wfolimiter = '';
    }
    $pslimiter = "";
    if (isset($form["limitps"]) && ($form["limitps"] == "yes")){
        $pslimiter = sprintf(
            " and phenomena = '%s' and significance = '%s' ",
            $form["phenomena"],
            $form["significance"],
        );
    }
    $statuslimiter = " status = 'NEW' ";
    if (isset($form["addsvs"]) && ($form["addsvs"] == "yes")){
        $statuslimiter = " status != 'CAN' ";
    }
    $rs = pg_prepare($db, "SELECT-INT", "SELECT 
        issue, expire, phenomena, significance, eventid, wfo, status,
           ST_askml(geom) as kml,
           round(ST_area(ST_transform(geom,2163)) / 1000000.0) as psize,
           polygon_begin, polygon_end, tornadotag, damagetag, windtag, hailtag
           from sbw
           WHERE $wfolimiter coalesce(issue, polygon_begin) >= $1
           and coalesce(issue, polygon_begin) <= $2
           and $statuslimiter and eventid > 0 $pslimiter");
    $rs = pg_prepare($db, "SELECT", "SELECT
        issue, expire, phenomena, significance, eventid, wfo, status,
           ST_askml(geom) as kml,
           round(ST_area(ST_transform(geom,2163)) / 1000000.0) as psize,
           polygon_begin, polygon_end, tornadotag, damagetag, windtag, hailtag
           from sbw
           WHERE $wfolimiter coalesce(issue, polygon_begin) <= $1 and
           expire > $2
           and $statuslimiter and eventid > 0 $pslimiter");

    if ($tsSQL != $tsSQL2)
    {
        $result = pg_execute($db, "SELECT-INT",  Array($tsSQL, $tsSQL2) );
    } else {
        $result = pg_execute($db, "SELECT",  Array($tsSQL, $tsSQL) );
    }
    return $result;
}
