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
  <link rel="stylesheet" type="text/css" media="screen" href="dcs.css" />
</head>

<body lang=EN-US style='tab-interval:.5in'>

<div class=WordSection1>

<img src="DataCollectionSheet_files/image001.jpg">

<h3>Data Collection Sheet</h3>

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

<?php for($field=1;$field<3;$field++){
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
} // End of field loop 
?>

<div class=WordSection2>




<div class=WordSection10>

<p class=MsoNormal align=center style='margin-bottom:6.0pt;text-align:center'><b
style='mso-bidi-font-weight:normal'><span style='font-size:16.0pt;mso-bidi-font-size:
11.0pt;line-height:115%;font-family:"Times New Roman","serif"'>Conservation
Questions<o:p></o:p></span></b></p>

<p class=MsoNormal style='margin-top:0in;margin-right:0in;margin-bottom:0in;
margin-left:.25in;margin-bottom:.0001pt;text-indent:-.25in'><span
style='font-size:12.0pt;mso-bidi-font-size:14.0pt;line-height:115%;font-family:
"Times New Roman","serif";mso-fareast-font-family:Arial;mso-bidi-font-family:
Arial;position:relative;top:.5pt;mso-text-raise:-.5pt'>1.</span><span
style='font-size:12.0pt;mso-bidi-font-size:10.0pt;line-height:115%;font-family:
"Times New Roman","serif";mso-fareast-font-family:"Times New Roman"'><span
style='mso-tab-count:1'>�� </span>What conservation practices are you already
implementing on these fields or on your entire farm (<b style='mso-bidi-font-weight:
normal'>See list below</b>)? Please include land that is set aside in CRP or
other government programs.</span><span style='font-family:"Times New Roman","serif"'><o:p></o:p></span></p>

<p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt'><span
style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>

<table class=MsoTableGrid border=1 cellspacing=0 cellpadding=0
 style='margin-left:23.4pt;border-collapse:collapse;border:none;mso-border-alt:
 solid windowtext .5pt;mso-yfti-tbllook:1184;mso-padding-alt:0in 5.4pt 0in 5.4pt'>
 <tr style='mso-yfti-irow:0;mso-yfti-firstrow:yes'>
  <td width=337 valign=top style='width:252.9pt;border:solid windowtext 1.0pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><b style='mso-bidi-font-weight:normal'><span style='font-family:"Times New Roman","serif"'>Conservation
  Practices<o:p></o:p></span></b></p>
  </td>
  <td width=110 valign=top style='width:1.15in;border:solid windowtext 1.0pt;
  border-left:none;mso-border-left-alt:solid windowtext .5pt;mso-border-alt:
  solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt'>
  <p class=MsoNormal align=center style='margin-bottom:0in;margin-bottom:.0001pt;
  text-align:center;line-height:normal'><b style='mso-bidi-font-weight:normal'><span
  style='font-family:"Times New Roman","serif"'>Field 1<o:p></o:p></span></b></p>
  </td>
  <td width=110 valign=top style='width:1.15in;border:solid windowtext 1.0pt;
  border-left:none;mso-border-left-alt:solid windowtext .5pt;mso-border-alt:
  solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt'>
  <p class=MsoNormal align=center style='margin-bottom:0in;margin-bottom:.0001pt;
  text-align:center;line-height:normal'><b style='mso-bidi-font-weight:normal'><span
  style='font-family:"Times New Roman","serif"'>Field 2<o:p></o:p></span></b></p>
  </td>
  <td width=164 valign=top style='width:123.3pt;border:solid windowtext 1.0pt;
  border-left:none;mso-border-left-alt:solid windowtext .5pt;mso-border-alt:
  solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><b style='mso-bidi-font-weight:normal'><span style='font-family:"Times New Roman","serif"'>On
  other land you farm<o:p></o:p></span></b></p>
  </td>
 </tr>
 <tr style='mso-yfti-irow:1;height:.4in'>
  <td width=337 style='width:252.9pt;border:solid windowtext 1.0pt;border-top:
  none;mso-border-top-alt:solid windowtext .5pt;mso-border-alt:solid windowtext .5pt;
  padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif";mso-bidi-font-family:
  "Times New Roman";mso-bidi-theme-font:minor-bidi'>Grassed waterways<o:p></o:p></span></p>
  </td>
  <td width=110 style='width:1.15in;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
  <td width=110 style='width:1.15in;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
  <td width=164 style='width:123.3pt;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
 </tr>
 <tr style='mso-yfti-irow:2;height:.4in'>
  <td width=337 style='width:252.9pt;border:solid windowtext 1.0pt;border-top:
  none;mso-border-top-alt:solid windowtext .5pt;mso-border-alt:solid windowtext .5pt;
  padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif";mso-bidi-font-family:
  "Times New Roman";mso-bidi-theme-font:minor-bidi'>Contour buffer strips<o:p></o:p></span></p>
  </td>
  <td width=110 style='width:1.15in;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
  <td width=110 style='width:1.15in;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
  <td width=164 style='width:123.3pt;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
 </tr>
 <tr style='mso-yfti-irow:3;height:.4in'>
  <td width=337 style='width:252.9pt;border:solid windowtext 1.0pt;border-top:
  none;mso-border-top-alt:solid windowtext .5pt;mso-border-alt:solid windowtext .5pt;
  padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif";mso-bidi-font-family:
  "Times New Roman";mso-bidi-theme-font:minor-bidi'>Filter strips along
  waterways and/or field borders<o:p></o:p></span></p>
  </td>
  <td width=110 style='width:1.15in;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
  <td width=110 style='width:1.15in;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
  <td width=164 style='width:123.3pt;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
 </tr>
 <tr style='mso-yfti-irow:4;height:.4in'>
  <td width=337 style='width:252.9pt;border:solid windowtext 1.0pt;border-top:
  none;mso-border-top-alt:solid windowtext .5pt;mso-border-alt:solid windowtext .5pt;
  padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif";mso-bidi-font-family:
  "Times New Roman";mso-bidi-theme-font:minor-bidi'>Windbreaks and shelterbelts<o:p></o:p></span></p>
  </td>
  <td width=110 style='width:1.15in;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
  <td width=110 style='width:1.15in;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
  <td width=164 style='width:123.3pt;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
 </tr>
 <tr style='mso-yfti-irow:5;height:.4in'>
  <td width=337 style='width:252.9pt;border:solid windowtext 1.0pt;border-top:
  none;mso-border-top-alt:solid windowtext .5pt;mso-border-alt:solid windowtext .5pt;
  padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif";mso-bidi-font-family:
  "Times New Roman";mso-bidi-theme-font:minor-bidi'>Terraces<o:p></o:p></span></p>
  </td>
  <td width=110 style='width:1.15in;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
  <td width=110 style='width:1.15in;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
  <td width=164 style='width:123.3pt;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
 </tr>
 <tr style='mso-yfti-irow:6;height:.4in'>
  <td width=337 style='width:252.9pt;border:solid windowtext 1.0pt;border-top:
  none;mso-border-top-alt:solid windowtext .5pt;mso-border-alt:solid windowtext .5pt;
  padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-top:6.0pt;margin-right:0in;margin-bottom:
  6.0pt;margin-left:0in;line-height:normal'><span style='font-family:"Times New Roman","serif";
  mso-bidi-font-family:"Times New Roman";mso-bidi-theme-font:minor-bidi'>Drainage/runoff
  treatment structures (e.g., nutrient removal wetlands, bioreactors)<o:p></o:p></span></p>
  </td>
  <td width=110 style='width:1.15in;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-top:6.0pt;margin-right:0in;margin-bottom:
  6.0pt;margin-left:0in;line-height:normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
  <td width=110 style='width:1.15in;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-top:6.0pt;margin-right:0in;margin-bottom:
  6.0pt;margin-left:0in;line-height:normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
  <td width=164 style='width:123.3pt;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-top:6.0pt;margin-right:0in;margin-bottom:
  6.0pt;margin-left:0in;line-height:normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
 </tr>
 <tr style='mso-yfti-irow:7;height:.4in'>
  <td width=337 style='width:252.9pt;border:solid windowtext 1.0pt;border-top:
  none;mso-border-top-alt:solid windowtext .5pt;mso-border-alt:solid windowtext .5pt;
  padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif";mso-bidi-font-family:
  "Times New Roman";mso-bidi-theme-font:minor-bidi'>Whole portions of cropland
  converted to grass/trees<o:p></o:p></span></p>
  </td>
  <td width=110 style='width:1.15in;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
  <td width=110 style='width:1.15in;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
  <td width=164 style='width:123.3pt;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
 </tr>
 <tr style='mso-yfti-irow:8;height:.4in'>
  <td width=337 style='width:252.9pt;border:solid windowtext 1.0pt;border-top:
  none;mso-border-top-alt:solid windowtext .5pt;mso-border-alt:solid windowtext .5pt;
  padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif";mso-bidi-font-family:
  "Times New Roman";mso-bidi-theme-font:minor-bidi'>Cover crops<o:p></o:p></span></p>
  </td>
  <td width=110 style='width:1.15in;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
  <td width=110 style='width:1.15in;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
  <td width=164 style='width:123.3pt;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
 </tr>
 <tr style='mso-yfti-irow:9;height:.4in'>
  <td width=337 style='width:252.9pt;border:solid windowtext 1.0pt;border-top:
  none;mso-border-top-alt:solid windowtext .5pt;mso-border-alt:solid windowtext .5pt;
  padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif";mso-bidi-font-family:
  "Times New Roman";mso-bidi-theme-font:minor-bidi'>Extended
  rotations/diversified with other grains/forage<o:p></o:p></span></p>
  </td>
  <td width=110 style='width:1.15in;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
  <td width=110 style='width:1.15in;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
  <td width=164 style='width:123.3pt;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
 </tr>
 <tr style='mso-yfti-irow:10;height:.4in'>
  <td width=337 style='width:252.9pt;border:solid windowtext 1.0pt;border-top:
  none;mso-border-top-alt:solid windowtext .5pt;mso-border-alt:solid windowtext .5pt;
  padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif";mso-bidi-font-family:
  "Times New Roman";mso-bidi-theme-font:minor-bidi'>Reduced tillage (i.e.
  strip, ridge)<o:p></o:p></span></p>
  </td>
  <td width=110 style='width:1.15in;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
  <td width=110 style='width:1.15in;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
  <td width=164 style='width:123.3pt;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
 </tr>
 <tr style='mso-yfti-irow:11;height:.4in'>
  <td width=337 style='width:252.9pt;border:solid windowtext 1.0pt;border-top:
  none;mso-border-top-alt:solid windowtext .5pt;mso-border-alt:solid windowtext .5pt;
  padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif";mso-bidi-font-family:
  "Times New Roman";mso-bidi-theme-font:minor-bidi'>No-till<o:p></o:p></span></p>
  </td>
  <td width=110 style='width:1.15in;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
  <td width=110 style='width:1.15in;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
  <td width=164 style='width:123.3pt;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
 </tr>
 <tr style='mso-yfti-irow:12;height:.4in'>
  <td width=337 style='width:252.9pt;border:solid windowtext 1.0pt;border-top:
  none;mso-border-top-alt:solid windowtext .5pt;mso-border-alt:solid windowtext .5pt;
  padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif";mso-bidi-font-family:
  "Times New Roman";mso-bidi-theme-font:minor-bidi'>Nutrient management (identify
  practices)<o:p></o:p></span></p>
  </td>
  <td width=110 style='width:1.15in;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
  <td width=110 style='width:1.15in;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
  <td width=164 style='width:123.3pt;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
 </tr>
 <tr style='mso-yfti-irow:13;height:.4in'>
  <td width=337 valign=top style='width:252.9pt;border:solid windowtext 1.0pt;
  border-top:none;mso-border-top-alt:solid windowtext .5pt;mso-border-alt:solid windowtext .5pt;
  padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif";mso-bidi-font-family:
  "Times New Roman";mso-bidi-theme-font:minor-bidi'>Canopy sensors for nitrogen
  deficiency<o:p></o:p></span></p>
  </td>
  <td width=110 valign=top style='width:1.15in;border-top:none;border-left:
  none;border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
  <td width=110 valign=top style='width:1.15in;border-top:none;border-left:
  none;border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
  <td width=164 valign=top style='width:123.3pt;border-top:none;border-left:
  none;border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
 </tr>
 <tr style='mso-yfti-irow:14;height:.4in'>
  <td width=337 style='width:252.9pt;border:solid windowtext 1.0pt;border-top:
  none;mso-border-top-alt:solid windowtext .5pt;mso-border-alt:solid windowtext .5pt;
  padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif";mso-bidi-font-family:
  "Times New Roman";mso-bidi-theme-font:minor-bidi'>IPM (identify practices)<o:p></o:p></span></p>
  </td>
  <td width=110 style='width:1.15in;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
  <td width=110 style='width:1.15in;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
  <td width=164 style='width:123.3pt;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
 </tr>
 <tr style='mso-yfti-irow:15;height:.4in'>
  <td width=337 style='width:252.9pt;border:solid windowtext 1.0pt;border-top:
  none;mso-border-top-alt:solid windowtext .5pt;mso-border-alt:solid windowtext .5pt;
  padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-top:6.0pt;margin-right:0in;margin-bottom:
  6.0pt;margin-left:0in;line-height:normal'><span style='font-family:"Times New Roman","serif";
  mso-bidi-font-family:"Times New Roman";mso-bidi-theme-font:minor-bidi'>Use of
  control structures to drain and store water depending on crop needs and soil
  conditions (�drainage water management,� not just tile)<o:p></o:p></span></p>
  </td>
  <td width=110 style='width:1.15in;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-top:6.0pt;margin-right:0in;margin-bottom:
  6.0pt;margin-left:0in;line-height:normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
  <td width=110 style='width:1.15in;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-top:6.0pt;margin-right:0in;margin-bottom:
  6.0pt;margin-left:0in;line-height:normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
  <td width=164 style='width:123.3pt;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-top:6.0pt;margin-right:0in;margin-bottom:
  6.0pt;margin-left:0in;line-height:normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
 </tr>
 <tr style='mso-yfti-irow:16;height:.4in'>
  <td width=337 style='width:252.9pt;border:solid windowtext 1.0pt;border-top:
  none;mso-border-top-alt:solid windowtext .5pt;mso-border-alt:solid windowtext .5pt;
  padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif";mso-bidi-font-family:
  "Times New Roman";mso-bidi-theme-font:minor-bidi'>Precision agriculture (identify
  practices)<o:p></o:p></span></p>
  </td>
  <td width=110 style='width:1.15in;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
  <td width=110 style='width:1.15in;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
  <td width=164 style='width:123.3pt;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
 </tr>
 <tr style='mso-yfti-irow:17;height:.4in'>
  <td width=337 style='width:252.9pt;border:solid windowtext 1.0pt;border-top:
  none;mso-border-top-alt:solid windowtext .5pt;mso-border-alt:solid windowtext .5pt;
  padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif";mso-bidi-font-family:
  "Times New Roman";mso-bidi-theme-font:minor-bidi'>Other:_____________________________________<o:p></o:p></span></p>
  </td>
  <td width=110 style='width:1.15in;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
  <td width=110 style='width:1.15in;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
  <td width=164 style='width:123.3pt;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
 </tr>
 <tr style='mso-yfti-irow:18;mso-yfti-lastrow:yes;height:.4in'>
  <td width=337 style='width:252.9pt;border:solid windowtext 1.0pt;border-top:
  none;mso-border-top-alt:solid windowtext .5pt;mso-border-alt:solid windowtext .5pt;
  padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal;tab-stops:right 237.15pt'><span style='font-family:"Times New Roman","serif";
  mso-bidi-font-family:"Times New Roman";mso-bidi-theme-font:minor-bidi'>Other:
  <u><span style='mso-tab-count:1'>������������������������������������������������������������������� </span><o:p></o:p></u></span></p>
  </td>
  <td width=110 style='width:1.15in;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
  <td width=110 style='width:1.15in;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
  <td width=164 style='width:123.3pt;border-top:none;border-left:none;
  border-bottom:solid windowtext 1.0pt;border-right:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-left-alt:solid windowtext .5pt;
  mso-border-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt;height:.4in'>
  <p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt;line-height:
  normal'><span style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
 </tr>
