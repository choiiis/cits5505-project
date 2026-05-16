document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("changeEmailForm");
    const emailInput = document.getElementById("newEmailInput");
    const passwordInput = document.getElementById("currentPasswordInput");
    const message = document.getElementById("changeEmailMessage");

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
        const passwordIsValid = passwordInput.value.trim().length > 0;

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
