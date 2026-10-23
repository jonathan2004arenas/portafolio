
# app/models/project.py

PROJECTS = [
    {
        "id": 1,
        "title": "Mi portafolio",
        "description": (
            "Aplicación web personal desarrollada con Flask para presentar "
            "mis proyectos, habilidades y recorrido como desarrollador."
        ),
        "technologies": [
            "Python", "Flask", "HTML", "CSS", "JavaScript"
        ],
        "github": "https://github.com/jonathan2004arenas/portafolio",
        "demo": "https://jonathan2004arenas.github.io/portafolio/",
        "image": "img/panorama-silueta-centro-manhattan-ciudad-nueva-york-al-atardecer-rascacielos-cielo-colorido-sobre-rio 1.png",
        "featured": False,
    },
    {
        "id": 2,
        "title": "Cinemafull",
        "description": (
            "Sitio web temático dedicado a películas y series, creado como "
            "práctica de diseño y desarrollo web."
        ),
        "technologies": ["HTML", "CSS", "PHP", "Git"],
        "github": "https://github.com/jonathan2004arenas/Cinemafull",
        "demo": "https://jonathan2004arenas.github.io/Cinemafull/",
        "image": "img/Cinemafull.png",
        "featured": True,
    },
    {
        "id": 3,
        "title": "Cara de Papa",
        "description": (
            "Ejercicio visual que construye un personaje inspirado en Toy "
            "Story utilizando elementos y estilos de HTML y CSS."
        ),
        "technologies": ["HTML", "CSS"],
        "github": "https://github.com/jonathan2004arenas/cara-de-papa",
        "demo": "https://jonathan2004arenas.github.io/cara-de-papa/",
        "image": "img/caradpapa.png",
        "featured": True,
    },
    {
        "id": 4,
        "title": "Rumbo",
        "description": (
            "Propuesta web dedicada a destinos turísticos y planificación "
            "de viajes."
        ),
        "technologies": ["HTML", "CSS", "JavaScript"],
        "github": "https://github.com/jonathan2004arenas/Rumbo",
        "demo": "https://jonathan2004arenas.github.io/Rumbo/",
        "image": "img/rumbo.png",
        "featured": True,
    },
    {
        "id": 5,
        "title": "Website Bootstrap",
        "description": (
            "Práctica de diseño web adaptable utilizando Bootstrap, HTML, "
            "CSS y JavaScript."
        ),
        "technologies": ["HTML", "CSS", "JavaScript", "Bootstrap"],
        "github": "https://github.com/jonathan2004arenas/Bootstrap",
        "demo": "https://jonathan2004arenas.github.io/Bootstrap/",
        "image": "img/website-bootstrap.png",
        "featured": True,
    },
]


def get_all_projects():
    """Devuelve todos los proyectos."""
    return PROJECTS.copy()


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


def get_featured_projects():
    """Devuelve únicamente los proyectos destacados."""
    return [
        project.copy()
        for project in PROJECTS
        if project["featured"]
    ]
