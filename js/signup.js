document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("signupForm");
    const fullNameInput = document.getElementById("fullNameInput");
    const roleSelect = document.getElementById("roleSelect");
    const emailInput = document.getElementById("emailInput");
    const passwordInput = document.getElementById("passwordInput");
    const ownerFields = document.getElementById("ownerFields");
    const restaurantNameInput = document.getElementById("restaurantNameInput");
    const abnInput = document.getElementById("abnInput");
    const contactNumberInput = document.getElementById("contactNumberInput");
    const message = document.getElementById("signupMessage");

    if (!form || !fullNameInput || !roleSelect || !emailInput || !passwordInput || !ownerFields || !message) {
        return;
    }

    const ownerInputs = [restaurantNameInput, abnInput, contactNumberInput];

    function setFieldState(input, isValid) {
        input.classList.toggle("is-invalid", !isValid);
        input.classList.toggle("is-valid", isValid && input.value.trim() !== "");
    }

    function isValidEmail(value) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
    }

    function isOwnerSelected() {
        return roleSelect.value === "owner";
    }

    function toggleOwnerFields() {
        const showOwnerFields = isOwnerSelected();

        ownerFields.classList.toggle("d-none", !showOwnerFields);
        ownerInputs.forEach((input) => {
            input.required = showOwnerFields;

            if (!showOwnerFields) {
                input.value = "";
                input.classList.remove("is-invalid", "is-valid");
            }
        });
    }

    function validateForm() {
        const fullNameIsValid = fullNameInput.value.trim().length >= 2;
        const emailIsValid = isValidEmail(emailInput.value.trim());
        const passwordIsValid = passwordInput.value.trim().length >= 6;

        setFieldState(fullNameInput, fullNameIsValid);
        setFieldState(emailInput, emailIsValid);
        setFieldState(passwordInput, passwordIsValid);

        let ownerFieldsAreValid = true;

        if (isOwnerSelected()) {
            const restaurantNameIsValid = restaurantNameInput.value.trim().length >= 2;
            const abnIsValid = /^\d{11}$/.test(abnInput.value.replace(/\s/g, ""));
            const contactNumberIsValid = /^[\d\s()+-]{8,}$/.test(contactNumberInput.value.trim());

            setFieldState(restaurantNameInput, restaurantNameIsValid);
            setFieldState(abnInput, abnIsValid);
            setFieldState(contactNumberInput, contactNumberIsValid);

            ownerFieldsAreValid = restaurantNameIsValid && abnIsValid && contactNumberIsValid;
        }

        return fullNameIsValid && emailIsValid && passwordIsValid && ownerFieldsAreValid;
    }

    [fullNameInput, emailInput, passwordInput, ...ownerInputs].forEach((input) => {
        input.addEventListener("input", () => {
            message.textContent = "";
            message.classList.remove("is-error");
            validateForm();
        });
    });

    roleSelect.addEventListener("change", () => {
        message.textContent = "";
        message.classList.remove("is-error");
        toggleOwnerFields();
        validateForm();
    });

    form.addEventListener("submit", (event) => {
        event.preventDefault();

        if (!validateForm()) {
            message.textContent = "Please fix the highlighted fields and try again.";
            message.classList.add("is-error");
            return;
        }

        message.textContent = isOwnerSelected()
            ? "Owner account details look good. ABN verification can be connected next."
            : "Account details look good. Backend registration can be connected next.";
        message.classList.remove("is-error");
        form.reset();
        [...form.elements].forEach((field) => field.classList.remove("is-invalid", "is-valid"));
        toggleOwnerFields();
    });

    toggleOwnerFields();
});
