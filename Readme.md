# ReShortcut Unsign

Atajo de iOS que quita la firma a un atajo y convierte entre `.shortcut`, JSON y plist (XML).

**Versión:** 0.0.2 (en pruebas)

## Entradas

| Entrada | Qué muestra |
| --- | --- |
| Enlace de iCloud (Compartir) | Menú de salidas |
| `.shortcut` firmado | Menú de salidas |
| `.shortcut` sin firma | Aviso y salidas JSON, plist o todos |
| `.json` o `.plist` | Pregunta si generar el `.shortcut` |
| Abrir el atajo | Elegir enlace o archivo |

## Actualizaciones

Al terminar, y como máximo una vez al día, consulta `version.json`. Si `build` es mayor y `url` es un enlace de iCloud, ofrece actualizar. La fecha se guarda en `Shortcuts/ReShortcutUnsign/ultima_revision.txt`; bórralo para forzar otra revisión.

Antes de publicar en `main`, cambia la acción de texto `Canal` de `dev` a `main`.

## Requisitos

[a-Shell](https://holzschu.github.io/a-Shell_iOS/) para procesar archivos. Con un enlace de iCloud y salida *Solo .shortcut* no se usa.

## Desarrollo

```sh
python3 tools/build.py      # incrusta src/unsign.py y genera dist/
python3 tools/validate.py   # revisa la estructura
```

`main` contiene lo publicado y `dev` el trabajo en curso.
