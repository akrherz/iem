<?php 
 /** Module for displaying currents */

class sortables {
 var $url;
 var $sortcol;
 var $addFavorites = true;
 var $data = Array();
 var $threshold = 3600;
 var $dvars = Array(
   "station" => Array("title" => "Site ID", "fmt" => "%s"),
   "sname" => Array("title" => "Site Name", "fmt" => "%s"),
   "ts" => Array("title" => "Ob Valid", "fmt" => "%I:%M %p", "time" => "true"),
    ); // Which variables to display!

 function sortables() {
 } // End of function Sortables()


 function addDisplayVars($newVars){
   while ( list($key,$val) = each($newVars) ){
     $this->dvars[$key] = $val;
   }
 } // End of function addDisplayVar

 function sort($sortcol, $sortdir="desc"){
  $this->sortcol = $sortcol;
  $this->sortdir = $sortdir;

  while (list($firstIndex, ) = each($this->data))
     $indexMap[$firstIndex] = $this->data[$firstIndex]->db[$sortcol];
  if ($sortdir == "desc") arsort($indexMap);
  else asort($indexMap);
  while (list($firstIndex, ) = each($indexMap))
    if (is_numeric($firstIndex))  $sortedArray[] = $this->data[$firstIndex];
    else $sortedArray[$firstIndex] = $this->data[$firstIndex];

//  echo $sortcol;
//  print_r($indexMap);
  $this->data = $sortedArray;
 }

 function printHTML() {
   $sbuf = Array();
   $osbuf = Array();

   $sbuf[] = "<table bgcolor=\"#ffffff\" border=1 cellspacing=0 cellpadding=2>";
   reset($this->dvars);
   $s = "<tr bgcolor=\"#336699\">";
   if ($this->addFavorites)
     $s .= "<td>Add:</td>";
   while ( list($k, $var) = each($this->dvars) ){
     $s .= "<td><font color=\"#fffacd\">". $var["title"] ."</font><br><a href=\"". $this->url . $k ."/asc\"><img src=\"/dv/pics/up-arrow.gif\" ";
     if ($k == $this->sortcol && $this->sortdir == "asc") $s .= "border=2";
     else $s .= "border=0";
     $s .= "></a><a href=\"". $this->url . $k ."/desc\"><img src=\"/dv/pics/down-arrow.gif\" ";
     if ($k == $this->sortcol && $this->sortdir == "desc") $s .= "border=2";
     else $s .= "border=0";
     $s .= "></a></td>";
   }
   $sbuf[] = $s ."</tr>";

   $c = 0;
   $now = time();
   while( list($key, $iemob) = each($this->data) ){
     $s = "<tr ";
     if ($c) $s .= "bgcolor=\"#EEEEEE\""; $c = ! $c;
     $s .= ">";
     if ($this->addFavorites)
       $s .= "<td><input type=\"checkbox\" name=\"st[]\" value=\"$key\"></td>";
     $old = ( ($now - $iemob->db["ts"]) > $this->threshold ) ? 1 : 0;
     if ($old){
       $osbuf[] = $s . sprintf("<td colspan=\"%s\">%s (%s) Offline</td></tr>\n",
          sizeof($this->dvars), $iemob->db["sname"], $key);
       continue;
     }

     reset($this->dvars);
     while( list($k, $var) = each($this->dvars) ){
       if ( $var["time"] ){
         $s .= sprintf("<td>". strftime($var["fmt"], $iemob->db[$k]) ."</td>");
         continue;
       }
       $qc = $iemob->db["qc_". $k];
       if (strlen($qc) == 0)
         $s .= sprintf("<td>". $var["fmt"] ."</td>", $iemob->db[$k]);
       else
         $s .= sprintf("<td>%s</td>", $iemob->db["qc_". $k]);
     }
     $sbuf[] = $s ."</tr>";
   }
   $sbuf[] = implode($osbuf, "\n");
   $sbuf[] = "</table>";

   return implode($sbuf, "\n");

 } // End of printCurrentsHTML

} ?>
