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
	return sprintf("<th>%s:</th>
  		<td><input type=\"text\" name=\"%s\" size=\"%s\" value=\"%s\"></td>",
  		$label, $varname, $inputwidth, get_field($varname));
}
function tdyn($label, $varname){
	return sprintf("<th>%s</th><td><input type=\"radio\" name=\"%s\" value=\"yes\">Yes <input type=\"radio\" name=\"%s\" value=\"no\">No</td>",
			$label, $varname, $varname);
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
    <script src="http://code.jquery.com/jquery-1.8.2.js"></script>
    <script src="http://code.jquery.com/ui/1.9.1/jquery-ui.js"></script>
  
 
 
<script type="text/javascript">
var clientId = '828718626869-s70grf0hkkfhujtf9u53138n6e5vdvc9.apps.googleusercontent.com';
var apiKey = 'AIzaSyBUkRDnhdnp-AuEgLHtSsn6hK0QHuYJ3m0';
var scopes = 'https://sites.google.com/feeds/ https://spreadsheets.google.com/feeds/ https://docs.google.com/feeds/ https://docs.googleusercontent.com/';
var service;
var access_token;
var currentEntry = [null, null, null];
var spreadsheetDocs = [null, null, null];
b = 'https://spreadsheets.google.com/feeds/list/0AqZGw0coobCxdG1HUFk5YXI3TzRlT1FfV0kzWXFEVVE';
var spreadkeys = [b+'/1/private/full', b+'/2/private/full', b+'/3/private/full'];
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
</head>
<body>

<img src="DataCollectionSheet_files/image001.jpg">
<h3>Data Collection Sheet</h3>

<form name='authform'>
<div id="needtoauthenticate">
To use this interface, you need to be authenticated to google.  A popup should
appear shortly to start that process...
</div>
<div id="authenticated" style="display: none;">
You are authenticated to Google and can use this interface!
</div>
</form>

<form name="blah">
Previously entered Farmer Surveys: 
<select name="farmercode" id='farmerselector' 
	onChange="javascript: setFarmer(this.options[this.selectedIndex].value);">
	<option value='invalid'>-- SELECT FROM LIST --</option>
</select>
</form>

<form method="POST" name="theform" id="theform">

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
<?php echo tdgen("Total Acres Owned", "ta_owned", 6); ?>
<?php echo tdgen("Acres Rented", "ta_rented", 6); ?>
</tr>
</table>
<table>
<tr>
<?php echo tdgen("Type of operation (sole proprietor/family/etc.)", "op_type"); ?>
</tr>
</table>

<p><strong>Field location details (Sufficient information for locating on a plat map or Google Earth, e.g. address, Township, Range):</strong>
<textarea name="field_details" rows="4" cols="72"></textarea>

<table>
<tr>
<?php echo tdyn("Farm has livestock:", "livestock"); ?>
<?php echo tdyn("Manure import from other farms:", "inport_manure"); ?>
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
		<?php echo tdgen("Other", "availability_other", 10); ?>
		</tr>
</table>

<p>
<table><tr>
<?php echo tdgen("Total # of fields", "total_fields", 10); ?>
<?php echo tdgen("Area of field 1 (acres)", "field1_acres", 10); ?>
<?php echo tdgen("Area of field 2 (acres)", "field2_acres", 10); ?>
</tr></table>

<p><strong>Livestock Information</strong>

<table>
<?php for($i=1;$i<4;$i++){ 
 echo "<tr>";
 echo tdgen("Type of livestock $i", "livestock${i}_type", 30); 
 echo tdgen("Head Count", "livestock${i}_count", 5); 
 echo tdgen("% feed produced on farm", "livestock${i}_feedonfarm", 4);
 echo "</tr>";
} ?> 
<tr>
<?php echo tdgen("Acres in pasture/hay", "pasturehay_acres", 10); ?>
</tr>
</table>

<div id="field-tabs">
    <ul>
        <li><a href="#tabs-1">Field One</a></li>
        <li><a href="#tabs-2">Field Two</a></li>
    </ul>

<?php for($field=1;$field<3;$field++){
    echo "<div id='tabs-${field}' style='background: url(DataCollectionSheet_files/field${field}.png) repeat-y;'>";
	echo "<div style='margin-left: 50px;'>
   <table><tr>". tdgen("Unique Name", "field${field}_name") ."</tr></table>
		";
  echo "<p>Cropping system for this field ". radio("field${field}_system", Array(
		"single"=> "Single crop per rotation year",
		"multi"=> "Multiple/Double/Cover crops"));
  echo "<table><tr><th>Field is</th><td>". radio("field${field}_tile", Array(
		"tiled"=> "Tiled",
		"not_tiled"=> "Not tiled")) ."</td>";
  echo "<th>Field is<th><td>". radio("field${field}_owned", Array(
		"owned"=> "Owned",
		"rented"=> "Rented")) ."</td>";
  echo "</tr></table>";
  
  echo "<table><tr>";
  echo tdgen("Soil type", "field${field}_soiltype", 30);
  echo tdgen("Soil test P", "field${field}_soiltest_p", 10);
  echo tdgen("Soil test type", "field${field}_soiltest_t", 20);
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
    echo tdgen("Crop Type", "field${field}_rotation${rotation}_croptype", 30);
    echo tdgen("Year", "field${field}_rotation${rotation}_year", 6);
    echo "</tr></table>";
		
	echo "<table><tr>";
	echo tdgen("Yield (per acre)", "field${field}_rotation${rotation}_yield", 10);
	echo tdyn("Irrigated", "field${field}_rotation${rotation}_irrigated");
	echo "<th>Harvest:</th><td>". radio("field${field}_rotation${rotation}_harvest", Array(
			"grain_only"=> "Grain only",
			"grain_and_res"=> "Grain and residue")) ."</td>";
	echo "</tr></table>";
	
	echo "<table><tr>";
	echo tdgen("Percent residue removed (%)", "field${field}_rotation${rotation}_resremoved", 5);
	echo tdyn("Shred cornstalks before tillage", "field${field}_rotation${rotation}_shredstalks");
	echo "</tr></table>";
	
	echo "<table><tr>";
	echo tdgen("Residue removal: (e.g. bale)", "field${field}_rotation${rotation}_resremovalmethod", 30);
	echo "</tr></table>";
	
	echo "<table>";
	for ($tillage=1;$tillage<7;$tillage++){
      echo "<tr>";
      $s = "field${field}_rotation${rotation}_tillage${tillage}";
      echo tdgen("Tillage equipment", "${s}_equip", 30);
      echo tdgen("Width", "${s}_width", 5);
      echo tdgen("Date", "${s}_date", 10);
      echo "</tr>";
	} // End of tillage
	echo "</table>";
	
	echo "<table><tr>";
	echo tdgen("Seeding rate (per acre)", "field${field}_rotation${rotation}_seedrate", 10);
	echo "<th>Units:</th><td>". radio("field${field}_rotation${rotation}_seedunits", Array(
			"seeds_per_acre"=> "seeds per acre",
			"lbs_per_acre"=> "lbs. per acre")) ."</td>";
	echo "</tr></table>";
	
	echo "<table><tr>";
	echo tdgen("Relative maturity", "field${field}_rotation${rotation}_maturity");
	echo "</tr></table>";
	
	echo "<table><tr>";
	echo tdgen("Planting equipment", "field${field}_rotation${rotation}_plantequip", 30);
	echo tdgen("Date", "field${field}_rotation${rotation}_plantdate", 10);
	echo "</tr><tr>";
	echo tdgen("Harvest equipment", "field${field}_rotation${rotation}_harvestequip", 30);
	echo tdgen("Date", "field${field}_rotation${rotation}_harvestdate", 10);	
	echo "</tr></table>";
	
	echo "<table>";
	for($weed=1;$weed<5;$weed++){
		$s = "field${field}_rotation${rotation}_weed${weed}";
		echo "<tr>";
		echo tdgen("Weed Control #${weed}", "${s}_control", 20);
		echo tdgen("Rate", "${s}_rate", 10);
		echo tdgen("# of passes", "${s}_passes", 4);
		echo tdgen("Date", "${s}_date", 10);
		echo "</tr>";
	} // End of weed
	echo "</table>";
	
	echo "<table>";
	for($fert=1;$fert<5;$fert++){
		$s = "field${field}_rotation${rotation}_fert${fert}";
		echo "<tr>";
		echo tdgen("Fertilizer #${fert}", "${s}_fert", 20);
		echo tdgen("Amount (lbs/acre)", "${s}_amount", 5);
		echo tdgen("Applicator type", "${s}_apptype", 15);
		echo tdgen("Date", "${s}_date", 5);
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
	echo "<div style='margin-left: 25px;'>";
  	echo "<table><tr>";
  	echo tdgen("Cover Crop Type", "field${field}_cover${cover}_type",30);
  	echo tdgen("Year", "field${field}_cover${cover}_year", 6);
  	echo "</tr></table>";
  
  	echo "<table><tr>";
  	echo tdgen("Seeding rate (per acre)", "field${field}_cover${cover}_seedrate", 10);
  	echo "<th>Units:</th><td>". radio("field${field}_cover${cover}_seedunits", Array(
  			"seeds_per_acre"=> "seeds per acre",
  			"lbs_per_acre"=> "lbs. per acre")) ."</td>";
    echo "</tr><tr>";
	echo tdgen("Planting equipment", "field${field}_cover${cover}_plantequip", 15);	
	echo tdgen("Date", "field${field}_cover${cover}_plantdate", 10);	
	echo "</tr><tr>";
	echo tdgen("Termination practice (e.g., herbicide)", "field${field}_cover${cover}_termination", 30);
	echo tdgen("Date", "field${field}_cover${cover}_termdate", 10);
	echo "</tr><tr>";
	echo tdgen("Yield (if applicable)", "field${field}_cover${cover}_yield", 10);
	echo "</tr></table>";
  	echo "</div></div>";
  } // End of cover
  echo "</div></div></div>";
} // End of field loop 

echo "</div>";

$conservation = Array(
"grassed_waterways" => "Grassed waterways",
"contour_buffer_strips" => "Contour buffer strips",
"filter_strips" => "Filter strips along waterways and/or field borders",
"windbreaks" => "Windbreaks and shelterbelts",
"terraces" => "Terraces",
"drainage_structures" => "Drainage/runoff treatment structures (e.g., nutrient removal wetlands, bioreactors)",
"conversion" => "Whole portions of cropland converted to grass/trees",
"cover_crops" => "Cover crops",
"extended_rotations" => "Extended rotations/diversified with other grains/forage",
"reduced_tillage" => "Reduced tillage (i.e. strip, ridge)",
"no_till" => "No-till",
"nutrient" => "Nutrient management (identify practices)", 
"canopy_sensors" => "Canopy sensors for nitrogen deficiency",
"ipm" => "IPM (identify practices)", 
"control_structures" => "Use of control structures to drain and store water depending on crop needs and soil conditions (drainage water management, not just tile)",
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
	<td><input type='text' name='field1_conserv_${k}'></td>
	<td><input type='text' name='field2_conserv_${k}'></td>
	<td><input type='text' name='fieldOther_conserv_${k}'></td>
	</tr>", $v);
} // End of conservation
echo "<tr><th>Other</th>";
echo "<td><input type='text' name='field1_other_type'></td>";
echo "<td><input type='text' name='field2_other_type'></td>";
echo "<td><input type='text' name='fieldOther_other_type'></td>";
echo "</tr>";

echo "<tr><th>Other</th>";
echo "<td><input type='text' name='field1_other2_type'></td>";
echo "<td><input type='text' name='field2_other2_type'></td>";
echo "<td><input type='text' name='fieldOther_other2_type'></td>";
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

<p><input type="button" value="Save as New Entry" onclick="addNewEntry();" />
<input type="button" value="Save as Edit to Previous Entry" onclick="updateRow();" />

</form>

</body>

</html>
