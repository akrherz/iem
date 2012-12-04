<?php
if (isset($_REQUEST["farmcode"])){
	
}

function get_field($varname){
	global $fields;
	$value = "";
	if (array_key_exists( $varname, $_REQUEST)){
		$value = $_REQUEST[$varname];
	}
	return $value;
}

function tdgen($label, $varname, $inputwidth=40){
	return sprintf("<th style=\"text-align: right\">%s:</th>
  		<td><input type=\"text\" name=\"%s\" size=\"%s\" value=\"%s\"></td>",
  		$label, $varname, $inputwidth, get_field($varname));
}
function tdyn($label, $varname){
	return sprintf("<th>%s</th><td><input type=\"radio\" name=\"%s\" value=\"yes\">Yes <input type=\"radio\" name=\"%s\" value=\"no\">No</td>",
			$label, $varname, $varname);
}
function tdyn2( $varname ){
	return sprintf("<td><input type=\"radio\" name=\"%s\" value=\"yes\">Yes <input type=\"radio\" name=\"%s\" value=\"no\">No</td>",
			$varname, $varname);
}
function radio($varname, $vals){
	$s = "";
	while( list($k,$v) = each($vals)){
		$s .= sprintf(" &nbsp; <input type='radio' name='%s' value='%s'>%s</input> &nbsp; ",
				$varname, $k, $v);
	}
	return $s;
}
?>
<html xmlns:v="urn:schemas-microsoft-com:vml"
xmlns:o="urn:schemas-microsoft-com:office:office"
xmlns:w="urn:schemas-microsoft-com:office:word"
xmlns:dt="uuid:C2F41010-65B3-11d1-A29F-00AA00C14882"
xmlns:m="http://schemas.microsoft.com/office/2004/12/omml"
xmlns="http://www.w3.org/TR/REC-html40">

<head>
 <title>CSCAP Data Collection Sheet Interface</title>
    <link rel="stylesheet" href="http://code.jquery.com/ui/1.9.1/themes/base/jquery-ui.css" />
    <link rel='stylesheet' media='print' href='dcs-print.css' />
    <script src="http://code.jquery.com/jquery-1.8.2.js"></script>
    <script src="http://code.jquery.com/ui/1.9.1/jquery-ui.js"></script>
  
 
 
<script type="text/javascript">
var clientId = '828718626869-s70grf0hkkfhujtf9u53138n6e5vdvc9.apps.googleusercontent.com';
var apiKey = 'AIzaSyBUkRDnhdnp-AuEgLHtSsn6hK0QHuYJ3m0';
var scopes = 'https://sites.google.com/feeds/ https://spreadsheets.google.com/feeds/ https://docs.google.com/feeds/ https://docs.googleusercontent.com/';
var service;
var access_token;
var currentEntry = [null, null, null, null, null, null, null];
var spreadsheetDocs = [null, null, null, null, null, null, null];
b = 'https://spreadsheets.google.com/feeds/list/0AqZGw0coobCxdG1HUFk5YXI3TzRlT1FfV0kzWXFEVVE';
var spreadkeys = [b+'/1/private/full', b+'/2/private/full', b+'/3/private/full',
                  b+'/4/private/full', b+'/5/private/full', b+'/6/private/full',
                  b+'/7/private/full'];
var editting = false;

$(function(){
	$( "#field-tabs" ).tabs();
	$( "#field1_tabs" ).tabs();
	$( "#field2_tabs" ).tabs();
	$( "#field1_ctabs" ).tabs();
	$( "#field2_ctabs" ).tabs();

});

</script>
<script src="oauth2.js"></script>
<script src="https://apis.google.com/js/client.js?onload=handleClientLoad"></script>
<style type="text/css">
.ui-widget{
  font-size: 1em !important;
  font: inherit;
}
</style>
</head>
<body>

