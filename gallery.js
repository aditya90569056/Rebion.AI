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

    // Lightbox / Collage Modal Logic
    const modal = document.getElementById("image-modal");
    const collage = document.getElementById("modal-collage");
    const captionText = document.getElementById("modal-caption");
    const closeModal = document.querySelector(".close-modal");

    function getCardImages(card) {
        // A card may define a group of photos via data-images="a.jpeg,b.jpeg".
        // Otherwise fall back to the card's single visible image.
        const group = card.getAttribute("data-images");
        if (group) {
            return group.split(",").map(src => src.trim()).filter(Boolean);
        }
        const img = card.querySelector("img");
        return img ? [img.getAttribute("src")] : [];
    }

    function openModal(card) {
        const images = getCardImages(card);
        if (!images.length) return;

        const title = card.querySelector("h4") ? card.querySelector("h4").innerText : "Media Gallery";

        collage.innerHTML = "";
        collage.classList.toggle("single", images.length === 1);

        images.forEach(src => {
            const image = document.createElement("img");
            image.src = src;
            image.alt = title;
            image.className = "collage-item";
            collage.appendChild(image);
        });

        captionText.innerText = title + "  •  " + images.length + (images.length === 1 ? " photo" : " photos");
        modal.style.display = "block";
        document.body.style.overflow = "hidden";
    }

    function closeLightbox() {
        modal.style.display = "none";
        document.body.style.overflow = "";
    }

    galleryCards.forEach(card => {
        card.addEventListener("click", () => openModal(card));
    });

    closeModal.addEventListener("click", closeLightbox);

    modal.addEventListener("click", (e) => {
        if (e.target === modal) {
            closeLightbox();
        }
    });

    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && modal.style.display === "block") {
            closeLightbox();
        }
    });
});
