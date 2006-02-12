<?php 
include("../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("setup.php");

$dir = isset($_GET["dir"]) ? $_GET["dir"]: "";

$current="pics";
$TITLE = "IEM | Current Data";
include("$rootpath/include/header.php"); 
include("$rootpath/include/nav_site.php");

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
       echo '<TD>'.$instr.'</TD>';
       echo "\n";
     }
    else
     {
      echo '<TD><a href="/sites/pics.php?station='.$station.'&dir='.$instr.'">'.$instr.'</a></TD>';
      echo "\n";
     }
    }
  else
    {
     echo '<TD>'.$instr.'</TD>';
     echo "\n";
    }
}

$filename='./pics/'.$station.'/'.$station.'.jpg';
$filename_site = file_exists($filename);

if ($filename_site){
   $URL='http://mesonet.agron.iastate.edu/sites/pics/'.$station.'/'.$station.'.jpg';
   $size=getimagesize('/mesonet/www/html/sites/pics/'.$station.'/'.$station.'.jpg');
   $tag='<a href="javascript:openWindow(\''.$URL.'\')">(Site Photo)</a>';
  }
  else
  {
  $tag='(Site Photo)';
  }

$filename='./pics/'.$station.'/'.$station.'_'.$dir.'.jpg';
$filename=filecheck($filename);

?>

<script type="text/javascript" language="JavaScript">
<!-- Begin

function openWindow(link){
var subWindow=window.open(link,"new","width=<?php echo ($size[0]);?>,height=<?php echo ($size[1]);?>,toolbar,status,resizable,scrollbars,menubar,location");
}
// End -->
</script>
<br>
<TABLE>
<TR>
        <TD>
          <TABLE>
            <TR><?php printtd("NW",$dir,$station);printtd("N",$dir,$station);printtd("NE",$dir,$station)?></TR>
            <TR><?php printtd("W",$dir,$station);echo '<TD class="hlink"><IMG class="pics" border="3" SRC="'.$filename.'"  
                    alt="'.$station.' , '.$dir.'" /></TD>';printtd("E",$dir,$station);?></TR>
            <TR><?php printtd("SW",$dir,$station);printtd("S",$dir,$station);printtd("SE",$dir,$station)?></TR>
          </TABLE>
          </TD></TR>
</TABLE>
</TD></TR>
</TABLE>

<?php include("$rootpath/include/footer.php"); ?>
