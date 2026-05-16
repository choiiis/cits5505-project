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

    document.querySelectorAll("[data-open-collection]").forEach((button) => {
        button.addEventListener("click", () => {
            const collectionId = button.dataset.openCollection;
            const modal = document.getElementById(`collectionModal-${collectionId}`);

            openModal(modal);
        });
    });

    document.querySelectorAll("[data-open-create-collection]").forEach((button) => {
        button.addEventListener("click", () => {
            openModal(document.getElementById("createCollectionModal"));
        });
    });

    document.querySelectorAll("[data-open-collection-settings]").forEach((button) => {
        button.addEventListener("click", () => {
            const collectionId = button.dataset.openCollectionSettings;
            const modal = document.getElementById(`collectionSettings-${collectionId}`);

            openModal(modal);
        });
    });

    document.querySelectorAll("[data-close-modal]").forEach((button) => {
        button.addEventListener("click", () => {
            closeModal(button.closest(".bookmark-modal"));
        });
    });

    document.querySelectorAll("[data-toggle-collection-heart]").forEach((button) => {
        button.addEventListener("click", () => {
            const isSaved = button.classList.toggle("is-saved");

            button.textContent = isSaved ? "♥" : "♡";
            button.setAttribute("aria-pressed", String(isSaved));
            button.setAttribute(
                "aria-label",
                isSaved ? "Remove saved status" : "Save restaurant"
            );
        });
    });

    document.querySelectorAll("[data-remove-collection-restaurant]").forEach((button) => {
        button.addEventListener("click", () => {
            const card = button.closest("[data-collection-restaurant]");

            if (card) {
                card.remove();
            }
        });
    });

    document.querySelectorAll("[data-copy-share-code]").forEach((button) => {
        button.addEventListener("click", () => {
            const input = button.closest(".collection-copy-row").querySelector("[data-share-code-input]");

            copyText(input.value, button);
        });
    });

    document.querySelectorAll("[data-save-collection-settings]").forEach((button) => {
        button.addEventListener("click", () => {
            const modal = button.closest("[data-collection-settings-modal]");
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
            button.textContent = "Saved";

            setTimeout(() => {
                button.textContent = "Save settings";
            }, 1400);

            applyBookmarkSearch();
        });
    });

    document.querySelector("[data-create-collection-submit]")?.addEventListener("click", () => {
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
        const card = document.createElement("article");

        card.className = "collection-card";
        card.dataset.collectionCard = "";
        card.dataset.collectionId = collectionId;
        card.dataset.searchText = `${name} ${visibility} new collection`;
        card.innerHTML = `
            <button class="collection-card__settings" type="button" aria-label="Open ${safeName} settings">
                ⚙
            </button>
            <button class="collection-card__main" type="button" aria-label="Open ${safeName}">
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
                    <span class="collection-card__code">Code: NEW-${Math.floor(1000 + Math.random() * 9000)}</span>
                </div>
            </button>
        `;

        updateVisibilityLabel(card.querySelector("[data-collection-visibility-label]"), visibility);
        grid.prepend(card);
        nameInput.value = "";
        visibilityInput.value = "Public";
        closeModal(modal);
        applyBookmarkSearch();
    });

    document.querySelectorAll("[data-open-share-import]").forEach((button) => {
        button.addEventListener("click", () => {
            openModal(document.getElementById("shareImportModal"));
        });
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
