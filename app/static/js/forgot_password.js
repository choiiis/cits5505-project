document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("forgotPasswordForm");
    const emailInput = document.getElementById("emailInput");
    const message = document.getElementById("forgotPasswordMessage");

    if (!form || !emailInput || !message) {
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
        const emailIsValid = isValidEmail(emailInput.value.trim());
        setFieldState(emailInput, emailIsValid);
        return emailIsValid;
    }

    emailInput.addEventListener("input", () => {
        message.textContent = "";
        message.classList.remove("is-error");
        validateForm();
    });

    form.addEventListener("submit", (event) => {
        if (!validateForm()) {
            event.preventDefault();
            message.textContent = "Please enter a valid email address.";
            message.classList.add("is-error");
        }
    });
});
