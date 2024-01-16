import scrapy
from slugify import slugify
import locale
from pathlib import Path
from urllib.parse import urlparse, unquote
import datetime

from markdownify import markdownify as md


locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")


class LaAgendaSpider(scrapy.Spider):
    name = "laagenda"
    start_urls = [f"https://laagenda.tumblr.com/page/{page}" for page in range(1, 525)]

    def parse(self, response):
        for post in response.css("#posts > div > article"):
            post_id = post.xpath("@data-post-id").get().split("_")[1]
            yield response.follow(f"/post/{post_id}", self.parse_post)

    def parse_post(self, response):
        url = response.url
        path = urlparse(url).path
        post_id, slug = path.split("/")[-2:]
        slug = unquote(slug).replace(".html", "")
        filename = f"{post_id}-{slug}.md"
        posts_path = Path("posts")
        posts_path.mkdir(exist_ok=True)
        file_path = posts_path / filename

        if file_path.exists():
            self.logger.info(f"Articulo ya bajado {file_path}")
            yield

        seccion = response.css("div.heading > div > div > div > h4::text").get().strip()
        titulo = response.css("div.heading > div > div > div > h1::text").get().strip()
        bajada = response.css("div.heading > div > div > div > h2::text").get().strip()
        fecha = (
            (
                response.css("div.heading > div > div > div > p.color-gray::text")
                .get()
                .strip()
            )
            .replace("de de", "de")
            .replace(".", "")
            .replace("31 de abril", "30 de abril")
            .replace("Publicada el ", "")
            .replace("Publicada ", "")
            .replace("1ro ", "1 ")
        )
        fecha_obj = datetime.datetime.strptime(fecha, "%d de %B de %Y")
        year = fecha_obj.year
        month = fecha_obj.month
        try:
            autor = response.css("div.author::text").get().strip()
        except AttributeError:
            autor = "Autor desconocido"

        body_html = "".join(response.css("div.bg div.author ~ *").getall())
        if not body_html:
            # when there is no author
            body_html = "".join(response.css("div.bg div.heading ~ *").getall())

        body = md(body_html).replace("\xa0", " ").replace("![Jordan]", "![]")

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
        Path(file_path).write_text(articulo)

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
