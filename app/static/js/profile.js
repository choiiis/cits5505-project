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

    function isOptionalUrl(value) {
        if (!value.trim()) {
            return true;
        }

        try {
            new URL(value);
            return true;
        } catch {
            return false;
        }
    }

    function validateForm() {
        const usernameIsValid = usernameInput.value.trim().length > 0;
        const emailIsValid = isValidEmail(emailInput.value.trim());
        const profileImageIsValid = isOptionalUrl(profileImageInput.value);

        setFieldState(usernameInput, usernameIsValid);
        setFieldState(emailInput, emailIsValid);
        setFieldState(profileImageInput, profileImageIsValid);

        return usernameIsValid && emailIsValid && profileImageIsValid;
    }

    [usernameInput, emailInput, profileImageInput].forEach((input) => {
        input.addEventListener("input", () => {
            message.textContent = "";
            message.classList.remove("is-error");
            validateForm();
        });
    });

    form.addEventListener("submit", (event) => {
        if (!validateForm()) {
            event.preventDefault();
            message.textContent = "Please fix the highlighted fields and try again.";
            message.classList.add("is-error");
        }
    });
});
