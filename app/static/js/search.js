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

    setMapVisible(true);
}

function getMapRestaurants() {
    const mapPreview = document.getElementById("mapPreview");

    if (!mapPreview) {
        return [];
    }

    try {
        return JSON.parse(mapPreview.dataset.mapRestaurants || "[]");
    } catch (error) {
        return [];
    }
}

function setActiveRestaurant(restaurantId) {
    document.querySelectorAll("[data-restaurant-id]").forEach(card => {
        const isActive = card.dataset.restaurantId === String(restaurantId);
        card.classList.toggle("search-restaurant-card--active", isActive);

        if (isActive) {
            card.scrollIntoView({ behavior: "smooth", block: "nearest" });
        }
    });
}

function escapeHtml(value) {
    const element = document.createElement("span");
    element.textContent = value || "";
    return element.innerHTML;
}

function createInfoWindowContent(restaurant) {
    return `
        <div class="search-map-info">
            <strong>${escapeHtml(restaurant.name)}</strong>
            <span>${escapeHtml(restaurant.category)} · ${escapeHtml(restaurant.suburb || restaurant.address)}</span>
            <span>${Number(restaurant.rating).toFixed(1)} (${restaurant.review_count} reviews)</span>
            <a href="${restaurant.detail_url}">View details</a>
        </div>
    `;
}

function setMapEmptyState(isVisible) {
    const emptyState = document.getElementById("mapFallbackEmpty");

    if (emptyState) {
        emptyState.classList.toggle("is-visible", isVisible);
    }
}

function createLeafletIcon(restaurant) {
    return L.divIcon({
        className: "search-leaflet-marker",
        html: `<span>${restaurant.marker_number}</span>`,
        iconSize: [34, 34],
        iconAnchor: [17, 34],
        popupAnchor: [0, -30],
    });
}

function initRestaurantSearchMap() {
    const restaurants = getMapRestaurants();
    const mapCanvas = document.getElementById("restaurantMap");

    if (!mapCanvas || !window.L) {
        setMapEmptyState(true);
        return;
    }

    setMapEmptyState(!restaurants.length);

    const map = L.map(mapCanvas, {
        scrollWheelZoom: false,
        zoomControl: true,
    }).setView([-31.9523, 115.8613], 12);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution: "&copy; OpenStreetMap contributors",
    }).addTo(map);

    if (!restaurants.length) {
        return;
    }

    const bounds = L.latLngBounds();

    restaurants.forEach(restaurant => {
        const position = [restaurant.latitude, restaurant.longitude];
        const marker = L.marker(position, {
            icon: createLeafletIcon(restaurant),
            title: restaurant.name,
        }).addTo(map);

        marker.restaurantId = restaurant.id;
        bounds.extend(position);

        marker.bindPopup(createInfoWindowContent(restaurant));
        marker.on("click", () => {
            setActiveRestaurant(restaurant.id);
        });
    });

    if (restaurants.length === 1) {
        map.setView(bounds.getCenter(), 14);
    } else {
        map.fitBounds(bounds, { padding: [44, 44], maxZoom: 14 });
    }

    window.setTimeout(() => map.invalidateSize(), 0);
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
    initBookmarks();
    initMapToggle();
    initFilterToggle();
    initRestaurantSearchMap();
}

document.addEventListener("DOMContentLoaded", initSearchPage);
