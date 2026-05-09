document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("loginForm");
    const emailInput = document.getElementById("emailInput");
    const passwordInput = document.getElementById("passwordInput");
    const message = document.getElementById("loginMessage");

    if (!form || !emailInput || !passwordInput || !message) {
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
        const passwordIsValid = passwordInput.value.trim().length >= 6;

        setFieldState(emailInput, emailIsValid);
        setFieldState(passwordInput, passwordIsValid);

        return emailIsValid && passwordIsValid;
    }

    [emailInput, passwordInput].forEach((input) => {
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
