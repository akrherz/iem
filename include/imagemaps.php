<?php

function networkSelect($network, $selected)
{
    global $rootpath;
    $network = strtoupper($network);
    $s = "";
    include_once("$rootpath/include/all_locs.php");
    reset($cities);
    $s .= '<select name="station">\n';
    while (list($sid, $tbl) = each($cities))
    {
        if ($tbl["network"] != $network) continue;
        $s .= "<option value=\"$sid\" ";
        if ($selected == $sid) { $s .= "SELECTED"; }
        $s .= ">". $tbl["city"] ."</option>\n";
   }
   $s .= "</select>\n";
   return $s;
}


function snetSelectMultiple($selected){
global $rootpath;
include("$rootpath/include/snetLoc.php");
asort($Scities);
echo "<select name=\"station[]\" size=7 MULTIPLE >\n";
                                                                                
for ($i = 0; $i < count($Scities); $i++) {
  $city = current($Scities);
  echo "<option value=\"". $city["id"] ."\"";
  if ($selected == $city["id"]){
        echo " SELECTED ";
  }   echo " >". $city["city"] ."</option>\n";
  next($Scities); }                                                                                 
echo "</select>\n";
                                                                                
}


function snetSelect($selected){
global $rootpath;
include("$rootpath/include/snetLoc.php");
echo "<select name=\"station\">\n";

for ($i = 0; $i < count($Scities); $i++) {
  $city = current($Scities);
  echo "<option value=\"". $city["id"] ."\"";
  if ($selected == $city["id"]){
  	echo " SELECTED ";
  }
  echo " >". $city["city"] ."</option>\n";
  next($Scities);
} 

echo "</select>\n";

} 

function keloSelect($selected){
    global $rootpath;
include("$rootpath/include/keloLoc.php");
echo "<select name=\"station\">\n";

for ($i = 0; $i < count($Scities); $i++) {
  $city = current($Scities);
  echo "<option value=\"". $city["id"] ."\"";
  if ($selected == $city["id"]){
        echo " SELECTED ";
  }
  echo " >". $city["city"] ."\n";
  next($Scities);
}

echo "</select>\n";

}

function kcciSelectAuto($selected, $pre, $post){
global $rootpath;
include("$rootpath/include/kcciLoc.php");
echo "<form><select name=\"station\" onChange=\"location=this.form.station.options[this.form.station.selectedIndex].value\">\n";

for ($i = 0; $i < count($Scities); $i++) {
  $city = current($Scities);
  echo "<option value=\"". $pre . $city["id"] . $post ."\"";
  if (strcmp($selected, $city["id"]) == 0){
        echo " SELECTED ";
  }
  echo " >". $city["city"] ."</option>\n";
  next($Scities);
}

echo "</select></form>\n";

}


function kcciSelect($selected){
global $rootpath;
include("$rootpath/include/kcciLoc.php");
echo "<select name=\"station\">\n";

for ($i = 0; $i < count($Scities); $i++) {
  $city = current($Scities);
  echo "<option value=\"". $city["id"] ."\"";
  if ($selected == $city["id"]){
        echo " SELECTED ";
  }
  echo " >". $city["city"] ."</option>\n";
  next($Scities);
}

echo "</select>\n";

}

function kcci2Select($selected){
global $rootpath;
include("$rootpath/include/kcciLoc.php");
echo "<select name=\"station\">\n";

for ($i = 0; $i < count($Scities); $i++) {
  $city = current($Scities);
  echo "<option value=\"". $city["id"] ."\"";
  if ($selected == $city["id"]){
        echo " SELECTED ";
  }
  echo " >". $city["city"] ."</option>\n";
  next($Scities);
}

echo "</select>\n";

}


?>


<?php

function awosSelect($selected){
global $rootpath;
include("$rootpath/include/awosLoc.php");
  echo "<select name=\"station\">\n";
  for ($i = 0; $i < count($Wcities); $i++) {
    $city = current($Wcities);
    echo "<option value=\"". $city["id"] ."\"";
    if ($selected == $city["id"]){
        echo " SELECTED ";
    }
    echo " >". $city["city"] ." (". $city["id"] .")\n";
    next($Wcities);
  }

  echo "</select>\n";
}

function awosMultiSelect($selected, $size){
global $rootpath;
include("$rootpath/include/awosLoc.php");
  echo "<select name=\"station[]\" size=\"". $size ."\" MULTIPLE>\n";
  echo "<option value=\"_ALL\">Select All</option>\n";
  for ($i = 0; $i < count($Wcities); $i++) {
    $city = current($Wcities);
    echo "<option value=\"". $city["id"] ."\"";
    if ($selected == $city["id"]){
        echo " SELECTED ";
    }
    echo " >". $city["city"] ." (". $city["id"] .")\n";
    next($Wcities);
  }

  echo "</select>\n";
}

