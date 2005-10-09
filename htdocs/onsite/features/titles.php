<?php $TITLE = "IEM | Feature Analysis";
include("../../../config/settings.inc.php");
include("$rootpath/include/database.inc.php");
include("$rootpath/include/header.php"); ?>

<h3 class="heading">IEM <i>Feature</i> Analysis</h3>

<div class="text">
<p>Recently, there has been some controversy in the department on the 
repetitiousness on the IEM <i>Feature</i> of the day.  In order to debunk
this wild speculation, this application was built to monitor the uniqueness
of the <i>Feature</i> title.</p>

<p>Listed below are all of the <i>Feature</i> titles in alphabetical order.  As
you see, none have been repeated.</p>

<table>

<?php 

  $connection = iemdb("mesosite");
  $query1 = "SELECT count(title), title, 
      to_char(valid, 'YYYY-MM-DD') as href
      from feature GROUP by title, href ORDER by title ASC";
  $result = pg_exec($connection, $query1);

  for( $i=0; $row = @pg_fetch_array($result,$i); $i++) 
  {
    if ($i == 0 || $i == 2){
      echo "<tr>\n";
    }
    echo "<td> <b>". $row['count'] ."</b> 
     <a href=\"cat.php?day=". $row['href'] ."\">".  $row['title'] ."</a></td>"; 

    if ($i % 3 == 0 && $i > 2){
      echo "</tr>\n";
    }
  }

?>

</td></tr></table>

<BR><BR></div>

<?php include("$rootpath/include/footer.php"); ?>

