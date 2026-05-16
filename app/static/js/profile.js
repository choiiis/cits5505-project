document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("profileForm");
    const usernameInput = document.getElementById("usernameInput");
    const profileImageInput = document.getElementById("profileImageInput");
    const message = document.getElementById("profileMessage");

    if (!form || !usernameInput || !profileImageInput || !message) {
        return;
    }

    function setFieldState(input, isValid) {
        input.classList.toggle("is-invalid", !isValid);
        input.classList.toggle("is-valid", isValid && input.value.trim() !== "");
    }

    function isOptionalImageFile(input) {
        if (!input.files || input.files.length === 0) {
            return true;
        }

        return ["image/png", "image/jpeg", "image/gif", "image/webp"].includes(input.files[0].type);
    }

    function validateForm() {
        const usernameIsValid = usernameInput.value.trim().length > 0;
        const profileImageIsValid = isOptionalImageFile(profileImageInput);

        setFieldState(usernameInput, usernameIsValid);
        setFieldState(profileImageInput, profileImageIsValid);

        return usernameIsValid && profileImageIsValid;
    }

    [usernameInput, profileImageInput].forEach((input) => {
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
});