<table><tr><td>
<img src="http://sustainablecorn.org/img/sustainablecorn-rgb-01.png" />
</td><td>
<h3>Data Collection Sheet</h3>

<form name='authform'>
<div id="needtoauthenticate" style="border: 3px solid #f00" >
To use this interface, you need to be authenticated to google.  
<input type="button" value="Click to Authenticate to Google" 
onclick="handleAuthClick()" />
</div>
<div id="authenticated" style="display: none;">
You are authenticated to Google and can use this interface!
</div>
</form>
</td></tr></table>

<form name="blah">
Previously entered Farmer Surveys: 
<select name="farmercode" id='farmerselector' 
	onChange="javascript: setFarmer(this.options[this.selectedIndex].value);">
	<option value='invalid'>-- SELECT FROM LIST --</option>
</select>

<input type="button" value="Refresh List of Surveys" onclick="getSpreadsheets();"/>
<input type="button" value="Print Form" onclick="print();" />
</form>

<form method="POST" name="theform" id="theform">
<input type='hidden' name='updated' />
<div style="border:1px #000 solid;">
<table>
<tr>
<?php echo tdgen("Farmer Code", "farmercode", 10); ?>
<?php echo tdgen("Interviewer", "interviewer", 40); ?>
<?php echo tdgen("Date", "date", 12); ?>
</tr>
</table>
</div>
<h3>Location/General</h3>

<table>
<tr>
<?php echo tdgen("State", "state", 20); ?>
<?php echo tdgen("County", "county", 30); ?>
</tr>
<tr>
<?php echo tdgen("Total Acres Owned", "taowned", 6); ?>
<?php echo tdgen("Acres Rented", "tarented", 6); ?>
</tr>
</table>
<table>
<tr>
<?php echo tdgen("Type of operation (sole proprietor/family/etc.)", "optype"); ?>
</tr>
</table>

<p><strong>Field location details (Sufficient information for locating on a plat map or Google Earth, e.g. address, Township, Range):</strong>
<textarea name="fielddetails" rows="4" cols="72"></textarea>

<table>
<tr>
<?php echo tdyn("Farm has livestock:", "livestock"); ?>
<?php echo tdyn("Manure import from other farms:", "importmanure"); ?>
</tr>
</table>

<p><strong>Farm labor availability: (3,000 hours = 1 person/year)</strong>
<br />
<table><tr><td>
<?php echo radio("availability", Array(
		"3000"=> "3,000",
		"4500"=> "4,500",
		"6000"=> "6,000",
		"other"=>"")); ?>
		</td>
		<?php echo tdgen("Other", "availabilityother", 10); ?>
		</tr>
</table>

<p>
<table><tr>
<?php echo tdgen("Total # of fields", "totalfields", 10); ?>
<?php echo tdgen("Area of field 1 (acres)", "field1acres", 10); ?>
<?php echo tdgen("Area of field 2 (acres)", "field2acres", 10); ?>
</tr></table>

<p><strong>Livestock Information</strong>

<table>
<?php for($i=1;$i<4;$i++){ 
 echo "<tr>";
 echo tdgen("Type of livestock $i", "livestock${i}type", 30); 
 echo tdgen("Head Count", "livestock${i}count", 5); 
 echo tdgen("% feed produced on farm", "livestock${i}feedonfarm", 4);
 echo "</tr>";
} ?> 
<tr>
<?php echo tdgen("Acres in pasture/hay", "pasturehayacres", 10); ?>
</tr>
</table>

<div id="field-tabs">
    <ul>
        <li><a href="#tabs-1">Field One</a></li>
        <li><a href="#tabs-2">Field Two</a></li>
    </ul>

