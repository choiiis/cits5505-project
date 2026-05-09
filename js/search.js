function getSearchParams() {
    return new URLSearchParams(window.location.search);
}

function setInitialSearchValues() {
    const params = getSearchParams();

    document.getElementById("keywordSearch").value = params.get("q") || "";
    document.getElementById("locationSearch").value = params.get("location") || "";
}

function updateSearchSummary() {
    const params = getSearchParams();
    const keyword = params.get("q") || "restaurants";
    const totalResults = document.querySelectorAll(".search-restaurant-card").length;

    document.getElementById("summaryText").textContent =
        `${totalResults} results for "${keyword}"`;
}

function initBookmarks() {
    const bookmarkButtons = document.querySelectorAll("[data-bookmark]");

    bookmarkButtons.forEach(button => {
        const restaurantId = button.dataset.bookmark;

        function updateButtonState() {
            const savedIds = JSON.parse(localStorage.getItem("tableTrailBookmarks") || "[]");
            const isSaved = savedIds.includes(restaurantId);

            button.textContent = isSaved ? "♥" : "♡";
            button.classList.toggle("active", isSaved);
            button.setAttribute(
                "aria-label",
                isSaved ? "Remove from saved restaurants" : "Save restaurant"
            );
        }

        updateButtonState();

        button.addEventListener("click", () => {
            const savedIds = JSON.parse(localStorage.getItem("tableTrailBookmarks") || "[]");

            const nextSavedIds = savedIds.includes(restaurantId)
                ? savedIds.filter(id => id !== restaurantId)
                : [...savedIds, restaurantId];

            localStorage.setItem("tableTrailBookmarks", JSON.stringify(nextSavedIds));
            updateButtonState();
        });
    });
}

function initSearchPage() {
    setInitialSearchValues();
    updateSearchSummary();
    initBookmarks();
}

document.addEventListener("DOMContentLoaded", initSearchPage);