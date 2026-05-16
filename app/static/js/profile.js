document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("profileForm");
    const usernameInput = document.getElementById("usernameInput");
    const emailInput = document.getElementById("emailInput");
    const profileImageInput = document.getElementById("profileImageInput");
    const message = document.getElementById("profileMessage");

    if (!form || !usernameInput || !emailInput || !profileImageInput || !message) {
        return;
    }

    function setFieldState(input, isValid) {
        input.classList.toggle("is-invalid", !isValid);
        input.classList.toggle("is-valid", isValid && input.value.trim() !== "");
    }

    function isValidEmail(value) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
    }

    function isOptionalImageFile(input) {
        if (!input.files || input.files.length === 0) {
            return true;
        }

        return ["image/png", "image/jpeg", "image/gif", "image/webp"].includes(input.files[0].type);
    }

    function validateForm() {
        const usernameIsValid = usernameInput.value.trim().length > 0;
        const emailIsValid = isValidEmail(emailInput.value.trim());
        const profileImageIsValid = isOptionalImageFile(profileImageInput);

        setFieldState(usernameInput, usernameIsValid);
        setFieldState(emailInput, emailIsValid);
        setFieldState(profileImageInput, profileImageIsValid);

        return usernameIsValid && emailIsValid && profileImageIsValid;
    }

    [usernameInput, emailInput].forEach((input) => {
        input.addEventListener("input", () => {
            message.textContent = "";
            message.classList.remove("is-error");
            validateForm();
        });
    });

    profileImageInput.addEventListener("change", () => {
        message.textContent = "";
        message.classList.remove("is-error");
        validateForm();
    });

    form.addEventListener("submit", (event) => {
        if (!validateForm()) {
            event.preventDefault();
            message.textContent = "Please fix the highlighted fields and try again.";
            message.classList.add("is-error");
        }
    });
        document.querySelectorAll(".js-review-edit-toggle").forEach((button) => {
        button.addEventListener("click", () => {
            const reviewId = button.dataset.reviewId;
            const editForm = document.querySelector(`[data-review-edit-form="${reviewId}"]`);

            if (!editForm) {
                return;
            }

        const isHidden = editForm.classList.toggle("d-none");
        button.setAttribute("aria-expanded", String(!isHidden));
        });
    });

    document.querySelectorAll(".js-review-edit-cancel").forEach((button) => {
        button.addEventListener("click", () => {
            const reviewId = button.dataset.reviewId;
            const editForm = document.querySelector(`[data-review-edit-form="${reviewId}"]`);

            if (!editForm) {
                return;
            }

            editForm.classList.add("d-none");
            const toggleButton = document.querySelector(`.js-review-edit-toggle[data-review-id="${reviewId}"]`);

if (toggleButton) {
    toggleButton.setAttribute("aria-expanded", "false");
}
        });
    });

    document.querySelectorAll(".js-review-delete-form").forEach((deleteForm) => {
        deleteForm.addEventListener("submit", (event) => {
            const confirmed = window.confirm("Are you sure you want to delete this review?");

            if (!confirmed) {
                event.preventDefault();
            }
        });
    });
});
