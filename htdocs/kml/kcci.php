<?php
header("Content-Type: application/vnd.google-earth.kml+xml");
echo <<<EOF
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://earth.google.com/kml/2.2">
<Folder>
   <name>SchoolNet8 Currents</name>
   <NetworkLink>
     <name>SchoolNet8 Webcams</name>
     <Link id="ID">
       <href>https://mesonet.agron.iastate.edu/kml/webcams.php?network=KCCI</href>
       <refreshInterval>600</refreshInterval>
       <refreshMode>onInterval</refreshMode>
     </Link>
   </NetworkLink>
</Folder>
</kml>
EOF;
?>
