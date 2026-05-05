const savedRestaurants = [
    {
        id: "green-bowl",
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
        id: "laneway-pizza",
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
        id: "harbour-sushi",
        name: "Harbour Sushi Bar",
        category: "Japanese",
        location: "Fremantle",
        price: "$$$",
        rating: 4.6,
        reviewCount: 286,
        description: "Fresh sashimi, hand rolls, and tidy bento sets close to the waterfront.",
        image: "https://images.unsplash.com/photo-1579871494447-9811cf80d66c?auto=format&fit=crop&w=1200&q=80"
    }
];

function renderStars(rating) {
    return `${"★".repeat(Math.round(rating))}${"☆".repeat(5 - Math.round(rating))}`;
}

document.addEventListener("DOMContentLoaded", () => {
    const shell = document.querySelector(".bookmark-stage-shell");
    const mount = document.getElementById("bookmarkMount");
    let currentItems = [...savedRestaurants];

    if (shell) {
        shell.setAttribute("data-stage", "step3");
    }

    function renderBookmarks() {
        if (!mount) {
            return;
        }

        if (!currentItems.length) {
            mount.innerHTML = `
                <div class="col-12">
                    <div class="bookmark-empty-state">
                        Your saved restaurant list is empty. Explore more places and save your favourites.
                    </div>
                </div>
            `;
            return;
        }

        mount.innerHTML = currentItems.map((item) => `
            <div class="col-md-6 col-xl-4">
                <article class="bookmark-card">
                    <img src="${item.image}" class="bookmark-card__image" alt="${item.name}">
                    <div class="bookmark-card__body">
                        <span class="bookmark-card__category">${item.category}</span>
                        <h2 class="bookmark-card__title">${item.name}</h2>
                        <p class="bookmark-card__meta">${item.location} · ${item.price}</p>
                        <p class="bookmark-card__rating">${renderStars(item.rating)} <span>${item.rating} (${item.reviewCount})</span></p>
                        <p class="bookmark-card__description">${item.description}</p>
                        <div class="bookmark-card__actions">
                            <a class="btn btn-dark" href="search.html">View details</a>
                            <button class="btn btn-outline-danger" data-remove-bookmark="${item.id}" type="button">Remove</button>
                        </div>
                    </div>
                </article>
            </div>
        `).join("");

        document.querySelectorAll("[data-remove-bookmark]").forEach((button) => {
            button.addEventListener("click", () => {
                currentItems = currentItems.filter((item) => item.id !== button.dataset.removeBookmark);
                renderBookmarks();
            });
        });
    }

    renderBookmarks();
});
