<?php
/* 
 * Generate KML of the county intersection of a SBW
 */
require_once "../../config/settings.inc.php";
require_once "../../include/database.inc.php";
require_once "../../include/forms.php";
$connect = iemdb("postgis");

$year = get_int404("year", 2006);
$wfo = isset($_GET["wfo"]) ? substr(xssafe($_GET["wfo"]),0,4) : "MPX";
if (strlen($wfo) > 3){
    $wfo = substr($wfo, 1, 3);
}
$eventid = get_int404("eventid", 103);
$phenomena = isset($_GET["phenomena"]) ? substr(xssafe($_GET["phenomena"]),0,2) : "SV";
$significance = isset($_GET["significance"]) ? substr(xssafe($_GET["significance"]),0,1) : "W";

$sql = <<<EOF
    WITH stormbased as (SELECT geom from sbw_$year where wfo = '$wfo' 
        and eventid = $eventid and significance = '$significance' 
        and phenomena = '$phenomena' and status = 'NEW'), 
    countybased as (SELECT ST_Union(u.geom) as geom from 
        warnings_$year w JOIN ugcs u on (u.gid = w.gid) 
        WHERE w.wfo = '$wfo' and eventid = $eventid and 
        significance = '$significance' and phenomena = '$phenomena') 
                
    SELECT ST_askml(geo) as kml, ST_Length(ST_transform(geo,9311)) as sz from
        (SELECT ST_SetSRID(ST_intersection(
          ST_buffer(ST_exteriorring(ST_geometryn(ST_multi(c.geom),1)),0.02),
          ST_exteriorring(ST_geometryn(ST_multi(s.geom),1))
            ), 4326) as geo
    from stormbased s, countybased c) as foo
EOF;
$rs = pg_exec($connect, $sql);
header('Content-disposition: attachment; filename=sbw.kml');
header("Content-Type: application/vnd.google-earth.kml+xml");

echo <<<EOM
<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<kml xmlns=\"http://earth.google.com/kml/2.2\">
 <Document>
    <Style id=\"iemstyle0\">
      <LineStyle>
        <width>7</width>
        <color>ff0000ff</color>
      </LineStyle>
    </Style>
    <Style id=\"iemstyle1\">
      <LineStyle>
        <width>7</width>
        <color>ff00ff00</color>
      </LineStyle>
    </Style>
    <Style id=\"iemstyle2\">
      <LineStyle>
        <width>7</width>
        <color>ffff0000</color>
      </LineStyle>
    </Style>
EOM;

for($i=0;$row=pg_fetch_assoc($rs);$i++){
  echo sprintf("<Placemark>
    <styleUrl>#iemstyle%s</styleUrl>
    <name>Intersect size: %.1f km ID: %s</name>", $i%3, $row["sz"] /1000.0, $i);
  echo $row["kml"];
  echo "</Placemark>";
}
echo " </Document>
</kml>";
