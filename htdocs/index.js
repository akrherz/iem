/* global $ */
function onFeatureData(data) {
    $("#feature_good_votes").html(data.good);
    $("#feature_bad_votes").html(data.bad);
    $("#feature_abstain_votes").html(data.abstain);
    if (!data.can_vote) {
        $("#feature_msg").html("<i class=\"fa fa-ok\"></i> Thanks for voting!");
        $("button.feature_btn").prop("disabled", true);
    }
}
$("button.feature_btn").click((event) => {
    console.log("Clicked");
    const btn = $(event.target);
    $.get(`/onsite/features/vote/${btn.data('voting')}.json`, onFeatureData);
});
$(document).ready(() => {
    $.get("/onsite/features/vote.json", onFeatureData);
});