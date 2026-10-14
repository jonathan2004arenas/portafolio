
# app/models/project.py

PROJECTS = [
    {
        "id": 1,
        "title": "Mi portafolio",
        "description": (
            "Aplicación web personal para presentar "
            "mis proyectos y habilidades."
        ),
        "technologies": ["Python", "Flask", "HTML", "CSS", "JavaScript"],
        "github": "https://github.com/jonathan2004arenas/portafolio",
        "demo": "https://jonathan2004arenas.github.io/portafolio/",
    },
    {
        "id": 2,
        "title": "Proyecto de pagina de cine",
        "description": (
            "Espacio para documentar otro proyecto "
            "que haya desarrollado."
        ),
        "technologies": ["PHP", "Git", "HTML"],
        "github": "https://github.com/jonathan2004arenas/Cinemafull",
        "demo": "https://jonathan2004arenas.github.io/Cinemafull/",
    },
    {
        "id": 3,
        "title": "Cara de papa",
        "description": (
            "Espacio para documentar otro proyecto "
            "que haya desarrollado."
        ),
        "technologies": ["HTML", "CSS"],
        "github": "https://github.com/jonathan2004arenas/cara-de-papa",
        "demo": "https://jonathan2004arenas.github.io/cara-de-papa/",
    },
]


def get_all_projects():
    """Devuelve todos los proyectos."""
    return PROJECTS


def get_project_by_id(project_id):
    """Busca un proyecto por su identificador."""
    for project in PROJECTS:
        if project["id"] == project_id:
            return project

    return None


def get_all_technologies():
    """Devuelve las tecnologías únicas de todos los proyectos."""
    technologies = {
        technology
        for project in PROJECTS
        for technology in project["technologies"]
    }

    return sorted(technologies, key=str.lower)
