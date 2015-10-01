<?php 
include("../../config/settings.inc.php");
define("IEM_APPID", 154);
include("../../include/myview.php");
$t = new MyView();

$t->jsextra = <<<EOF
<script type="text/javascript" src="https://extjs.cachefly.net/ext/gpl/5.1.0/build/ext-all.js"></script>
<script type="text/javascript" src="/ext/ux/ExcelGridPanel.js"></script>
<script type="text/javascript" src="search.js?v=12"></script>
EOF;
$t->headextra = <<<EOF
<script src="https://maps.googleapis.com/maps/api/js?sensor=false" type="text/javascript"></script>
<link rel="stylesheet" type="text/css" href="https://extjs.cachefly.net/ext/gpl/5.1.0/build/packages/ext-theme-neptune/build/resources/ext-theme-neptune-all.css"/>
		  <style>
  #map {
    width: 100%;
    height: 400px;
    float: left;
  }
		#warntable { float: right; }
		</style>
EOF;
$t->thispage ="severe-search";
$t->title = "NWS Warning Search by Point or County/Zone";

$t->content = <<<EOF
<p>This application allows you to search for National Weather Service Watch,
Warning, and Advisories.  There are currently two options:
<ul>
	<li><a href="#bypoint">1. Search for Storm Based Warnings by Point</a></li>
	<li><a href="#byugc">2. Search of Watch/Warning/Advisories by County/Zone</a></li>
</ul>

<div class="alert alert-info"><strong>Troubles downloading Excel File?</strong>
<br />It turns out that making an export to Excel option that works for all
	variants of Microsoft Office and web browsers is very difficult.  Here are
	some tips.
<ul>
	<li>When you "Export to Excel", you should get a file saved in your downloads
		folder with a .xml ending.</li>
	<li>When you double click this .xml file, Microsoft Windows may not know
		what to do with the file.  Try opening Excel first and then go to 
		File -&gt; Open to attempt to open the file.</li>
	<li>If that fails, attempt to right click the file and go to 'Open With'
		and then select Excel from the available options.</li>
</ul>
		</div>
		
<h3><a name="bypoint">1.</a> Search for Storm Based Warnings by Point</h3>

<br />The official warned area for some products the NWS issues is a polygon.
This section allows you to specify a point on the map below by dragging the 
marker to where you are interested in.  Once you stop dragging the marker, the
grid will update and provide a listing of storm based warnings found.  
<br clear="all" />
<div class="row">
		<div class="col-md-4"><div id="map"></div></div>
		<div class="col-md-8"><div id="warntable" style="width: 100%"></div></div>
</div>

<br clear="all" />
<h3><a name="byugc">2.</a> Search for NWS Watch/Warning/Advisories Products by County/Zone</h3>
<br />
<p>The NWS issues watch, warnings, and advisories (WWA) for counties/parishes.  For 
some products (like winter warnings), they issue for forecast zones.  
 In many parts of the country, these zones are exactly the 
 same as the counties/parishes.  When you get into regions with topography, 
 then zones will start to differ to the local counties.</p>

<p>This application allows you to search the IEM's archive of NWS WWA products.  
 Our archive is not complete, but there are no known holes since 12 November 2005. 
 This archive is of those products that contain VTEC codes, which are nearly all 
 WWAs that the NWS issues for. There are Severe Thunderstorm, Tornado, and 
 Flash Flood Warnings included in this archive for dates prior to 2005.  These  
 were retroactively assigned VTEC event identifiers by the IEM based on some
 hopefully intelligent logic.</p>
<br />
<div class="alert alert-warning">Please note: NWS forecast offices have 
changed over the years, this application may incorrectly label old warnings as coming from
an office that did not exist at the time.</div>
<br />

<div class="row">
		<div class="col-md-4"><div id="myform" style="width:100%"></div></div>
		<div class="col-md-8"><div id="mytable" style="width:100%"></div></div>
</div>
		
EOF;
$t->render('single.phtml');
?>
