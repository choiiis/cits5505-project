document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("profileForm");
    const usernameInput = document.getElementById("usernameInput");
    const emailInput = document.getElementById("emailInput");
    const message = document.getElementById("profileMessage");

    if (!form || !usernameInput || !emailInput || !message) {
        return;
    }

    function setFieldState(input, isValid) {
        input.classList.toggle("is-invalid", !isValid);
        input.classList.toggle("is-valid", isValid && input.value.trim() !== "");
    }

    function isValidEmail(value) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
    }

    function validateForm() {
        const usernameIsValid = usernameInput.value.trim().length > 0;
        const emailIsValid = isValidEmail(emailInput.value.trim());

        setFieldState(usernameInput, usernameIsValid);
        setFieldState(emailInput, emailIsValid);

        return usernameIsValid && emailIsValid;
    }

    [usernameInput, emailInput].forEach((input) => {
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