function rwisMultiSelect($selected, $size){
global $rootpath;
include("$rootpath/include/rwisLoc.php");
  echo "<select name=\"station[]\" size=\"". $size ."\" MULTIPLE>\n";
  echo "<option value=\"_ALL\">Select All</option>\n";
  for ($i = 0; $i < count($Rcities); $i++) {
    $city = current($Rcities);
    echo "<option value=\"". $city["id"] ."\"";
    if ($selected == $city["id"]){
        echo " SELECTED ";
    }
    echo " >". $city["city"] ." (". $city["id"] .")\n";
    next($Rcities);
  }

  echo "</select>\n";
}



function asosSelect($selected){
global $rootpath;
include("$rootpath/include/azosLoc.php");
echo "<select name=\"station\">\n";

for ($i = 0; $i < count($Zcities); $i++) {
  $city = current($Zcities);
  echo "<option value=\"". $city["id"] ."\"";
  if ($selected == $city["id"]){
  	echo " SELECTED ";
  }
  echo " >". $city["city"] ."\n";
  next($Zcities);
} 

echo "</select>\n";

} ?>

<?php 

function print_asos($stationPre) {

?>
<FORM name="myForm" action="nowhere">
Selected Station: <input type="text" name="city" size="30">
</FORM>

<DIV class="center">
<BR><IMG SRC="/include/asosMap.gif" BORDER=0 USEMAP="#amap" ALT="ASOS Map"><BR><BR>
</DIV>

<MAP NAME="amap">
<!-- #$-:Image Map file created by GIMP Imagemap Plugin -->
<!-- #$-:GIMP Imagemap Plugin by Maurits Rijk -->
<!-- #$-:Please do not edit lines starting with "#$" -->
<!-- #$VERSION:1.3 -->
<!-- #$AUTHOR:Daryl Herzmann -->
<AREA SHAPE="RECT" COORDS="294,77,332,96" onMouseover="document.myForm.city.value = 'Charles City';"  HREF="<?= $stationPre ?>=CCY">
<AREA SHAPE="RECT" COORDS="143,43,179,64" onMouseover="document.myForm.city.value = 'Estherville';"  HREF="<?= $stationPre ?>=EST">
<AREA SHAPE="RECT" COORDS="107,66,146,86"  onMouseover="document.myForm.city.value = 'Spencer';" HREF="<?= $stationPre ?>=SPW">
<AREA SHAPE="RECT" COORDS="61,57,101,79" onMouseover="document.myForm.city.value = 'Sheldon';"  HREF="<?= $stationPre ?>=SHL">
<AREA SHAPE="RECT" COORDS="44,84,82,101"  onMouseover="document.myForm.city.value = 'Orange City';" HREF="<?= $stationPre ?>=ORC">
<AREA SHAPE="RECT" COORDS="33,102,73,122" onMouseover="document.myForm.city.value = 'Le Mars';"  HREF="<?= $stationPre ?>=LRJ">
<AREA SHAPE="RECT" COORDS="19,138,61,161" onMouseover="document.myForm.city.value = 'Sioux City';"  HREF="<?= $stationPre ?>=SUX">
<AREA SHAPE="RECT" COORDS="62,250,98,271"  onMouseover="document.myForm.city.value = 'Council Bluffs';" HREF="<?= $stationPre ?>=CBF">
<AREA SHAPE="RECT" COORDS="84,304,121,322"  onMouseover="document.myForm.city.value = 'Shenandoah';" HREF="<?= $stationPre ?>=SDA">
<AREA SHAPE="RECT" COORDS="122,310,151,326"  onMouseover="document.myForm.city.value = 'Clarinda';" HREF="<?= $stationPre ?>=ICL">
<AREA SHAPE="RECT" COORDS="97,277,136,298" onMouseover="document.myForm.city.value = 'Red Oak';"  HREF="<?= $stationPre ?>=RDK">
<AREA SHAPE="RECT" COORDS="163,277,204,300"  onMouseover="document.myForm.city.value = 'Creston';" HREF="<?= $stationPre ?>=CSQ">
<AREA SHAPE="RECT" COORDS="194,317,235,340"  onMouseover="document.myForm.city.value = 'Lamoni';" HREF="<?= $stationPre ?>=LWD">
<AREA SHAPE="RECT" COORDS="355,55,397,76" onMouseover="document.myForm.city.value = 'Decorah';"  HREF="<?= $stationPre ?>=DEH">
<AREA SHAPE="RECT" COORDS="343,113,378,132"  onMouseover="document.myForm.city.value = 'Oelwein';" HREF="<?= $stationPre ?>=OLZ">
<AREA SHAPE="RECT" COORDS="309,129,345,146" onMouseover="document.myForm.city.value = 'Waterloo';"  HREF="<?= $stationPre ?>=ALO">
<AREA SHAPE="RECT" COORDS="435,141,470,159"  onMouseover="document.myForm.city.value = 'Dubuque';" HREF="<?= $stationPre ?>=DBQ">
<AREA SHAPE="RECT" COORDS="399,156,437,177"  onMouseover="document.myForm.city.value = 'Monticello';" HREF="<?= $stationPre ?>=MXO">
<AREA SHAPE="RECT" COORDS="363,192,400,212"  onMouseover="document.myForm.city.value = 'Cedar Rapids';" HREF="<?= $stationPre ?>=CID">
<AREA SHAPE="RECT" COORDS="377,217,411,237" onMouseover="document.myForm.city.value = 'Iowa City';"  HREF="<?= $stationPre ?>=IOW">
<AREA SHAPE="RECT" COORDS="464,193,497,215"  onMouseover="document.myForm.city.value = 'Clinton';" HREF="<?= $stationPre ?>=CWI">
<AREA SHAPE="RECT" COORDS="444,217,483,238" onMouseover="document.myForm.city.value = 'Davenport';"  HREF="<?= $stationPre ?>=DVN">
<AREA SHAPE="RECT" COORDS="404,243,444,261" onMouseover="document.myForm.city.value = 'Muscatine';"  HREF="<?= $stationPre ?>=MUT">
<AREA SHAPE="RECT" COORDS="366,253,404,273" onMouseover="document.myForm.city.value = 'Washington';"  HREF="<?= $stationPre ?>=AWG">
<AREA SHAPE="RECT" COORDS="409,301,446,316"  onMouseover="document.myForm.city.value = 'Burlington';" HREF="<?= $stationPre ?>=BRL">
<AREA SHAPE="RECT" COORDS="390,315,435,330"  onMouseover="document.myForm.city.value = 'Fort Madison';" HREF="<?= $stationPre ?>=FSW">
<AREA SHAPE="RECT" COORDS="385,332,424,352"  onMouseover="document.myForm.city.value = 'Keokuk';" HREF="<?= $stationPre ?>=EOK">
<AREA SHAPE="RECT" COORDS="347,275,380,295"  onMouseover="document.myForm.city.value = 'Fairfield';" HREF="<?= $stationPre ?>=FFL">
<AREA SHAPE="RECT" COORDS="308,269,344,289"  onMouseover="document.myForm.city.value = 'Ottumwa';" HREF="<?= $stationPre ?>=OTM">
<AREA SHAPE="RECT" COORDS="257,255,296,272"  onMouseover="document.myForm.city.value = 'Knoxville';" HREF="<?= $stationPre ?>=OXV">
<AREA SHAPE="RECT" COORDS="241,277,279,298"  onMouseover="document.myForm.city.value = 'Chariton';" HREF="<?= $stationPre ?>=CNC">
<AREA SHAPE="RECT" COORDS="218,231,257,247"  onMouseover="document.myForm.city.value = 'Des Moines';" HREF="<?= $stationPre ?>=DSM">
<AREA SHAPE="RECT" COORDS="226,213,262,231" onMouseover="document.myForm.city.value = 'Ankeny';"  HREF="<?= $stationPre ?>=IKV">
<AREA SHAPE="RECT" COORDS="270,212,303,234"  onMouseover="document.myForm.city.value = 'Newton';" HREF="<?= $stationPre ?>=TNU">
<AREA SHAPE="RECT" COORDS="224,188,257,200" onMouseover="document.myForm.city.value = 'Ames';"  HREF="<?= $stationPre ?>=AMW">
<AREA SHAPE="RECT" COORDS="204,178,239,189"  onMouseover="document.myForm.city.value = 'Boone';" HREF="<?= $stationPre ?>=BNW">
<AREA SHAPE="RECT" COORDS="273,170,312,191"  onMouseover="document.myForm.city.value = 'Marshalltown';" HREF="<?= $stationPre ?>=MIW">
<AREA SHAPE="RECT" COORDS="203,144,240,158" onMouseover="document.myForm.city.value = 'Webster City';"  HREF="<?= $stationPre ?>=EBS">
<AREA SHAPE="RECT" COORDS="213,108,249,127" onMouseover="document.myForm.city.value = 'Clarion';"  HREF="<?= $stationPre ?>=CAV">
<AREA SHAPE="RECT" COORDS="243,68,279,89"  onMouseover="document.myForm.city.value = 'Mason City';" HREF="<?= $stationPre ?>=MCW">
<AREA SHAPE="RECT" COORDS="175,75,215,97" onMouseover="document.myForm.city.value = 'Algona';"  HREF="<?= $stationPre ?>=AXA">
<AREA SHAPE="RECT" COORDS="103,119,146,145" onMouseover="document.myForm.city.value = 'Storm Lake';"  HREF="<?= $stationPre ?>=SLB">
<AREA SHAPE="RECT" COORDS="182,127,216,145"  onMouseover="document.myForm.city.value = 'Fort Dodge';" HREF="<?= $stationPre ?>=FOD">
<AREA SHAPE="RECT" COORDS="139,176,174,198"  onMouseover="document.myForm.city.value = 'Carroll';" HREF="<?= $stationPre ?>=CIN">
<AREA SHAPE="RECT" COORDS="92,181,129,204"  onMouseover="document.myForm.city.value = 'Denison';" HREF="<?= $stationPre ?>=DNS">
<AREA SHAPE="RECT" COORDS="129,212,163,231"  onMouseover="document.myForm.city.value = 'Audubon';" HREF="<?= $stationPre ?>=ADU">
<AREA SHAPE="RECT" COORDS="92,220,129,239"  onMouseover="document.myForm.city.value = 'Harlan';" HREF="<?= $stationPre ?>=HNR">
<AREA SHAPE="RECT" COORDS="117,241,154,260"  onMouseover="document.myForm.city.value = 'Atlantic';" HREF="<?= $stationPre ?>=AIO">
<AREA SHAPE="RECT" COORDS="275,243,310,258"  onMouseover="document.myForm.city.value = 'Pella';" HREF="<?= $stationPre ?>=PEA">
<AREA SHAPE="RECT" COORDS="382,286,414,305"  onMouseover="document.myForm.city.value = 'Mount Pleasant';" HREF="<?= $stationPre ?>=MPZ">
<AREA SHAPE="RECT" COORDS="348,141,380,159"  onMouseover="document.myForm.city.value = 'Independence';" HREF="<?= $stationPre ?>=IIB">
<AREA SHAPE="RECT" COORDS="340,162,375,182"  onMouseover="document.myForm.city.value = 'Vinton';" HREF="<?= $stationPre ?>=VTI">
</MAP>

<?php
}

