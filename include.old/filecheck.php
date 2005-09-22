<?php

function filecheck($file){

  $test=file_exists($file);
  if ($test!="TRUE")
   {
     $file="/images/nophoto.png";
   }

  return $file;
}

