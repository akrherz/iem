<?php

/**
 * Generate the long URL for radmap calls.
 *
 * @param int $basets The base timestamp for the radmap request.
 * @param int $tzoff The timezone offset in seconds to apply to the base timestamp.
 * @param int $imgi The image index to determine how far back in time to go for the radar data.
 * @param int $interval The interval in minutes between radar images.
 * @param int $width The width of the radar image in pixels.
 * @param int $height The height of the radar image in pixels.
 * @param string $tz The timezone identifier for the radar image timestamps.
 * @param int $zoom The zoom level for the radar image, where 100 represents the default zoom.
 * @param float $lon0 The longitude of the center point for the radar image.
 * @param float $lat0 The latitude of the center point for the radar image.
 * @param array $layers An array of layer identifiers to include in the radar image (e.g., "goes_vis", "nexrad", "warnings").
 * @param string $warngeo The geographic scope for warnings to include in the radar image (e.g., "both", "county", "sbw").
 * @param int $lsrwindow The time window in minutes for including Local Storm Reports (LSRs) in the radar image, centered around the base timestamp.
 * @return string The generated URL for the radmap request based on the provided parameters.
 */
function generate_radmap_url(
    $basets,
    $tzoff,
    $imgi,
    $interval,
    $width,
    $height,
    $tz,
    $zoom,
    $lon0,
    $lat0,
    $layers,
    $warngeo,
    $lsrwindow,
){
    $url = "/GIS/radmap.php?";

    /* Set us ahead to UTC and then back into the archive */
    $ts = $basets + $tzoff - ($imgi * 60 * $interval);
    $url .= sprintf(
        "ts=%s&width=%s&height=%s&tz=%s&",
        date("YmdHi", $ts),
        $width,
        $height,
        $tz
    );

    $lpad = $zoom / 100.0;
    $url .= sprintf(
        "bbox=%.3f,%.3f,%.3f,%.3f&",
        $lon0 - $lpad,
        $lat0 - $lpad,
        $lon0 + $lpad,
        $lat0 + $lpad
    );
    if (in_array("goes_vis", $layers)) {
        $url .= "layers[]=goes&goes_product=VIS&";
    }
    if (in_array("goes_wv", $layers)) {
        $url .= "layers[]=goes&goes_product=WV&";
    }
    if (in_array("goes_ir", $layers)) {
        $url .= "layers[]=goes&goes_product=IR&";
    }

    if (in_array("goes_east1V", $layers)) {
        $url .= "layers[]=goes&goes_product=VIS&";
    }
    if (in_array("goes_west1V", $layers)) {
        $url .= "layers[]=goes&goes_product=VIS&";
    }

    if (in_array("goes_west04I4", $layers)) {
        $url .= "layers[]=goes&goes_product=IR&";
    }
    if (in_array("goes_east04I4", $layers)) {
        $url .= "layers[]=goes&goes_product=IR&";
    }

    if (in_array("interstates", $layers)) {
        $url .= "layers[]=interstates&";
    }
    if (in_array("usdm", $layers)) {
        $url .= "layers[]=usdm&";
    }
    if (in_array("uscounties", $layers)) {
        $url .= "layers[]=uscounties&";
    }
    if (in_array("cwas", $layers)) {
        $url .= "layers[]=cwas&";
    }
    if (in_array("cwsu", $layers)) {
        $url .= "layers[]=cwsu&";
    }
    if (in_array("watches", $layers)) {
        $url .= "layers[]=watches&";
    }
    if (in_array("nexrad", $layers)) {
        $url .= "layers[]=nexrad&";
    } else if (in_array("prn0q", $layers)) {
        $url .= "layers[]=prn0q&";
    } else if (in_array("hin0q", $layers)) {
        $url .= "layers[]=hin0q&";
    } else if (in_array("akn0q", $layers)) {
        $url .= "layers[]=akn0q&";
    }

    if (in_array("warnings", $layers)) {
        if ($warngeo == "both" or $warngeo == "county") {
            $url .= "layers[]=county_warnings&";
        }
        if ($warngeo == "both" or $warngeo == "sbw") {
            $url .= "layers[]=sbw&";
        }
    }

    if ($lsrwindow > 0) {
        $lsr_etime = $ts + ($lsrwindow * 60);
        $lsr_stime = $ts - ($lsrwindow * 60);
        $url .= sprintf(
            "layers[]=lsrs&ts1=%s&ts2=%s",
            date("YmdHi", $lsr_stime),
            date("YmdHi", $lsr_etime)
        );
    }
    return $url;
}
