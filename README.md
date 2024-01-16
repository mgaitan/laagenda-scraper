# Scraper de La Agenda Revista


Nota: por ahora sólo los articulos antiguops

Sitio nuevo: https://laagenda.buenosaires.gob.ar/
Sitio antiguo: https://laagenda.tumblr.com


Para actualizar los articulos

```
pip install -r requirements.txt
scrapy runspider laagenda.py
```

Para generar un epub desde un autor/a se puede usar pandoc. 


```
pandoc posts/por-autor/camila-sosa-villada/*.md --css=epub.css --metadata title="La Agenda Revista - Camila Sosa Villada" --toc --toc-depth=1 -o laagenda-camila-sosa.epub
```

Y luego opcionalmente convertir a mobi para Kindle usando Calibre

```
ebook-converter laagenda-camila-sosa.epub laagenda-camila-sosa.mobi
```




