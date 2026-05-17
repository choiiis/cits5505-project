document.addEventListener("DOMContentLoaded", function () {
    const bookmarkBtn = document.querySelector(".restaurant-bookmark-btn");
    const openReviewPanelButtons = document.querySelectorAll(".open-review-panel");
    const closeReviewPanelButton = document.getElementById("closeReviewPanel");
    const reviewOverlay = document.getElementById("reviewOverlay");
    const reviewSlidePanel = document.getElementById("reviewSlidePanel");
    const isLoggedIn = Boolean(window.tableTrailIsLoggedIn);
    const reviewLoginMessage = document.getElementById("reviewLoginMessage");
    const reviewForm = document.getElementById("reviewForm");

    const reviewFilterForm = document.getElementById("reviewFilterForm");
    const reviewList = document.getElementById("reviewList");
    const clearReviewFilters = document.getElementById("clearReviewFilters");

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

    async function updateReviews(url) {
        if (!reviewList) return;

        reviewList.classList.add("is-loading");

        try {
            const response = await fetch(url, {
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            });

            if (!response.ok) {
                throw new Error("Unable to load reviews.");
            }

            const html = await response.text();
            reviewList.innerHTML = html;

            const browserUrl = url.replace("/reviews", "") + "#reviews";
            window.history.replaceState({}, "", browserUrl);
        } catch (error) {
            console.error(error);

            reviewList.innerHTML = `
                <div class="review-item">
                    <p class="mb-0 text-secondary">Unable to update reviews. Please try again.</p>
                </div>
            `;
        } finally {
            reviewList.classList.remove("is-loading");
        }
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

    if (reviewFilterForm) {
        reviewFilterForm.addEventListener("submit", function (event) {
            event.preventDefault();

            const formData = new FormData(reviewFilterForm);
            const params = new URLSearchParams(formData);
            const url = `${reviewFilterForm.action}?${params.toString()}`;

            updateReviews(url);
        });
    }

    if (clearReviewFilters && reviewFilterForm) {
        clearReviewFilters.addEventListener("click", function (event) {
            event.preventDefault();

            reviewFilterForm.reset();
            updateReviews(reviewFilterForm.action);
        });
    }
});