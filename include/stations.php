<?php

function networkSelect($dbconn, $network, $selected, $orderby="name")
{
  $rs = pg_prepare($dbconn, "Q", "SELECT * from stations WHERE network = $1
                                  ORDER by $orderby ASC");
  $rs = pg_execute($dbconn, "Q", Array($network));

  $s = "<select name=\"station\">\n";
  for($i=0;$row=@pg_fetch_array($rs,$i);$i++)
  {
    $s .= "<option value=\"". $row["id"] ."\" ";
    if ($selected == $row["id"]) { $s .= "SELECTED"; }
    $s .= ">[".$row["id"]."] ". $row["name"] ."</option>\n";
  }
  $s .= "</select>";
  return $s;
}
?>