<?php for($field=1;$field<3;$field++){
	echo "<div class='phidden' style='display: none;'><hr /><h3>Field $field</h3></div>\n";
    echo "<div id='tabs-${field}' style='background: url(DataCollectionSheet_files/field${field}.png) repeat-y;'>";
	echo "<div style='margin-left: 50px;'>
   <table><tr>". tdgen("Unique Name", "field${field}name") ."
  			  ". tdgen("Field Number", "field${field}id", 14) ."
  				</tr></table>
		";
  echo "<p><strong>Cropping system for this field:</strong> ". radio("field${field}system", Array(
		"single"=> "Single crop per rotation year",
		"multi"=> "Multiple/Double/Cover crops"));
  echo "<table><tr><th>Field is: </th><td>". radio("field${field}tile", Array(
		"tiled"=> "Tiled",
		"not_tiled"=> "Not tiled")) ."</td>";
  echo "<th>Field is: <th><td>". radio("field${field}owned", Array(
		"owned"=> "Owned",
		"rented"=> "Rented")) ."</td>";
  echo "</tr></table>";
  
  echo "<table><tr>";
  echo tdgen("Soil type", "field${field}soiltype", 30);
  echo tdgen("Soil test P", "field${field}soiltestp", 10);
  echo tdgen("Soil test type", "field${field}soiltestt", 20);
  echo "</tr></table>";
  
  echo "<div id=\"field${field}_tabs\">
  <ul>
  <li><a href=\"#field${field}_tabs1\">Rotation One</a></li>
  <li><a href=\"#field${field}_tabs2\">Rotation Two</a></li>
  <li><a href=\"#field${field}_tabs3\">Rotation Three</a></li>
  </ul>";
  
  for ($rotation=1;$rotation<4;$rotation++){
    echo "<div id='field${field}_tabs${rotation}' style='background: url(DataCollectionSheet_files/rotation${rotation}.png) repeat-y;'>";
    echo "<div style='margin-left: 25px;'>";
    echo "<table><tr>";
    echo tdgen("Crop Type", "f${field}r${rotation}croptype", 30);
    echo tdgen("Year", "f${field}r${rotation}year", 6);
    echo "</tr></table>";
		
	echo "<table><tr>";
	echo tdgen("Yield (per acre)", "f${field}r${rotation}yield", 10);
	echo tdyn("Irrigated", "f${field}r${rotation}irrigated");
	echo "<th>Harvest:</th><td>". radio("f${field}r${rotation}harvest", Array(
			"grain_only"=> "Grain only",
			"grain_and_res"=> "Grain and residue")) ."</td>";
	echo "</tr></table>";
	
	echo "<table><tr>";
	echo tdgen("Percent residue removed (%)", "f${field}r${rotation}resremoved", 5);
	echo tdyn("Shred cornstalks before tillage", "f${field}r${rotation}shredstalks");
	echo "</tr></table>";
	
	echo "<table><tr>";
	echo tdgen("Residue removal: (e.g. bale)", "f${field}r${rotation}resremovalmethod", 30);
	echo "</tr></table>";
	
	echo "<table>";
	for ($tillage=1;$tillage<7;$tillage++){
      echo "<tr>";
      $s = "f${field}r${rotation}tillage${tillage}";
      echo tdgen("Tillage equipment", "${s}equip", 30);
      echo tdgen("Width", "${s}width", 5);
      echo tdgen("Date", "${s}date", 10);
      echo "</tr>";
	} // End of tillage
	echo "</table>";
	
	echo "<table><tr>";
	echo tdgen("Seeding rate (per acre)", "f${field}r${rotation}seedrate", 10);
	echo "<th>Units:</th><td>". radio("f${field}r${rotation}seedunits", Array(
			"seeds_per_acre"=> "seeds per acre",
			"lbs_per_acre"=> "lbs. per acre")) ."</td>";
	echo "</tr></table>";
	
	echo "<table><tr>";
	echo tdgen("Relative maturity", "f${field}r${rotation}maturity");
	echo "</tr></table>";
	
	echo "<table><tr>";
	echo tdgen("Planting equipment", "f${field}r${rotation}plantequip", 30);
	echo tdgen("Date", "f${field}r${rotation}plantdate", 10);
	echo "</tr><tr>";
	echo tdgen("Harvest equipment", "f${field}r${rotation}harvestequip", 30);
	echo tdgen("Date", "f${field}r${rotation}harvestdate", 10);	
	echo "</tr></table>";
	
	echo "<p style=\"font-size: 1.2em; color: #00f;\"><u>Weed Control</u></p>";
	echo "<table>";
	for($weed=1;$weed<7;$weed++){
		$s = "f${field}r${rotation}weed${weed}";
		echo "<tr>";
		echo tdgen("#${weed}", "${s}control", 20);
		echo tdgen("Rate", "${s}rate", 10);
		//echo tdgen("# of passes", "${s}passes", 4);
		echo tdgen("Date", "${s}date", 10);
		echo "</tr>";
	} // End of weed
	echo "</table>";
	
	echo "<p style=\"font-size: 1.2em; color: #00f;\"><u>Pest &amp; Disease Control</u></p>";
	echo "<table>";
	for($pest=1;$pest<7;$pest++){
		$s = "f${field}r${rotation}pest${pest}";
		echo "<tr>";
		echo tdgen("#${pest}", "${s}control", 20);
		echo tdgen("Rate", "${s}rate", 10);
		//echo tdgen("# of passes", "${s}passes", 4);
		echo tdgen("Date", "${s}date", 10);
		echo "</tr>";
	} // End of weed
	echo "</table>";
	
	echo "<p style=\"font-size: 1.2em; color: #00f;\"><u>Fertilizer</u></p>";
	echo "<table>";
	for($fert=1;$fert<7;$fert++){
		$s = "f${field}r${rotation}fert${fert}";
		echo "<tr>";
		echo tdgen("#${fert}", "${s}fert", 15);
		echo tdgen("Amount (lbs/acre)", "${s}amount", 5);
		echo tdgen("Applicator type", "${s}apptype", 10);
		echo tdgen("Date", "${s}date", 10);
		echo "</tr>";
	} // End of fert
	echo "</table>";
	echo "</div></div>";

  } // End of rotation
  echo "</div>";
  
  echo "<div id=\"field${field}_ctabs\">
  <ul>
  <li><a href=\"#field${field}_ctabs1\">Cover Crop One</a></li>
  <li><a href=\"#field${field}_ctabs2\">Cover Crop Two</a></li>
  <li><a href=\"#field${field}_ctabs3\">Cover Crop Three</a></li>
  </ul>";
  
  for ($cover=1;$cover<4;$cover++){
	echo "<div id='field${field}_ctabs${cover}' style='background: url(DataCollectionSheet_files/cover${cover}.png) repeat-y;'>";
	echo "<div style='margin: 25px;'>";
  	echo "<table><tr>";
  	echo tdgen("Cover Crop Type", "field${field}cover${cover}type",30);
  	echo tdgen("Year", "field${field}cover${cover}year", 6);
  	echo "</tr></table>";
  
  	echo "<table><tr>";
  	echo tdgen("Seeding rate (per acre)", "field${field}cover${cover}seedrate", 10);
  	echo "<th>Units:</th><td>". radio("field${field}cover${cover}seedunits", Array(
  			"seeds_per_acre"=> "seeds per acre",
  			"lbs_per_acre"=> "lbs. per acre")) ."</td>";
    echo "</tr><tr>";
	echo tdgen("Planting equipment", "field${field}cover${cover}plantequip", 15);	
	echo tdgen("Date", "field${field}cover${cover}plantdate", 10);	
	echo "</tr><tr>";
	echo tdgen("Termination practice (e.g., herbicide)", "field${field}cover${cover}termination", 30);
	echo tdgen("Date", "field${field}cover${cover}termdate", 10);
	echo "</tr><tr>";
	echo tdgen("Yield (if applicable)", "field${field}cover${cover}yield", 10);
	echo "</tr></table>";
  	echo "</div></div>";
  } // End of cover
  echo "</div></div></div>";
} // End of field loop 

