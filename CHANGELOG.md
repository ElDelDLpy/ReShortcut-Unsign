# Cambios

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