?>


<?php 

function print_awos($stationPre) {

?>
<FORM name="myForm" action="nowhere">
Selected Station: <input type="text" name="city" size="30">
</FORM>

<BR><IMG class="center" SRC="/include/asosMap.gif" BORDER=0 USEMAP="#amap" ALT="ASOS Map">

<MAP NAME="amap">
<!-- #$-:Image Map file created by GIMP Imagemap Plugin -->
<!-- #$-:GIMP Imagemap Plugin by Maurits Rijk -->
<!-- #$-:Please do not edit lines starting with "#$" -->
<!-- #$VERSION:1.3 -->
<!-- #$AUTHOR:Daryl Herzmann -->
<AREA SHAPE="RECT" COORDS="294,77,332,96" onMouseover="document.myForm.city.value = 'Charles City';"  HREF="<?= $stationPre ?>=CCY">
<AREA SHAPE="RECT" COORDS="61,57,101,79" onMouseover="document.myForm.city.value = 'Sheldon';"  HREF="<?= $stationPre ?>=SHL">
<AREA SHAPE="RECT" COORDS="44,84,82,101"  onMouseover="document.myForm.city.value = 'Orange City';" HREF="<?= $stationPre ?>=ORC">
<AREA SHAPE="RECT" COORDS="33,102,73,122" onMouseover="document.myForm.city.value = 'Le Mars';"  HREF="<?= $stationPre ?>=LRJ">
<AREA SHAPE="RECT" COORDS="62,250,98,271"  onMouseover="document.myForm.city.value = 'Council Bluffs';" HREF="<?= $stationPre ?>=CBF">
<AREA SHAPE="RECT" COORDS="84,304,121,322"  onMouseover="document.myForm.city.value = 'Shenandoah';" HREF="<?= $stationPre ?>=SDA">
<AREA SHAPE="RECT" COORDS="122,310,151,326"  onMouseover="document.myForm.city.value = 'Clarinda';" HREF="<?= $stationPre ?>=ICL">
<AREA SHAPE="RECT" COORDS="97,277,136,298" onMouseover="document.myForm.city.value = 'Red Oak';"  HREF="<?= $stationPre ?>=RDK">
<AREA SHAPE="RECT" COORDS="163,277,204,300"  onMouseover="document.myForm.city.value = 'Creston';" HREF="<?= $stationPre ?>=CSQ">
<AREA SHAPE="RECT" COORDS="355,55,397,76" onMouseover="document.myForm.city.value = 'Decorah';"  HREF="<?= $stationPre ?>=DEH">
<AREA SHAPE="RECT" COORDS="343,113,378,132"  onMouseover="document.myForm.city.value = 'Oelwein';" HREF="<?= $stationPre ?>=OLZ">
<AREA SHAPE="RECT" COORDS="399,156,437,177"  onMouseover="document.myForm.city.value = 'Monticello';" HREF="<?= $stationPre ?>=MXO">
<AREA SHAPE="RECT" COORDS="464,193,497,215"  onMouseover="document.myForm.city.value = 'Clinton';" HREF="<?= $stationPre ?>=CWI">
<AREA SHAPE="RECT" COORDS="404,243,444,261" onMouseover="document.myForm.city.value = 'Muscatine';"  HREF="<?= $stationPre ?>=MUT">
<AREA SHAPE="RECT" COORDS="366,253,404,273" onMouseover="document.myForm.city.value = 'Washington';"  HREF="<?= $stationPre ?>=AWG">
<AREA SHAPE="RECT" COORDS="390,315,435,330"  onMouseover="document.myForm.city.value = 'Fort Madison';" HREF="<?= $stationPre ?>=FSW">
<AREA SHAPE="RECT" COORDS="385,332,424,352"  onMouseover="document.myForm.city.value = 'Keokuk';" HREF="<?= $stationPre ?>=EOK">
<AREA SHAPE="RECT" COORDS="347,275,380,295"  onMouseover="document.myForm.city.value = 'Fairfield';" HREF="<?= $stationPre ?>=FFL">
<AREA SHAPE="RECT" COORDS="257,253,298,271"  onMouseover="document.myForm.city.value = 'Knoxville';" HREF="<?= $stationPre ?>=OXV">
<AREA SHAPE="RECT" COORDS="241,277,279,298"  onMouseover="document.myForm.city.value = 'Chariton';" HREF="<?= $stationPre ?>=CNC">
<AREA SHAPE="RECT" COORDS="226,213,262,231" onMouseover="document.myForm.city.value = 'Ankeny';"  HREF="<?= $stationPre ?>=IKV">
<AREA SHAPE="RECT" COORDS="270,212,303,234"  onMouseover="document.myForm.city.value = 'Newton';" HREF="<?= $stationPre ?>=TNU">
<AREA SHAPE="RECT" COORDS="204,178,239,189"  onMouseover="document.myForm.city.value = 'Boone';" HREF="<?= $stationPre ?>=BNW">
<AREA SHAPE="RECT" COORDS="203,144,240,158" onMouseover="document.myForm.city.value = 'Webster City';"  HREF="<?= $stationPre ?>=EBS">
<AREA SHAPE="RECT" COORDS="213,108,249,127" onMouseover="document.myForm.city.value = 'Clarion';"  HREF="<?= $stationPre ?>=CAV">
<AREA SHAPE="RECT" COORDS="175,75,215,97" onMouseover="document.myForm.city.value = 'Algona';"  HREF="<?= $stationPre ?>=AXA">
<AREA SHAPE="RECT" COORDS="103,119,146,145" onMouseover="document.myForm.city.value = 'Storm Lake';"  HREF="<?= $stationPre ?>=SLB">
<AREA SHAPE="RECT" COORDS="182,127,216,145"  onMouseover="document.myForm.city.value = 'Fort Dodge';" HREF="<?= $stationPre ?>=FOD">
<AREA SHAPE="RECT" COORDS="139,176,174,198"  onMouseover="document.myForm.city.value = 'Carroll';" HREF="<?= $stationPre ?>=CIN">
<AREA SHAPE="RECT" COORDS="92,181,129,204"  onMouseover="document.myForm.city.value = 'Denison';" HREF="<?= $stationPre ?>=DNS">
<AREA SHAPE="RECT" COORDS="129,212,163,231"  onMouseover="document.myForm.city.value = 'Audubon';" HREF="<?= $stationPre ?>=ADU">
<AREA SHAPE="RECT" COORDS="92,220,129,239"  onMouseover="document.myForm.city.value = 'Harlan';" HREF="<?= $stationPre ?>=HNR">
<AREA SHAPE="RECT" COORDS="117,241,154,260"  onMouseover="document.myForm.city.value = 'Atlantic';" HREF="<?= $stationPre ?>=AIO">
</MAP>

<?php
}

