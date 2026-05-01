function updateMapLink() {
    const keyword = document.getElementById("keywordSearch")?.value.trim() || "";
    const location = document.getElementById("locationSearch")?.value.trim() || "";
    const params = new URLSearchParams({ map: "true" });

    if (keyword) {
        params.set("q", keyword);
    }

    if (location) {
        params.set("location", location);
    }

    const mapLink = document.getElementById("mapLink");
    if (mapLink) {
        mapLink.href = `search.html?${params.toString()}`;
    }
}

document.addEventListener("DOMContentLoaded", () => {
    ["keywordSearch", "locationSearch"].forEach((id) => {
        const input = document.getElementById(id);
        if (input) {
            input.addEventListener("input", updateMapLink);
        }
    });

    updateMapLink();
});
