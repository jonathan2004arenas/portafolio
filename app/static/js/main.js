
"use strict";

// ========================================
// 1. SELECTORES
// ========================================

const html = document.documentElement;
const themeToggle = document.querySelector("#theme-toggle");
const themeIcon = document.querySelector("#theme-icon");
const menuToggle = document.querySelector("#menu-toggle");
const mainNav = document.querySelector("#main-nav");
const currentYear = document.querySelector("#current-year");

// ========================================
// 2. TEMA CLARO Y OSCURO
// ========================================

function getPreferredTheme() {
    try {
        const savedTheme = localStorage.getItem("portfolio-theme");

        if (savedTheme === "dark" || savedTheme === "light") {
            return savedTheme;
        }
    } catch (error) {
        // Si el navegador bloquea el almacenamiento,
        // utilizamos el tema oscuro como alternativa.
    }

    return "dark";
}

function applyTheme(theme) {
    const normalizedTheme = theme === "light" ? "light" : "dark";

    html.dataset.theme = normalizedTheme;

    if (themeIcon) {
        themeIcon.textContent = normalizedTheme === "dark" ? "☀" : "☾";
    }

    if (themeToggle) {
        const nextTheme = normalizedTheme === "dark" ? "claro" : "oscuro";

        themeToggle.setAttribute("aria-label", `Cambiar a tema ${nextTheme}`);
        themeToggle.setAttribute("title", `Cambiar a tema ${nextTheme}`);
    }

    const themeColor = document.querySelector('meta[name="theme-color"]');

    if (themeColor) {
        themeColor.setAttribute(
            "content",
            normalizedTheme === "dark" ? "#101522" : "#f7f8fc"
        );
    }
}

applyTheme(getPreferredTheme());

if (themeToggle) {
    themeToggle.addEventListener("click", () => {
        const nextTheme = html.dataset.theme === "dark" ? "light" : "dark";

        applyTheme(nextTheme);

        try {
            localStorage.setItem("portfolio-theme", nextTheme);
        } catch (error) {
            // El cambio de tema sigue funcionando durante esta visita
            // aunque no sea posible guardar la preferencia.
        }
    });
}

// ========================================
// 3. MENÚ PARA MÓVILES
// ========================================

function closeMenu() {
    if (!menuToggle || !mainNav) return;

    mainNav.classList.remove("is-open");
    menuToggle.setAttribute("aria-expanded", "false");
    menuToggle.setAttribute("aria-label", "Abrir menú");
}

if (menuToggle && mainNav) {
    menuToggle.addEventListener("click", () => {
        const isOpen = mainNav.classList.toggle("is-open");

        menuToggle.setAttribute("aria-expanded", String(isOpen));
        menuToggle.setAttribute(
            "aria-label",
            isOpen ? "Cerrar menú" : "Abrir menú"
        );
    });

    mainNav.querySelectorAll("a").forEach((link) => {
        link.addEventListener("click", closeMenu);
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            closeMenu();
        }
    });

    window.addEventListener("resize", () => {
        if (window.innerWidth > 760) {
            closeMenu();
        }
    });
}

// ========================================
// 4. AÑO AUTOMÁTICO DEL PIE DE PÁGINA
// ========================================

if (currentYear) {
    currentYear.textContent = String(new Date().getFullYear());
}

// ========================================
// 5. ANIMACIONES AL DESPLAZARSE
// ========================================

const revealElements = document.querySelectorAll(".reveal");
const reduceMotion = window.matchMedia(
    "(prefers-reduced-motion: reduce)"
).matches;

if ("IntersectionObserver" in window && !reduceMotion) {
    const revealObserver = new IntersectionObserver(
        (entries, observer) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("is-visible");
                    observer.unobserve(entry.target);
                }
            });
        },
        {
            threshold: 0.12,
            rootMargin: "0px 0px -35px 0px"
        }
    );

    revealElements.forEach((element) => {
        revealObserver.observe(element);
    });
} else {
    revealElements.forEach((element) => {
        element.classList.add("is-visible");
    });
}

// ========================================
// 6. FILTROS DE LA PÁGINA DE PROYECTOS
// ========================================

const searchInput = document.querySelector("#project-search");
const technologyFilter = document.querySelector("#technology-filter");
const projectCards = document.querySelectorAll(".project-card");
const resultsCount = document.querySelector("#results-count");
const noResults = document.querySelector("#no-results");

if (searchInput && technologyFilter) {
    function filterProjects() {
        const query = searchInput.value.trim().toLowerCase();
        const selectedTechnology = technologyFilter.value.toLowerCase();

        let visibleCount = 0;

        projectCards.forEach((card) => {
            const searchableText = card.dataset.search || "";
            const technologies = (card.dataset.technologies || "")
                .toLowerCase()
                .split(",");

            const matchesText = searchableText.includes(query);

            const matchesTechnology =
                !selectedTechnology ||
                technologies.includes(selectedTechnology);

            const isVisible = matchesText && matchesTechnology;

            card.hidden = !isVisible;

            if (isVisible) {
                visibleCount++;
            }
        });

        if (resultsCount) {
            resultsCount.textContent =
                `${visibleCount} ${visibleCount === 1 ? "proyecto encontrado" : "proyectos encontrados"}`;
        }

        if (noResults) {
            noResults.hidden = visibleCount !== 0;
        }
    }

    searchInput.addEventListener("input", filterProjects);
    technologyFilter.addEventListener("change", filterProjects);
}
