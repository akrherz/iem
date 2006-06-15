<?php

// Distribution.php

// Copyright 2003, John Pezullo
// Released under same terms as PHP.
// PHP Port and OO'fying by Paul Meagher

class Distribution {

  function doCommonMath($q, $i, $j, $b) {
    
    $zz = 1; 
    $z  = $zz; 
    $k  = $i; 
    
    
    while($k <= $j) { 
      $zz = $zz * $q * $k / ($k - $b); 
      $z  = $z + $zz; 
      $k  = $k + 2; 
    }
    return $z;
  }
    
  function getStudentT($t, $df) {  

    $t  = abs($t); 
    $w  = $t  / sqrt($df); 
    $th = atan($w);
    
    if ($df == 1) { 
      return 1 - $th / (pi() / 2); 
    }
  
    $sth = sin($th); 
    $cth = cos($th);
  
    if( ($df % 2) ==1 ) { 
      return 1 - ($th + $sth * $cth * $this->doCommonMath($cth * $cth, 2, $df - 3, -1)) / (pi()/2);
    } else {
      return 1 - $sth * $this->doCommonMath($cth * $cth, 1, $df - 3, -1); 
    }
  
  }
  
  function getInverseStudentT($p, $df) { 
    
    $v =  0.5; 
    $dv = 0.5; 
    $t  = 0;
    
    while($dv > 1e-6) { 
      $t = (1 / $v) - 1; 
      $dv = $dv / 2; 
      if ( $this->getStudentT($t, $df) > $p) { 
        $v = $v - $dv;
      } else { 
        $v = $v + $dv;
      } 
    }
    return $t;
  }
  

  function getFisherF($f, $n1, $n2) {
    
    $x = $n2 / ($n1 * $f + $n2);
        
    if(($n1%2)==0) { 
      return $this->doCommonMath(1-$x, $n2, $n1+$n2-4, $n2-2) * pow($x, $n2/2); 
    }
    if(($n2%2)==0){ 
      return 1 - $this->doCommonMath($x, $n1, $n1+$n2-4, $n1-2) * pow(1-$x, $n1/2); 
    }
    $th = atan(sqrt($n1 * $f / $n2)); 
    $a = $th / (pi() / 2); 
    $sth = sin($th); 
    $cth = cos($th);
    if($n2 > 1) { 
      $a = $a + $sth * $cth * $this->doCommonMath($cth*$cth, 2, $n2-3, -1) / (pi()/2);  
    }
    if($n1==1) { 
      return 1 - $a; 
    }
    $c = 4 * $this->doCommonMath($sth*$sth, $n2+1, $n1+$n2-4, $n2-2)* $sth * pow($cth,$n2) / pi();
    if($n2==1) { 
      return 1 - $a + $c/2; 
    }
    $k=2; 
    while($k<=($n2-1)/2) {
      $c = $c * $k/($k-.5); 
      $k=$k+1; 
    }
    return 1-$a+$c;
  }

  function getInverseFisherF($p, $n1, $n2) { 
    
    $v = 0.5; 
    $dv = 0.5; 
    $f = 0.0;
   
    while($dv > 1e-10) { 
      
      $f  = (1 / $v) - 1; 
      $dv = $dv / 2; 

      if($this->getFisherF($f, $n1, $n2) > $p) { 
        $v = $v - $dv; 
      } else { 
        $v = $v + $dv; 
      } 
    }
    return $f;
  }

}
?>
