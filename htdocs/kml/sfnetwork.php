<?php
/* Sucks to render a KML */
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
$connect = iemdb("access");

/* Now we fetch warning and perhaps polygon */
$query2 = "SELECT *, askml(geom) as kml
           from current
           WHERE network = 'KCCI' and valid > (now() - '30 minutes'::interval)";

$result = pg_exec($connect, $query2);

header("Content-Type:", "application/vnd.google-earth.kml+xml");
echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<kml xmlns=\"http://earth.google.com/kml/2.2\">
 <Document>
   <NetworkLink>
     <name>SchoolNet8 Currents</name>
     <Link id=\"ID\">
       <href>http://mesonet.agron.iastate.edu/kml/kcci.php</href>
       <refreshInterval>60</refreshInterval>
       <refreshMode>onInterval</refreshMode>
     </Link>
   </NetworkLink>
   <Style id=\"iemstyle\">
     <BalloonStyle>
      <bgColor>ffffffbb</bgColor>
    </BalloonStyle>
  </Style>";
for ($i=0;$row=@pg_fetch_array($result,$i);$i++)
{
  echo "<Placemark>
    <description>
        <![CDATA[
  <p><font color=\"red\"><i>Location:</i></font> ". $row["tmpf"] ." ". $row["dwpf"] ." 
   </p>
        ]]>
    </description>
    <styleUrl>#iemstyle</styleUrl>
    <name>". $row["tmpf"] ."</name>\n";
echo $row["kml"];
echo "</Placemark>";
}
echo "
 </Document>
</kml>";

?>
