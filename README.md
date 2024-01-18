# Scraper y archivo de resplado de La Agenda Revista - Buenos Aires

> Quienes hacemos La Agenda procuramos (...) una mentalidad abierta no sólo en cuanto a la pluralidad de sus voces sino también con respecto a los formatos y los géneros que usamos. Intentamos hablar sobre cómo vivimos y sobre cómo queremos vivir, contar y contarnos historias de personas que nos parecen admirables o increíbles, leernos fragmentos de libros imperdibles y ocasionalmente detectar algo por lo que valga la pena indignarse. Siempre con libertad, rigor, desenfado y el mayor de los respetos por el lector.

De [Qué es La Agenda](https://laagenda.buenosaires.gob.ar/contenido/5137-que-es-la-agenda?origin=Qu%C3%A9%20es%20La%20Agenda)


Este proyecto es un "scraper" (un software para la obtencion automatizada de información en internet) y a la vez un archivo histórico que almacena los textos publicados en La Agenda Revista desde sus inicios en 2015 hasta la actualidad. 



Sitio nuevo: https://laagenda.buenosaires.gob.ar/. Sitio antiguo: https://laagenda.tumblr.com


## Cómo usar el archivo. 

Los articulos se guardan en la carpeta [posts/](https://github.com/mgaitan/laagenda-scraper/tree/main/posts/por-autor) en formato Markdown (`.md`). 
Tambien estan "linkeados" desde subcarpetas [posts/por-autor/](https://github.com/mgaitan/laagenda-scraper/tree/main/posts/por-autor), [posts/por-fecha/](https://github.com/mgaitan/laagenda-scraper/tree/main/posts/por-fecha) y [posts/por-seccion/](https://github.com/mgaitan/laagenda-scraper/tree/main/posts/por-seccion)


## Cómo utilizar el scraper

En primer lugar, instalar los requerimientos

```
pip install -r requirements.txt
```

Para actualizar los articulos del sitio antiguo en Tumblr:

```
scrapy runspider laagenda_tumblr.py
```

De sitio nuevo 
```
scrapy runspider laagenda_tumblr.py
```

## Cómo crear un ebook a partir de un conjunto de archivos. 

Para generar un epub desde los archivos Markdown se puede usar [pandoc](https://pandoc.org/). 
Por ejemplo, para crear un epub para los articulos de un autor. 


```
pandoc posts/por-autor/camila-sosa-villada/*.md --metadata title="La Agenda Revista - Camila Sosa Villada" --toc --toc-depth=1 -o laagenda-camila-sosa.epub
```

Y luego opcionalmente convertir a mobi para Kindle usando Calibre

```
ebook-converter laagenda-camila-sosa.epub laagenda-camila-sosa.mobi
```
