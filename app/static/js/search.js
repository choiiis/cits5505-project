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

function createFallbackPin(restaurant) {
    const pin = document.createElement("button");
    pin.className = "search-map-fallback-pin";
    pin.type = "button";
    pin.style.left = `${restaurant.map_x}%`;
    pin.style.top = `${restaurant.map_y}%`;
    pin.dataset.restaurantId = restaurant.id;
    pin.setAttribute(
        "aria-label",
        `${restaurant.marker_number}. ${restaurant.name}, ${restaurant.suburb || restaurant.address}`
    );
    pin.innerHTML = `
        <span class="search-map-fallback-pin__marker">
            <span>${restaurant.marker_number}</span>
        </span>
        <span class="search-map-fallback-pin__label">
            <strong>${escapeHtml(restaurant.name)}</strong>
            <span>${escapeHtml(restaurant.suburb || restaurant.address)}</span>
        </span>
    `;

    pin.addEventListener("click", () => {
        setActiveRestaurant(restaurant.id);
    });

    return pin;
}

function renderFallbackPins(restaurants) {
    const pinLayer = document.getElementById("mapFallbackPins");
    const emptyState = document.getElementById("mapFallbackEmpty");

    if (!pinLayer) {
        return;
    }

    pinLayer.replaceChildren();

    if (emptyState) {
        emptyState.classList.toggle("is-visible", !restaurants.length);
    }

    restaurants.forEach(restaurant => {
        pinLayer.appendChild(createFallbackPin(restaurant));
    });
}

function showMapFallback() {
    const fallback = document.getElementById("mapFallback");
    const mapCanvas = document.getElementById("restaurantMap");
    const mapPreview = document.getElementById("mapPreview");
    const restaurants = getMapRestaurants();

    if (mapPreview) {
        mapPreview.classList.add("is-fallback-visible");
    }

    if (fallback) {
        fallback.classList.add("is-visible");
    }

    if (mapCanvas) {
        mapCanvas.classList.add("is-hidden");
    }

    renderFallbackPins(restaurants);
}

function hideMapFallback() {
    const fallback = document.getElementById("mapFallback");
    const mapCanvas = document.getElementById("restaurantMap");
    const mapPreview = document.getElementById("mapPreview");

    if (mapPreview) {
        mapPreview.classList.remove("is-fallback-visible");
    }

    if (fallback) {
        fallback.classList.remove("is-visible");
    }

    if (mapCanvas) {
        mapCanvas.classList.remove("is-hidden");
    }
}

window.initRestaurantSearchMap = function initRestaurantSearchMap() {
    const restaurants = getMapRestaurants();
    const mapCanvas = document.getElementById("restaurantMap");

    if (!mapCanvas || !window.google || !restaurants.length) {
        showMapFallback();
        return;
    }

    hideMapFallback();

    const map = new google.maps.Map(mapCanvas, {
        center: { lat: -31.9523, lng: 115.8613 },
        zoom: 12,
        mapTypeControl: false,
        streetViewControl: false,
        fullscreenControl: false,
    });

    const geocoder = new google.maps.Geocoder();
    const bounds = new google.maps.LatLngBounds();
    const infoWindow = new google.maps.InfoWindow();
    let resolvedMarkers = 0;
    let completedGeocodes = 0;

    restaurants.forEach((restaurant, index) => {
        geocoder.geocode(
            { address: `${restaurant.name}, ${restaurant.address}, Australia` },
            (results, status) => {
                completedGeocodes += 1;

                if (status !== "OK" || !results[0]) {
                    if (resolvedMarkers === 0 && completedGeocodes === restaurants.length) {
                        showMapFallback();
                    }

                    return;
                }

                const marker = new google.maps.Marker({
                    map,
                    position: results[0].geometry.location,
                    title: restaurant.name,
                    label: String(index + 1),
                });

                marker.restaurantId = restaurant.id;
                bounds.extend(marker.getPosition());
                resolvedMarkers += 1;

                marker.addListener("click", () => {
                    infoWindow.setContent(createInfoWindowContent(restaurant));
                    infoWindow.open(map, marker);
                    setActiveRestaurant(restaurant.id);
                });

                if (resolvedMarkers === 1) {
                    map.setCenter(marker.getPosition());
                }

                if (resolvedMarkers > 1) {
                    map.fitBounds(bounds);
                }
            }
        );
    });
};

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

    if (!window.google) {
        showMapFallback();
    }
}

document.addEventListener("DOMContentLoaded", initSearchPage);
