<?php 
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("setup.php");

$dir = isset($_GET["dir"]) ? $_GET["dir"]: "";

$THISPAGE = "iem-sites";
$TITLE = "IEM | Site Photos";
include("$rootpath/include/header.php"); 
?>
<?php $current = "pics"; include("sidebar.php"); ?>
<?php
function filecheck($file){
  global $rooturl;
  $test=file_exists($file);
  if ($test!="TRUE")
   {
     $file="$rooturl/images/nophoto.png";
   }

  return $file;
}


function printtd($instr,$selected,$station){

  $filename='./pics/'.$station.'/'.$station.'_'.$instr.'.jpg'; 
  $present = file_exists($filename);
  if ($present)
    {
    if ($instr == $selected)
     {
       echo '<TD align="center" style="background: #ee0;">'.$instr.'</TD>';
       echo "\n";
     }
    else
     {
      echo '<TD align="center"><a href="pics.php?station='.$station.'&dir='.$instr.'">'.$instr.'</a></TD>';
      echo "\n";
     }
    }
  else
    {
     echo '<TD align="center">'.$instr.'</TD>';
     echo "\n";
    }
}

$filename='./pics/'.$station.'/'.$station.'.jpg';
$filename_site = file_exists($filename);
if ($dir != ""){
 $filename='pics/'.$station.'/'.$station.'_'.$dir.'.jpg';
 $filename=filecheck($filename);
}

?>

<h3>Directional Photos</h3>

<p>This application shows you photos of the observation site if they are
available.  In general, the IEM only has photos for some of the sites in 
Iowa...</p>

<TABLE>
            <TR><?php printtd("NW",$dir,$station);printtd("N",$dir,$station);printtd("NE",$dir,$station)?></TR>
            <TR><?php printtd("W",$dir,$station);echo '<TD class="hlink"><IMG class="pics" border="3" SRC="'.$filename.'"  
                    alt="'.$station.' , '.$dir.'" /></TD>';printtd("E",$dir,$station);?></TR>
            <TR><?php printtd("SW",$dir,$station);printtd("S",$dir,$station);printtd("SE",$dir,$station)?></TR>
          </TABLE>
<?php
$filename='./pics/'.$station.'/'.$station.'_span.jpg';
$lfilename='./pics/'.$station.'/'.$station.'_pan.jpg';
if (file_exists($filename))
{
  echo "<h3>Panoramic Shot</h3><img src=\"$filename\"><br /><a href=\"$lfilename\">Full resolution version</a>";
}



?>
<?php include("$rootpath/include/footer.php"); ?>
