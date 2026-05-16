document.addEventListener("DOMContentLoaded", function () {
    const bookmarkBtn = document.querySelector(".restaurant-bookmark-btn");
    const openReviewPanelButtons = document.querySelectorAll(".open-review-panel");
    const closeReviewPanelButton = document.getElementById("closeReviewPanel");
    const reviewOverlay = document.getElementById("reviewOverlay");
    const reviewSlidePanel = document.getElementById("reviewSlidePanel");
    const isLoggedIn = Boolean(window.tableTrailIsLoggedIn);
    const reviewLoginMessage = document.getElementById("reviewLoginMessage");
    const reviewForm = document.getElementById("reviewForm");

    function openReviewPanel() {
        if (!reviewOverlay || !reviewSlidePanel) return;

        reviewOverlay.classList.add("active");
        reviewSlidePanel.classList.add("active");
        document.body.style.overflow = "hidden";
    }

    function closeReviewPanel() {
        if (!reviewOverlay || !reviewSlidePanel) return;

        reviewOverlay.classList.remove("active");
        reviewSlidePanel.classList.remove("active");
        document.body.style.overflow = "";
    }

    if (bookmarkBtn) {
        bookmarkBtn.addEventListener("click", function () {
            bookmarkBtn.classList.toggle("active");
            bookmarkBtn.textContent = bookmarkBtn.classList.contains("active") ? "♥" : "♡";
        });
    }

    openReviewPanelButtons.forEach(function (button) {
        button.addEventListener("click", openReviewPanel);
    });

    if (closeReviewPanelButton) {
        closeReviewPanelButton.addEventListener("click", closeReviewPanel);
    }

    if (reviewOverlay) {
        reviewOverlay.addEventListener("click", closeReviewPanel);
    }
    if (reviewLoginMessage && reviewForm) {
        if (isLoggedIn) {
            reviewLoginMessage.style.display = "none";
            reviewForm.style.display = "flex";
        } else {
            reviewLoginMessage.style.display = "block";
            reviewForm.style.display = "none";
        }
    }
});
