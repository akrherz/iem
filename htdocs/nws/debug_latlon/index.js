$("#thebutton").click(function(){
    var text = $("#thetext").val();
    var title = $("#thetitle").val();
    $.post(
        "generate_plot.py",
        {text: text, title: title},
        function(data){
            $("#theimage").attr("src", data.imgurl);
            $("#thegeojson").html(JSON.stringify(data.geojson));
        }
    ).fail(function() {
        alert("Image Generation Failed, sorry!");
    });
});