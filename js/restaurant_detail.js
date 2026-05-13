document.addEventListener("DOMContentLoaded", function () {
    const bookmarkBtn = document.querySelector(".restaurant-bookmark-btn");
    const openReviewPanelButtons = document.querySelectorAll(".open-review-panel");
    const closeReviewPanelButton = document.getElementById("closeReviewPanel");
    const reviewOverlay = document.getElementById("reviewOverlay");
    const reviewSlidePanel = document.getElementById("reviewSlidePanel");
    const isLoggedIn = true;
    const reviewLoginMessage = document.getElementById("reviewLoginMessage");
    const reviewForm = document.getElementById("reviewForm");

    function escapeHtml(value) {
        return String(value || "").replace(/[&<>"']/g, function (character) {
            return {
                "&": "&amp;",
                "<": "&lt;",
                ">": "&gt;",
                '"': "&quot;",
                "'": "&#039;",
            }[character];
        });
    }

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

    function initRestaurantLocationMap() {
        const mapCanvas = document.getElementById("restaurantLocationMap");

        if (!mapCanvas || !window.L) {
            return;
        }

        let markerData = null;

        try {
            markerData = JSON.parse(mapCanvas.dataset.mapMarker || "null");
        } catch (error) {
            markerData = null;
        }

        if (!markerData || !markerData.latitude || !markerData.longitude) {
            mapCanvas.classList.add("restaurant-location-map--empty");
            mapCanvas.textContent = "Map unavailable";
            return;
        }

        const position = [markerData.latitude, markerData.longitude];
        const map = L.map(mapCanvas, {
            scrollWheelZoom: false,
            zoomControl: true,
        }).setView(position, 15);

        L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
            attribution: "&copy; OpenStreetMap contributors &copy; CARTO",
            maxZoom: 19,
        }).addTo(map);

        const markerIcon = L.divIcon({
            className: "restaurant-location-marker",
            html: '<span class="restaurant-location-marker__pin"></span>',
            iconSize: [28, 28],
            iconAnchor: [14, 28],
            popupAnchor: [0, -28],
        });

        L.marker(position, {
            icon: markerIcon,
            title: markerData.name,
        })
            .addTo(map)
            .bindPopup(
                `<strong>${escapeHtml(markerData.name)}</strong><br>${escapeHtml(markerData.address)}`
            );

        setTimeout(function () {
            map.invalidateSize();
        }, 100);
    }

    if (bookmarkBtn) {
        bookmarkBtn.addEventListener("click", function () {
            bookmarkBtn.classList.toggle("active");
            bookmarkBtn.textContent = bookmarkBtn.classList.contains("active") ? "\u2665" : "\u2661";
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

    initRestaurantLocationMap();
});
