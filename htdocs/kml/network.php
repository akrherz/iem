<?php
require_once "../../config/settings.inc.php";
require_once "../../include/database.inc.php";
require_once "../../include/network.php";
require_once "../../include/forms.php";
$network = isset($_GET["network"]) ? xssafe($_GET["network"]) : "IA_ASOS"; 

header("Content-Type: application/vnd.google-earth.kml+xml");
echo <<<EOM
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
 <Document>
   <Style id="iemstyle">
     <IconStyle>
      <scale>0.8</scale>
      <Icon>
        <href>http://maps.google.com/mapfiles/kml/shapes/webcam.png</href>
      </Icon>
     </IconStyle>
     <BalloonStyle>
      <bgColor>ffffffff</bgColor>
    </BalloonStyle>
  </Style>
EOM;

$nt = new NetworkTable($network);

foreach($nt->table as $sid => $data)
{

  echo "<Placemark>
    <name>". $data["name"] ."</name>
    <description>
<![CDATA[
  <p>Blah!</p>
        ]]>
    </description>
<ExtendedData>
  <Data name=\"sid\"><value>". $sid ."</value></Data>
</ExtendedData>
    <styleUrl>#iemstyle</styleUrl>
    <Point>
       <coordinates>". $data["lon"] .",". $data["lat"] .",0</coordinates>
    </Point>
</Placemark>";
}
echo "</Document></kml>";
