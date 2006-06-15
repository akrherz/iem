<?php

// SimpleLinearRegression.php

// Copyright 2003, Paul Meagher
// Distributed under GPL  

require_once "Distribution.php";

class SimpleLinearRegression {
  
  var $n; 
  var $X = array();
  var $Y = array();  
  var $ConfInt;  
  var $Alpha;
  var $XMean;
  var $YMean;
  var $SumXX;
  var $SumXY;
  var $SumYY;  
  var $Slope;
  var $YInt;  
  var $PredictedY   = array();
  var $Error        = array();
  var $SquaredError = array();
  var $TotalError;  
  var $SumError;
  var $SumSquaredError;  
  var $ErrorVariance;
  var $StdErr;
  var $SlopeStdErr;  
  var $SlopeVal;   // T value of Slope 
  var $YIntStdErr;    
  var $YIntTVal;   // T value for Y Intercept
  var $R;
  var $RSquared;    
  var $DF;         // Degrees of Freedom
  var $SlopeProb;  // Probability of Slope Estimate
  var $YIntProb;   // Probability of Y Intercept Estimate
  var $AlphaTVal;  // T Value for given alpha setting
  var $ConfIntOfSlope;        
  
  var $RPath  = "/usr/local/lib/R/bin/R"; // Your path here   
     
  var $format = "%01.2f"; // Used for formatting output 
     
  function SimpleLinearRegression($X, $Y, $ConfidenceInterval) {

    $numX = count($X);
    $numY = count($Y);

    if ($numX != $numY) {
      die("Error: Size of X and Y vectors must be the same.");

    } 
    if ($numX <= 1) { 
      die("Error: Size of input array must be at least 2.");      
    }
    
    $this->n                    = $numX;
    $this->X                    = $X;
    $this->Y                    = $Y;  

    $this->ConfInt              = $ConfidenceInterval;    
    $this->Alpha                = (100 - $this->ConfInt) / 100;
       
    $this->XMean                = $this->getMean($this->X);
    $this->YMean                = $this->getMean($this->Y);
    $this->SumXX                = $this->getSumXX();
    $this->SumYY                = $this->getSumYY();
    $this->SumXY                = $this->getSumXY();    
    $this->Slope                = $this->getSlope();
    $this->YInt                 = $this->getYInt();
    $this->PredictedY           = $this->getPredictedY();
    $this->Error                = $this->getError();
    $this->SquaredError         = $this->getSquaredError();
    $this->SumError             = $this->getSumError();
    $this->TotalError           = $this->getTotalError();    
    $this->SumSquaredError      = $this->getSumSquaredError();    
    $this->ErrorVariance        = $this->getErrorVariance();    
    $this->StdErr               = $this->getStdErr();  
    $this->SlopeStdErr          = $this->getSlopeStdErr();         
    $this->YIntStdErr           = $this->getYIntStdErr();             
    $this->SlopeTVal            = $this->getSlopeTVal();            
    $this->YIntTVal             = $this->getYIntTVal();                
    $this->R                    = $this->getR();                
    $this->RSquared             = $this->getRSquared();  
    $this->DF                   = $this->getDF();                        
    
    
    $dist = new Distribution;  
    $this->SlopeProb            = $dist->getStudentT($this->SlopeTVal, $this->DF);                        
    $this->YIntProb             = $dist->getStudentT($this->YIntTVal, $this->DF);         
    $this->AlphaTVal            = $dist->getInverseStudentT($this->Alpha, $this->DF); 
    
    /*
    
    // If you have R installed you can compare output use these methods
    // instead of 3 methods above.  The Alpha value that R expects is 
    // computed differently and is included as well.

    $this->Alpha                = (1 + ($this->ConfInt / 100) ) / 2; 
        
    $this->SlopeProb            = $this->getStudentProb($this->SlopeTVal, $this->DF);                         
    $this->YIntProb             = $this->getStudentProb($this->YIntTVal, $this->DF);          
    $this->AlphaTVal            = $this->getInverseStudentProb($this->Alpha, $this->DF);                            
    
    */
                              
    $this->ConfIntOfSlope       = $this->getConfIntOfSlope();          

    return true;
  }

  function getMean($data) {  
    $mean = 0.0;
    $sum  = 0.0;     
    for ($i = 0; $i < $this->n; $i++) {
      $sum += $data[$i];
    }
    $mean  = $sum/$this->n;   
    return $mean;
  }

  function getSumXX(){  
    $SumXX = 0.0;     
    for ($i = 0; $i < $this->n; $i++) {
      $SumXX += ($this->X[$i] - $this->XMean) * ($this->X[$i] - $this->XMean);
    }   
    return $SumXX;
  }

  function getSumYY(){  
    $SumYY = 0.0;     
    for ($i = 0; $i < $this->n; $i++) {
      $SumYY += ($this->Y[$i] - $this->YMean) * ($this->Y[$i] - $this->YMean);
    }   
    return $SumYY;
  }

