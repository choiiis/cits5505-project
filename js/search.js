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

function initMapToggle() {
    const mapToggle = document.getElementById("mapToggle");
    const mapButton = document.getElementById("mapButton");
    const mapPreview = document.getElementById("mapPreview");

    if (!mapToggle || !mapPreview) {
        return;
    }

    function setMapVisible(isVisible) {
        mapToggle.checked = isVisible;
        mapPreview.classList.toggle("d-none", !isVisible);
    }

    mapToggle.addEventListener("change", event => {
        setMapVisible(event.target.checked);
    });

    if (mapButton) {
        mapButton.addEventListener("click", () => {
            setMapVisible(!mapToggle.checked);
        });
    }
}

function initFilterToggle() {
    const filterToggle = document.getElementById("filterToggle");
    const filterPanel = document.getElementById("filterPanel");

    if (!filterToggle || !filterPanel) {
        return;
    }

    filterToggle.addEventListener("click", () => {
        const isOpen = filterPanel.classList.toggle("active");

        filterToggle.textContent = isOpen ? "Hide filters" : "Show filters";
        filterToggle.setAttribute("aria-expanded", String(isOpen));
        filterToggle.classList.toggle("btn-outline-dark", !isOpen);
        filterToggle.classList.toggle("btn-dark", isOpen);
    });
}

function initSearchPage() {
    setInitialSearchValues();
    updateSearchSummary();
    initBookmarks();
    initMapToggle();
    initFilterToggle();
}

document.addEventListener("DOMContentLoaded", initSearchPage);