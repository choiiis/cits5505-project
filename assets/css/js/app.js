function params() {
  return new URLSearchParams(window.location.search);
}

function renderHome() {
  App.attachShell("home");
  document.querySelector("#searchMount").innerHTML = App.searchBar(params().get("q") || "", params().get("location") || "");
  document.querySelector("#categoryMount").innerHTML = App.categoryPills();
  document.querySelector("#featuredMount").innerHTML = App.restaurants.slice(0, 4).map((item) => `<div class="col-md-6 col-xl-3">${App.restaurantCard(item, true)}</div>`).join("");
  App.initBookmarks();
}

function applySearchFilters() {
  const query = (params().get("q") || document.querySelector("#keywordSearch")?.value || "").toLowerCase();
  const locationQuery = (params().get("location") || "").toLowerCase();
  const category = document.querySelector("#categoryFilter")?.value || params().get("category") || "";
  const location = document.querySelector("#locationFilter")?.value || "";
  const rating = Number(document.querySelector("#ratingFilter")?.value || 0);
  const sort = document.querySelector("#sortFilter")?.value || "rating";

  let results = App.restaurants.filter((item) => {
    const text = `${item.name} ${item.category} ${item.cuisine} ${item.location}`.toLowerCase();
    const matchesQuery = !query || text.includes(query);
    const matchesLocationQuery = !locationQuery || item.location.toLowerCase().includes(locationQuery);
    const matchesCategory = !category || item.category === category;
    const matchesLocation = !location || item.location === location;
    const matchesRating = !rating || item.rating >= rating;
    return matchesQuery && matchesLocationQuery && matchesCategory && matchesLocation && matchesRating;
  });

  results = results.sort((a, b) => {
    if (sort === "reviews") return b.reviewCount - a.reviewCount;
    if (sort === "newest") return a.name.localeCompare(b.name);
    return b.rating - a.rating;
  });

  const keyword = params().get("q") || "restaurants";
  document.querySelector("#summaryMount").textContent = `${results.length} results for "${keyword}"`;
  document.querySelector("#resultsMount").innerHTML = results.length
    ? results.map((item) => `<div class="col-md-6 col-xl-4">${App.restaurantCard(item)}</div>`).join("")
    : `<div class="col-12"><div class="alert alert-warning">No restaurants match these filters. Try another category or location.</div></div>`;
  App.initBookmarks();
}

function renderSearch() {
  App.attachShell("search");
  document.querySelector("#searchMount").innerHTML = App.searchBar(params().get("q") || "", params().get("location") || "");
  document.querySelector("#filterMount").innerHTML = App.filterBar();
  const category = params().get("category");
  if (category) document.querySelector("#categoryFilter").value = category;
  ["categoryFilter", "locationFilter", "ratingFilter", "sortFilter"].forEach((id) => {
    document.querySelector(`#${id}`).addEventListener("change", applySearchFilters);
  });
  document.querySelector("#mapToggle").addEventListener("change", (event) => {
    document.querySelector("#mapPreview").classList.toggle("d-none", !event.target.checked);
  });
  if (params().get("map") === "true") {
    document.querySelector("#mapToggle").checked = true;
    document.querySelector("#mapPreview").classList.remove("d-none");
  }
  applySearchFilters();
}

function renderRestaurant() {
  App.attachShell("search");
  const item = App.findRestaurant(params().get("id"));
  document.title = `${item.name} | TableTrail`;
  document.querySelector("#detailMount").innerHTML = `
    <img src="${item.image}" alt="${item.name}" class="img-fluid w-100 detail-hero shadow-sm">
    <section class="container py-4">
      <div class="row g-4 align-items-start">
        <div class="col-lg-8">
          <span class="badge text-bg-light border">${item.category}</span>
          <h1 class="display-6 fw-bold mt-2">${item.name}</h1>
          <p class="rating mb-2">${App.stars(item.rating)} <span>${item.rating} · ${item.reviewCount} reviews</span></p>
          <p class="lead text-secondary">${item.description}</p>
          <p class="mb-1"><strong>Address:</strong> ${item.address}</p>
          <p><strong>Hours:</strong> ${item.hours}</p>
          <div class="d-flex flex-wrap gap-2">
            <button class="btn btn-success" data-bs-toggle="modal" data-bs-target="#reviewModal">Write review</button>
            <button class="btn btn-outline-success bookmark-toggle" data-bookmark="${item.id}" type="button">Save</button>
            <a class="btn btn-outline-dark" href="search.html?location=${encodeURIComponent(item.location)}&map=true">View map</a>
          </div>
        </div>
        <aside class="col-lg-4">
          <div class="card shadow-sm">
            <div class="card-body">
              <h2 class="h5">Popular menu</h2>
              <ul class="list-group list-group-flush">
                ${item.menu.map((menuItem) => `<li class="list-group-item px-0">${menuItem}</li>`).join("")}
              </ul>
            </div>
          </div>
        </aside>
      </div>
    </section>
    <section class="section-band py-4">
      <div class="container">
        <h2 class="h4 mb-3">Photos</h2>
        <div class="row g-3">
          ${item.gallery.map((image, index) => `<div class="col-6 col-lg-4"><img src="${image}" class="img-fluid rounded shadow-sm gallery-img" alt="${item.name} gallery ${index + 1}"></div>`).join("")}
        </div>
      </div>
    </section>
    <section class="container py-4">
      <div class="d-flex flex-column flex-md-row justify-content-between gap-3 mb-3">
        <div>
          <h2 class="h4 mb-1">Reviews</h2>
          <p class="text-secondary mb-0">Filter reviews by star rating or open the review panel.</p>
        </div>
        <select class="form-select w-auto" id="reviewStarFilter" aria-label="Filter reviews by stars">
          <option value="">All stars</option>
          <option value="5">5 stars</option>
          <option value="4">4 stars</option>
          <option value="3">3 stars</option>
        </select>
      </div>
      <div id="reviewList" class="row g-3"></div>
    </section>
    ${App.reviewModal()}
  `;

  function renderReviews() {
    const rating = Number(document.querySelector("#reviewStarFilter").value || 0);
    const reviews = item.reviews.filter((review) => !rating || review.rating === rating);
    document.querySelector("#reviewList").innerHTML = reviews.map((review) => `<div class="col-lg-6">${App.reviewCard(review)}</div>`).join("");
  }

  document.querySelector("#reviewStarFilter").addEventListener("change", renderReviews);
  renderReviews();
  App.initBookmarks();
}

