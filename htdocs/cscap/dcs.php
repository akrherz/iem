<?php 
function tdgen($label, $varname){
  return sprintf("<th>%s</th><td><input type=\"text\" name=\"%s\"></td>",
  		$label, $varname);
}
function tdyn($label, $varname){
	return sprintf("<th>%s</th><td><input type=\"radio\" name=\"%s\" value=\"yes\">Yes <input type=\"radio\" name=\"%s\" value=\"no\">No</td>",
			$label, $varname, $varname);
}
function radio($varname, $vals){
	$s = "";
	while( list($k,$v) = each($vals)){
		$s .= sprintf("<input type='radio' name='%s' value='%s'>%s</input>",
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
  
 <script src="https://apis.google.com/js/client.js?onload=handleClientLoad"></script>
 <script src="https://www.google.com/jsapi?key=ABQIAAAArXt77YptylBNPFEy0AgJxBQV4szfgV8zGZZkur1B-B3W8b5AThTSlomZliOt8JQHJGH1m63sgDu1rg" type="text/javascript"></script>

<script type="text/javascript">
var clientId = '828718626869-s70grf0hkkfhujtf9u53138n6e5vdvc9.apps.googleusercontent.com';
var apiKey = 'AIzaSyBUkRDnhdnp-AuEgLHtSsn6hK0QHuYJ3m0';
var scopes = 'https://sites.google.com/feeds/ https://spreadsheets.google.com/feeds/ https://docs.google.com/feeds/ https://docs.googleusercontent.com/';

$(function(){
	$( "#field-tabs" ).tabs();
});

function handleClientLoad() {
	  gapi.client.setApiKey(apiKey);
	  window.setTimeout(checkAuth,1);
	}

	function checkAuth() {
	  gapi.auth.authorize({client_id: clientId, scope: scopes, immediate: true}, handleAuthResult);
	}

	function handleAuthResult(authResult) {
	  var authorizeButton = document.getElementById('authorize-button');
	  if (authResult && !authResult.error) {
	    authorizeButton.style.visibility = 'hidden';

	    gapi.client.load("drive", "v2", function(){

		    });
	    gapi.client.load("fusiontables", "v1", function(){
	    	gapi.client.fusiontables.table.insert({'tableID':"1_rt_nw7XmSic3L7rbA5Ok9BbrVyrYiP9sIZRUj4"}, function(){ console.log('here');})
	    });
	    //google.load("jquery", "1.7.1", {callback : function(){} });
	    //google.load("jqueryui", "1.8.16", {callback : function(){} });
	   

	  } else {
	    authorizeButton.style.visibility = '';
	    authorizeButton.onclick = handleAuthClick;
	  }
	}

	function handleAuthClick(event) {
	  gapi.auth.authorize({client_id: clientId, scope: scopes, immediate: false}, handleAuthResult);
	  return false;
	}

function OnLoadCallback(){

}
function myinit(){
}

</script>
</head>

<body onload="javascript: handleClientLoad();">

<input type="button" id="authorize-button" value="Auth!" />

<img src="DataCollectionSheet_files/image001.jpg">

<h3>Data Collection Sheet</h3>

<form method="POST" name="theform">

<div style="border:1px #000 solid;">
<table>
<tr>
<?php echo tdgen("Farmer Code", "farmcode"); ?>
<?php echo tdgen("Interviewer", "interviewer"); ?>
<?php echo tdgen("Date", "date"); ?>
</tr>
</table>
</div>
<h3>Location/General</h3>

<table>
<tr>
<?php echo tdgen("State", "state"); ?>
<?php echo tdgen("County", "county"); ?>
</tr>
<tr>
<?php echo tdgen("Total Acres Owned", "ta_owned"); ?>
<?php echo tdgen("Acres Rented", "ta_rented"); ?>
</tr>
</table>
<table>
<tr>
<?php echo tdgen("Type of operation (sole proprietor/family/etc.)", "op_type"); ?>
</tr>
</table>

<p><strong>Field location details (Sufficient information for locating on a plat map or Google Earth, e.g. address, Township, Range):</strong>
<textarea name="field_details"></textarea>

<table>
<tr>
<?php echo tdyn("Farm has livestock", "livestock"); ?>
<?php echo tdyn("Manure import from other farms", "inport_manure"); ?>
</tr>
</table>

<p><strong>Farm labor availability: (3,000 hours = 1 person/year)</strong>
<br />
<?php echo radio("availability", Array(
		"3000"=> "3,000",
		"4500"=> "4,500",
		"6000"=> "6,000",
		"other"=>"other (add input box...)")); ?>

<p>
<table><tr>
<?php echo tdgen("Total # of fields", "total_fields"); ?>
<?php echo tdgen("Area of field 1 (acres)", "field1_acres"); ?>
<?php echo tdgen("Area of field 2 (acres)", "field2_acres"); ?>
</tr></table>

<p><strong>Livestock Information</strong>

<table>
<?php for($i=1;$i<4;$i++){ 
 echo "<tr>";
 echo tdgen("Type of livestock $i", "livestock${i}_type"); 
 echo tdgen("Head Count", "livestock${i}_count"); 
 echo tdgen("% feed produced on farm", "livestock${i}_feedonfarm");
 echo "</tr>";
} ?> 
<tr>
<?php echo tdgen("Acres in pasture/hay", "pasturehay_acres"); ?>
</tr>
</table>

<div id="field-tabs">
    <ul>
        <li><a href="#tabs-1">Field One</a></li>
        <li><a href="#tabs-2">Field Two</a></li>
    </ul>

<?php for($field=1;$field<3;$field++){
    echo "<div id='tabs-${field}'>";
	echo "<div style='background:#EEEEEE;'><strong>Field ${field}</strong>
   <table><tr>". tdgen("Unique Name", "field${field}_name") ."</tr></table>
		</div>";
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
  echo tdgen("Soil type", "field${field}_soiltype");
  echo tdgen("Soil test P", "field${field}_soiltest_p");
  echo tdgen("Soil test type", "field${field}_soiltest_t");
  echo "</tr></table>";
  
  for ($rotation=1;$rotation<4;$rotation++){
    echo "<table><tr>";
    echo tdgen("Crop Type", "field${field}_rotation${rotation}_croptype");
    echo tdgen("Year", "field${field}_rotation${rotation}_year");
    echo "</tr></table>";
		
	echo "<table><tr>";
	echo tdgen("Yield (per acre)", "field${field}_rotation${rotation}_yield");
	echo tdyn("Irrigated", "field${field}_rotation${rotation}_irrigated");
	echo "<th>Harvest:</th><td>". radio("field${field}_rotation${rotation}_harvest", Array(
			"grain_only"=> "Grain only",
			"grain_and_res"=> "Grain and residue")) ."</td>";
	echo "</tr></table>";
	
	echo "<table><tr>";
	echo tdgen("Percent residue removed (%)", "field${field}_rotation${rotation}_resremoved");
	echo tdyn("Shred cornstalks before tillage", "field${field}_rotation${rotation}_shredstalks");
	echo "</tr></table>";
	
	echo "<table><tr>";
	echo tdgen("Residue removal: (e.g. bale)", "field${field}_rotation${rotation}_resremovalmethod");
	echo "</tr></table>";
	
	echo "<table>";
	for ($tillage=1;$tillage<7;$tillage++){
      echo "<tr>";
      $s = "field${field}_rotation${rotation}_tillage${tillage}";
      echo tdgen("Tillage equipment", "${s}_equip");
      echo tdgen("Width", "${s}_width");
      echo tdgen("Date", "${s}_date");
      echo "</tr>";
	} // End of tillage
	echo "</table>";
	
	echo "<table><tr>";
	echo tdgen("Seeding rate (per acre)", "field${field}_rotation${rotation}_seedrate");
	echo "<th>Units:</th><td>". radio("field${field}_rotation${rotation}_seedunits", Array(
			"seeds_per_acre"=> "seeds per acre",
			"lbs_per_acre"=> "lbs. per acre")) ."</td>";
	echo "</tr></table>";
	
	echo "<table><tr>";
	echo tdgen("Relative maturity", "field${field}_rotation${rotation}_maturity");
	echo "</tr></table>";
	
	echo "<table><tr>";
	echo tdgen("Planting equipment", "field${field}_rotation${rotation}_plantequip");
	echo tdgen("Date", "field${field}_rotation${rotation}_plantdate");
	echo "</tr><tr>";
	echo tdgen("Harvest equipment", "field${field}_rotation${rotation}_harvestequip");
	echo tdgen("Date", "field${field}_rotation${rotation}_harvestdate");	
	echo "</tr></table>";
	
	echo "<table>";
	for($weed=1;$weed<5;$weed++){
		$s = "field${field}_rotation${rotation}_weed${weed}";
		echo "<tr>";
		echo tdgen("Weed Control #${weed}", "${s}_control");
		echo tdgen("Rate", "${s}_rate");
		echo tdgen("# of passes", "${s}_passes");
		echo tdgen("Date", "${s}_date");
		echo "</tr>";
	} // End of weed
	echo "</table>";
	
	echo "<table>";
	for($fert=1;$fert<5;$fert++){
		$s = "field${field}_rotation${rotation}_fert${fert}";
		echo "<tr>";
		echo tdgen("Fertilizer #${fert}", "${s}_fert");
		echo tdgen("Amount (lbs/acre)", "${s}_amount");
		echo tdgen("Applicator type", "${s}_apptype");
		echo tdgen("Date", "${s}_date");
		echo "</tr>";
	} // End of fert
	echo "</table>";
	

  } // End of rotation
  
  for ($cover=1;$cover<4;$cover++){
  	echo "<table><tr>";
  	echo tdgen("Cover Crop Type", "field${field}_cover${cover}_type");
  	echo tdgen("Year", "field${field}_cover${cover}_year");
  	echo "</tr></table>";
  
  	echo "<table><tr>";
  	echo tdgen("Seeding rate (per acre)", "field${field}_cover${cover}_seedrate");
  	echo "<th>Units:</th><td>". radio("field${field}_cover${cover}_seedunits", Array(
  			"seeds_per_acre"=> "seeds per acre",
  			"lbs_per_acre"=> "lbs. per acre")) ."</td>";
    echo "</tr><tr>";
	echo tdgen("Planting equipment", "field${field}_cover${cover}_plantequip");	
	echo tdgen("Date", "field${field}_cover${cover}_plantdate");	
	echo "</tr><tr>";
	echo tdgen("Termination practice (e.g., herbicide)", "field${field}_cover${cover}_termination");
	echo tdgen("Date", "field${field}_cover${cover}_termdate");
	echo "</tr><tr>";
	echo tdgen("Yield (if applicable)", "field${field}_cover${cover}_yield");
	echo "</tr></table>";
  	
  } // End of cover
  echo "</div>";
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

<table>
<tr><th>Conservation Practices</th><td>Field 1</td><td>Field 2</td><td>On other land you farm</td></tr>
<?php 
while (list($k,$v) = each($conservation)){
  if ($k == 'precision' || $k == 'ipm' || $k == 'nutrient'){
  }
  echo sprintf("<tr><th>%s</th>
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

<textarea name='challenges'></textarea>

<p>3. Other Notes:

<textarea name='notes'></textarea>

<p><input type="submit" value="Save Data!" />

</form>

</body>

</html>