?>


<?php 

function print_prec($stationPre) {
?>

<FORM name="myForm" action="nowhere">
Selected Station: <input type="text" name="city" size="50">
</FORM>

<BR><IMG SRC="/include/precipClimo.gif" BORDER=0 USEMAP="#pmap" ALT="Precip Climo">

<MAP NAME="pmap">
<!-- #$-:Image Map file created by GIMP Imagemap Plugin -->
<!-- #$-:GIMP Imagemap Plugin by Maurits Rijk -->
<!-- #$-:Please do not edit lines starting with "#$" -->
<!-- #$VERSION:1.3 -->
<!-- #$AUTHOR:Daryl Herzmann -->
<AREA SHAPE="RECT" COORDS="284,123,320,145" onMouseover="document.myForm.city.value = 'Waterloo;" HREF="<?= $stationPre ?>=ALO">
<AREA SHAPE="RECT" COORDS="221,64,263,91" onMouseover="document.myForm.city.value = 'Mason City';" HREF="<?= $stationPre ?>=MCW">
<AREA SHAPE="RECT" COORDS="136,45,169,67" onMouseover="document.myForm.city.value = 'Estherville';" HREF="<?= $stationPre ?>=EST">
<AREA SHAPE="RECT" COORDS="104,67,144,86" onMouseover="document.myForm.city.value = 'Spencer';" HREF="<?= $stationPre ?>=SPW">
<AREA SHAPE="RECT" COORDS="195,101,232,121" onMouseover="document.myForm.city.value = 'Clarion';" HREF="<?= $stationPre ?>=CAV">
<AREA SHAPE="RECT" COORDS="166,123,207,142" onMouseover="document.myForm.city.value = 'Fort Dodge';" HREF="<?= $stationPre ?>=FOD">
<AREA SHAPE="RECT" COORDS="30,128,68,158" onMouseover="document.myForm.city.value = 'Sioux City';" HREF="<?= $stationPre ?>=SUX">
<AREA SHAPE="RECT" COORDS="186,164,210,187" onMouseover="document.myForm.city.value = 'Boone';" HREF="<?= $stationPre ?>=BNW">
<AREA SHAPE="RECT" COORDS="210,169,242,191" onMouseover="document.myForm.city.value = 'Ames';" HREF="<?= $stationPre ?>=AMW">
<AREA SHAPE="RECT" COORDS="249,158,287,184" onMouseover="document.myForm.city.value = 'Marshalltown';" HREF="<?= $stationPre ?>=MIW">
<AREA SHAPE="RECT" COORDS="384,125,432,157" onMouseover="document.myForm.city.value = 'Dubuque';" HREF="<?= $stationPre ?>=DBQ">
<AREA SHAPE="RECT" COORDS="402,193,440,220" onMouseover="document.myForm.city.value = 'Davenport';" HREF="<?= $stationPre ?>=DVN">
<AREA SHAPE="RECT" COORDS="367,219,401,240" onMouseover="document.myForm.city.value = 'Muscatine';" HREF="<?= $stationPre ?>=MUT">
<AREA SHAPE="RECT" COORDS="328,171,366,195" onMouseover="document.myForm.city.value = 'Cedar Rapids';" HREF="<?= $stationPre ?>=CID">
<AREA SHAPE="RECT" COORDS="339,199,372,218" onMouseover="document.myForm.city.value = 'Iowa City';" HREF="<?= $stationPre ?>=IOW">
<AREA SHAPE="RECT" COORDS="368,269,407,298" onMouseover="document.myForm.city.value = 'Burlington';" HREF="<?= $stationPre ?>=BRL">
<AREA SHAPE="RECT" COORDS="278,241,314,266" onMouseover="document.myForm.city.value = 'Ottumwa';" HREF="<?= $stationPre ?>=OTM">
<AREA SHAPE="RECT" COORDS="223,251,259,277" onMouseover="document.myForm.city.value = 'Chariton';" HREF="<?= $stationPre ?>=CNC">
<AREA SHAPE="RECT" COORDS="199,202,243,236" onMouseover="document.myForm.city.value = 'Des Moines';" HREF="<?= $stationPre ?>=DSM">
<AREA SHAPE="RECT" COORDS="172,282,222,313" onMouseover="document.myForm.city.value = 'Lamoni';" HREF="<?= $stationPre ?>=LWD">
<AREA SHAPE="RECT" COORDS="97,201,125,219" onMouseover="document.myForm.city.value = 'Harlan';" HREF="<?= $stationPre ?>=HNR">
<AREA SHAPE="RECT" COORDS="90,163,126,187" onMouseover="document.myForm.city.value = 'Denison';" HREF="<?= $stationPre ?>=DNS">
</MAP>


<?php
}