function renderBookmarks() {
  App.attachShell("bookmarks");
  const refresh = () => {
    const savedIds = JSON.parse(localStorage.getItem("tableTrailBookmarks") || "[]");
    const saved = App.restaurants.filter((item) => savedIds.includes(item.id));
    document.querySelector("#bookmarkMount").innerHTML = saved.length
      ? saved.map((item) => `
        <div class="col-md-6 col-xl-4">
          <article class="card restaurant-card h-100 shadow-sm">
            <img src="${item.image}" class="card-img-top" alt="${item.name}" loading="lazy">
            <div class="card-body d-flex flex-column">
              <span class="badge text-bg-light border align-self-start">${item.category}</span>
              <h2 class="h5 mt-2 mb-1">${item.name}</h2>
              <p class="text-secondary mb-2">${item.location} · ${item.price}</p>
              <p class="rating mb-2">${App.stars(item.rating)} <span>${item.rating} (${item.reviewCount})</span></p>
              <div class="d-flex gap-2 mt-auto">
                <a href="restaurant.html?id=${item.id}" class="btn btn-dark flex-fill">View details</a>
                <button class="btn btn-outline-danger" data-remove-bookmark="${item.id}" type="button">Remove</button>
              </div>
            </div>
          </article>
        </div>`).join("")
      : `<div class="col-12"><div class="alert alert-info">Your saved restaurant list is empty. Explore restaurants and press Save.</div></div>`;
    document.querySelectorAll("[data-remove-bookmark]").forEach((button) => {
      button.addEventListener("click", () => {
        const next = JSON.parse(localStorage.getItem("tableTrailBookmarks") || "[]").filter((id) => id !== button.dataset.removeBookmark);
        localStorage.setItem("tableTrailBookmarks", JSON.stringify(next));
        refresh();
      });
    });
  };
  refresh();
}

function renderProfile() {
  App.attachShell("profile");
  document.querySelector("#myReviewsMount").innerHTML = App.restaurants.slice(0, 3).map((item, index) => {
    const review = { author: "Haemin Choi", rating: 5 - (index % 2), date: "Apr 2026", text: `My review for ${item.name}: reliable food, clear service, and worth revisiting.` };
    return `<div class="col-lg-4">${App.reviewCard(review, true)}</div>`;
  }).join("");
}

function renderOwner() {
  App.attachShell("owner");
  document.querySelector("#ownerReviewsMount").innerHTML = App.restaurants.slice(0, 4).map((item) => `
    <div class="card review-card shadow-sm mb-3">
      <div class="card-body">
        <div class="d-flex justify-content-between gap-3">
          <div><h3 class="h6 mb-1">${item.name}</h3><p class="rating mb-0">${App.stars(item.rating)} <span>${item.reviewCount} reviews</span></p></div>
          <span class="badge text-bg-light border">${item.category}</span>
        </div>
        <p class="mt-3 mb-3">${item.reviews[0].text}</p>
        <textarea class="form-control mb-2" rows="2" placeholder="Respond publicly as the owner"></textarea>
        <button class="btn btn-outline-success btn-sm">Post response</button>
      </div>
    </div>`).join("");
}

function renderAdmin() {
  App.attachShell("admin");
  document.querySelector("#adminTableMount").innerHTML = App.restaurants.map((item, index) => `
    <tr>
      <td>${item.name}</td>
      <td>${item.category}</td>
      <td>${item.location}</td>
      <td>${item.rating}</td>
      <td>${item.reviewCount}</td>
      <td><span class="status-dot"></span>${index % 4 === 0 ? "Needs review" : "Healthy"}</td>
      <td class="text-end"><button class="btn btn-outline-danger btn-sm">Remove review</button></td>
    </tr>`).join("");
}

function renderAuth(active) {
  App.attachShell(active);
}

document.addEventListener("DOMContentLoaded", () => {
  const page = document.body.dataset.page;
  if (page === "home") renderHome();
  if (page === "search") renderSearch();
  if (page === "restaurant") renderRestaurant();
  if (page === "bookmarks") renderBookmarks();
  if (page === "profile") renderProfile();
  if (page === "owner") renderOwner();
  if (page === "admin") renderAdmin();
  if (["login", "signup", "forgot"].includes(page)) renderAuth(page);
});
