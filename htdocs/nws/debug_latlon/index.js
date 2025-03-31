/* global $ */
$("#thebutton").click(() => {
    const text = $("#thetext").val();
    const title = $("#thetitle").val();
    $.post(
        "generate_plot.py",
        {text, title},
        (data) => {
            $("#theimage").attr("src", data.imgurl);
            $("#thegeojson").html(JSON.stringify(data.geojson));
        }
    ).fail(() => {
        alert("Image Generation Failed, sorry!"); // skipcq
    });
});
