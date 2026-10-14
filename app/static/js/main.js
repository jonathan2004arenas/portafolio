
const searchInput = document.querySelector("#project-search");
const technologyFilter = document.querySelector("#technology-filter");
const projectCards = document.querySelectorAll(".project-card");
const resultsCount = document.querySelector("#results-count");
const noResults = document.querySelector("#no-results");

if (searchInput && technologyFilter) {
    function filterProjects() {
        const query = searchInput.value.trim().toLowerCase();
        const selectedTechnology = technologyFilter.value;

        let visibleCount = 0;

        projectCards.forEach((card) => {
            const searchableText = card.dataset.search;
            const technologies = card.dataset.technologies
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

        resultsCount.textContent =
            `${visibleCount} proyectos encontrados`;

        noResults.hidden = visibleCount !== 0;
    }

    searchInput.addEventListener("input", filterProjects);
    technologyFilter.addEventListener("change", filterProjects);
}
