$(document).ready(() => {
    // Get the modal
    const modal = document.getElementById("myModal");
    const modalImg = document.getElementById("img01");
    // Get the image and insert it inside the modal - use its "alt" text as a caption
    $("div.clickme img").click(function(img){
        console.log(img);
        modal.style.display = "block";
        modalImg.src = this.src;
    });

    // Get the <span> element that closes the modal
    var span = document.getElementsByClassName("close")[0];

    // When the user clicks on <span> (x), close the modal
    span.onclick = function() {
        modal.style.display = "none";
    }
});
