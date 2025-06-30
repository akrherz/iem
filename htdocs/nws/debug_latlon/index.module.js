import { requireElement } from '/js/iemjs/domUtils.js';

document.addEventListener("DOMContentLoaded", () => {
    const theButton = requireElement("thebutton");
    const theText = requireElement("thetext");
    const theTitle = requireElement("thetitle");
    const theImage = requireElement("theimage");
    const theGeojson = requireElement("thegeojson");

    theButton.addEventListener("click", () => {
        const text = theText.value;
        const title = theTitle.value;
        fetch("generate_plot.py", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: new URLSearchParams({ text, title })
        })
        .then(response => {
            if (!response.ok) throw new Error("Network response was not ok");
            return response.json();
        })
        .then(data => {
            theImage.setAttribute("src", data.imgurl);
            theGeojson.textContent = JSON.stringify(data.geojson);
        })
        .catch(() => {
            alert("Image Generation Failed, sorry!");
        });
    });
});
