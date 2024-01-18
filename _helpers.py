from pathlib import Path
from slugify import slugify
from urllib.parse import urlparse, unquote

import os


def k():
    os.kill(os.getpid(), 9)


def url2filename(url):
    path = urlparse(url).path
    post_id, slug = path.split("/")[-2:]
    slug = unquote(slug).replace(".html", "")

    filename = f"{post_id}-{slug}.md"

    posts_path = Path("posts")
    posts_path.mkdir(exist_ok=True)
    file_path = posts_path / filename
    if file_path.exists():
        raise ValueError(f"Articulo ya bajado {file_path}")
        
    return filename
    

def write_md(titulo, bajada, fecha, seccion, autor, url, body, year, month):
    filename = url2filename(url)
    path = urlparse(url).path
    post_id, slug = path.split("/")[-2:]
    slug = unquote(slug).replace(".html", "")

    articulo = "\n".join(
        (
            f"# {titulo}",
            "",
            f"**{bajada}**" if bajada else "",
            "",
            f"{fecha} - {seccion}",
            "",
            f"_por {autor}_",
            "",
            f"Link original: {url}",
            "",
            body,
        )
    )

    # guardamos el archivo en posts/
    # y luego enlaces simbolicos en posts/por-seccion posts/por-autor/ posts/por-fecha
    (Path("posts")/filename).write_text(articulo)

    for folder_name in [
        f"posts/por-seccion/{slugify(seccion)}",
        f"posts/por-autor/{slugify(autor)}",
        f"posts/por-fecha/{year}-{month}",
    ]:
        folder_path = Path(folder_name)
        folder_path.mkdir(parents=True, exist_ok=True)

        symlink_path = folder_path / filename
        if not symlink_path.exists():
            symlink_path.symlink_to(f"../../{filename}")