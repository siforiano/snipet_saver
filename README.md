# SnippetSaver - Gestor Visual de Snippets de Código Python

## Descripción

SnippetSaver es una aplicación de escritorio visual para guardar, gestionar, buscar y exportar fragmentos de código (snippets) en Python. Usa una interfaz gráfica moderna basada en CustomTkinter, pensada para ser intuitiva y atractiva.

Ofrece funcionalidades para:
- Agregar, editar y eliminar snippets fácilmente.
- Búsqueda en tiempo real por descripción, etiquetas o contenido del código.
- Exportación directa y selectiva de snippets a PDF.
- Selección entre tema claro, oscuro o automático.
- Gestión eficiente de los snippets en un archivo JSON local.

Perfecta para desarrolladores que quieren organizar su base de código reutilizable con estilo y productividad.

---

## Requisitos

- Python 3.8 o superior
- Paquetes Python especificados en `requirements.txt`

---

## Instalación

Clona el repositorio y crea un entorno virtual (recomendado):

git clone <tu-repo-url>
cd snippetsaver
python -m venv venv
source venv/bin/activate # Linux / macOS
venv\Scripts\activate # Windows
pip install -r requirements.txt

---

## Uso

Ejecuta la aplicación con:

python snippetsaver.py

---

## Funcionalidades destacadas

- Interfaz gráfica moderna, maximizada y con selector de tema.
- Añade y edita snippets con etiquetas para fácil búsqueda.
- Búsqueda dinámica en toda la base de snippets.
- Exporta a PDF los snippets seleccionados mediante un diálogo intuitivo.
- Confirmaciones visuales para acciones críticas.
- Archivo `snippets.json` simple y legible para almacenar tus fragmentos.

---

## Dependencias

- [customtkinter](https://github.com/TomSchimansky/CustomTkinter) para UI moderna.
- [CTkMessagebox](https://pypi.org/project/CTkMessagebox/) para cuadros de diálogo bonitos.
- [reportlab](https://www.reportlab.com/) para generación de PDFs.

---

## Licencia

Este proyecto está licenciado bajo MIT License.

---
