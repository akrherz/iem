<?php

/*
 * This is a histogram class that accepts and unidimensional array of data
 * Returns 2 arrays by using the getStats() and getBins() methods.
 * (c) Jesus M. Castagnetto, 1999.
 * Gnu GPL'd code, see www.fsf.org for the details.
 */


class Histogram {

	/* variables */

	var $N,$MIN,$MAX,$AVG,$STDV,$SUM,$SUM2,$NBINS;
	var $BINS = array();
	var $BINGRAPH = array();
	var $STATS = array();

	/* Constructor */

	function Histogram($data="", $nbins=0, $title="") {
		if ($data && $nbins) {
			$this->create($data,$nbins,$title);
		}
	}

	/* Create the histogram */
	
	function create($data,$nbins,$title="") {
		
		/* Check if we got a valid set of data and bins */
		(($this->N = count($data)) > 1) or die("Not enough data, number of values: ".$this->N."\n");
		($this->NBINS = $nbins) > 1 or die("Insuficient number of bins\n");
		
		/* initialize values */
		$this->MIN = (float) min($data);
		$this->MAX = (float) max($data);
		$delta = (float) ($this->MAX - $this->MIN)/$this->NBINS;
		$this->setTitle($title);
		
		/* init bins array */
		for ($i=0; $i < $this->NBINS; $i++) {
			$bin[$i] = (float) $this->MIN + $delta * $i;
			$this->BINS[ (string) $bin[$i] ] = 0;
		}
		
		/* stats */
		for ($i = 0; $i < $this->N ; $i++) {
			$this->SUM += (float) $data[$i];
			$this->SUM2 += (float) pow($data[$i],2);
		}
		$this->AVG = $this->SUM/$this->N;
		$this->STDV = sqrt(($this->SUM2 - $this->N*pow($this->AVG,2))/(float)($this->N - 1));

		/* make the STATS array */
		$this->STATS =	array (
									'MIN'=>$this->MIN,
									'MAX'=>$this->MAX,
									'N'=>$this->N,
									'SUM'=>$this->SUM,
									'SUM2'=>$this->SUM2,
									'AVG'=>$this->AVG,
									'STDV'=>$this->STDV,
									'NBINS'=>$this->NBINS
								);

		/* calculate frequencies and populate bins array */
		sort($data);
		$tmp = ($this->NBINS - 1);
		for ($i = 0; $i < $this->N; $i++) {
			for ($j = $tmp; $j >= 0; $j--) {
				if ($data[$i] >= $bin[$j]) {
					$this->BINS[ (string) $bin[$j] ]++;
					break;
				}
			}
		}
	}


	/* sets the Title */
	function setTitle($title) {
		$this->TITLE=$title;
	}

	/* send back STATS array */
	function getStats() {
		return $this->STATS;
	}

	/* send back BINS array */
	function getBins() {
		return $this->BINS;
	}

	/* send back BINS array suitable for plotting with class.graph */
	function getGraphBins() {
		while (list($k,$v) = each($this->BINS)) {
			$bin[] = sprintf("%5.2f",$k); $val[] = $v;
		}
		$bingraph = array($bin,$val);
		return $bingraph;
	}

	/* simple printStats */
	function printStats() {
		$s = "Statistics for histogram: ".$this->TITLE."\n";
		$s .= sprintf("N = %8d\t\tMin = %-8.4f\tMax = %-8.4f\tAvg = %-8.4f\n",$this->N,$this->MIN,$this->MAX,$this->AVG);
		$s .= sprintf("StDev = %-8.4f\tSum = %-8.4f\tSum^2 = %-8.4f\n",$this->STDV,$this->SUM,$this->SUM2);
		echo $s;
	}

	/* simple printBins */
	function printBins() {
		echo "Number of bins: ".count($this->BINS)."\n";
		echo "BIN\tVAL\t\tFREQ\n";
		$maxbin = max($this->BINS);
		reset($this->BINS);
		for ($i = 0; $i < $this->NBINS; $i++) {
			list($key,$val) = each($this->BINS);
			echo sprintf("%d\t%-8.4f\t%-8d |%s\n",$i+1,$key,$val,$this->_printBar($val,$maxbin));
		}
	}

	/* internal function to generate the histogram bars */
	function _printBar($val,$maxbin) {
		$fact = (float) ($maxbin > 40) ? 40/$maxbin : 1;
		$niter = (int) $val * $fact;
		$out = "";
		for ($i=0; $i<$niter; $i++) 
			$out .= "*";
		return $out;
	}

} /* end of Histogram class */

?>
