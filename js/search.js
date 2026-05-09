function getSearchParams() {
    return new URLSearchParams(window.location.search);
}

function getRestaurants() {
    if (!window.AppData || !window.AppData.restaurants) {
        return [];
    }

    return window.AppData.restaurants;
}

function setInitialSearchValues() {
    const params = getSearchParams();

    document.getElementById("keywordSearch").value = params.get("q") || "";
    document.getElementById("locationSearch").value = params.get("location") || "";
}

function updateSearchSummary() {
    const params = getSearchParams();
    const keyword = params.get("q") || "restaurants";
    const totalResults = getRestaurants().length;

    document.getElementById("summaryText").textContent =
        `${totalResults} results for "${keyword}"`;
}

function initSearchPage() {
    setInitialSearchValues();
    updateSearchSummary();
}

document.addEventListener("DOMContentLoaded", initSearchPage);