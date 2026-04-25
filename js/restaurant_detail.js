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

        // inject HTML in target element
        target.innerHTML = htmlText;

        // activate header
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
    links.forEach(link => {
        if (link.getAttribute("href") && link.getAttribute("href").includes("restaurant")) {
            link.classList.add("active");
        }
    });
}

// page init
async function init() {
    // load header & footer
    await Promise.all([
        loadPartial("headerInclude", "header.html"),
        loadPartial("footerInclude", "footer.html")
    ]);
}

document.addEventListener("DOMContentLoaded", init);