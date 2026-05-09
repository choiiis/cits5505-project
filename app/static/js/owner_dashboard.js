document.addEventListener("DOMContentLoaded", () => {
  const editRestaurantBtn = document.getElementById("editRestaurantInfoBtn");
  const editableInfoFields = document.querySelectorAll("[data-info-field]");
  const message = document.getElementById("ownerActionMessage");

  const addMenuItemBtn = document.getElementById("addMenuItemBtn");
  const editCategoriesBtn = document.getElementById("editCategoriesBtn");
  const menuItemForm = document.getElementById("menuItemForm");
  const cancelMenuEditBtn = document.getElementById("cancelMenuEditBtn");
  const menuTableBody = document.getElementById("menuTableBody");

  const nameInput = document.getElementById("menuItemName");
  const categoryInput = document.getElementById("menuItemCategory");
  const priceInput = document.getElementById("menuItemPrice");
  const statusInput = document.getElementById("menuItemStatus");
const closedCheckboxes = document.querySelectorAll(".owner-closed-checkbox");

closedCheckboxes.forEach((checkbox) => {
  checkbox.addEventListener("change", () => {
    const row = checkbox.closest("tr");
    const timeInputs = row.querySelectorAll(".owner-time-input");

    timeInputs.forEach((input) => {
      input.disabled = checkbox.checked;

      if (checkbox.checked) {
        input.value = "";
      }
    });
  });
});
  let restaurantEditMode = false;
  let editingRow = null;

  function showMessage(text) {
    if (!message) return;
    message.textContent = text;

    window.clearTimeout(showMessage.timer);
    showMessage.timer = window.setTimeout(() => {
      message.textContent = "";
    }, 3000);
  }

  function setRestaurantEditMode(isEditing) {
    restaurantEditMode = isEditing;

    editableInfoFields.forEach((field) => {
      field.contentEditable = String(isEditing);
      field.closest(".owner-info-item")?.classList.toggle("is-editing", isEditing);
    });

    editRestaurantBtn.textContent = isEditing ? "Save information" : "Edit information";
  }

  function resetMenuForm() {
    editingRow = null;
    nameInput.value = "";
    categoryInput.value = "";
    priceInput.value = "";
    statusInput.value = "Available";
    menuItemForm.classList.add("is-hidden");
  }

  function showMenuForm(row = null) {
    editingRow = row;
    menuItemForm.classList.remove("is-hidden");

    if (row) {
      const cells = row.querySelectorAll("td");
      nameInput.value = cells[0].textContent.trim();
      categoryInput.value = cells[1].textContent.trim();
      priceInput.value = cells[2].textContent.trim();
      statusInput.value = cells[3].textContent.trim();
    } else {
      nameInput.value = "";
      categoryInput.value = "";
      priceInput.value = "";
      statusInput.value = "Available";
    }

    nameInput.focus();
  }

  function createStatusBadge(status) {
    const className =
      status === "Hidden"
        ? "owner-status owner-status--hidden"
        : "owner-status owner-status--available";

    return `<span class="${className}">${status}</span>`;
  }

  function createMenuRow(name, category, price, status) {
    const row = document.createElement("tr");

    row.innerHTML = `
      <td>${name}</td>
      <td>${category}</td>
      <td>${price}</td>
      <td>${createStatusBadge(status)}</td>
      <td>
        <button type="button" class="owner-table-button" data-action="edit-menu">
          Edit
        </button>
      </td>
    `;

    return row;
  }

  if (editRestaurantBtn) {
    editRestaurantBtn.addEventListener("click", () => {
      if (restaurantEditMode) {
        setRestaurantEditMode(false);
        showMessage("Restaurant information updated on this page.");
      } else {
        setRestaurantEditMode(true);
        showMessage("You can now edit the restaurant information fields.");
      }
    });
  }

  if (addMenuItemBtn) {
    addMenuItemBtn.addEventListener("click", () => {
      showMenuForm();
      showMessage("Add a new menu item using the form below.");
    });
  }

  if (editCategoriesBtn) {
    editCategoriesBtn.addEventListener("click", () => {
      showMessage("Category editing placeholder opened. This can connect to backend logic later.");
    });
  }

  if (cancelMenuEditBtn) {
    cancelMenuEditBtn.addEventListener("click", resetMenuForm);
  }

  if (menuTableBody) {
    menuTableBody.addEventListener("click", (event) => {
      const button = event.target.closest("[data-action='edit-menu']");

      if (!button) return;

      const row = button.closest("tr");
      showMenuForm(row);
      showMessage("Edit the selected menu item using the form below.");
    });
  }

  if (menuItemForm) {
    menuItemForm.addEventListener("submit", (event) => {
      event.preventDefault();

      const name = nameInput.value.trim();
      const category = categoryInput.value.trim();
      const price = priceInput.value.trim();
      const status = statusInput.value;

      if (!name || !category || !price) {
        showMessage("Please complete item name, category, and price.");
        return;
      }

      if (editingRow) {
        const cells = editingRow.querySelectorAll("td");
        cells[0].textContent = name;
        cells[1].textContent = category;
        cells[2].textContent = price;
        cells[3].innerHTML = createStatusBadge(status);
        showMessage("Menu item updated on this page.");
      } else {
        menuTableBody.appendChild(createMenuRow(name, category, price, status));
        showMessage("New menu item added on this page.");
      }

      resetMenuForm();
    });
  }
});