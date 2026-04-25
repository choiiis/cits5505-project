const bookmarkBtn = document.querySelector(".restaurant-bookmark-btn");

bookmarkBtn.addEventListener("click", function () {
    bookmarkBtn.classList.toggle("active");
    bookmarkBtn.textContent = bookmarkBtn.classList.contains("active") ? "♥" : "♡";
});