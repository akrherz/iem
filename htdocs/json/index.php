<?php 
  include("../../config/settings.inc.php");
  $THISPAGE = "current-jsonp";
  $HEADEXTRA = "<style>
  .sect {
	border-top: 1px solid #ccc; 
	background: #EEFFCC; 
	border-bottom: 1px solid #ccc; 
	margin-left: 25px;
  		padding-left: 5px;
  		line-height: 1.3em;
  		margin-bottom: 10px;
  	}
  		</style>";
  $TITLE = "IEM | JSONP Web Services";
  include("$rootpath/include/header.php"); 
?>
<div style="width: 800px;">
<h3>IEM Provided JSON-P Webservices</h3>

<p>This page is an attempt to document the various JSON-P web services the
 IEM uses to drive its various applications.  These services are provided without
 warranty and may be disabled without warning if "bad things happen". We do
 try our best to keep them running, so please <a href="/info/contacts.php">Contact Us</a>
 if you have difficulties.
 
 <p>These services support <a href="http://en.wikipedia.org/wiki/JSONP">JSONP</a>,
 which is a technique that allows the deliver of data from a cross-domain origin.
 The technique involves placing or injecting &lt;script&gt; tags into your webpage
 and specifying a javascript function to callback.  For example,
 <br /><pre>
 &lt;script type="text/javascript"&gt;
  function gotData(data){
     console.log(data);
  }
 &lt;/script&gt;
 &lt;script type="text/javascript"
         src="http://mesonet.agron.iastate.edu/json/example.php?callback=gotData"&gt;
 
 </pre>
 
 <p>This &lt;script&gt; tag above that requests data from this server will return
 javascript that looks like:
 <br /><pre>
 gotData({"Name": "daryl", "Profession": "nerd", "Age": 99});
 </pre>

 <p>Okay, so you are all set for documentation on what services are available!
<?php 
$services = array();
$services[] = Array(
    "title" => "SHEF Station Variables",
	"url" => "/json/dcp_vars.php?station={station}",
    "desc" => "Provides SHEF variables provided by this station.",
	"vars" => Array(
		"station" => "National Weather Service Location Identifier (nwsli)",
	),
	"example" => Array(
		"{station}" => "AMWI4", 
	)
);

$services[] = Array(
		"title" => "Data Collection Network Details",
		"url" => "/json/network.php?network={network}",
		"desc" => "The IEM bunches observation stations into networks. This 
service provides metadata for sites within a network.  A listing of networks
can be found on <a href='/sites/locate.php'>this page.</a>",
		"vars" => Array(
				"network" => "IEM Network Identifier",
		),
		"example" => Array(
				"{network}" => "IA_ASOS",
		)
); 

$services[] = Array(
		"title" => "IEM Archived Data Products",
		"url" => "/json/products.php?",
		"desc" => "The IEM generates and archives a large number of products.
 This service provides some metadata details necessary to build programic URIs
 against this archive of data.  This service drives the <a href='/timemachine'>Timemachine</a>
 application.",
		"vars" => Array(
		),
		"example" => Array(
		)
);

$services[] = Array(
		"title" => "RIDGE Single Site Available NEXRADs",
		"url" => "/json/radar?operation=available&amp;lat={lat}&amp;lon={lon}&amp;start={start}",
		"desc" => "This service returns an estimate of which NEXRAD RADARs have
imagery available for the timestamp and latitude / longitude location you specify.",
		"vars" => Array(
			"lat" => "Point location latitude (degrees north)",
			"lon" => "Point location longitude (degrees east)",
			"start" => "ISO-8601 UTC Timestamp"
		),
		"example" => Array(
			"{lat}" => 41.99,
			"{lon}" => 93.50,
			"{start}" => "2012-12-01T00:00:00Z",
		)
);

