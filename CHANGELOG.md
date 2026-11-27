# Cambios

## 0.0.8 (en pruebas)

- Menús, preguntas y alertas con emojis como iconos. El emoji va fijo en el atajo, delante del texto traducido, así que `lang/es.json` y `lang/en.json` quedan sin emojis y no hay que volver a subir los idiomas.
- Selector de idioma con 🌐, 🇪🇸 y 🇬🇧.
- Corrige «No se pudo abrir el archivo idioma.txt» en la primera ejecución: antes de leer el idioma el atajo crea la carpeta `ReShortcutUnsign/lang` (guarda `carpeta.txt`), porque sin la carpeta Atajos daba error aunque «Error si no se encuentra» estuviera desactivado.

## 0.0.7 (en pruebas)

- El atajo se llama ReShortcut-Unsign (antes ReShortcut Unsign) y su fuente en `src/` pasa de JSON a plist: `src/ReShortcut-Unsign.plist`.
- Idioma: el pack se guarda como texto en `ReShortcutUnsign/lang/<código>.txt` (igual que `idioma.txt`) y se lee de ahí, porque Atajos fuerza `.txt` al guardar texto y el `.json` no se encontraba. El contenido sigue siendo JSON.
- Actualizar: con un enlace de GitHub descarga el `.shortcut` firmado (Obtener contenido de URL) y lo abre con Abrir archivo (antes Abrir URL); `shortcuts://import-workflow` no funcionó en las pruebas. Los enlaces de iCloud se abren igual que antes.

## 0.0.6 (en pruebas)

- La revisión diaria vuelve a descargar el idioma guardado (por ejemplo `en`) y lo reemplaza si la descarga es válida.

## 0.0.5 (en pruebas)

- Menús, preguntas y avisos pasan a claves de `lang/*.json` (español e inglés).
- Las notas de la versión se muestran en el idioma elegido.
- Corrige la versión del comentario inicial del atajo.
- `validate.py` revisa la versión del comentario y que las claves usadas existan en `es.json`.

## 0.0.4 (en pruebas)

- La actualización acepta, además de iCloud, un enlace directo al `.shortcut` firmado en GitHub (se abre con `shortcuts://import-workflow`).
- `validate.py` revisa que las versiones coincidan y que `url` sea un enlace admitido.

## 0.0.3 (en pruebas)

- Prototipo de idiomas: menú de salida en español o inglés.
- Opción **Idioma / Language** al abrir el atajo.

## 0.0.2 (en pruebas)

- Revisión de actualizaciones al terminar, una vez al día.
- `version.json` con versión, build, enlace y notas.

## 0.0.1 (en pruebas)

- Nuevo nombre: ReShortcut Unsign (antes ShortcutSimpleTool).
- Detección de JSON y plist por contenido, no solo por el nombre.
- Acepta más tipos de entrada desde Compartir.
- Un JSON o plist con enlaces de iCloud dentro se trata como archivo.
- Menú propio para un `.shortcut` sin firma.
