<?php

function determine_curve_number()
{
	if ($some_value > 2.1)
		$curve_number = 3;
	else if ($some_valie > 1.4)
		$curve_number = 2;
	else
		$curve_number = 1;
	$data[$basin][5][$storm] = $curvenumber;
}

function surface_runoff()
{
	$s = ( 1000 / $curve_number ) - 10;
	$accum_precip($basin) += $storm_precip;
	$surface_runoff = $total_surface_runoff($basin);
	$total_surface_runoff($basin) = ($accum_precip($basin) - (0.2 * $s))^2
		/ ($accum_precip($basin) + (0.8 * $s) );
	$surface_runoff = $total_surface_runoff($basin) - $surface_runoff;
	$data[$basin][6][$storm] = $surface_runoff;

}

function peak_flow()
{
	$q_peak = $qslope * $surface_runoff;
	$data[$basin][7][$storm] = $q_peak;

}

function time_of_peak_flow()
{
	$duration = $data[$basin][4][$storm];
	$duradj = (1.5 * (($duration)^2 - (7*$duration) + 6) /(-6)) +
			(3.75*($duration ^2 - (4*$duration) + 3) / 15 );
	$tpk2 = $tpk1 + $duradj;
	$tpk3 = $tpk2 + fntdif1( $data[$basin][9][$storm], 
		$data[$basin][10][$storm], $data[$basin][3][$storm], $month, $day, 
		$tbase);
	$tpk = $tpk3 * 4;
	$data[$basin][8][$storm] = $tpk3;
}

function calculate_flow_at_gage()
{
	if ($storm == 1 && $tpk - $nrise >= 1 )
	{
		$qmax($basin) = $flosum[15][$tpk - $nrise] * $farea;
	}
	if ($storm == 1 && $tpk - $nrise < 1 )
	{
		$qmax($basin) = $flosum[15][0] * $farea;
	}
	if ($storm > 1)
	{
		$farea = 0;
	}
	if ($tpk - $nrise > 1)
	{
		if ($storm > 1)
		{
			$k8 = $tpk - $nrise;
		}
	}
	// Read rise table for each time step between $tpk , $nrise
}

function flow_at_gauge()
{
	if ($storm == 1 && ($tpeak - $nrise ) >= 1)
	{
		$qmax($basin) = $flosum(15, $tpeak - $nrise) * $farea;
	}
	if ($storm == 1 && ($tpeak - $nrise ) < 1)
	{
		$qmax($basin) = $flosum(15, 0) * $farea;
	}
	if ($storm > 1)
	{
		$farea = 0;
	}
	if ($tpeak - $nrise > 1)
	{
		if ($storm > 1)
		{
			$k8 = $tpeak - $nrise;
		}
	}else {
		for($k8 = $tpeak - $nrise; $k8 <= 0; $k8++)
		{
	4650 READ RISE
		}
	} else{
		$k8 = 1;
	}
	4680 GOTO 4780
	4690 REM+++FILL IN BASEFLOW PRIOR TO SRO
	4700 IF ST%>1 THEN K8=TPK%-NRISE%:  GOTO 4780
4710 FOR K8 = 1 TO TPK%-NRISE%-1
4720 INCR= FAREA*FLOSUM%(15,K8)
4730 FLOSUM%(KK7,K8) = INCR + FLOSUM%(KK7,K8)
4740 FLOSUM%(14,K8) = FLOSUM%(14,K8) + INCR/2
4750 IF FLOSUM%(KK7,K8)> QMAX%(KK7) THEN QMAX%(KK7)=FLOSUM%(KK7,K8)
4770 NEXT K8
4780 REM+++ADD SRO TO BASEFLOW
4800 CKMARK%=0
4810 PFLAG% = 0
4820 FOR K8 =  K8 TO 240
4830 READ RISE
4840 IF RISE = 100 THEN PFLAG%=PFLAG% + 1
4850 IF RISE=0 THEN 4960
4860 INCR = QPK*RISE/100 + FAREA*FLOSUM%(15,K8)
4870 FLOSUM%(KK7,K8) = INCR + FLOSUM%(KK7,K8)
4880 FLOSUM%(14,K8) = FLOSUM%(14,K8) + INCR/2
4890 IF FLOSUM%(KK7,K8) > QMAX%(KK7) THEN QMAX%(KK7)=FLOSUM%(KK7,K8)
4910 IF CKMARK%=1 THEN 4950
4920 IF FLOSUM%(KK7,K8) <= .2*QMAX%(KK7) AND PFLAG%>0 THEN CKMARK%=1:MARK%(KK7)=K8
4930 IF K8=240 AND CKMARK%=0 THEN MARK%(KK7)=240
4940 IF OUTP%=2 AND CKMARK%=1 THEN LPRINT"SUBBASIN ";NNAME$(KK7),"STORM # ";ST%," MARK = ";K8
4950 NEXT K8
	4960 REM+++CONTINUE WITH FLOW PRECEEDING 1ST STORM
	4970 FOR K8 = K8 TO 240
	4980 INCR = FAREA*FLOSUM%(15,K8)
	4990 FLOSUM%(KK7,K8) = FLOSUM%(KK7,K8) + INCR
	5000 FLOSUM%(14,K8) = FLOSUM%(14,K8) + INCR/2
5010 IF CKMARK%=1 THEN 5050
5020 IF FLOSUM%(KK7,K8) <= .2*QMAX%(KK7) AND PFLAG%>0 THEN CKMARK%=1:MARK%(KK7)=K8
5030 IF K8=240 AND CKMARK%=0 THEN MARK%(KK7)=240
5060 NEXT K8
5080 RETURN 

}

?>