echo "</div>";

$conservation = Array(
"grassedwaterways" => "Grassed waterways",
"contourbufferstrips" => "Contour buffer strips",
"filterstrips" => "Filter strips along waterways and/or field borders",
"windbreaks" => "Windbreaks and shelterbelts",
"terraces" => "Terraces",
"drainagestructures" => "Drainage/runoff treatment structures (e.g., nutrient removal wetlands, bioreactors)",
"conversion" => "Whole portions of cropland converted to grass/trees",
"covercrops" => "Cover crops",
"extendedrotations" => "Extended rotations/diversified with other grains/forage",
"reducedtillage" => "Reduced tillage (i.e. strip, ridge)",
"notill" => "No-till",
"nutrient" => "Nutrient management (identify practices)", 
"canopysensors" => "Canopy sensors for nitrogen deficiency",
"ipm" => "IPM (identify practices)", 
"controlstructures" => "Use of control structures to drain and store water depending on crop needs and soil conditions (drainage water management, not just tile)",
"precision" => "Precision agriculture (identify practices)" 
);

?>

<h3>Conservation Questions</h3>

<p>1. What conservation practices are you already implementing on these fields 
or on your entire farm (See list below)? Please include land that is set aside 
in CRP or other government programs.

<table cellpadding='2' cellspacing='0' border='1'>
<tr><th>Conservation Practices</th><td>Field 1</td><td>Field 2</td><td>On other land you farm</td></tr>
<?php 
$i = True;
while (list($k,$v) = each($conservation)){
 if ($i){ $color = '#FFFFFF'; $i = False; }
 else{ $color = '#EEEEEE'; $i = True; }
 
 if ($k == 'precision' || $k == 'ipm' || $k == 'nutrient'){
  }
  echo sprintf("<tr style='background: ${color}'><th>%s</th>
    %s %s %s
	</tr>", $v, tdyn2("field1conserv${k}"),tdyn2("field2conserv${k}"),
	tdyn2("fieldotherconserv${k}") );
} // End of conservation
echo "<tr><th>Other</th>";
echo "<td><input type='text' name='field1othertype'></td>";
echo "<td><input type='text' name='field2othertype'></td>";
echo "<td><input type='text' name='fieldotherothertype'></td>";
echo "</tr>";

