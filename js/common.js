/**
 * Load external HTML into target element
 * @param {string} targetId
 * @param {string} fileName
 */
async function loadPartial(targetId, fileName) {
    const target = document.getElementById(targetId);

    try {
        const response = await fetch(fileName);

        if (!response.ok) {
            throw new Error(`Failed to load ${fileName}: ${response.status}`);
        }

        const htmlText = await response.text();
        target.innerHTML = htmlText;

        if (targetId === "headerInclude") {
            activateHeaderLink();
        }

    } catch (error) {
        console.error("Error loading partial:", error);
        target.innerHTML = "";
    }
}

function activateHeaderLink() {
    const links = document.querySelectorAll(".site-header__link");
    const currentPage = window.location.pathname.split("/").pop();

    links.forEach(link => {
        const href = link.getAttribute("href");
        if (!href) {
            return;
        }

        const linkPage = href.split("/").pop();

        if (linkPage === currentPage) {
            link.classList.add("active");
        } else {
            link.classList.remove("active");
        }
    });
}

async function init() {
    await Promise.all([
        loadPartial("headerInclude", "header.html"),
        loadPartial("footerInclude", "footer.html")
    ]);
}

document.addEventListener("DOMContentLoaded", init);
