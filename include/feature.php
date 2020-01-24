<?php
  // Here is where we start pulling station Information
function printTags($tokens)
{
  if (sizeof($tokens) == 0 || $tokens[0] == ""){ return "";}
  $s = "<br /><span style=\"font-size: smaller; float: left;\">Tags: &nbsp; ";
  foreach($tokens as $k => $v)
  {
    $s .= sprintf("<a href=\"/onsite/features/tags/%s.html\">%s</a> &nbsp; ", 
    		$v, $v);
  }
  $s .= "</span>";
  return $s;
}

?>