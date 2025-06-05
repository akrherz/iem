
/**
 * Initialize modal functionality for soil temperature images
 */
function initializeModal() {
    // Get the modal elements
    const modal = document.getElementById("myModal");
    const modalImg = document.getElementById("img01");
    const span = document.getElementsByClassName("close")[0];

    if (!modal || !modalImg || !span) {
        return;
    }

    // Add click handlers to all clickable images
    const clickableImages = document.querySelectorAll("div.clickme img");
    clickableImages.forEach(img => {
        img.addEventListener("click", (evt) => {
            modal.style.display = "block";
            modalImg.src = evt.target.src;
        });
    });

    // Close modal when clicking the close button
    span.addEventListener("click", () => {
        modal.style.display = "none";
    });

    // Close modal when clicking outside the image
    modal.addEventListener("click", (evt) => {
        if (evt.target === modal) {
            modal.style.display = "none";
        }
    });
}

/**
 * Initialize the soil temperature page functionality
 */
function init() {
    initializeModal();
}

// Initialize when DOM is loaded
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
} else {
    init();
}
