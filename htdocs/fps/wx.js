// The current weather widget
function wxCurrents(){
    // Show Weather
    $.ajax({
        url: "/json/current.py?network=ISUSM&station=BOOI4",
        dataType: "json",
        success: function(data) {
            var dt = moment.utc(data.last_ob.utc_valid);
            $("#wxtime").text(dt.local().format("LT"));
            var tmpf = data.last_ob["airtemp[F]"].toFixed(1);
            $("#tmpf").text(tmpf);
            var pday = data.last_ob["precip_today[in]"];
            pday = (pday === null) ? "0.00": pday.toFixed(2);
            $("#pday").text(pday);
            var soil4 = data.last_ob["c1tmpf[F]"].toFixed(1);
            $("#soil4").text(soil4);
        }
    });

}

$(document).ready(function() {
    wxCurrents();
    window.setInterval(wxCurrents, 120000);
});