  function getSumXY(){  
    $SumXY = 0.0;     
    for ($i = 0; $i < $this->n; $i++) {
      $SumXY += ($this->X[$i] - $this->XMean) * ($this->Y[$i] - $this->YMean);
    }
    return $SumXY;
  }

  function getSlope() {
    $Slope = 0.0;
    $Slope = $this->SumXY / $this->SumXX;
    return $Slope;
  }

  function getYInt() {
    $YInt = 0.0;
    $YInt = $this->YMean - ($this->Slope * $this->XMean);
    return $YInt;
  }

  function getPredictedY(){       
    for ($i = 0; $i < $this->n; $i++) {
      $PredictedY[$i] = $this->YInt + ($this->Slope * $this->X[$i]);
    }   
    return $PredictedY;
  }

  function getError() {          
    $Error = array();
    for ($i = 0; $i < $this->n; $i++) {
      $Error[$i] = $this->Y[$i] - $this->PredictedY[$i];
    }   
    return $Error;
  }

  function getTotalError() {          
    $TotalError = 0.0;
    for ($i = 0; $i < $this->n; $i++) {
      $TotalError += pow(($this->Y[$i] - $this->YMean), 2);
    }   
    return $TotalError;
  }

  function getSquaredError() {          
    $SquaredError = array();
    for ($i = 0; $i < $this->n; $i++) {
      $SquaredError[$i] = pow(($this->Y[$i] - $this->PredictedY[$i]), 2);
    }   
    return $SquaredError;
  }

  function getSumError() {   
    $SumError = 0.0;       
    for ($i = 0; $i < $this->n; $i++) {
      $SumError += $this->Error[$i];
    }   
    return $SumError;
  }

  function getSumSquaredError() {   
    $SumSquaredError = 0.0;       
    for ($i = 0; $i < $this->n; $i++) {
      $SumSquaredError += $this->SquaredError[$i];
    }   
    return $SumSquaredError;
  }

  function getErrorVariance() {   
    $ErrorVariance = 0.0;       
    $ErrorVariance = $this->SumSquaredError / ($this->n - 2);   
    return $ErrorVariance;
  }

  function getStdErr() {   
    $StdErr = 0.0;       
    $StdErr = sqrt($this->ErrorVariance);   
    return $StdErr;
  }

  function getSlopeStdErr() {   
    $SlopeStdErr = 0.0;       
    $SlopeStdErr = $this->StdErr / sqrt($this->SumXX);   
    return $SlopeStdErr;
  }

  function getYIntStdErr() {  
    $YIntStdErr = 0.0;       
    $YIntStdErr = $this->StdErr * sqrt(1 / $this->n + pow($this->XMean, 2) / $this->SumXX);   
    return $YIntStdErr;
  }

  function getSlopeTVal() {   
    $SlopeTVal = 0.0;       
    $SlopeTVal = $this->Slope / $this->SlopeStdErr;   
    return $SlopeTVal;
  }

  function getYIntTVal() {   
    $YIntTVal = 0.0;       
    $YIntTVal = $this->YInt / $this->YIntStdErr;  
    return $YIntTVal;
  }

  function getR() {   
    $R = 0.0;       
    $R = $this->SumXY / sqrt($this->SumXX * $this->SumYY);
    return $R;
  }

  function getRSquared() {  
    $RSquared = 0.0;       
    $RSquared = $this->R * $this->R;   
    return $RSquared;
  }

  function getDF() {    
    $DF = 0.0;       
    $DF = $this->n - 2;
    return $DF;
  }

  function getStudentProb($T, $df) {    
    $Probability = 0.0;   
    $cmd = "echo 'dt($T, $df)' | $this->RPath --slave";    
    $result = shell_exec($cmd);    
    list($LineNumber, $Probability) = explode(" ", trim($result));    
    return $Probability;
  }

  function getStudentProb($T, $df) {    
    $Probability = 0.0;   
    $cmd = "echo 'dt($T, $df)' | $this->RPath --slave";   
    $result = shell_exec($cmd);    
    list($LineNumber, $Probability) = explode(" ", trim($result));    
    return $Probability;
  }

  function getInverseStudentProb($alpha, $df) {    
    $InverseProbability = 0.0;   
    $cmd = "echo 'qt($alpha, $df)' | $this->RPath --slave";    
    $result = shell_exec($cmd);    
    list($LineNumber, $InverseProbability) = explode(" ", trim($result));    
    return $InverseProbability;
  }

  function getConfIntOfSlope() {    
    $ConfIntOfSlope = 0.0;        
    $ConfIntOfSlope = $this->AlphaTVal * $this->SlopeStdErr ;        
    return $ConfIntOfSlope;
  }
    
}
?>
