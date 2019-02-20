<?php 
/**
 * Produce a map of SHEF values
 */
require_once "../../config/settings.inc.php";
define("IEM_APPID", 119);
require_once "../../include/myview.php";
$t = new MyView();
$t->title = "SHEF Physical Code Map";
$t->thispage = "networks-dcp";
$OL = '4.6.4';
$t->headextra = <<<EOF
<link rel="stylesheet" href="/vendor/openlayers/{$OL}/ol.css" type="text/css">
<link rel="stylesheet" href="/vendor/jquery-ui/1.11.4/jquery-ui.min.css" />
<link type="text/css" href="/vendor/openlayers/{$OL}/ol3-layerswitcher.css" rel="stylesheet" />
<style>
.map {
	height: 75%;
	width: 100%;
	background-color: #D2B48C;
}
.popover {
		width: 300px;
		}
</style>
EOF;
$t->jsextra = <<<EOF
<script src="/vendor/openlayers/{$OL}/ol.js" type="text/javascript"></script>
<script src="/vendor/jquery-ui/1.11.4/jquery-ui.js"></script>
<script src='/vendor/openlayers/{$OL}/ol3-layerswitcher.js'></script>
<script src='map.js'></script>
EOF;

$t->content = <<<EOF

<div id="popover-content" style="display: none">
  <!-- Hidden div with the popover content -->
  <p>This is the popover content</p>
</div>

<div class="breadcrumb">
		<li><a href="/DCP/">DCP/HADS Mainpage</a></li>
		<li class="active">Map of SHEF Reports</li>
		</div>
		
<div class="row">
<div class="col-md-12">
		
<div class="pull-right">
<i class="fa fa-text-size"></i>
<button id="fminus" class="btn btn-default"><i class="fa fa-minus"></i></button>
<button id="fplus" class="btn btn-default"><i class="fa fa-plus"></i></button>
</div>

<p>The IEM processes the raw SHEF encoded data into its raw components which
include the physical code and time duration.  This tool presents a simple map
of the last parsed value for a given physical code and duration.  The within days
limits the map to only show stations that have reported the value within the
given number of days.  This is a work-in-progress here and <a href="/info/contacts.php">your feedback</a> would
be wonderful.</p>

		<form name='bah'><p><strong>Select Physical Code:</strong> 