?>

<?php

function rwisSelect($selected){
global $rootpath;
include("$rootpath/include/rwisLoc.php");
echo "<select name=\"station\">\n";

for ($i = 0; $i < count($Rcities); $i++) {
  $city = current($Rcities);
  echo "<option value=\"". $city["id"] ."\"";
  if ($selected == $city["id"]){
  	echo " SELECTED ";
  }
  echo " >". $city["city"] ."\n";
  next($Rcities);
} 

echo "</select>\n";

} ?>

<?php 

function print_rwis($stationPre) {
?>

<FORM name="myForm" action="nowhere">
Selected Station: <input type="text" name="city" size="30">
</FORM>

<DIV class="center">
<BR><IMG SRC="/include/rwisMap.gif" BORDER=0 USEMAP="#rmap" ALT="RWIS Map"><BR><BR>
</DIV class="center">

<MAP NAME="rmap">
<!-- #$-:Image Map file created by GIMP Imagemap Plugin -->
<!-- #$-:GIMP Imagemap Plugin by Maurits Rijk -->
<!-- #$-:Please do not edit lines starting with "#$" -->
<!-- #$VERSION:1.3 -->
<!-- #$AUTHOR:Daryl Herzmann -->
<AREA SHAPE="RECT" COORDS="394,61,439,83" onMouseover="document.myForm.city.value = 'Decorah (IA 9)';" HREF="<?= $stationPre ?>=RDEC">
<AREA SHAPE="RECT" COORDS="332,80,376,103" onMouseover="document.myForm.city.value = 'New Hampton (US 18)';" HREF="<?= $stationPre ?>=RNEW">
<AREA SHAPE="RECT" COORDS="266,47,307,67" onMouseover="document.myForm.city.value = 'Hanlontown (I-35)';" HREF="<?= $stationPre ?>=RHAN">
<AREA SHAPE="RECT" COORDS="266,85,305,105" onMouseover="document.myForm.city.value = 'Mason City(I-35)';"  HREF="<?= $stationPre ?>=RMCW">
<AREA SHAPE="RECT" COORDS="180,78,221,101" onMouseover="document.myForm.city.value = 'Algona (US 18)';"  HREF="<?= $stationPre ?>=RALG">
<AREA SHAPE="RECT" COORDS="126,72,169,95" onMouseover="document.myForm.city.value = 'Spencer (US 18)';"  HREF="<?= $stationPre ?>=RSPE">
<AREA SHAPE="RECT" COORDS="46,86,89,107"  onMouseover="document.myForm.city.value = 'Alton (IA 10)';" HREF="<?= $stationPre ?>=RATN">
<AREA SHAPE="RECT" COORDS="22,138,63,164"  onMouseover="document.myForm.city.value = 'Sioux City (I-29)';" HREF="<?= $stationPre ?>=RSIO">
<AREA SHAPE="RECT" COORDS="49,209,91,231"  onMouseover="document.myForm.city.value = 'Onawa (I-29)';" HREF="<?= $stationPre ?>=RONA">
<AREA SHAPE="RECT" COORDS="52,241,95,265"  onMouseover="document.myForm.city.value = 'Missouri Valley (I-29)';" HREF="<?= $stationPre ?>=RMIS">
<AREA SHAPE="RECT" COORDS="60,280,101,301"  onMouseover="document.myForm.city.value = 'Council Bluffs(I-80)';" HREF="<?= $stationPre ?>=RCOU">
<AREA SHAPE="RECT" COORDS="66,339,105,360"  onMouseover="document.myForm.city.value = 'Sidney (I-29)';" HREF="<?= $stationPre ?>=RSID">
<AREA SHAPE="RECT" COORDS="107,250,147,275"  onMouseover="document.myForm.city.value = 'Avoca (I-80)';" HREF="<?= $stationPre ?>=RAVO">
<AREA SHAPE="RECT" COORDS="128,308,173,329"  onMouseover="document.myForm.city.value = 'Red Oak (US 34/US 71)';" HREF="<?= $stationPre ?>=RRED">
<AREA SHAPE="RECT" COORDS="188,302,227,323"  onMouseover="document.myForm.city.value = 'Creston (US 34)';" HREF="<?= $stationPre ?>=RCRE">
<AREA SHAPE="RECT" COORDS="156,254,192,273"  onMouseover="document.myForm.city.value = 'Adair (I-80)';" HREF="<?= $stationPre ?>=RADA">
<AREA SHAPE="RECT" COORDS="141,184,179,211"  onMouseover="document.myForm.city.value = 'Carroll (US 30)';" HREF="<?= $stationPre ?>=RCAR">
<AREA SHAPE="RECT" COORDS="116,116,164,137"  onMouseover="document.myForm.city.value = 'Storm Lake (US 71/IA 3)';" HREF="<?= $stationPre ?>=RSTO">
<AREA SHAPE="RECT" COORDS="208,247,246,265"  onMouseover="document.myForm.city.value = 'De Soto (I-80/US 169)';" HREF="<?= $stationPre ?>=RDST">
<AREA SHAPE="RECT" COORDS="241,263,280,278"  onMouseover="document.myForm.city.value = 'Des Moines (I-35)';" HREF="<?= $stationPre ?>=RDSM">
<AREA SHAPE="RECT" COORDS="246,245,283,260"  onMouseover="document.myForm.city.value = 'Des Moines (I-235)';" HREF="<?= $stationPre ?>=RDES">
<AREA SHAPE="RECT" COORDS="250,231,292,245"  onMouseover="document.myForm.city.value = 'Altoona (I-80/US 65)';" HREF="<?= $stationPre ?>=RALT">
<AREA SHAPE="RECT" COORDS="233,302,267,325"  onMouseover="document.myForm.city.value = 'Osceola (I-35)';" HREF="<?= $stationPre ?>=ROSC">
<AREA SHAPE="RECT" COORDS="225,336,264,357"  onMouseover="document.myForm.city.value = 'Leon (I-35/IA 2)';" HREF="<?= $stationPre ?>=RLEO">
<AREA SHAPE="RECT" COORDS="297,332,334,357"  onMouseover="document.myForm.city.value = 'Centerville (IA 2)';" HREF="<?= $stationPre ?>=RCEN">
<AREA SHAPE="RECT" COORDS="342,306,383,325"  onMouseover="document.myForm.city.value = 'Ottumwa (US 63)';" HREF="<?= $stationPre ?>=ROTT">
<AREA SHAPE="RECT" COORDS="247,138,285,163"  onMouseover="document.myForm.city.value = 'Williams (I-35)';" HREF="<?= $stationPre ?>=RWIL">
<AREA SHAPE="RECT" COORDS="195,146,238,170"  onMouseover="document.myForm.city.value = 'Fort Dodge (US 20)';" HREF="<?= $stationPre ?>=RFOD">
<AREA SHAPE="RECT" COORDS="184,192,222,212"  onMouseover="document.myForm.city.value = 'Jefferson (IA 4) ';" HREF="<?= $stationPre ?>=RJEF">
<AREA SHAPE="RECT" COORDS="302,264,343,287"  onMouseover="document.myForm.city.value = 'Pella (IA 163)';" HREF="<?= $stationPre ?>=RPEL">
<AREA SHAPE="RECT" COORDS="248,211,289,230"  onMouseover="document.myForm.city.value = 'Ankeny (I-35)';" HREF="<?= $stationPre ?>=RANK">
<AREA SHAPE="RECT" COORDS="246,192,289,211"  onMouseover="document.myForm.city.value = 'Ames (I 35)';" HREF="<?= $stationPre ?>=RAME">
<AREA SHAPE="RECT" COORDS="352,269,389,291"  onMouseover="document.myForm.city.value = 'Sigourney (IA 92)';" HREF="<?= $stationPre ?>=RSIG">
<AREA SHAPE="RECT" COORDS="411,317,453,336"  onMouseover="document.myForm.city.value = 'Mount Pleasant (US 218) ';" HREF="<?= $stationPre ?>=RMOU">
<AREA SHAPE="RECT" COORDS="454,324,490,345"  onMouseover="document.myForm.city.value = 'Burlington (US 34)';" HREF="<?= $stationPre ?>=RBUR">
<AREA SHAPE="RECT" COORDS="409,249,446,267"  onMouseover="document.myForm.city.value = 'Iowa City (US 218)';" HREF="<?= $stationPre ?>=RIAC">
<AREA SHAPE="RECT" COORDS="373,230,410,250"  onMouseover="document.myForm.city.value = 'Williamsburg (I-80)';" HREF="<?= $stationPre ?>=RWBG">
<AREA SHAPE="RECT" COORDS="316,231,354,252"  onMouseover="document.myForm.city.value = 'Grinnell (I-80)';" HREF="<?= $stationPre ?>=RGRI">
<AREA SHAPE="RECT" COORDS="294,194,336,216"  onMouseover="document.myForm.city.value = 'Marshalltown (US 30)';" HREF="<?= $stationPre ?>=RMAR">
<AREA SHAPE="RECT" COORDS="346,147,384,166"  onMouseover="document.myForm.city.value = 'Waterloo (US 20)';" HREF="<?= $stationPre ?>=RWAT">
<AREA SHAPE="RECT" COORDS="417,143,457,167"  onMouseover="document.myForm.city.value = 'Manchester (US 20)';" HREF="<?= $stationPre ?>=RMAN">
<AREA SHAPE="RECT" COORDS="473,141,514,161"  onMouseover="document.myForm.city.value = 'Dubuque (US 20)';" HREF="<?= $stationPre ?>=RDUB">
<AREA SHAPE="RECT" COORDS="476,187,521,208"  onMouseover="document.myForm.city.value = 'Maquoketa (US 61/IA 64)';" HREF="<?= $stationPre ?>=RMAQ">
<AREA SHAPE="RECT" COORDS="375,165,414,182"  onMouseover="document.myForm.city.value = 'Urbana (I-380)';" HREF="<?= $stationPre ?>=RURB">
<AREA SHAPE="RECT" COORDS="402,197,440,217"  onMouseover="document.myForm.city.value = 'Cedar Rapids (I-380) ';" HREF="<?= $stationPre ?>=RCDR">
<AREA SHAPE="RECT" COORDS="399,217,441,230"  onMouseover="document.myForm.city.value = 'Cedar Rapids (US 30)';" HREF="<?= $stationPre ?>=RCID">
<AREA SHAPE="RECT" COORDS="411,230,447,247"  onMouseover="document.myForm.city.value = 'Iowa City (I-80)';" HREF="<?= $stationPre ?>=RIOW">
<AREA SHAPE="RECT" COORDS="449,236,482,255"  onMouseover="document.myForm.city.value = 'Tipton (I-80)';" HREF="<?= $stationPre ?>=RTIP">
<AREA SHAPE="RECT" COORDS="488,237,519,258"  onMouseover="document.myForm.city.value = 'Davenport (I-80/I-280)';" HREF="<?= $stationPre ?>=RDAV">
<AREA SHAPE="RECT" COORDS="491,214,530,233"  onMouseover="document.myForm.city.value = 'De Witt (US 30/US 61)';" HREF="<?= $stationPre ?>=RDEW">
</MAP>


<?php } ?>
