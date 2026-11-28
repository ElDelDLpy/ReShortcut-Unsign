# ReShortcut-Unsign

Atajo de iOS que quita la firma a un atajo y convierte entre `.shortcut`, JSON y plist (XML).

**Versión:** 0.1.2 (en pruebas)

## Entradas

| Entrada | Qué muestra |
| --- | --- |
| Enlace de iCloud (Compartir) | Menú de salidas |
| `.shortcut` firmado | Menú de salidas |
| `.shortcut` sin firma | Aviso y salidas JSON, plist o todos |
| `.json` o `.plist` | Pregunta si generar el `.shortcut` |
| Abrir el atajo | Elegir enlace o archivo |

## Actualizaciones

Al abrir el atajo, y con la frecuencia que elijas, avisa antes de buscar: muestra un menú con `RSU` y su versión, la frecuencia y una nota («Requiere internet…») con 🔄 **Revisar ahora** o ⏩ **Omitir**. Con Omitir no consulta nada y no vuelve a preguntar hasta el siguiente periodo. Con Revisar ahora consulta `version.json`; si la `version` es distinta de la instalada y `url` es un enlace de iCloud o el `.shortcut` firmado de este repo en GitHub, muestra un menú con la versión instalada, la nueva y las notas (en tu idioma) y ofrece ⬇️ Instalar u ⏩ Omitir: un enlace de iCloud se abre directamente; un `.shortcut` de GitHub se descarga y se abre. El periodo de la última revisión se guarda en `Shortcuts/ReShortcutUnsign/ultima_revision.txt` después de descargar `version.json` (si falla, se vuelve a preguntar la próxima vez); bórralo para forzar otra revisión.

Las actualizaciones y los idiomas se descargan de la rama `main`.

## Configuración

Abre el atajo sin entrada (menú principal, que dice `RSU` y su versión) y elige **⚙️ Configuración**:

| Opción | Qué hace | Archivo (`Shortcuts/ReShortcutUnsign/`) |
| --- | --- | --- |
| ⏱️ Frecuencia | Cada día (por defecto), cada semana, cada mes o solo manual | `frecuencia.txt` |
| 🔔 Aviso antes de buscar | Activado (por defecto) o desactivado. Desactivado busca directo, sin menú | `aviso.txt` (`si` o `no`) |
| 🔄 Buscar ahora | Fuerza la revisión la próxima vez que abras el atajo | `ultima_revision.txt` |
| 🐚 Verificar a-Shell otra vez | Vuelve a preguntar si tienes a-Shell | `ashell.txt` |
| ♻️ Restablecer configuración | Frecuencia cada día, aviso activado y a-Shell por verificar (pide confirmación; el idioma no cambia) | los tres anteriores |

## Idiomas

Se traducen menús, preguntas y avisos (español e inglés). El selector de idioma y el aviso de error de descarga van siempre en ambos idiomas. Abre el atajo sin entrada y elige **Idioma / Language**. El español va incrustado desde `shortcut/lang/es.json`; el inglés se descarga y se guarda como texto en `Shortcuts/ReShortcutUnsign/lang/en.txt` (Atajos fuerza `.txt` al guardar texto; el contenido sigue siendo JSON). El idioma guardado se vuelve a descargar con la revisión diaria de actualizaciones, así que se actualiza sin tener que elegirlo otra vez; si la descarga falla, se queda el anterior. Las claves no llevan puntos, porque Atajos los interpreta como rutas.

## Instalación

1. Instala [a-Shell](https://holzschu.github.io/a-Shell_iOS/) (ver Requisitos).
2. Desde el iPhone, descarga `shortcut/ReShortcut-Unsign.shortcut` de este repo y ábrelo con Atajos.
3. La primera vez, Atajos pedirá permisos; acéptalos.

## Requisitos

[a-Shell](https://holzschu.github.io/a-Shell_iOS/) para procesar archivos. Con un enlace de iCloud y salida *Solo .shortcut* no se usa.

Antes de usar a-Shell, el atajo pregunta una vez si lo tienes instalado (Atajos no puede detectarlo) y lo recuerda en `Shortcuts/ReShortcutUnsign/ashell.txt`. Si contestas que no, avisa y abre a-Shell en la App Store. Para que vuelva a preguntar, usa **⚙️ Configuración → 🐚 Verificar a-Shell otra vez** (o borra `ashell.txt`).

## Estructura del repositorio

Todo lo que el atajo necesita vive en `shortcut/` (la URL siempre es `main/shortcut/...`):

```
shortcut/
  ReShortcut-Unsign.shortcut   atajo firmado
  version.json                 versión, build, url y notas
  lang/es.json, lang/en.json   idiomas
backups/
  <versión>/shortcut/...       copia de cada versión publicada anterior
```

Cada vez que se publica una versión nueva en `main`, la anterior se guarda en `backups/<versión>/` con los mismos archivos. Para instalar una versión anterior, descarga su `.shortcut` de esa carpeta.

## Licencia

Sin licencia: todos los derechos reservados. Proyecto personal.
