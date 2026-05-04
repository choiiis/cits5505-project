document.addEventListener("DOMContentLoaded", () => {
    const shell = document.querySelector(".bookmark-stage-shell");
    const draftMount = document.getElementById("bookmarkDraftMount");

    if (shell) {
        shell.setAttribute("data-stage", "step2");
    }

    if (draftMount) {
        draftMount.innerHTML = Array.from({ length: 3 }, () => `
            <div class="col-md-6 col-xl-4">
                <article class="bookmark-draft-card">
                    <div class="bookmark-draft-card__media"></div>
                    <div class="bookmark-draft-card__body">
                        <div class="bookmark-draft-badge"></div>
                        <div class="bookmark-draft-line bookmark-draft-line--title"></div>
                        <div class="bookmark-draft-line bookmark-draft-line--meta"></div>
                        <div class="bookmark-draft-line bookmark-draft-line--rating"></div>
                        <div class="bookmark-draft-actions">
                            <div class="bookmark-draft-action bookmark-draft-action--primary"></div>
                            <div class="bookmark-draft-action bookmark-draft-action--secondary"></div>
                        </div>
                    </div>
                </article>
            </div>
        `).join("");
    }
});
