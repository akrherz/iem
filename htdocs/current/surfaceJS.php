<HTML>
<HEAD>
	<TITLE>IEM | Surface Data Viewer</TITLE>

<script language="JavaScript">

image0=new Image();
image1=new Image();
image2=new Image();
image3=new Image();
image4=new Image();

areaString = "";
currentNum = "0";
currentTime = "";

basicURL = "/data/";
image0name = "surfaceTW.gif";
image1name = "surfaceDW.gif";
image2name = "surfaceMD.gif";
image3name = "surfaceTE.gif";

image0.src="0surfaceTW.gif";
image1.src="0surfaceDW.gif";
image2.src="0surfaceMD.gif";
image3.src="0surfaceTE.gif";


function changeArea(pref) {
	areaString = pref;
	showImage(currentNum);
}

function changeTime(selT) {
	currentTime = selT;
	showImage(currentNum);
}

function showImage(num) {
	currentNum = num;
	if (num=="0")  document.pic.src = basicURL + currentTime + areaString + image0name;
        if (num=="1")  document.pic.src = basicURL + currentTime + areaString + image1name;
        if (num=="2")  document.pic.src = basicURL + currentTime + areaString + image2name;
        if (num=="3")  document.pic.src = basicURL + currentTime + areaString + image3name;
}

</script>

</HEAD>
<BODY BGCOLOR="WHITE">

<form method="GET" action="">

<TABLE>

<TR>
   <TD colspan="3">
<input type="radio" name="time" onClick="changeTime('0'); return true;" CHECKED>Current
<input type="radio" name="time" onClick="changeTime('2'); return true;"> -1 hour
<input type="radio" name="time" onClick="changeTime('4'); return true;"> -2 hour
<input type="radio" name="time" onClick="changeTime('6'); return true;"> -3 hour
<input type="radio" name="time" onClick="changeTime('8'); return true;"> -4 hour
<input type="radio" name="time" onClick="changeTime('10'); return true;"> -5 hour
   </TD>
</TR>

<TR>
   <TD colspan="3">
<input type="radio" name="type" onClick="showImage(0); return true;" CHECKED>Surface Temps
<input type="radio" name="type" onClick="showImage(1); return true;">Surface Dew Point
<input type="radio" name="type" onClick="showImage(2); return true;">Surface Moisture Div
<input type="radio" name="type" onClick="showImage(3); return true;">Surface Theta-E
   </TD>
</TR>

<TR>
  <TD colspan="3">
<IMG SRC="0surfaceTW.gif" name="pic" WIDTH="720" HEIGHT="540" BORDER=0>
  </TD>
</TR>

</TABLE>

</BODY>

</HTML>

