document.addEventListener("DOMContentLoaded", () => {
    const shell = document.querySelector(".bookmark-stage-shell");
    const emptyState = document.getElementById("bookmarkEmptyState");
    const collectionsData = document.getElementById("bookmarkCollectionsData");
    const bookmarkCollections = collectionsData ? JSON.parse(collectionsData.textContent) : [];

    if (shell) {
        shell.setAttribute("data-stage", "jinja");
    }

    function updateEmptyState() {
        if (!emptyState) {
            return;
        }

        const visibleCards = document.querySelectorAll("[data-bookmark-card]:not(.d-none)");
        emptyState.classList.toggle("d-none", visibleCards.length > 0);
    }

    function applyBookmarkSearch() {
        const searchInput = document.querySelector("[data-bookmark-search]");
        const query = searchInput ? searchInput.value.trim().toLowerCase() : "";

        document.querySelectorAll("[data-bookmark-card], [data-collection-card]").forEach((card) => {
            const searchText = (card.dataset.searchText || card.textContent).toLowerCase();
            const matches = !query || searchText.includes(query);

            card.classList.toggle("d-none", !matches);
        });

        updateEmptyState();
    }

    document.querySelector("[data-bookmark-search]")?.addEventListener("input", applyBookmarkSearch);

    document.querySelectorAll("[data-remove-bookmark]").forEach((button) => {
        button.addEventListener("click", () => {
            const card = button.closest("[data-bookmark-card]");

            if (card) {
                card.classList.add("d-none");
                updateEmptyState();
            }
        });
    });

    function openModal(modal) {
        if (!modal) {
            return;
        }

        modal.classList.add("is-open");
        modal.setAttribute("aria-hidden", "false");
        document.body.classList.add("modal-open");
    }

    function closeModal(modal) {
        if (!modal) {
            return;
        }

        modal.classList.remove("is-open");
        modal.setAttribute("aria-hidden", "true");
        document.body.classList.remove("modal-open");
    }

    function copyText(text, button) {
        navigator.clipboard.writeText(text).then(() => {
            const originalText = button.textContent;

            button.textContent = "Copied";

            setTimeout(() => {
                button.textContent = originalText;
            }, 1400);
        }).catch(() => {
            button.textContent = "Copy failed";
        });
    }

    function updateVisibilityLabel(label, visibility) {
        if (!label) {
            return;
        }

        label.textContent = visibility;
        label.classList.toggle("is-public", visibility === "Public");
    }

    function escapeHtml(value) {
        const element = document.createElement("div");

        element.textContent = value;
        return element.innerHTML;
    }

    function escapeAttribute(value) {
        return escapeHtml(value).replace(/"/g, "&quot;");
    }

    function createCollectionDetailModal(collectionId, safeName, visibility, shareCode) {
        const modal = document.createElement("div");
        const visibilityText = visibility === "Private" ? "Private · " : "";

        modal.className = "bookmark-modal";
        modal.id = `collectionModal-${collectionId}`;
        modal.dataset.collectionModal = "";
        modal.setAttribute("aria-hidden", "true");
        modal.innerHTML = `
            <div class="bookmark-modal__overlay" data-close-modal></div>
            <section class="bookmark-modal__panel" role="dialog" aria-modal="true"
                aria-labelledby="collectionTitle-${collectionId}">
                <button class="bookmark-modal__close" type="button" data-close-modal aria-label="Close collection">
                    ×
                </button>
                <div class="collection-modal-header">
                    <div>
                        <p class="collection-modal-header__meta mb-2">
                            ${visibilityText}0 places
                        </p>
                        <h2 class="h4 fw-bold mb-2" id="collectionTitle-${collectionId}">
                            ${safeName}
                        </h2>
                        <p class="text-secondary mb-0">Start adding saved restaurants to this collection.</p>
                    </div>
                    <span class="collection-modal-header__code">${shareCode}</span>
                </div>
                <div class="bookmark-empty-state">
                    No restaurants have been added to this collection yet.
                </div>
            </section>
        `;

        document.querySelector(".bookmarks-page").append(modal);
    }

    function createCollectionSettingsModal(collectionId, safeName, visibility, shareCode) {
        const modal = document.createElement("div");

        modal.className = "bookmark-modal";
        modal.id = `collectionSettings-${collectionId}`;
        modal.dataset.collectionSettingsModal = "";
        modal.setAttribute("aria-hidden", "true");
        modal.innerHTML = `
            <div class="bookmark-modal__overlay" data-close-modal></div>
            <section class="bookmark-modal__panel collection-settings-panel" role="dialog" aria-modal="true"
                aria-labelledby="collectionSettingsTitle-${collectionId}">
                <button class="bookmark-modal__close" type="button" data-close-modal aria-label="Close settings">
                    ×
                </button>
                <div class="collection-settings-header">
                    <p class="collection-modal-header__meta mb-2">Collection settings</p>
                    <h2 class="h4 fw-bold mb-0" id="collectionSettingsTitle-${collectionId}">
                        ${safeName}
                    </h2>
                </div>
                <div class="collection-settings-form">
                    <label class="form-label" for="collectionName-${collectionId}">Collection name</label>
                    <input class="form-control" id="collectionName-${collectionId}" type="text"
                        value="${escapeAttribute(safeName)}" data-collection-name-input>
                    <label class="form-label" for="collectionVisibility-${collectionId}">Visibility</label>
                    <select class="form-select" id="collectionVisibility-${collectionId}"
                        data-collection-visibility-input>
                        <option value="Public"${visibility === "Public" ? " selected" : ""}>Public</option>
                        <option value="Private"${visibility === "Private" ? " selected" : ""}>Private</option>
                    </select>
                    <label class="form-label" for="collectionShareCode-${collectionId}">Share code</label>
                    <div class="collection-copy-row">
                        <input class="form-control" id="collectionShareCode-${collectionId}" type="text"
                            value="${shareCode}" readonly data-share-code-input>
                        <button class="btn btn-outline-success" type="button" data-copy-share-code>
                            Copy
                        </button>
                    </div>
                </div>
                <div class="collection-settings-actions">
                    <button class="btn btn-success" type="button" data-save-collection-settings>
                        Save settings
                    </button>
                </div>
            </section>
        `;

        document.querySelector(".bookmarks-page").append(modal);
    }

    document.addEventListener("click", (event) => {
        const closeButton = event.target.closest("[data-close-modal]");
        const openCollectionButton = event.target.closest("[data-open-collection]");
        const openCreateButton = event.target.closest("[data-open-create-collection]");
        const openSettingsButton = event.target.closest("[data-open-collection-settings]");
        const heartButton = event.target.closest("[data-toggle-collection-heart]");
        const removeRestaurantButton = event.target.closest("[data-remove-collection-restaurant]");
        const copyShareButton = event.target.closest("[data-copy-share-code]");
        const saveSettingsButton = event.target.closest("[data-save-collection-settings]");
        const createCollectionButton = event.target.closest("[data-create-collection-submit]");
        const openShareButton = event.target.closest("[data-open-share-import]");
        const openPublicCollectionButton = event.target.closest("[data-open-public-collection]");
        const subscribePublicCollectionButton = event.target.closest("[data-subscribe-public-collection]");

        if (closeButton) {
            closeModal(closeButton.closest(".bookmark-modal"));
            return;
        }

        if (openCollectionButton) {
            const collectionId = openCollectionButton.dataset.openCollection;
            const modal = document.getElementById(`collectionModal-${collectionId}`);

            openModal(modal);
            return;
        }

        if (openCreateButton) {
            openModal(document.getElementById("createCollectionModal"));
            return;
        }

        if (openSettingsButton) {
            const collectionId = openSettingsButton.dataset.openCollectionSettings;
            const modal = document.getElementById(`collectionSettings-${collectionId}`);

            openModal(modal);
            return;
        }

        if (heartButton) {
            const isSaved = heartButton.classList.toggle("is-saved");

            heartButton.textContent = isSaved ? "♥" : "♡";
            heartButton.setAttribute("aria-pressed", String(isSaved));
            heartButton.setAttribute(
                "aria-label",
                isSaved ? "Remove saved status" : "Save restaurant"
            );
            return;
        }

        if (removeRestaurantButton) {
            const card = removeRestaurantButton.closest("[data-collection-restaurant]");

            if (card) {
                card.remove();
            }

            return;
        }

        if (copyShareButton) {
            const input = copyShareButton.closest(".collection-copy-row").querySelector("[data-share-code-input]");

            copyText(input.value, copyShareButton);
            return;
        }

        if (saveSettingsButton) {
            const modal = saveSettingsButton.closest("[data-collection-settings-modal]");
            const collectionId = modal.id.replace("collectionSettings-", "");
            const card = document.querySelector(`[data-collection-id="${collectionId}"]`);
            const nameInput = modal.querySelector("[data-collection-name-input]");
            const visibilityInput = modal.querySelector("[data-collection-visibility-input]");
            const nextName = nameInput.value.trim();

            if (card && nextName) {
                card.querySelector("[data-collection-name-label]").textContent = nextName;
                updateVisibilityLabel(
                    card.querySelector("[data-collection-visibility-label]"),
                    visibilityInput.value
                );
                card.dataset.searchText = `${nextName} ${visibilityInput.value} ${card.textContent}`;
            }

            modal.querySelector("h2").textContent = nextName || modal.querySelector("h2").textContent;
            saveSettingsButton.textContent = "Saved";

            setTimeout(() => {
                saveSettingsButton.textContent = "Save settings";
            }, 1400);

            applyBookmarkSearch();
            return;
        }

        if (createCollectionButton) {
            const modal = document.getElementById("createCollectionModal");
            const nameInput = modal.querySelector("[data-create-collection-name]");
            const visibilityInput = modal.querySelector("[data-create-collection-visibility]");
            const grid = document.querySelector("[data-collections-grid]");
            const name = nameInput.value.trim();
            const safeName = escapeHtml(name);
            const visibility = visibilityInput.value;

            if (!name) {
                nameInput.focus();
                return;
            }

            const firstImage = document.querySelector(".collection-card__image")?.getAttribute("src") || "";
            const collectionId = `created-${Date.now()}`;
            const shareCode = `NEW-${Math.floor(1000 + Math.random() * 9000)}`;
            const card = document.createElement("article");

            card.className = "collection-card";
            card.dataset.collectionCard = "";
            card.dataset.collectionId = collectionId;
            card.dataset.searchText = `${name} ${visibility} ${shareCode} new collection`;
            card.innerHTML = `
                <button class="collection-card__settings" type="button"
                    data-open-collection-settings="${collectionId}"
                    aria-label="Open ${safeName} settings">
                    ⚙
                </button>
                <button class="collection-card__main" type="button" data-open-collection="${collectionId}"
                    aria-label="Open ${safeName}">
                    <div class="collection-card__media">
                        <img class="collection-card__image" src="${firstImage}" alt="${safeName} cover image">
                        <div class="collection-card__badges">
                            <span data-collection-visibility-label>${visibility}</span>
                            <span>0 places</span>
                        </div>
                    </div>
                    <div class="collection-card__body">
                        <h3 data-collection-name-label>${safeName}</h3>
                        <p>Start adding saved restaurants to this collection.</p>
                        <span class="collection-card__code">Code: ${shareCode}</span>
                    </div>
                </button>
            `;

            updateVisibilityLabel(card.querySelector("[data-collection-visibility-label]"), visibility);
            createCollectionDetailModal(collectionId, safeName, visibility, shareCode);
            createCollectionSettingsModal(collectionId, safeName, visibility, shareCode);
            grid.prepend(card);
            nameInput.value = "";
            visibilityInput.value = "Public";
            closeModal(modal);
            applyBookmarkSearch();
            return;
        }

        if (openShareButton) {
            openModal(document.getElementById("shareImportModal"));
            return;
        }

        if (openPublicCollectionButton) {
            const collectionId = openPublicCollectionButton.dataset.openPublicCollection;
            const modal = document.getElementById(`publicCollectionModal-${collectionId}`);

            openModal(modal);
            return;
        }

        if (subscribePublicCollectionButton) {
            subscribePublicCollectionButton.textContent = "Subscribed";
            subscribePublicCollectionButton.classList.remove("btn-outline-success");
            subscribePublicCollectionButton.classList.add("btn-success");
        }
    });

    document.querySelector("[data-preview-share-code]")?.addEventListener("click", () => {
        const input = document.getElementById("shareCodeInput");
        const preview = document.getElementById("sharePreview");
        const shareCode = input.value.trim().toUpperCase();
        const collection = bookmarkCollections.find((item) => item.share_code === shareCode);

        if (!collection) {
            preview.textContent = "No matching collection was found for that share code.";
            return;
        }

        const visibilityText = collection.visibility === "Private" ? " · Private" : "";

        preview.innerHTML = `
            <div class="collection-share-preview__eyebrow">Matched collection</div>
            <h3>${collection.name}</h3>
            <p>${collection.restaurant_count} places${visibilityText}</p>
            <div class="collection-share-preview__actions">
                <button class="btn btn-success" type="button" data-subscribe-shared-collection>
                    Subscribe
                </button>
                <button class="btn btn-outline-success" type="button" data-copy-shared-collection>
                    Copy
                </button>
            </div>
        `;
    });

    document.getElementById("sharePreview")?.addEventListener("click", (event) => {
        const button = event.target.closest("button");

        if (!button) {
            return;
        }

        if (button.matches("[data-subscribe-shared-collection]")) {
            button.textContent = "Subscribed";
        }

        if (button.matches("[data-copy-shared-collection]")) {
            button.textContent = "Copied";
        }
    });

    document.addEventListener("keydown", (event) => {
        if (event.key !== "Escape") {
            return;
        }

        document.querySelectorAll(".bookmark-modal.is-open").forEach(closeModal);
    });

    updateEmptyState();
    applyBookmarkSearch();
});
