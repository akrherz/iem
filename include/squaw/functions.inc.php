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
}}}

?>