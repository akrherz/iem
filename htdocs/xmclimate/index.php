<?php $TITLE = "IEM | xmClimate"; include("/mesonet/php/include/header.php"); ?>

<script LANGUAGE="JavaScript">     
<!-- Begin 
function search(form) { 
 
isstation(form) 
allblanks2(form) 
 
} 
         function allblanks2(form) { 
                if (isstation(form) == true) { 
                location="/cgi-bin/xmclimate/searchClimData?station=" + document.form.result.value;
              }  
                else { 
                       compose(form) 
                }
        } 
 
 
        function isstation(form) { 
                teststation=(document.form.result.value.length); 
                if (teststation < 2) { 
                        return false 
                } 
                else { 
                        return true 
                } 
        } 
 
function validate(form) { 
                 
isstat(form) 
allblanks(form) 
 
} 
         function allblanks(form) { 
                if (isstat(form) == true) { 
                for (i=0;i<document.form.radio.length;i++) { 
                if (document.form.radio[i].checked){ 
                break 
                } 
                } 
                location="/cgi-bin/xmclimate/getClimData?form_test=true&station=" + document.form.result.value + "&monthname=" + document.form.Month.options[document.form.Month.selectedIndex].text + "&ob_norm=" + document.form.radio[i].value + "&year=" + document.form.Year.options[document.form.Year.selectedIndex].text; 
                }  
                else { 
                       compose(form) 
                } 
                 
        } 
 
function compose(form) { 
                var text = "Please check the following:"    
                if(isstat(form) == false) { 
                        text += "\n* You must select a station before submitting" 
                } 
                 
           alert(text) 
        } 
        function isstat(form) { 
                teststat=(document.form.result.value.length); 
                if (teststat < 2) { 
                        return false 
                } 
                else { 
                        return true 
                } 
        } 
         
function tempstat(statname) { 
document.form.temp.value = statname; 
} 
// End --> 
</script> 
 
<form name="form"> 
<table border="0" cellpadding="0" cellspacing="0">
  <tr>
    <td colspan=2>
     <b>Select Network:</b>  
       <a href="index.php?network=ASOS">ASOS</a>
  </td></tr>
 
  <tr>
    <td colspan=2>  
      <b>Selected Site:</b><INPUT TYPE="text" NAME="temp" SIZE=20 > 
    </td></tr>

  <tr> 
    <td rowspan="2"> 
<IMG SRC="/include/asosMap.gif" BORDER=0 USEMAP="#amap" ALT="ASOS Map">
<MAP NAME="amap">
<!-- #$-:Image Map file created by GIMP Imagemap Plugin -->
<!-- #$-:GIMP Imagemap Plugin by Maurits Rijk -->
<!-- #$-:Please do not edit lines starting with "#$" -->
<!-- #$VERSION:1.3 -->
<!-- #$AUTHOR:Daryl Herzmann -->
<AREA SHAPE="RECT" COORDS="143,43,179,64" onMouseover="document.form.temp.value = 'Estherville';"  HREF="javascript:changeSite('KEST')">
<AREA SHAPE="RECT" COORDS="107,66,146,86"  onMouseover="document.form.temp.value = 'Spencer';" HREF="javascript:changeSite('KSPW')">
<AREA SHAPE="RECT" COORDS="44,84,82,101"  onMouseover="document.form.temp.value = 'Orange City';" HREF="javascript:changeSite('KORC')">
<AREA SHAPE="RECT" COORDS="19,138,61,161" onMouseover="document.form.temp.value = 'Sioux City';"  HREF="javascript:changeSite('KSUX')">
<AREA SHAPE="RECT" COORDS="194,317,235,340"  onMouseover="document.form.temp.value = 'Lamoni';" HREF="javascript:changeSite('KLWD')">
<AREA SHAPE="RECT" COORDS="309,129,345,146" onMouseover="document.form.temp.value = 'Waterloo';"  HREF="javascript:changeSite('KALO')">
<AREA SHAPE="RECT" COORDS="435,141,470,159"  onMouseover="document.form.temp.value = 'Dubuque';" HREF="javascript:changeSite('KDBQ')">
<AREA SHAPE="RECT" COORDS="363,192,400,212"  onMouseover="document.form.temp.value = 'Cedar Rapids';" HREF="javascript:changeSite('KCID')">
<AREA SHAPE="RECT" COORDS="377,217,411,237" onMouseover="document.form.temp.value = 'Iowa City';"  HREF="javascript:changeSite('KIOW')">
<AREA SHAPE="RECT" COORDS="444,217,483,238" onMouseover="document.form.temp.value = 'Davenport';"  HREF="javascript:changeSite('KDVN')">
<AREA SHAPE="RECT" COORDS="409,301,446,316"  onMouseover="document.form.temp.value = 'Burlington';" HREF="javascript:changeSite('KBRL')">
<AREA SHAPE="RECT" COORDS="308,269,344,289"  onMouseover="document.form.temp.value = 'Ottumwa';" HREF="javascript:changeSite('KOTM')">
<AREA SHAPE="RECT" COORDS="218,231,257,247"  onMouseover="document.form.temp.value = 'Des Moines';" HREF="javascript:changeSite('KDSM')">
<AREA SHAPE="RECT" COORDS="224,188,257,200" onMouseover="document.form.temp.value = 'Ames';"  HREF="javascript:changeSite('KAMW')">
<AREA SHAPE="RECT" COORDS="273,170,312,191"  onMouseover="document.form.temp.value = 'Marshalltown';" HREF="javascript:changeSite('KMIW')">
<AREA SHAPE="RECT" COORDS="243,68,279,89"  onMouseover="document.form.temp.value = 'Mason City';" HREF="javascript:changeSite('KMCW')">

