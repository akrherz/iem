$(document).ready(() => {
    // Get the modal
    const modal = document.getElementById("myModal");
    const modalImg = document.getElementById("img01");
    // Get the image and insert it inside the modal - use its "alt" text as a caption
    $("div.clickme img").click((evt) => {
        modal.style.display = "block";
        modalImg.src = evt.target.src;
    });

    // Get the <span> element that closes the modal
    const span = document.getElementsByClassName("close")[0];

    // When the user clicks on <span> (x), close the modal
    span.onclick = () => {
        modal.style.display = "none";
    }
});
