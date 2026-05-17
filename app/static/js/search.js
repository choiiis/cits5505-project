function initBookmarks() {
    const bookmarkButtons = document.querySelectorAll("[data-bookmark]");
    const pickerModal = document.getElementById("collectionPickerModal");
    const pickerRestaurant = document.getElementById("collectionPickerRestaurant");
    const pickerOptions = document.querySelectorAll("[data-picker-collection]");
    const saveButton = document.querySelector("[data-save-to-collections]");
    const csrfToken = document.querySelector("meta[name='csrf-token']")?.content || "";
    let activeRestaurantId = null;
    let activeBookmarkButton = null;

    function getRestaurantCollections(button) {
        try {
            return JSON.parse(button.dataset.savedCollections || "[]").map(String);
        } catch (error) {
            return [];
        }
    }

    function setModalOpen(isOpen) {
        if (!pickerModal) {
            return;
        }

        pickerModal.classList.toggle("is-open", isOpen);
        pickerModal.setAttribute("aria-hidden", String(!isOpen));
        document.body.classList.toggle("modal-open", isOpen);
    }

    bookmarkButtons.forEach(button => {
        const restaurantId = button.dataset.bookmark;

        function updateButtonState() {
            const savedCollections = getRestaurantCollections(button);
            const isSaved = savedCollections.length > 0;

            button.textContent = isSaved ? "♥" : "♡";
            button.classList.toggle("active", isSaved);
            button.setAttribute(
                "aria-label",
                isSaved ? "Edit saved collections" : "Save restaurant to collection"
            );
        }

        updateButtonState();

        button.addEventListener("click", () => {
            activeRestaurantId = restaurantId;
            activeBookmarkButton = button;

            if (pickerRestaurant) {
                pickerRestaurant.textContent = `Save ${button.dataset.restaurantName} to one or more collections.`;
            }

            const selectedCollections = getRestaurantCollections(button);

            pickerOptions.forEach(option => {
                option.classList.toggle(
                    "is-selected",
                    selectedCollections.includes(option.dataset.pickerCollection)
                );
            });

            setModalOpen(true);
        });
    });

    pickerOptions.forEach(option => {
        option.addEventListener("click", () => {
            option.classList.toggle("is-selected");
        });
    });

    document.querySelectorAll("[data-close-collection-picker]").forEach(button => {
        button.addEventListener("click", () => {
            setModalOpen(false);
        });
    });

    saveButton?.addEventListener("click", () => {
        if (!activeRestaurantId || !activeBookmarkButton) {
            return;
        }

        const selectedCollections = [...pickerOptions]
            .filter(option => option.classList.contains("is-selected"))
            .map(option => option.dataset.pickerCollection);

        saveButton.disabled = true;
        saveButton.textContent = "Saving...";

        fetch(`/restaurants/${activeRestaurantId}/collections`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": csrfToken,
            },
            credentials: "same-origin",
            body: JSON.stringify({
                collection_ids: selectedCollections,
            }),
        })
            .then(response => response.json().then(data => ({
                ok: response.ok,
                data,
            })))
            .then(({ ok, data }) => {
                if (!ok) {
                    if (data.redirect_url) {
                        window.location.href = data.redirect_url;
                        return;
                    }

                    throw new Error(data.message || "Restaurant could not be saved.");
                }

                const savedCollections = (data.collection_ids || []).map(String);

                activeBookmarkButton.dataset.savedCollections = JSON.stringify(savedCollections);
                activeBookmarkButton.textContent = savedCollections.length ? "♥" : "♡";
                activeBookmarkButton.classList.toggle("active", savedCollections.length > 0);
                saveButton.textContent = "Saved";

                window.setTimeout(() => {
                    saveButton.textContent = "Save";
                    saveButton.disabled = false;
                    setModalOpen(false);
                }, 700);
            })
            .catch(error => {
                saveButton.disabled = false;
                saveButton.textContent = error.message || "Save";
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

        if (isVisible && window.restaurantSearchMap) {
            window.setTimeout(() => {
                window.restaurantSearchMap.invalidateSize();

                if (window.restaurantSearchMapBounds && window.restaurantSearchMapBounds.isValid()) {
                    fitRestaurantSearchMap();
                }
            }, 150);
        }
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
            <span>
                ${escapeHtml(restaurant.category)}
                <span class="search-map-location-chip" style="--marker-color: ${restaurant.location_color}">
                    ${escapeHtml(restaurant.suburb || restaurant.address)}
                </span>
            </span>
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
        html: `
            <span class="search-leaflet-marker__pin" style="--marker-color: ${restaurant.location_color}"></span>
        `,
        iconSize: [28, 28],
        iconAnchor: [14, 28],
        popupAnchor: [0, -30],
    });
}

function fitRestaurantSearchMap() {
    if (!window.restaurantSearchMap || !window.restaurantSearchMapBounds) {
        return;
    }

    const restaurants = getMapRestaurants();

    if (!restaurants.length || !window.restaurantSearchMapBounds.isValid()) {
        return;
    }

    if (restaurants.length === 1) {
        window.restaurantSearchMap.setView(window.restaurantSearchMapBounds.getCenter(), 15);
    } else {
        window.restaurantSearchMap.fitBounds(
            window.restaurantSearchMapBounds,
            { padding: [64, 64], maxZoom: 14 }
        );
    }
}

function whenMapContainerIsReady(mapCanvas, callback, attempt = 0) {
    const hasSize = mapCanvas.offsetWidth > 0 && mapCanvas.offsetHeight > 0;

    if (hasSize || attempt >= 20) {
        callback();
        return;
    }

    window.setTimeout(() => {
        whenMapContainerIsReady(mapCanvas, callback, attempt + 1);
    }, 50);
}

function initRestaurantSearchMap() {
    const restaurants = getMapRestaurants();
    const mapCanvas = document.getElementById("restaurantMap");

    if (!mapCanvas || !window.L) {
        setMapEmptyState(true);
        return;
    }

    if (window.restaurantSearchMap) {
        window.restaurantSearchMap.remove();
        window.restaurantSearchMap = null;
        window.restaurantSearchMapBounds = null;
    }

    whenMapContainerIsReady(mapCanvas, () => {
        renderRestaurantSearchMap(mapCanvas, restaurants);
    });
}

function renderRestaurantSearchMap(mapCanvas, restaurants) {
    setMapEmptyState(!restaurants.length);

    const map = L.map(mapCanvas, {
        scrollWheelZoom: false,
        zoomControl: true,
    }).setView([-31.9523, 115.8613], 12);

    L.tileLayer("https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png", {
        subdomains: "abcd",
        maxZoom: 19,
        attribution: "&copy; OpenStreetMap contributors &copy; CARTO",
    }).addTo(map);

    window.restaurantSearchMap = map;

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

    window.restaurantSearchMapBounds = bounds;
    fitRestaurantSearchMap();

    [0, 150, 400].forEach(delay => {
        window.setTimeout(() => {
            map.invalidateSize();
            fitRestaurantSearchMap();
        }, delay);
    });
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
window.addEventListener("load", () => {
    if (window.restaurantSearchMap) {
        window.restaurantSearchMap.invalidateSize();
        fitRestaurantSearchMap();
    }
});
