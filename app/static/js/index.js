const featuredRestaurants = [
    {
        name: "Green Bowl Kitchen",
        category: "Healthy",
        location: "Perth CBD",
        price: "$$",
        rating: 4.8,
        reviewCount: 324,
        description: "Fresh bowls, cold-pressed juices, and quick lunches for busy city workers.",
        image: "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=1200&q=80"
    },
    {
        name: "Laneway Pizza Co.",
        category: "Italian",
        location: "Northbridge",
        price: "$$",
        rating: 4.7,
        reviewCount: 512,
        description: "Wood-fired pizza, shared plates, and a lively dinner atmosphere in the laneway.",
        image: "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=1200&q=80"
    },
    {
        name: "Harbour Sushi Bar",
        category: "Japanese",
        location: "Fremantle",
        price: "$$$",
        rating: 4.6,
        reviewCount: 286,
        description: "Fresh sashimi, hand rolls, and tidy bento sets close to the waterfront.",
        image: "https://images.unsplash.com/photo-1579871494447-9811cf80d66c?auto=format&fit=crop&w=1200&q=80"
    },
    {
        name: "Taco Yard",
        category: "Mexican",
        location: "Subiaco",
        price: "$$",
        rating: 4.5,
        reviewCount: 198,
        description: "Street-style tacos, loaded nachos, and colourful drinks for a casual meal.",
        image: "https://images.unsplash.com/photo-1565299585323-38d6b0865b47?auto=format&fit=crop&w=1200&q=80"
    }
];

function renderStars(rating) {
    return `${"★".repeat(Math.round(rating))}${"☆".repeat(5 - Math.round(rating))}`;
}

function renderFeaturedRestaurants() {
    const mount = document.getElementById("featuredMount");

    if (!mount) {
        return;
    }

    mount.innerHTML = featuredRestaurants.map((item) => `
        <div class="col-md-6 col-xl-3">
            <article class="featured-card">
                <img src="${item.image}" class="featured-card__image" alt="${item.name}">
                <div class="featured-card__body">
                    <div class="featured-card__top">
                        <span class="featured-card__category">${item.category}</span>
                        <button class="featured-card__save" type="button">Save</button>
                    </div>
                    <h3 class="featured-card__title">${item.name}</h3>
                    <p class="featured-card__meta">${item.location} · ${item.price}</p>
                    <p class="featured-card__rating">${renderStars(item.rating)} <span>${item.rating} (${item.reviewCount})</span></p>
                    <p class="featured-card__description">${item.description}</p>
                    <a class="btn btn-dark featured-card__action" href="search.html">View details</a>
                </div>
            </article>
        </div>
    `).join("");
}

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

    renderFeaturedRestaurants();
    updateMapLink();
});
