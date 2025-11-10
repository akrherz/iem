<?php
require_once "../../config/settings.inc.php";
require_once "../../include/database.inc.php";
require_once "../../include/network.php";
require_once "../../include/forms.php";

// Get network parameter with validation
$network = get_str404("network", "IA_ASOS", 20);

header("Content-Type: application/vnd.google-earth.kml+xml");
echo <<<EOM
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
 <Document>
   <name>{$network} Network Stations</name>
   <description>IEM Network Station Locations for {$network}</description>
   <Style id="iemstyle">
     <IconStyle>
      <scale>0.8</scale>
      <Icon>
        <href>https://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href>
      </Icon>
     </IconStyle>
     <BalloonStyle>
      <bgColor>ffffffff</bgColor>
    </BalloonStyle>
  </Style>
EOM;

$nt = new NetworkTable($network);

foreach ($nt->table as $sid => $data) {
    // Properly escape XML special characters
    $name = htmlspecialchars($data["name"], ENT_XML1 | ENT_COMPAT, 'UTF-8');
    $sid_safe = htmlspecialchars($sid, ENT_XML1 | ENT_COMPAT, 'UTF-8');

    // Build description with available station information
    $description = "<![CDATA[\n";
    $description .= "<h3>{$name}</h3>\n";
    $description .= "<table>\n";
    $description .= "<tr><th>Station ID:</th><td>{$sid_safe}</td></tr>\n";
    if (!empty($data["elevation"])) {
        $description .= "<tr><th>Elevation:</th><td>" . round($data["elevation"], 1) . " m</td></tr>\n";
    }
    if (!empty($data["county"])) {
        $description .= "<tr><th>County:</th><td>" . htmlspecialchars($data["county"], ENT_XML1) . "</td></tr>\n";
    }
    if (!empty($data["climate_site"])) {
        $description .= "<tr><th>Climate Site:</th><td>" . htmlspecialchars($data["climate_site"], ENT_XML1) . "</td></tr>\n";
    }
    if (isset($data["archive_begin"]) && $data["archive_begin"] instanceof DateTime) {
        $description .= "<tr><th>Archive Begin:</th><td>" . $data["archive_begin"]->format('Y-m-d') . "</td></tr>\n";
    }
    $description .= "<tr><th>More Info:</th><td><a href=\"{$EXTERNAL_BASEURL}/sites/site.php?station={$sid_safe}&amp;network={$network}\">View Station Page</a></td></tr>\n";
    $description .= "</table>\n";
    $description .= "]]>";

    echo "<Placemark>\n";
    echo "  <name>{$name}</name>\n";
    echo "  <description>\n{$description}\n  </description>\n";
    echo "  <ExtendedData>\n";
    echo "    <Data name=\"sid\"><value>{$sid_safe}</value></Data>\n";
    echo "    <Data name=\"network\"><value>{$network}</value></Data>\n";
    if (!empty($data["elevation"])) {
        echo "    <Data name=\"elevation\"><value>" . $data["elevation"] . "</value></Data>\n";
    }
    echo "  </ExtendedData>\n";
    echo "  <styleUrl>#iemstyle</styleUrl>\n";
    echo "  <Point>\n";
    echo "    <coordinates>{$data["lon"]},{$data["lat"]},0</coordinates>\n";
    echo "  </Point>\n";
    echo "</Placemark>\n";
}
echo "</Document></kml>";
