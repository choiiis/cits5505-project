    const params = new URLSearchParams(window.location.search);
    const cards = Array.from(document.querySelectorAll(".restaurant-result"));
    const keywordSearch = document.querySelector("#keywordSearch");
    const locationSearch = document.querySelector("#locationSearch");
    const categoryFilter = document.querySelector("#categoryFilter");
    const locationFilter = document.querySelector("#locationFilter");
    const ratingFilter = document.querySelector("#ratingFilter");
    const sortFilter = document.querySelector("#sortFilter");
    const summaryMount = document.querySelector("#summaryMount");
    const resultsMount = document.querySelector("#resultsMount");
    const emptyState = document.querySelector("#emptyState");
    const mapToggle = document.querySelector("#mapToggle");
    const mapPreview = document.querySelector("#mapPreview");

    keywordSearch.value = params.get("q") || "";
    locationSearch.value = params.get("location") || "";
    categoryFilter.value = params.get("category") || "";

    if (params.get("map") === "true") {
      mapToggle.checked = true;
      mapPreview.classList.remove("d-none");
    }

    function applyFilters() {
      const query = keywordSearch.value.trim().toLowerCase();
      const locationQuery = locationSearch.value.trim().toLowerCase();
      const category = categoryFilter.value;
      const location = locationFilter.value;
      const minimumRating = Number(ratingFilter.value || 0);
      const sortBy = sortFilter.value;

      const sortedCards = cards.slice().sort((a, b) => {
        if (sortBy === "reviews") return Number(b.dataset.reviews) - Number(a.dataset.reviews);
        if (sortBy === "newest") return a.dataset.name.localeCompare(b.dataset.name);
        return Number(b.dataset.rating) - Number(a.dataset.rating);
      });

      sortedCards.forEach((card) => resultsMount.appendChild(card));

      let visibleCount = 0;
      sortedCards.forEach((card) => {
        const text = `${card.dataset.name} ${card.dataset.category} ${card.dataset.cuisine} ${card.dataset.location}`.toLowerCase();
        const isVisible =
          (!query || text.includes(query)) &&
          (!locationQuery || card.dataset.location.toLowerCase().includes(locationQuery)) &&
          (!category || card.dataset.category === category) &&
          (!location || card.dataset.location === location) &&
          (!minimumRating || Number(card.dataset.rating) >= minimumRating);

        card.classList.toggle("d-none", !isVisible);
        if (isVisible) visibleCount += 1;
      });

      const keyword = query || "restaurants";
      summaryMount.textContent = `${visibleCount} results for "${keyword}"`;
      emptyState.classList.toggle("d-none", visibleCount !== 0);
    }

    function initBookmarks() {
      document.querySelectorAll("[data-bookmark]").forEach((button) => {
        const id = button.dataset.bookmark;
        const setState = () => {
          const saved = JSON.parse(localStorage.getItem("tableTrailBookmarks") || "[]");
          const isSaved = saved.includes(id);
          button.textContent = isSaved ? "Saved" : "Save";
          button.classList.toggle("btn-success", isSaved);
          button.classList.toggle("btn-outline-success", !isSaved);
        };

        button.addEventListener("click", () => {
          const saved = JSON.parse(localStorage.getItem("tableTrailBookmarks") || "[]");
          const next = saved.includes(id) ? saved.filter((item) => item !== id) : [...saved, id];
          localStorage.setItem("tableTrailBookmarks", JSON.stringify(next));
          setState();
        });

        setState();
      });
    }

    [keywordSearch, locationSearch].forEach((input) => input.addEventListener("input", applyFilters));
    [categoryFilter, locationFilter, ratingFilter, sortFilter].forEach((input) => input.addEventListener("change", applyFilters));
    mapToggle.addEventListener("change", (event) => {
      mapPreview.classList.toggle("d-none", !event.target.checked);
    });

    initBookmarks();
    applyFilters();
