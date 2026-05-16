document.addEventListener("DOMContentLoaded", () => {
  const closedCheckboxes = document.querySelectorAll(".owner-closed-checkbox");
  const addMenuItemBtn = document.getElementById("addMenuItemBtn");
  const menuItemForm = document.getElementById("menuItemForm");
  const cancelMenuEditBtn = document.getElementById("cancelMenuEditBtn");
  const menuTableBody = document.getElementById("menuTableBody");
  const menuFormTitle = document.getElementById("menuFormTitle");
  const menuItemIdInput = document.getElementById("menuItemId");
  const menuItemNameInput = document.getElementById("menuItemName");
  const menuItemDescriptionInput = document.getElementById("menuItemDescription");
  const menuItemPriceInput = document.getElementById("menuItemPrice");
  const menuItemImageInput = document.getElementById("menuItemImage");
  const menuFormAction = document.getElementById("menuFormAction");

  function updateTimeInputState(checkbox, clearValues = false) {
    const row = checkbox.closest("tr");

    if (!row) return;

    const timeInputs = row.querySelectorAll(".owner-time-input");

    timeInputs.forEach((input) => {
      input.disabled = checkbox.checked;

      if (checkbox.checked && clearValues) {
        input.value = "";
      }
    });
  }

  closedCheckboxes.forEach((checkbox) => {
    updateTimeInputState(checkbox, false);

    checkbox.addEventListener("change", () => {
      updateTimeInputState(checkbox, true);
    });
  });

  function resetMenuForm() {
    if (!menuItemForm) return;

    menuItemForm.classList.add("is-hidden");

    if (menuItemForm.dataset.addUrl) {
      menuItemForm.action = menuItemForm.dataset.addUrl;
    }

    if (menuFormTitle) {
      menuFormTitle.textContent = "Add menu item";
    }

    if (menuItemIdInput) {
      menuItemIdInput.value = "";
    }

    if (menuItemNameInput) {
      menuItemNameInput.value = "";
    }

    if (menuItemDescriptionInput) {
      menuItemDescriptionInput.value = "";
    }

    if (menuItemPriceInput) {
      menuItemPriceInput.value = "";
    }

    if (menuItemImageInput) {
      menuItemImageInput.value = "";
    }

    if (menuFormAction) {
      menuFormAction.value = "add";
    }
  }

  function showMenuForm() {
    if (!menuItemForm) return;

    menuItemForm.classList.remove("is-hidden");
    menuItemForm.scrollIntoView({ behavior: "smooth", block: "start" });

    if (menuItemNameInput) {
      menuItemNameInput.focus();
    }
  }

  if (addMenuItemBtn) {
    addMenuItemBtn.addEventListener("click", () => {
      resetMenuForm();
      showMenuForm();
    });
  }

  if (cancelMenuEditBtn) {
    cancelMenuEditBtn.addEventListener("click", () => {
      resetMenuForm();
    });
  }

  if (menuTableBody) {
    menuTableBody.addEventListener("click", (event) => {
      const editButton = event.target.closest("[data-action='edit-menu']");

      if (!editButton) return;

      const row = editButton.closest("tr");
      const updateUrl = row ? row.dataset.updateUrl : "";

      if (updateUrl && menuItemForm) {
        menuItemForm.action = updateUrl;
      }

      if (menuFormTitle) {
        menuFormTitle.textContent = "Edit menu item";
      }

      if (menuFormAction) {
        menuFormAction.value = "edit";
      }

      if (menuItemIdInput) {
        menuItemIdInput.value = editButton.dataset.menuItemId || "";
      }

      if (menuItemNameInput) {
        menuItemNameInput.value = editButton.dataset.menuItemName || "";
      }

      if (menuItemDescriptionInput) {
        menuItemDescriptionInput.value = editButton.dataset.menuItemDescription || "";
      }

      if (menuItemPriceInput) {
        menuItemPriceInput.value = editButton.dataset.menuItemPrice || "";
      }

      if (menuItemImageInput) {
        menuItemImageInput.value = editButton.dataset.menuItemImage || "";
      }

      showMenuForm();
    });
  }
});
