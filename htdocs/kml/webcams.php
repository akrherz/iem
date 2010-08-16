<?php
/* Generate GR placefile of webcam stuff */
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/cameras.inc.php");
$network = isset($_GET["network"]) ? $_GET["network"] : "KCCI"; 

header("Content-Type: application/vnd.google-earth.kml+xml");
echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<kml xmlns=\"http://earth.google.com/kml/2.2\">
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

$conn = iemdb("mesosite");
$sql = "SELECT * from camera_current WHERE valid > (now() - '30 minutes'::interval)"; 
$rs = pg_exec($conn, $sql);
for ($i=0;$row=@pg_fetch_array($rs,$i);$i++)
{
  $key = $row["cam"];
  if ($cameras[$key]["network"] != $network){ continue; }

  echo "<Placemark>
    <name>". $cameras[$key]["name"] ."</name>
    <description>
<![CDATA[
  <p><img src=\"http://mesonet.agron.iastate.edu/data/camera/stills/$key.jpg\" /></p>
        ]]>
    </description>
    <styleUrl>#iemstyle</styleUrl>
    <Point>
       <coordinates>". $cameras[$key]["lon"] .",". $cameras[$key]["lat"] .",0</coordinates>
    </Point>
</Placemark>";
}
echo "</Document></kml>";
?>
