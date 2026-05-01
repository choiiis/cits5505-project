// DOM elements
const bookmarkBtn = document.querySelector(".restaurant-bookmark-btn");
const openReviewPanelButtons = document.querySelectorAll(".open-review-panel");
const closeReviewPanelButton = document.getElementById("closeReviewPanel");
const reviewOverlay = document.getElementById("reviewOverlay");
const reviewSlidePanel = document.getElementById("reviewSlidePanel");
// login mock test (true : logged in / false: guest)
const isLoggedIn = true;
const reviewLoginMessage = document.getElementById("reviewLoginMessage");
const reviewForm = document.getElementById("reviewForm");

// Functions
function openReviewPanel() {
    reviewOverlay.classList.add("active");
    reviewSlidePanel.classList.add("active");
    document.body.style.overflow = "hidden";
}

function closeReviewPanel() {
    reviewOverlay.classList.remove("active");
    reviewSlidePanel.classList.remove("active");
    document.body.style.overflow = "";
}

// Event Listeners
bookmarkBtn.addEventListener("click", function () {
    bookmarkBtn.classList.toggle("active");
    bookmarkBtn.textContent = bookmarkBtn.classList.contains("active") ? "♥" : "♡";
});

openReviewPanelButtons.forEach(function (button) {
    button.addEventListener("click", openReviewPanel);
});

closeReviewPanelButton.addEventListener("click", closeReviewPanel);
reviewOverlay.addEventListener("click", closeReviewPanel);

// login mock test
if (isLoggedIn) {
    reviewLoginMessage.style.display = "none";
    reviewForm.style.display = "flex";
} else {
    reviewLoginMessage.style.display = "block";
    reviewForm.style.display = "none";
}