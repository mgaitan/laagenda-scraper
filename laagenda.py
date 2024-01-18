import re
import scrapy
import itertools
from textwrap import dedent
from slugify import slugify
import json
from pathlib import Path
from datetime import datetime
from markdownify import markdownify as md
from _helpers import write_md, url2filename, k

import locale

locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")

def transform_entity(entity):
    if entity["type"] == "LINK":
        url = entity["data"]["url"]
        return f'<a href="{url}">{{}}</a>'
    elif entity["type"] == "IMAGE":
        src = entity["data"]["src"]
        return f'\n<img src="{src}" >\n'
    elif entity["type"] == "EMBEDDED_LINK" and "youtube" in entity["data"]["src"]:
        m = re.search(r"embed/([^?]+)", entity["data"]["src"])
        code = m.group(1) if m else None
        if code:
            return f'<a href="https://www.youtube.com/watch?v={code}"><img src="https://img.youtube.com/vi/{code}/0.jpg"></a>'
    return ""


def transform(text, inline_or_range, entities):
    if (key := inline_or_range.get("key")) is not None:
        # aplica contenido de entidad
        transformation = lambda f: entities[str(key)].format(f)
    elif inline_or_range["length"] <= 1:
        transformation = lambda f: f
    elif inline_or_range.get("style") == "ITALIC":
        transformation = lambda f: f"<i>{f}</i>"
    elif inline_or_range.get("style") == "BOLD" or (
        (size := inline_or_range.get("style", "").partition("fontsize-")[-1].replace("pt", ""))
        and int(size) > 16
    ):
        # cualquier tamaño de letra grande lo ponemos en negrita.
        transformation = lambda f: f"<b>{f}</b>"
    else:
        transformation = lambda f: f

    start = inline_or_range["offset"]
    end = start + inline_or_range["length"]

    text = text[:start] + transformation(text[start:end]) + text[end:]
    return text


def feater_parser(content):
    """
    Ingenieria inversa del contenido del framework https://www.feater.me/

    Considera
    https://laagenda.buenosaires.gob.ar/contenido/37504-una-pelicula-inagotable


    Cada contenido tiene un json de la siguiente forma.

    {
    "id": 37504,
    "name": 'Una película inagotable',
    "additions": 'Por Gustavo Nielsen;La época',
    "synopsis": 'Cumple treinta años "El acto en cuestión", la película maldita de Alejandro Agresti que se estrenó en el festival de Cannes pero nunca llegó a los cines.',

    "description": {     # json encoded
        "blocks": [
            {
                "key": "2p7fa",
                "text": "La avenida Calchaquí, tal como la avenida Hipólito Yrigoyen (ex Pavón), es una de las calles míticas del conurbano bonaerense. Su topografía interminable de pozos y oscuridad poco cambió con el transcurso de los años, y es tan sinónimo de suburbio como el Camino Negro. Maxi Prietto mamó ese asfalto caliente de chiquito, y por eso decidió bautizar como “Avenida Calchaquí” a la quinta canción de La montaña, el flamante disco de Los Espíritus. Y allí Prietto vuelve a dar cuenta de sus influencias musicales y sus obsesiones poéticas. En el primer caso, un boogie porteño que podría haber sido compuesto por Vox Dei, grupo que ya fue versionado por Los Espíritus en Sancocho Stereo (“Jeremías pies de plomo”, junto a Carca), por alguien que conoce tan bien la Calchaquí como Soulé o Willy Quiroga, y que tiene a Juanse de invitado en el papel de un Marc Bolan de Villa Devoto. ",
                "type": "unstyled",
                "depth": 0,
                "inlineStyleRanges": [
                    {"offset": 0, "length": 1, "style": "fontsize-30"},
                    {"offset": 1, "length": 877, "style": "fontsize-16"},
                    {"offset": 397, "length": 10, "style": "ITALIC"},
                ],
                "entityRanges": [{"offset": 11, "length": 9, "key": 1}],
                "data": {},
            }
        ],
        "entityMap": {
            "0": {
                "type": "LINK",
                "mutability": "MUTABLE",
                "data": {
                    "url": "http://www.conlosojosabiertos.com/el-acto-en-cuestion/",
                    "targetOption": "_blank",
                },
            },
            "1": {
                "type": "LINK",
                "mutability": "MUTABLE",
                "data": {
                    "url": "https://www.comunidadcinefila.org/",
                    "targetOption": "_blank",
                },
            },
            "2": {
                "type": "IMAGE",
                "mutability": "MUTABLE",
                "data": {
                    "src": "https://cdn.feater.me/files/images/1286896/aef474d1-8020-45f1-97cb-2289fc5a9226.jpg",
                    "height": "auto",
                    "width": "700px",
                },
                },
            },
        }
    }


    """
    url = f"https://laagenda.buenosaires.gob.ar/contenido/{content['id']}-{slugify(content['name'])}"
    try:
        autor, seccion = content["additions"][4:].split(";")
    except Exception:
        # try default
        if content["synopsis"] and content["synopsis"].startswith("por "):
            autor = content["synopsis"][4:].title()
            seccion = "Miradas"
        else:
            filename = url2filename(url)
            Path(f"{filename}.json").write_text(json.dumps(content))
            raise ValueError(f"Error {url}")

    fecha = datetime.strptime(content["created_at"], "%Y-%m-%d %H:%M:%S")
    data = {
        "url": url,
        "autor": autor,
        "seccion": seccion,
        "titulo": content["name"],
        "bajada": content["synopsis"],
        "fecha": fecha,
    }

    description = json.loads(content["description"])
    blocks = description["blocks"]

    entities = {k: transform_entity(v) for k, v in description["entityMap"].items()}

    paragraphs = []
    for block in blocks[4:]:
        text = block["text"].strip()

        if (not text and not block["type"] == "atomic") or text.lower() in (
            f"por {autor.lower()}",
            "_ _ _",
        ):
            continue

        # juntamos las transformaciones de entidades y inline en una sola lista.
        # y aplicamos de atras hacia adelante.
        # asume que no hay superposicion.
        transforms = sorted(
            itertools.chain(block["inlineStyleRanges"], block["entityRanges"]),
            reverse=True,
            key=lambda x: x["offset"],
        )

        for t in transforms:
            text = transform(text, t, entities)

        paragraphs.append(
            dedent(
                f"""
                <p>
                {text}
                </p>
                """
            )
        )
    data["body"] = md("".join(paragraphs))
    return data


class LaAgendaSpider(scrapy.Spider):
    name = "laagenda"
    start_urls = [
        f"https://laagenda.buenosaires.gob.ar/api/public/clients/171/channels/24/contentCreators?per_page=500&page={page}"
        for page in range(1, 8)
    ]

    def parse(self, response):
        for content in response.json()["data"]:
            try:
                data = feater_parser(content)
            except ValueError:
                self.logger.info(f"No se pudo parsear")
                continue
            url = data["url"]
            try:
                url2filename(url)
            except ValueError:
                self.logger.info(f"Articulo ya bajado {url}")
                continue
            fecha = data["fecha"]
            data["year"] = fecha.year
            data["month"] = fecha.month
            data["fecha"] = fecha.strftime("%d de %B de %Y")
            write_md(**data)
