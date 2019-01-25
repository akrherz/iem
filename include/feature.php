<?php
  // Here is where we start pulling station Information
function printTags($tokens)
{
  if (sizeof($tokens) == 0 || $tokens[0] == ""){ return "";}
  $s = "<br /><span style=\"font-size: smaller; float: left;\">Tags: &nbsp; ";
  while (list($k,$v) = each($tokens))
  {
    $s .= sprintf("<a href=\"/onsite/features/tags/%s.html\">%s</a> &nbsp; ", 
    		$v, $v);
  }
  $s .= "</span>";
  return $s;
}

?>