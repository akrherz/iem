<?php

/**
 * Helper to generate a set of links on common download pages
 * @param string $current the current page to avoid linking to
 * @return string HTML content for the related links section
 */
function aviation_request_related_links($current): string
{
    $links = array(
        "cwas.phtml" => array(
            "href" => "/request/gis/cwas.phtml",
            "label" => "CWSU Center Weather Advisories",
        ),
        "awc_gairmets.phtml" => array(
            "href" => "/request/gis/awc_gairmets.phtml",
            "label" => "AWC G-AIRMETs",
        ),
        "pireps.php" => array(
            "href" => "/request/gis/pireps.php",
            "label" => "PIREPs",
        ),
        "awc_sigmets.phtml" => array(
            "href" => "/request/gis/awc_sigmets.phtml",
            "label" => "SIGMETs",
        ),
        "taf" => array(
            "href" => "/request/taf.php",
            "label" => "TAFs",
        ),
        "tempwind_aloft" => array(
            "href" => "/request/tempwind_aloft.php",
            "label" => "Temp/Winds Aloft",
        ),
    );

    $buttons = "";
    foreach ($links as $key => $link) {
        if ($key === $current) {
            continue;
        }
        $buttons .= sprintf(
            '<a class="btn btn-outline-primary btn-sm" href="%s">%s</a>',
            $link["href"],
            $link["label"]
        );
    }

    return <<<EOM
<section class="card shadow-sm mb-4" aria-labelledby="related-links-heading">
  <div class="card-body">
    <h2 id="related-links-heading" class="h5 card-title mb-3">Related Links</h2>
    <div class="d-flex flex-wrap gap-2">
      {$buttons}
    </div>
  </div>
</section>
EOM;
}
