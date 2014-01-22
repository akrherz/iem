<?php 
/*
 * My purpose in life is to produce pics
 */
include("../../config/settings.inc.php");
include("../../include/database.inc.php");
include("setup.php");

include("../../include/myview.php");
$t = new MyView();

$dir = isset($_GET["dir"]) ? $_GET["dir"]: "";

$filename='/mesonet/share/pics/'.$station.'/'.$station.'.jpg'; 
$puri='pics/'.$station.'/'.$station.'.jpg';

if ($dir != ""){
 $filename='/mesonet/share/pics/'.$station.'/'.$station.'_'.$dir.'.jpg';
 $puri='pics/'.$station.'/'.$station.'_'.$dir.'.jpg';
}
if (! file_exists($filename)){
	$puri = sprintf('%s/images/nophoto.png', $rooturl);
}

$t->thispage = "iem-sites";
$t->title = "Site Photos";

$t->sites_current = "pics"; 


function printtd($instr,$selected,$station){
  	global $network;
  	$s = "";
  	$filename='/mesonet/share/pics/'.$station.'/'.$station.'_'.$instr.'.jpg';
  	if (file_exists($filename)){ 
  		if ($instr == $selected){
       	$s .= '<TD align="center" style="background: #ee0;">'.$instr.'</TD>';
       	$s .= "\n";
    	} else {
      	$s .= '<TD align="center"><a href="pics.php?network='.$network.'&station='.$station.'&dir='.$instr.'">'.$instr.'</a></TD>';
      	$s .= "\n";
    	}
	} else {
     $s .= '<td align="center">'.$instr.'</td>';
     $s .= "\n";
    }
	return $s;
}

$table = sprintf("<tr>%s%s%s</tr><tr>%s%s%s</tr><tr>%s%s%s</tr>",
 		printtd("NW",$dir,$station), printtd("N",$dir,$station), 
		printtd("NE",$dir,$station), printtd("W",$dir,$station),
 	"<td><img src=\"{$puri}\" alt=\"{$station} {$dir}\" /></td>",
    	printtd("E",$dir,$station), printtd("SW",$dir,$station),
  		printtd("S",$dir,$station), printtd("SE",$dir,$station));

$more = "";
$filename='/mesonet/share/pics/'.$station.'/'.$station.'_span.jpg';
$puri='pics/'.$station.'/'.$station.'_span.jpg';
$lfilename='/mesonet/share/pics/'.$station.'/'.$station.'_pan.jpg';
$pluri='pics/'.$station.'/'.$station.'_pan.jpg';
if (file_exists($filename))
{
	$more = "<h3>Panoramic Shot</h3><img src=\"$puri\"><br /><a href=\"$pluri\">Full resolution version</a>";
}
if (file_exists("/mesonet/share/pics/$station/HEADER.html")){
	$more .= "<p><strong>". file_get_contents("/mesonet/share/pics/$station/HEADER.html") ."</strong>";
}


$t->content = <<<EOF
<h3>Directional Photos</h3>

<p>This application shows you photos of the observation site if they are
available.  In general, the IEM only has photos for some of the sites in 
Iowa...</p>

<p><a href="pics.php?network={$network}&station={$station}">Site Photo</a>

<table>
{$table}
</table>

{$more}
EOF;
$t->render('sites.phtml');
?>