echo "<tr style='background: #EEEEEE'><th>Other</th>";
echo "<td><input type='text' name='field1other2type'></td>";
echo "<td><input type='text' name='field2other2type'></td>";
echo "<td><input type='text' name='fieldotherother2type'></td>";
echo "</tr>";
echo "</table>";
?>

<p>2. Do you have any management challenges on these two fields, which might 
inspire you to consider new management strategies [identify conservation goals]? 
(e.g. drainage management, greater erosion control, pests/disease control, 
nitrogen deficiency, diversified income streams?
<br />
<textarea name='challenges' rows='6' cols='72'></textarea>

<p>3. Other Notes:<br />

<textarea name='notes' rows='6' cols='72'></textarea>

<p>You are presented with three options below.
<ul>
 <li><strong>Save as New Entry</strong>: This saves the data you entered above
  as a new entry in the database. </li>
 <li><strong>Save as Edit to Previous Entry</strong>: If you loaded a previously
 entered survey, this option will save this data overtop the old entry in the
 database.</li>
 <li><strong>Clear Form for New Entry</strong>: Clears all form values allowing
 for a new entry to be added.</li>
</ul>

<p>Please only click the button once and be patient, it may take 10-30 seconds 
to process!

<p><input type="button" value="Save as New Entry" onclick="addNewEntry();" />
<input type="button" value="Save as Edit to Previous Entry" onclick="updateRow();"/>
<input type="reset" value="Clear Form for New Entry" />

</form>

</body>

</html>