</table>

</div>

<span style='font-size:11.0pt;line-height:115%;font-family:"Times New Roman","serif";
mso-fareast-font-family:Calibri;mso-fareast-theme-font:minor-latin;mso-ansi-language:
EN-US;mso-fareast-language:EN-US;mso-bidi-language:AR-SA'><br clear=all
style='page-break-before:always;mso-break-type:section-break'>
</span>

<div class=WordSection11>

<p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt'><span
style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>

<p class=MsoNormal style='margin-top:0in;margin-right:0in;margin-bottom:0in;
margin-left:.25in;margin-bottom:.0001pt;text-indent:-.25in'><span
style='font-size:12.0pt;mso-bidi-font-size:10.0pt;line-height:115%;font-family:
"Times New Roman","serif";mso-fareast-font-family:"Times New Roman"'>2.<span
style='mso-tab-count:1'>�� </span>Do you have any management challenges on
these two fields, which might inspire you to consider new management strategies
[identify conservation goals]? (<span class=GramE>e.g</span>. drainage
management,<span style='mso-spacerun:yes'>� </span>greater erosion control,
pests/disease control, nitrogen deficiency, diversified income streams?</span><span
style='font-family:"Times New Roman","serif"'><o:p></o:p></span></p>

<table class=MsoTableGrid border=0 cellspacing=0 cellpadding=0
 style='margin-left:23.4pt;border-collapse:collapse;border:none;mso-yfti-tbllook:
 1184;mso-padding-alt:0in 5.4pt 0in 5.4pt;mso-border-insideh:none;mso-border-insidev:
 none'>
 <tr style='mso-yfti-irow:0;mso-yfti-firstrow:yes'>
  <td width=697 valign=top style='width:522.9pt;border:none;border-bottom:solid windowtext 1.0pt;
  mso-border-bottom-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt'>
  <p class=MsoNormal style='margin-top:6.0pt;margin-right:0in;margin-bottom:
  0in;margin-left:0in;margin-bottom:.0001pt;line-height:150%'><span
  style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
 </tr>
 <tr style='mso-yfti-irow:1'>
  <td width=697 valign=top style='width:522.9pt;border:none;border-bottom:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-top-alt:solid windowtext .5pt;
  mso-border-bottom-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt'>
  <p class=MsoNormal style='margin-top:6.0pt;margin-right:0in;margin-bottom:
  0in;margin-left:0in;margin-bottom:.0001pt;line-height:150%'><span
  style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
 </tr>
 <tr style='mso-yfti-irow:2'>
  <td width=697 valign=top style='width:522.9pt;border:none;border-bottom:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-top-alt:solid windowtext .5pt;
  mso-border-bottom-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt'>
  <p class=MsoNormal style='margin-top:6.0pt;margin-right:0in;margin-bottom:
  0in;margin-left:0in;margin-bottom:.0001pt;line-height:150%'><span
  style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
 </tr>
 <tr style='mso-yfti-irow:3'>
  <td width=697 valign=top style='width:522.9pt;border:none;border-bottom:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-top-alt:solid windowtext .5pt;
  mso-border-bottom-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt'>
  <p class=MsoNormal style='margin-top:6.0pt;margin-right:0in;margin-bottom:
  0in;margin-left:0in;margin-bottom:.0001pt;line-height:150%'><span
  style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
 </tr>
 <tr style='mso-yfti-irow:4'>
  <td width=697 valign=top style='width:522.9pt;border:none;border-bottom:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-top-alt:solid windowtext .5pt;
  mso-border-bottom-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt'>
  <p class=MsoNormal style='margin-top:6.0pt;margin-right:0in;margin-bottom:
  0in;margin-left:0in;margin-bottom:.0001pt;line-height:150%'><span
  style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
 </tr>
 <tr style='mso-yfti-irow:5;mso-yfti-lastrow:yes'>
  <td width=697 valign=top style='width:522.9pt;border:none;border-bottom:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-top-alt:solid windowtext .5pt;
  mso-border-bottom-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt'>
  <p class=MsoNormal style='margin-top:6.0pt;margin-right:0in;margin-bottom:
  0in;margin-left:0in;margin-bottom:.0001pt;line-height:150%'><span
  style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
 </tr>
</table>

<p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt'><span
style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>

<p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt'><span
style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>

<p class=MsoNormal style='margin-bottom:6.0pt;line-height:normal'><b
style='mso-bidi-font-weight:normal'><span style='font-family:"Times New Roman","serif"'>Other
Notes:<o:p></o:p></span></b></p>

<table class=MsoTableGrid border=0 cellspacing=0 cellpadding=0
 style='margin-left:23.4pt;border-collapse:collapse;border:none;mso-yfti-tbllook:
 1184;mso-padding-alt:0in 5.4pt 0in 5.4pt;mso-border-insideh:none;mso-border-insidev:
 none'>
 <tr style='mso-yfti-irow:0;mso-yfti-firstrow:yes'>
  <td width=697 valign=top style='width:522.9pt;border:none;border-bottom:solid windowtext 1.0pt;
  mso-border-bottom-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt'>
  <p class=MsoNormal style='margin-top:6.0pt;margin-right:0in;margin-bottom:
  0in;margin-left:0in;margin-bottom:.0001pt;line-height:150%'><span
  style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
 </tr>
 <tr style='mso-yfti-irow:1'>
  <td width=697 valign=top style='width:522.9pt;border:none;border-bottom:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-top-alt:solid windowtext .5pt;
  mso-border-bottom-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt'>
  <p class=MsoNormal style='margin-top:6.0pt;margin-right:0in;margin-bottom:
  0in;margin-left:0in;margin-bottom:.0001pt;line-height:150%'><span
  style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
 </tr>
 <tr style='mso-yfti-irow:2'>
  <td width=697 valign=top style='width:522.9pt;border:none;border-bottom:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-top-alt:solid windowtext .5pt;
  mso-border-bottom-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt'>
  <p class=MsoNormal style='margin-top:6.0pt;margin-right:0in;margin-bottom:
  0in;margin-left:0in;margin-bottom:.0001pt;line-height:150%'><span
  style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
 </tr>
 <tr style='mso-yfti-irow:3'>
  <td width=697 valign=top style='width:522.9pt;border:none;border-bottom:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-top-alt:solid windowtext .5pt;
  mso-border-bottom-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt'>
  <p class=MsoNormal style='margin-top:6.0pt;margin-right:0in;margin-bottom:
  0in;margin-left:0in;margin-bottom:.0001pt;line-height:150%'><span
  style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
 </tr>
 <tr style='mso-yfti-irow:4'>
  <td width=697 valign=top style='width:522.9pt;border:none;border-bottom:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-top-alt:solid windowtext .5pt;
  mso-border-bottom-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt'>
  <p class=MsoNormal style='margin-top:6.0pt;margin-right:0in;margin-bottom:
  0in;margin-left:0in;margin-bottom:.0001pt;line-height:150%'><span
  style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
 </tr>
 <tr style='mso-yfti-irow:5'>
  <td width=697 valign=top style='width:522.9pt;border:none;border-bottom:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-top-alt:solid windowtext .5pt;
  mso-border-bottom-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt'>
  <p class=MsoNormal style='margin-top:6.0pt;margin-right:0in;margin-bottom:
  0in;margin-left:0in;margin-bottom:.0001pt;line-height:150%'><span
  style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
 </tr>
 <tr style='mso-yfti-irow:6'>
  <td width=697 valign=top style='width:522.9pt;border:none;border-bottom:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-top-alt:solid windowtext .5pt;
  mso-border-bottom-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt'>
  <p class=MsoNormal style='margin-top:6.0pt;margin-right:0in;margin-bottom:
  0in;margin-left:0in;margin-bottom:.0001pt;line-height:150%'><span
  style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
 </tr>
 <tr style='mso-yfti-irow:7'>
  <td width=697 valign=top style='width:522.9pt;border:none;border-bottom:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-top-alt:solid windowtext .5pt;
  mso-border-bottom-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt'>
  <p class=MsoNormal style='margin-top:6.0pt;margin-right:0in;margin-bottom:
  0in;margin-left:0in;margin-bottom:.0001pt;line-height:150%'><span
  style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
 </tr>
 <tr style='mso-yfti-irow:8;mso-yfti-lastrow:yes'>
  <td width=697 valign=top style='width:522.9pt;border:none;border-bottom:solid windowtext 1.0pt;
  mso-border-top-alt:solid windowtext .5pt;mso-border-top-alt:solid windowtext .5pt;
  mso-border-bottom-alt:solid windowtext .5pt;padding:0in 5.4pt 0in 5.4pt'>
  <p class=MsoNormal style='margin-top:6.0pt;margin-right:0in;margin-bottom:
  0in;margin-left:0in;margin-bottom:.0001pt;line-height:150%'><span
  style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>
  </td>
 </tr>
</table>

<p class=MsoNormal style='margin-bottom:0in;margin-bottom:.0001pt'><span
style='font-family:"Times New Roman","serif"'><o:p>&nbsp;</o:p></span></p>

</div>

</body>

</html>
