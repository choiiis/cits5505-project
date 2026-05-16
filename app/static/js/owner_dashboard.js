document.addEventListener("DOMContentLoaded", () => {
  const closedCheckboxes = document.querySelectorAll(".owner-closed-checkbox");

  const addMenuItemBtn = document.getElementById("addMenuItemBtn");
  const menuItemModal = document.getElementById("menuItemModal");
  const menuItemForm = document.getElementById("menuItemForm");
  const menuTableBody = document.getElementById("menuTableBody");

  const menuFormTitle = document.getElementById("menuFormTitle");
  const menuItemIdInput = document.getElementById("menuItemId");
  const menuItemNameInput = document.getElementById("menuItemName");
  const menuItemDescriptionInput = document.getElementById("menuItemDescription");
  const menuItemPriceInput = document.getElementById("menuItemPrice");
  const menuItemImageInput = document.getElementById("menuItemImage");
  const menuFormAction = document.getElementById("menuFormAction");

  function updateTimeInputState(checkbox, shouldClearValues = false) {
    const row = checkbox.closest("tr");
    if (!row) return;

    const timeInputs = row.querySelectorAll(".owner-time-input");

    timeInputs.forEach((input) => {
      input.disabled = checkbox.checked;

      if (checkbox.checked && shouldClearValues) {
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

  function openMenuModal() {
    if (!menuItemModal) return;

    menuItemModal.classList.remove("is-hidden");
    document.body.classList.add("owner-modal-open");

    if (menuItemNameInput) {
      menuItemNameInput.focus();
    }
  }

  function closeMenuModal() {
    if (!menuItemModal) return;

    menuItemModal.classList.add("is-hidden");
    document.body.classList.remove("owner-modal-open");
  }

  function resetMenuForm() {
    if (!menuItemForm) return;

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

  if (addMenuItemBtn) {
    addMenuItemBtn.addEventListener("click", () => {
      resetMenuForm();
      openMenuModal();
    });
  }

  document.querySelectorAll("[data-modal-close]").forEach((button) => {
    button.addEventListener("click", closeMenuModal);
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closeMenuModal();
    }
  });

  if (menuTableBody) {
    menuTableBody.addEventListener("click", (event) => {
      const editButton = event.target.closest("[data-action='edit-menu']");
      if (!editButton) return;

      const card = editButton.closest(".owner-menu-card");
      const updateUrl = card ? card.dataset.updateUrl : "";

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
        menuItemDescriptionInput.value =
          editButton.dataset.menuItemDescription || "";
      }

      if (menuItemPriceInput) {
        menuItemPriceInput.value = editButton.dataset.menuItemPrice || "";
      }

      if (menuItemImageInput) {
        menuItemImageInput.value = "";
      }

      openMenuModal();
    });
  }
});