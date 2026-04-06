const searchForm = document.querySelector("#searchForm");
const saveButton = document.querySelector("#saveButton");
const reviewForm = document.querySelector("#reviewForm");

if (searchForm) {
  searchForm.addEventListener("submit", (event) => {
    event.preventDefault();

    const nameValue = document.querySelector("#searchName").value.trim().toLowerCase();
    const locationValue = document.querySelector("#searchLocation").value.trim().toLowerCase();
    const cuisineValue = document.querySelector("#searchCuisine").value;
    const cards = [...document.querySelectorAll(".restaurant-listing")];

    let visibleCount = 0;

    cards.forEach((card) => {
      const name = card.dataset.name.toLowerCase();
      const location = card.dataset.location.toLowerCase();
      const cuisine = card.dataset.cuisine;
      const matchesName = !nameValue || name.includes(nameValue);
      const matchesLocation = !locationValue || location.includes(locationValue);
      const matchesCuisine = cuisineValue === "all" || cuisine === cuisineValue;
      const isVisible = matchesName && matchesLocation && matchesCuisine;

      card.classList.toggle("hidden", !isVisible);
      if (isVisible) {
        visibleCount += 1;
      }
    });

    const resultCount = document.querySelector("#resultCount");
    resultCount.textContent = `Showing ${visibleCount} restaurant${visibleCount === 1 ? "" : "s"}`;
  });
}

if (saveButton) {
  saveButton.addEventListener("click", () => {
    const saveNote = document.querySelector("#saveNote");
    saveButton.textContent = "Saved";
    saveButton.disabled = true;
    saveNote.textContent = "Harbor Lantern has been added to your saved list.";
  });
}

if (reviewForm) {
  reviewForm.addEventListener("submit", (event) => {
    event.preventDefault();

    const name = document.querySelector("#reviewerName").value.trim();
    const message = document.querySelector("#reviewMessage");
    message.textContent = `${name || "Your"} review draft has been captured. In a full app, this would be stored and shown after moderation.`;
    reviewForm.reset();
  });
}
