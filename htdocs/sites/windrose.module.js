document.addEventListener('DOMContentLoaded', () => {
    const imageModal = document.getElementById('imageModal');
    if (imageModal) {
        imageModal.addEventListener('show.bs.modal', (event) => {
            // Get the element that triggered the modal (could be the anchor or img)
            let triggerElement = event.relatedTarget;

            // If we clicked on the image, get the parent anchor element
            if (triggerElement && triggerElement.tagName === 'IMG') {
                triggerElement = triggerElement.closest('a[data-bs-toggle="modal"]');
            }

            if (triggerElement) {
                const imageSrc = triggerElement.getAttribute('data-bs-image');
                const imageTitle = triggerElement.getAttribute('data-bs-title');
                const modalImage = document.getElementById('modalImage');
                const modalTitle = imageModal.querySelector('.modal-title');

                if (imageSrc) {
                    modalImage.src = imageSrc;
                    modalImage.alt = imageTitle || 'Wind rose';
                }
                if (imageTitle && modalTitle) {
                    modalTitle.textContent = imageTitle;
                }
            }
        });
    }
});
