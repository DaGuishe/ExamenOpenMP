#!/usr/bin/env python3
"""Genera informe/informe.pdf: informe de la Parte IV + bitácora de IA como anexo.

Cadena: Markdown --(pandoc, MathML)--> HTML --(Chromium vía Playwright/Node)--> PDF.
Requiere pandoc y node con playwright.
"""
import os
import subprocess

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INF = os.path.join(RAIZ, "informe")

CSS = """
@page { size: letter; margin: 1.6cm 1.7cm; }
body { font-family: 'DejaVu Serif', Georgia, serif; font-size: 9.6pt; line-height: 1.33;
       color: #111; background: #fff; max-width: none; margin: 0; }
header#title-block-header { text-align: center; margin-bottom: 4pt; }
h1.title { font-size: 13.5pt; color: #7a0026; margin: 0; }
p.subtitle { font-size: 11pt; margin: 2pt 0 0; color: #7a0026; }
p.meta { text-align: center; font-size: 8.4pt; color: #444; margin: 2pt 0 6pt; }
h2 { font-size: 11pt; color: #7a0026; border-bottom: 1px solid #c9a3ae; margin: 9pt 0 3pt; }
p { margin: 2pt 0; text-align: justify; }
li { margin: 1.5pt 0; text-align: left; }
ol, ul { margin: 2pt 0; padding-left: 16pt; }
code { font-size: 8.6pt; background: #f3f0f1; padding: 0 2px; }
table { border-collapse: collapse; margin: 4pt auto; font-size: 8.6pt; }
th, td { border-bottom: 1px solid #ccc; padding: 1.5pt 6pt; vertical-align: top; }
th { border-bottom: 1.5px solid #7a0026; }
.figura { text-align: center; }
.figura img { width: 50%; }
.pendiente { background: #fff3b0; }
.anexo { page-break-before: always; }
.anexo table { font-size: 7.6pt; }
.anexo h1 { font-size: 13pt; color: #7a0026; }
math { font-size: 105%; }
"""

JS = """
const { chromium } = require('playwright');
(async () => {
  const [html, pdf] = process.argv.slice(2);
  const b = await chromium.launch();
  const pg = await b.newPage();
  await pg.goto('file://' + html, { waitUntil: 'load' });
  await pg.pdf({ path: pdf, format: 'Letter', printBackground: true,
                 displayHeaderFooter: true, headerTemplate: '<span></span>',
                 footerTemplate: '<div style="font-size:7pt;width:100%;text-align:center;color:#777">' +
                                 '<span class="pageNumber"></span> / <span class="totalPages"></span></div>',
                 margin: { top: '1.5cm', bottom: '1.6cm', left: '1.7cm', right: '1.7cm' } });
  await b.close();
})();
"""


def pandoc_fragmento(ruta):
    return subprocess.run(["pandoc", ruta, "--mathml", "-t", "html5"],
                          capture_output=True, text=True, check=True).stdout


def main():
    css = os.path.join(INF, "estilo.css")
    with open(css, "w") as f:
        f.write(CSS)
    anexo = pandoc_fragmento(os.path.join(RAIZ, "bitacora_ia.md"))
    anexo_html = os.path.join(INF, "anexo.html")
    with open(anexo_html, "w") as f:
        f.write(f'<div class="anexo">\n{anexo}\n</div>\n')
    html = os.path.join(INF, "informe.html")
    subprocess.run(["pandoc", os.path.join(INF, "informe.md"), "--standalone", "--mathml",
                    "--css", "estilo.css", "--metadata", "lang=es",
                    "--include-after-body", anexo_html, "-o", html], check=True)
    os.remove(anexo_html)
    js = os.path.join(INF, "_pdf.js")
    with open(js, "w") as f:
        f.write(JS)
    try:
        subprocess.run(["node", js, html, os.path.join(INF, "informe.pdf")], check=True,
                       cwd=INF)
    finally:
        os.remove(js)
    print("Generado informe/informe.pdf")


if __name__ == "__main__":
    main()