</MAP>
    </td> 
    <td valign="top"> 
      <p><span style="background-color: #FFFF00"><b>Selected Site:</b> 
        </span> <INPUT TYPE="text" NAME="result" SIZE=20 > 
      </p> 
      <p><input type="radio" value="Observed%20Data" checked name="radio"><span style="background-color: #FFFF00"><b>Observed Data</b></span></p> 
        <p><input type="radio" value="Normals" name="radio"><span style="background-color: #FFFF00"><b>Normals</b></span></p> 
        <p><input type="radio" value="Records" name="radio"><span style="background-color: #FFFF00"><b>Records</b></span></p> 
    <p><b><span style="background-color: #FFFF00">Select Month:</span></b> 
<script LANGUAGE="JavaScript">     
<!-- Begin 
now = new Date() 
mon = (now.getMonth()) 
text='<select name=Month>' 
for (i=1; i<13 ; i++) { 
   mon = (mon+1) 
   if (mon == 13) { 
   mon = 1} 
   if (mon==1){ 
   montext="January"; 
   } 
   if (mon==2){ 
   montext="February"; 
   } 
   if (mon==3){ 
   montext="March"; 
   } 
   if (mon==4){ 
   montext="April"; 
   } 
   if (mon==5){ 
   montext="May"; 
   } 
   if (mon==6){ 
   montext="June"; 
   } 
   if (mon==7){ 
   montext="July"; 
   } 
   if (mon==8){ 
   montext="August"; 
   } 
   if (mon==9){ 
   montext="September"; 
   } 
   if (mon==10){ 
   montext="October"; 
   } 
   if (mon==11){ 
   montext="November"; 
   } 
   if (mon==12){ 
   montext="December"; 
   }   
   if (i==1) { 
   text += '\n<option selected value="' + montext + '">'+ montext+'</option>';  
   }else{ 
   text += '\n<option value="' + montext + '">'+ montext+'</option>'; 
   } 
  } 
text += '</select>'; 
document.write(text); 
 
 
// End --> 
</script> 
</p> 
    <p> <span style="background-color: #FFFF00"><b>Select Year:</b>&nbsp;&nbsp;&nbsp; 
    </span> 
    <select name=Year size="1"> 
     <option selected value=2001>2001</option> 
     <option value=" "></option> 
<option value=" "></option> 
<option value=" "></option> 
<option value=" "></option> 
<option value=" "></option> 
<option value=" "></option> 
<option value=" "></option> 
<option value=" "></option> 
<option value=" "></option> 
<option value=" "></option> 
<option value=" "></option> 
<option value=" "></option> 
    </select> 
    <p align="left"><SCRIPT LANGUAGE="JavaScript"><!-- 
function changeSite(item) {		// Show the name of the clicked site in  
	flag = document.form.result.value 
	document.form.result.value = item;		// the result box. 
        nowy = new Date()
        yr = (nowy.getYear())
        if ( yr < 1000) {
        yr = yr + 1900;
        }
        statyr = yr; 
//	if (item == "DSM") { 
	  statyr = 1948; 
//	  } 
	 
j = ( yr - statyr) 
yrar = new Array() 
document.form.Year.options.length = 0; // removes all options. 
yr = (yr+1) 
for (i=0; i<j+1 ; i++) { 
  yrar[i] = (yr - 1) 
 yr=(yr-1) 
 } 
  
for (i=0;i<(yrar.length);i++) { 
 document.form.Year.options[i] = new Option(yrar[i],yrar[i]);  
} 
document.form.Year.options[0].selected=true;  
} 
// End --> 
</SCRIPT> 
<input TYPE="button" VALUE="Submit" onClick="validate(this.form)"> 
        <p>&nbsp;</p> 
       </td> 
  </tr> 
  <tr> 
    <td valign="top" align="center" bgcolor="#FFFF00"> 
      <p align="center">&nbsp;<b>To search on 
      selected fields, click the search button below after selecting a site.</b><p align="center"><input TYPE="button" VALUE="Search" onClick="search(this.form)"> 
    </td> 
  </tr> 
  <tr> 
    <td height="21"> 
      <p align="center"> 
      <a href="/index.php"><span style="background-color: #FFFFFF">Mesonet Homepage</span></a></p> 
    </td> 
    <td height="21"> 
      <p align="center"></td> 
  </tr> 
</table> 
</form> 
 
<?php include("/mesonet/php/include/footer.php"); ?>
