document.addEventListener("DOMContentLoaded", () => {
    // Category Filtering Logic
    const filterButtons = document.querySelectorAll(".filter-btn");
    const galleryCards = document.querySelectorAll(".gallery-card");

    filterButtons.forEach(button => {
        button.addEventListener("click", () => {
            filterButtons.forEach(btn => btn.classList.remove("active"));
            button.classList.add("active");

            const filterValue = button.getAttribute("data-filter");

            galleryCards.forEach(card => {
                if (filterValue === "all" || card.getAttribute("data-category") === filterValue) {
                    card.style.display = "block";
                } else {
                    card.style.display = "none";
                }
            });
        });
    });

    // Lightbox Modal Logic
    const modal = document.getElementById("image-modal");
    const modalImg = document.getElementById("modal-img");
    const captionText = document.getElementById("modal-caption");
    const closeModal = document.querySelector(".close-modal");

    galleryCards.forEach(card => {
        card.addEventListener("click", () => {
            const img = card.querySelector("img");
            const title = card.querySelector("h4").innerText;
            modal.style.display = "block";
            modalImg.src = img.src;
            captionText.innerText = title;
        });
    });

    closeModal.addEventListener("click", () => {
        modal.style.display = "none";
    });

    modal.addEventListener("click", (e) => {
        if (e.target === modal) {
            modal.style.display = "none";
        }
    });
});