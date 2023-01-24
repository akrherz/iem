$("#thebutton").click(function(){
    const text = $("#thetext").val();
    const title = $("#thetitle").val();
    $.post(
        "generate_plot.py",
        {text: text, title: title},
        (data) => {
            $("#theimage").attr("src", data.imgurl);
            $("#thegeojson").html(JSON.stringify(data.geojson));
        }
    ).fail(function() {
        alert("Image Generation Failed, sorry!");
    });
});
