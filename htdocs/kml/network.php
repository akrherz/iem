<?php
/* Generate a KML file of a network locations, yummy */
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/network.php");
$network = isset($_GET["network"]) ? $_GET["network"] : "KCCI"; 

header("Content-Type: application/vnd.google-earth.kml+xml");
echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<kml xmlns=\"http://www.opengis.net/kml/2.2\">
 <Document>
   <Style id=\"iemstyle\">
     <IconStyle>
      <scale>0.8</scale>
      <Icon>
        <href>http://maps.google.com/mapfiles/kml/shapes/webcam.png</href>
      </Icon>
     </IconStyle>
     <BalloonStyle>
      <bgColor>ffffffff</bgColor>
    </BalloonStyle>
  </Style>";

$nt = new NetworkTable($network);

while (list($sid,$data) = each($nt->table))
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
?>
