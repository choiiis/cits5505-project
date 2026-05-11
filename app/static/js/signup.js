document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("signupForm");
    const usernameInput = document.getElementById("usernameInput");
    const roleInput = document.getElementById("roleInput");
    const emailInput = document.getElementById("emailInput");
    const passwordInput = document.getElementById("passwordInput");
    const confirmPasswordInput = document.getElementById("confirmPasswordInput");
    const ownerFields = document.getElementById("ownerFields");
    const abnNumberInput = document.getElementById("abnNumberInput");
    const contactNumberInput = document.getElementById("contactNumberInput");
    const message = document.getElementById("signupMessage");

    if (!form || !usernameInput || !roleInput || !emailInput || !passwordInput || !confirmPasswordInput || !ownerFields || !abnNumberInput || !contactNumberInput || !message) {
        return;
    }

    function setFieldState(input, isValid) {
        input.classList.toggle("is-invalid", !isValid);
        input.classList.toggle("is-valid", isValid && input.value.trim() !== "");
    }

    function isValidEmail(value) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
    }

    function isOwnerSignup() {
        return roleInput.value === "owner";
    }

    function syncOwnerFields() {
        const ownerSelected = isOwnerSignup();
        ownerFields.hidden = !ownerSelected;

        [abnNumberInput, contactNumberInput].forEach((input) => {
            input.required = ownerSelected;

            if (!ownerSelected) {
                input.classList.remove("is-invalid", "is-valid");
            }
        });
    }

    function validateForm() {
        const usernameIsValid = usernameInput.value.trim().length > 0;
        const emailIsValid = isValidEmail(emailInput.value.trim());
        const passwordIsValid = passwordInput.value.trim().length >= 6;
        const passwordsMatch = confirmPasswordInput.value === passwordInput.value && confirmPasswordInput.value.length >= 6;
        const ownerSelected = isOwnerSignup();
        const abnNumberIsValid = !ownerSelected || /^\d{11}$/.test(abnNumberInput.value.trim());
        const contactNumberIsValid = !ownerSelected || contactNumberInput.value.trim().length > 0;

        setFieldState(usernameInput, usernameIsValid);
        setFieldState(emailInput, emailIsValid);
        setFieldState(passwordInput, passwordIsValid);
        setFieldState(confirmPasswordInput, passwordsMatch);
        setFieldState(abnNumberInput, abnNumberIsValid);
        setFieldState(contactNumberInput, contactNumberIsValid);

        return usernameIsValid && emailIsValid && passwordIsValid && passwordsMatch && abnNumberIsValid && contactNumberIsValid;
    }

    roleInput.addEventListener("change", () => {
        syncOwnerFields();
        validateForm();
    });

    [usernameInput, emailInput, passwordInput, confirmPasswordInput, abnNumberInput, contactNumberInput].forEach((input) => {
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

    syncOwnerFields();
});
