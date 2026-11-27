# ReShortcut Unsign

Atajo de iOS que quita la firma a un atajo y convierte entre `.shortcut`, JSON y plist (XML).

**Versión:** 0.0.1 (en pruebas)

## Entradas

| Entrada | Qué muestra |
| --- | --- |
| Enlace de iCloud (Compartir) | Menú de salidas |
| `.shortcut` firmado | Menú de salidas |
| `.shortcut` sin firma | Aviso y salidas JSON, plist o todos |
| `.json` o `.plist` | Pregunta si generar el `.shortcut` |
| Abrir el atajo | Elegir enlace o archivo |

## Requisitos

[a-Shell](https://holzschu.github.io/a-Shell_iOS/) para procesar archivos. Con un enlace de iCloud y salida *Solo .shortcut* no se usa.

## Desarrollo

```sh
python3 tools/build.py      # incrusta src/unsign.py y genera dist/
python3 tools/validate.py   # revisa la estructura
```

`main` contiene lo publicado y `dev` el trabajo en curso.
