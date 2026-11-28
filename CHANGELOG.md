# Cambios

## 0.1.2 (en pruebas)

- Aviso antes de buscar actualización, como en DLpy: cuando toca revisar (según la frecuencia), el atajo muestra un menú con `RSU vX.Y.Z`, la frecuencia y una nota («Requiere internet. Si falla, se volverá a preguntar la próxima vez que abras el atajo») con dos opciones: 🔄 Revisar ahora o ⏩ Omitir. Con Omitir no se consulta nada y no vuelve a preguntar hasta el siguiente periodo. Con Revisar ahora se consulta `version.json` y, si hay una versión distinta, sale el menú de actualización de siempre.
- La marca de la última revisión (`ultima_revision.txt`) ahora se guarda **después** de descargar `version.json`: si no hay internet o falla la descarga, no se marca y se vuelve a preguntar la próxima vez que abras el atajo (en 0.1.1 se marcaba antes de consultar). Con el aviso desactivado se mantiene el comportamiento anterior (marca antes de consultar, para no mostrar un error cada vez que abras el atajo sin internet).
- Configuración reorganizada en dos niveles (⚙️ Configuración, al abrir el atajo sin entrada): ⏱️ Frecuencia (cada día, cada semana, cada mes o solo manual), 🔔 Aviso antes de buscar (activado por defecto; se guarda en `ReShortcutUnsign/aviso.txt` como `si` o `no`), 🔄 Buscar ahora, 🐚 Verificar a-Shell otra vez (borra la respuesta guardada en `ashell.txt` y vuelve a preguntar; antes había que borrar el archivo a mano) y ♻️ Restablecer configuración (frecuencia cada día, aviso activado y a-Shell por verificar; no cambia el idioma, y pide confirmación). El menú de configuración muestra la frecuencia y el aviso actuales.
- El menú principal ahora dice `RSU vX.Y.Z` (la versión sale de la misma variable que usa la revisión de actualizaciones).
- Textos nuevos en `lang/` (`menu_check_*`, `cfg_freq`, `cfg_notice`, `cfg_on`, `cfg_off`, `cfg_ashell`, `cfg_reset`, `alert_cfg_ashell_message`, `alert_cfg_reset_*`). Los packs pasan a la revisión 4. Hasta que la revisión baje el inglés nuevo, los textos que falten salen en español.
- `validate.py` ahora también revisa que cada menú tenga tantos casos como opciones, que ninguna variable se use antes de definirse, que el aviso previo vaya antes de consultar `version.json` (y que Omitir no consulte), que el menú principal diga `RSU v` y la versión y que el aviso esté activado por defecto.

## 0.1.1 (en pruebas)

- Aviso de a-Shell: antes del modo a-Shell (todo menos enlace de iCloud + solo .shortcut) el atajo pregunta una vez si a-Shell está instalado. Atajos no puede detectar apps instaladas ni capturar el error de una acción de otra app, así que la respuesta se guarda en `ReShortcutUnsign/ashell.txt`. Con «No, instalar» muestra un aviso y, al pulsar OK, abre a-Shell en la App Store y termina; con «Sí» sigue y no vuelve a preguntar. Para volver a preguntar, borra `ashell.txt`.
- Menú de actualización con el mismo diseño que DLpy: título, `Instalada:`, `Nueva:` y las notas en el idioma elegido, con ⬇️ Instalar y ⏩ Omitir. La revisión ahora salta **al abrir el atajo** (antes era al terminar), antes de procesar la entrada y con la frecuencia configurada (ver abajo); si instalas, el atajo termina para no seguir procesando mientras se actualiza, y si omites continúa normal. Si no hay internet justo cuando toca revisar, Atajos muestra un error esa vez (la marca se guarda antes de consultar) y se reintenta en el siguiente periodo; con ⏸️ Solo manual no ocurre; instalar abre el enlace de iCloud o descarga el `.shortcut` de GitHub como antes. El script va incrustado en el atajo, así que no hay una actualización de script aparte.
- Configuración: al abrir el atajo sin entrada hay una opción ⚙️ Configuración para elegir cada cuánto se buscan actualizaciones: cada día (por defecto, como hasta ahora), cada semana, cada mes o solo manual. También hay 🔄 Buscar ahora (la búsqueda se hace la próxima vez que abras el atajo). La frecuencia se guarda en `ReShortcutUnsign/frecuencia.txt` y la última revisión en `ultima_revision.txt` (ahora guarda el periodo: `2026-11-28`, `2026-48`, `2026-11` o `manual`).
- Textos nuevos en `lang/` (`menu_update_installed`, `menu_update_new`, `menu_ashell_*`, `alert_ashell_missing_*`, `menu_source_config`, `cfg_*`, `alert_cfg_*`) y nuevos `menu_update_title`, `menu_update_now`, `menu_update_later`. Los packs pasan a la revisión 3. Hasta que la revisión diaria baje el inglés nuevo, los textos que falten salen en español.

## 0.1.0 (en pruebas)

- Corrige la condición de actualización que Atajos marcaba como incompleta («Elige un valor para cada parámetro»): la versión remota pasa por una acción de Texto y se compara con la instalada con una coincidencia de texto (`remota|instalada`), el mismo método que la revisión diaria. Si no coinciden, ofrece actualizar; si son iguales, no avisa.
- `validate.py` revisa esa comparación.

## 0.0.9 (en pruebas)

- Corrige la detección de actualizaciones: avisaba siempre porque comparaba el `build` remoto con un número fijo. Ahora compara la `version` de `version.json` con la instalada y solo ofrece actualizar si es **distinta** (también si la remota es menor).
- `validate.py` revisa que la condición de actualización compare la versión instalada y no un número fijo.

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