<select onChange="javascript: updateMap();" id="pe">
<option value="AD">AD</option>
<option value="AF">AF</option>
<option value="AM">AM</option>
<option value="BA">BA</option>
<option value="BD">BD</option>
<option value="BO">BO</option>
<option value="BP">BP</option>
<option value="BQ">BQ</option>
<option value="CA">CA</option>
<option value="CB">CB</option>
<option value="CC">CC</option>
<option value="CD">CD</option>
<option value="CE">CE</option>
<option value="CG">CG</option>
<option value="CI">CI</option>
<option value="CP">CP</option>
<option value="CR">CR</option>
<option value="EP">EP Pan Evaporation</option>
<option value="ET">ET</option>
<option value="EV">EV</option>
<option value="FT">FT</option>
<option value="GC">GC</option>
<option value="GD">GD Frost Depth</option>
<option value="GL">GL</option>
<option value="GP">GP</option>
<option value="GT">GT</option>
<option value="GW">GW</option>
<option value="HA">HA</option>
<option value="HB">HB</option>
<option value="HC">HC</option>
<option value="HF">HF</option>
<option value="HG">HG</option>
<option value="HH">HH</option>
<option value="HI">HI</option>
<option value="HJ">HJ</option>
<option value="HK">HK</option>
<option value="HL">HL</option>
<option value="HM">HM</option>
<option value="HP">HP</option>
<option value="HQ">HQ</option>
<option value="HR">HR</option>
<option value="HS">HS</option>
<option value="HT">HT</option>
<option value="HU">HU</option>
<option value="HV">HV</option>
<option value="HW">HW</option>
<option value="HZ">HZ</option>
<option value="IC">IC</option>
<option value="IE">IE</option>
<option value="IR">IR</option>
<option value="IT">IT</option>
<option value="LA">LA</option>
<option value="LC">LC</option>
<option value="LS">LS</option>
<option value="MI">MI</option>
<option value="MM">MM</option>
<option value="MS">MS</option>
<option value="MT">MT</option>
<option value="MV">MV</option>
<option value="MW">MW</option>
<option value="NG">NG</option>
<option value="NN">NN</option>
<option value="NO">NO</option>
<option value="NS">NS</option>
<option value="PA">PA</option>
<option value="PC">PC</option>
<option value="PE">PE</option>
<option value="PL">PL</option>
<option value="PM">PM</option>
<option value="PP">PP</option>
<option value="PR">PR</option>
<option value="PT">PT</option>
<option value="QA">QA</option>
<option value="QB">QB</option>
<option value="QC">QC</option>
<option value="QD">QD</option>
<option value="QE">QE</option>
<option value="QF">QF</option>
<option value="QG">QG</option>
<option value="QI">QI</option>
<option value="QM">QM</option>
<option value="QR">QR</option>
<option value="QS">QS</option>
<option value="QT">QT</option>
<option value="QU">QU</option>
<option value="RA">RA</option>
<option value="RI">RI</option>
<option value="RN">RN</option>
<option value="RP">RP</option>
<option value="RT">RT</option>
<option value="RW">RW</option>
<option value="SA">SA</option>
<option value="SD">SD</option>
<option value="SE">SE</option>
<option value="SF">SF</option>
<option value="SI">SI</option>
<option value="SM">SM</option>
<option value="SP">SP</option>
<option value="SR">SR</option>
<option value="SS">SS</option>
<option value="SW">SW Snow, water equivalent</option>
<option value="TA">TA</option>
<option value="TB">TB</option>
<option value="TD">TD</option>
<option value="TM">TM</option>
<option value="TP">TP</option>
<option value="TR">TR</option>
<option value="TS">TS</option>
<option value="TV">TV</option>
<option value="TW">TW</option>
<option value="TZ">TZ</option>
<option value="UC">UC</option>
<option value="UD">UD</option>
<option value="UE">UE</option>
<option value="UG">UG</option>
<option value="UL">UL</option>
<option value="UP">UP</option>
<option value="UQ">UQ</option>
<option value="UR">UR</option>
<option value="US">US</option>
<option value="VB">VB</option>
<option value="VE">VE</option>
<option value="VJ">VJ</option>
<option value="VT">VT</option>
<option value="VU">VU</option>
<option value="VW">VW</option>
<option value="WC">WC</option>
<option value="WD">WD</option>
<option value="WG">WG</option>
<option value="WO">WO</option>
<option value="WP">WP</option>
<option value="WS">WS</option>
<option value="WT">WT</option>
<option value="WV">WV</option>
<option value="WX">WX</option>
<option value="XC">XC</option>
<option value="XG">XG</option>
<option value="XP">XP</option>
<option value="XR">XR</option>
<option value="XV">XV</option>
<option value="XW">XW</option>
<option value="YI">YI</option>
<option value="YP">YP</option>
<option value="YS">YS</option>
<option value="YV">YV</option>
</select>	
		
&nbsp; &nbsp; <strong>Duration:</strong>
<select onChange="javascript: updateMap();" id="duration">
	<option value="D">D Day (24 Hour)</option>
	<option value="I">I Instantaneous</option>
	<option value="Q">Q 6 Hour</option>
</select>	

&nbsp; <strong>Within # of Days:</strong> <input id="days" onChange="javascript: updateMap();" type="text" size="5" name="days" value="2">

</form>
</div></div>

		
<div id="map" class="map">
<div id="popup"></div>
</div>

EOF;

$t->render('full.phtml');
?>