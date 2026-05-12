function buildMapQuery() {
    const keyword = document.getElementById("keywordSearch")?.value.trim() || "";
    const location = document.getElementById("locationSearch")?.value.trim() || "";

    if (keyword && location) {
        return `${keyword} restaurants near ${location}, Western Australia`;
    }

    if (location) {
        return `restaurants near ${location}, Western Australia`;
    }

    if (keyword) {
        return `${keyword} restaurants near Perth, Western Australia`;
    }

    return "restaurants near Perth, Western Australia";
}

function updateMapPreview() {
    const mapFrame = document.getElementById("homeMapFrame");
    const mapLink = document.getElementById("homeMapLink");
    const query = buildMapQuery();
    const params = new URLSearchParams({
        q: query,
        z: "13",
        output: "embed",
    });
    const searchParams = new URLSearchParams({
        api: "1",
        query,
    });

    if (mapFrame) {
        mapFrame.src = `https://maps.google.com/maps?${params.toString()}`;
        mapFrame.title = `Map of ${query}`;
    }

    if (mapLink) {
        mapLink.href = `https://www.google.com/maps/search/?${searchParams.toString()}`;
    }
}

function initHomeMapToggle() {
    const mapToggle = document.getElementById("mapToggle");
    const mapPanel = document.getElementById("homeMapPanel");

    if (!mapToggle || !mapPanel) {
        return;
    }

    mapToggle.addEventListener("click", () => {
        const isHidden = mapPanel.classList.toggle("d-none");
        const isOpen = !isHidden;

        mapToggle.setAttribute("aria-expanded", String(isOpen));
        mapToggle.classList.toggle("btn-outline-success", !isOpen);
        mapToggle.classList.toggle("btn-success", isOpen);

        if (isOpen) {
            updateMapPreview();
        }
    });
}

document.addEventListener("DOMContentLoaded", () => {
    ["keywordSearch", "locationSearch"].forEach((id) => {
        const input = document.getElementById(id);
        if (input) {
            input.addEventListener("input", () => {
                if (!document.getElementById("homeMapPanel")?.classList.contains("d-none")) {
                    updateMapPreview();
                }
            });
        }
    });

    initHomeMapToggle();
});
