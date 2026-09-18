# AltUI – panel de vestuario y apariencia

Versión en español de la descripción de la [página de AltUI en Nexus Mods](https://www.nexusmods.com/thekillingantidote/mods/988). El original en inglés de la página de Nexus es el que manda.

El vestuario del juego da a cada autor de mods su propia pestaña, así que con unos cuantos mods de ropa instalados el mismo tipo de prenda queda repartido por una docena de pestañas y no hay forma de buscar. AltUI ordena cada prenda del juego y de todos los mods instalados en **una lista por ranura** (tops, faldas, zapatos, …), con búsqueda, filtros, favoritos y ocultación – y mete peinado, maquillaje, cuerpo y conjuntos en el mismo panel. Se abre en cualquier punto de un nivel con **B**; no hace falta ir al vestuario ni al espejo.

También disponible en el [Workshop de Steam](https://steamcommunity.com/sharedfiles/filedetails/?id=3802875867). El mismo mod, los mismos archivos – elige una fuente, no las dos.

> ⚠ **Hecho para la versión 0.6.x del juego.** Una actualización del juego que cambie las tablas de ropa / maquillaje o el gestor de cámara puede romper el mod.

## Instalación

El archivo contiene dos paks que van en dos carpetas distintas (rutas relativas a la instalación del juego, p. ej. *Steam\steamapps\common\TheKillingAntidote\*):

1. **AltUI.pak** → *TheKillingAntidote\Mods\*
2. **AltUI_Hook_P.pak** → *TheKillingAntidote\Content\Paks\~mods\* – crea la carpeta **~mods** si no existe (el nombre empieza por una tilde ~). El nombre de la carpeta del juego aparece dos veces en la ruta – es correcto.
3. Inicia el juego y pulsa B en un nivel.

Los dos archivos son necesarios. El hook tiene que sobrescribir uno de los blueprints del propio juego (el gestor de cámara del jugador), y eso solo funciona desde *~mods*; sin él, **B no hace nada**. El hook entra en conflicto con cualquier otro mod que sustituya *TKA_PlayerCameraManager* (no se conoce ninguno).

**«B no hace nada»** → falta el archivo hook o está en la carpeta equivocada. Tiene que estar en *Content\Paks\~mods*, no en *Mods*.

Para desinstalar: borra los dos archivos. Los guardados propios del mod (*Saved\SaveGames\AltUI.sav*, *AltUI_Looks.sav* y las fotos de looks en *Saved\SaveGames\AltUI\*) también se pueden borrar; no se toca nada más – ropa, conjuntos, maquillaje y peinado se escriben a través de los guardados del propio juego.

## Qué hace

* **Vestimenta** – cada prenda que conocen el juego y tus mods, agrupada por ranura, subpestañas por mod (plegables), búsqueda, filtros «solo poseídos» / «solo favoritos» / «solo vanilla», favoritos, color con la paleta del juego, restablecer color, meter en la mochila y sacar, ocultar prendas.
* **Conjuntos** – los conjuntos predefinidos del juego, con nombre (clic derecho → renombrar).
* **Looks** – un look completo (ropa con colores, peinado y su color, maquillaje, ojos, piel, deslizadores del cuerpo, mod de cuerpo) guardado con una foto de cuerpo entero hecha en el juego. Aplicar, actualizar, renombrar, borrar.
* **Mochila** – lo que Jodi lleva puesto y encima: ponerse, quitarse, reparar, devolver al vestuario, ordenar.
* **Peinado** – todos los peinados, color de pelo, valores de fábrica.
* **Apariencia** – piel, todos los tipos de maquillaje, ojos, apariencias predefinidas con iconos.
* **Curvas** – deslizadores de pecho / cintura y un selector de los mods de cuerpo instalados.
* **Opciones** – tecla del panel, idioma, velocidad de desplazamiento, tamaño de las casillas, longitud de los nombres de grupo y altura de la fila de grupos, parte de la pantalla reservada para Jodi, FOV / distancia / seguimiento de la cámara, esquema de colores y opacidad, «se puede quitar la ropa interior».
* Deshacer / rehacer (5 pasos), descripciones emergentes que indican de qué mod viene cada prenda.

Idiomas: inglés, alemán, chino, ruso, español (detección automática, cambiable en Opciones).

## Controles

* **B** – abrir / cerrar (cambiable en Opciones). **Esc** cierra.
* Clic izquierdo – seleccionar / ponerse / aplicar. Clic derecho – menú contextual. Rueda del ratón – desplazar.
* Mientras el panel está abierto Jodi no puede andar; arrastra sobre el fondo para girar la cámara, +/− cambia la distancia.

## Mods de cuerpo

Todos los paks que sustituyen el cuerpo sobrescriben el mismo archivo del juego, así que solo puede haber uno activo. **bodypak.pyz** (en el archivo; Python 3.8+, sin paquetes) transforma un sustituto en un pak de mod normal que guarda la malla en su propia ruta; se pueden instalar tantos cuerpos convertidos como quieras, uno junto a otro, y aparecen como chips en la pestaña Curvas.

```
python bodypak.pyz SomeBodyReplacer.pak --name Body_Some --title SomeBody
```

Copia el *Body_Some.pak* resultante en *TheKillingAntidote\Mods\* y quita el sustituto original (o déjalo en *~mods* – entonces se convierte en el chip «Estándar»).

## Compatibilidad

Hecho para la versión 0.6.x del juego. Funciona con mods de ropa, peinados, maquillaje y mapas de Nexus y del Workshop – simplemente aparecen en las listas.

## Actualizaciones

Una versión nueva es un archivo nuevo con los dos ficheros; cópialos encima de los antiguos. El archivo hook cambia rara vez – solo lanza el panel y mueve la cámara, todo lo demás está en AltUI.pak. Cada entrada del registro de cambios indica si el hook ha cambiado; si dice «unchanged», puedes conservar el que tienes. Solo hace falta un hook nuevo cuando lo dice el registro de cambios o cuando una actualización del juego sustituye el gestor de cámara del jugador.

No se incluye ningún recurso del juego; todo lo que hay en el pak está generado.

## Código fuente e incidencias

[github.com/Zyiakk/AltUI](https://github.com/Zyiakk/AltUI) – código fuente (MIT), todas las descargas, informes de errores.
