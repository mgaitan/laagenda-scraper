import scrapy
import locale
from pathlib import Path
import datetime

from markdownify import markdownify as md

from _helpers import write_md, url2filename


locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")


class LaAgendaSpider(scrapy.Spider):
    name = "laagenda_tumblr"
    start_urls = [f"https://laagenda.tumblr.com/page/{page}" for page in range(1, 525)]

    def parse(self, response):
        for post in response.css("#posts > div > article"):
            post_id = post.xpath("@data-post-id").get().split("_")[1]
            yield response.follow(f"/post/{post_id}", self.parse_post)

    def parse_post(self, response):
        url = response.url
        try:
            filename = url2filename(url)
        except ValueError:
            self.logger.info(f"Articulo ya bajado {url}")
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

        write_md(filename, titulo, bajada, fecha, seccion, autor, url, body, year, month)
        