$services[] = Array(
		"title" => "RIDGE Single Site Available Products for single NEXRAD",
		"url" => "/json/radar?operation=products&amp;radar={radar}&amp;start={start}",
		"desc" => "This service returns available NEXRAD level 3 products for
a given RADAR and date.",
		"vars" => Array(
				"radar" => "NEXRAD 3 character identifier",
				"start" => "ISO-8601 UTC Timestamp"
		),
		"example" => Array(
				"{radar}" => 'DMX',
				"{start}" => "2012-12-01T00:00:00Z",
		)
);

$services[] = Array(
		"title" => "RIDGE Single Site Available Volume Scan Times",
		"url" => "/json/radar?operation=list&amp;radar={radar}&amp;product={product}&amp;start={start}&amp;end={end}",
		"desc" => "This service returns NEXRAD volume scan times for a given 
RADAR, level 3 product, and start/end timestamp.",
		"vars" => Array(
				"radar" => "NEXRAD 3 character identifier",
				"product" => "Three character level 3 NEXRAD product identifier.",
				"start" => "ISO-8601 UTC Timestamp",
				"end" => "ISO-8601 UTC Timestamp"
		),
		"example" => Array(
				"{radar}" => 'DMX',
				"{product}" => 'N0Q',
				"{start}" => "2012-12-01T00:00:00Z",
				"{end}" => "2012-12-01T23:59:59Z",
		)
);

$services[] = Array(
		"title" => "NWS State UGC Codes",
		"url" => "/json/state_ugc.php?state={state}",
		"desc" => "This service returns metadata for UGC codes used by the
National Weather Service to issue warnings for in a given state.",
		"vars" => Array(
				"state" => "Two character state identifier",
		),
		"example" => Array(
				"{state}" => 'IA'
		)
);

$services[] = Array(
		"title" => "IEM Tracked Station Metadata Changes",
		"url" => "/json/stations.php?date={date}",
		"desc" => "This service returns metadata for any IEM tracked 
station locations with changed metadata since the given date.  This provides 
a programic mechanism to keep up with metadata updates done on a daily basis.",
		"vars" => Array(
				"date" => "Request changes since this date",
		),
		"example" => Array(
				"{date}" => date('Y-m-d')
		)
);

$services[] = Array(
		"title" => "IEM Webcam Availability",
		"url" => "/json/webcams.php?network={network}&amp;ts={ts}",
		"desc" => "This service returns metadata on available webcam imagery
for a given network that collects webcams and a UTC timestamp.",
		"vars" => Array(
				"network" => "IEM Webcam network (KCCI, KELO, KCRG, IDOT)",
				"ts" => "UTC Timestamp that you want images for",
		),
		"example" => Array(
				"{network}" => "KCCI",
				"{ts}" => "201212070600",
		)
);

 while (list($key, $ws) = each($services)){
    echo sprintf("<div class='sect'><strong>%s</strong>
	<br /><strong>URI:</strong> %s%s&amp;callback=gotData
	<br /><strong>Description:</strong> %s
	<br /><strong>Method GET Parameters:</strong>
	<br /><table border='1' cellspacing='0' cellpadding='3'>", 
		$ws["title"], ROOTURL, $ws["url"], $ws["desc"]);
 	while (list($key2, $vs) = each($ws['vars'])){
        echo sprintf("<tr><th>%s</th><td>%s</td></tr>", $key2, $vs);
    }
    echo "</table>";
    $url = $ws['url'];
    while (list($key2, $vs) = each($ws['example'])){
		$url = str_replace($key2, $vs, $url);
    }
    echo sprintf("<br /><a href=\"%s%s\">Example JSON</a>
     	&nbsp; <a href=\"%s%s&callback=gotData\">Example JSONP</a>", 
		ROOTURL, $url, ROOTURL, $url);
    echo "</div>\n";
}
 ?>
 
 <p>That is all for now. Enjoy!
 
 </div>
<?php include("$rootpath/include/footer.php"); ?>
