# AltUI – panel de vestuario y apariencia

Versión en español de la descripción de la [página de AltUI en Nexus Mods](https://www.nexusmods.com/thekillingantidote/mods/988). El original en inglés de la página de Nexus es el que manda.

El vestuario del juego da a cada autor de mods su propia pestaña, así que con unos cuantos mods de ropa instalados el mismo tipo de prenda queda repartido por una docena de pestañas y no hay forma de buscar. AltUI ordena cada prenda del juego y de todos los mods instalados en **una lista por ranura** (tops, faldas, zapatos, …), con búsqueda, filtros, favoritos y ocultación – y mete peinado, maquillaje, cuerpo y conjuntos en el mismo panel. Se abre en cualquier punto de un nivel con **B**; no hace falta ir al vestuario ni al espejo.

También disponible en el [Workshop de Steam](https://steamcommunity.com/sharedfiles/filedetails/?id=3802875867). El mismo mod, los mismos archivos – elige una fuente, no las dos.

> ⚠ **Hecho para la versión 0.6.x del juego.** Una actualización del juego que cambie las tablas de ropa / maquillaje o el gestor de cámara puede romper el mod.

## Instalación

**AltUI.pak** es el mod entero, y hace falta un archivo más que lo ponga en marcha. Hay dos formas – elige una, y las dos juntas también funcionan. Las rutas son relativas a la instalación del juego, p. ej. *Steam\steamapps\common\TheKillingAntidote\*; el nombre de la carpeta del juego aparece dos veces en ellas, es correcto.

**1. Con el Blueprint Loader (AltUI no sustituye nada del juego)**

1. Descarga **TKA_BlueprintLoader.pak** de [Blueprint Loader](https://www.nexusmods.com/thekillingantidote/mods/994) y ponlo en *TheKillingAntidote\Content\Paks\~mods\* – crea la carpeta **~mods** si no existe (el nombre empieza por una tilde ~).
2. **AltUI.pak** del archivo de aquí → *TheKillingAntidote\Mods\*
3. Inicia el juego y pulsa B en un nivel.

AltUI.pak incluye una tabla que el cargador lee, y a partir de ella el cargador lanza el panel. Ese mismo cargador lanza cualquier otro mod que traiga una tabla así, por eso es la vía recomendable si usas más de uno.

**Si vienes de una versión anterior de AltUI: si aún hay un AltUI_Hook_P.pak en ~mods, bórralo. El hook se queda con la clase del gestor de cámara, y uno anterior a 1.5.0 no lanza el cargador: el panel se abriría sin que la vista se aparte y los mods hechos para el cargador no arrancarían.**

**2. Con el pak hook (sin instalar un segundo mod)**

1. **AltUI.pak** → *TheKillingAntidote\Mods\*
2. **AltUI_Hook_P.pak** → *TheKillingAntidote\Content\Paks\~mods\* – la misma regla de carpeta que arriba.
3. Inicia el juego y pulsa B en un nivel.

El hook sustituye uno de los blueprints del propio juego (el gestor de cámara del jugador) y lanza el panel desde ahí; eso solo funciona desde *~mods*. Cualquier mod que sustituya ese mismo blueprint entra en conflicto con él – el Blueprint Loader es uno de ellos, y justo esa pareja es la excepción: con los dos instalados el hook se queda con la clase y lanza el cargador él mismo, así que los mods que necesitan el cargador siguen funcionando.

**«B no hace nada»** → nada ha lanzado el panel: o falta el segundo archivo, o está en *Mods* en lugar de *Content\Paks\~mods*.

El encuadre de cámara junto al panel abierto ya no depende del hook – se engancha al gestor de cámara que tenga el nivel, incluido el del propio juego.

Para desinstalar: borra los archivos que copiaste. Los guardados propios del mod (*Saved\SaveGames\AltUI.sav*, *AltUI_Looks.sav*, *AltUI_Names.sav*, las fotos de looks en *Saved\SaveGames\AltUI\* y las imágenes de armas en *Saved\SaveGames\WeaponIcons\*) también se pueden borrar; no se toca nada más – ropa, conjuntos, maquillaje y peinado se escriben a través de los guardados del propio juego.

## Qué hace

* **Vestimenta** – cada prenda que conocen el juego y tus mods, agrupada por ranura, subpestañas por mod (plegables), búsqueda, filtros «solo poseídos» / «solo favoritos» / «solo vanilla», favoritos, color con la paleta del juego, restablecer color, meter en la mochila y sacar, ocultar prendas.
* **Conjuntos** – los conjuntos predefinidos del juego, con nombre (clic derecho → renombrar).
* **Looks** – un look completo (ropa con colores, peinado y su color, maquillaje, ojos, piel, deslizadores del cuerpo, mod de cuerpo) guardado con una foto de cuerpo entero hecha en el juego. Aplicar, actualizar, renombrar, borrar.
* **Mochila** – lo que Jodi lleva puesto y encima: ponerse, quitarse, reparar, devolver al vestuario, ordenar.
* **Peinado** – todos los peinados, color de pelo, 14 colores de pelo naturales, valores de fábrica.
* **Apariencia** – piel, todos los tipos de maquillaje, ojos, apariencias predefinidas con iconos.
* **Curvas** – deslizadores de pecho / cintura, un selector de los mods de cuerpo instalados y – para cuerpos convertidos – deslizadores de escala de huesos: escala, busto, cintura extra, glúteos/caderas, muslos, pantorrillas, brazos, manos, pies, guardados por cuerpo.
* **Armas** – un modelo y un skin por arma, juntos de todos los mods de armas, con una imagen renderizada en cada casilla.
* **Poses** – todas las animaciones de acción del juego y de los mods de poses, ordenadas en de pie, sentada y tumbada.
* **Opciones** – tecla del panel, idioma, velocidad de desplazamiento, tamaño de las casillas, longitud de los nombres de grupo y altura de la fila de grupos, parte de la pantalla reservada para Jodi, FOV / distancia / seguimiento de la cámara, esquema de colores y opacidad, «se puede quitar la ropa interior», «objetos no poseídos» bloqueado / atenuado / como poseído, liberar los conflictos de ranura del juego (sujetador y camisa …), fusionar grupos / mods con el mismo nombre, opciones de tooltips.
* **Gestión** – tus propios nombres para mods, grupos, prendas, peinados, piel y maquillaje – en todo el panel y en la búsqueda; «Renombrar…» en el menú contextual de cada casilla; exportables / importables como JSON con `altui_names.pyz`.
* Deshacer / rehacer (5 pasos), descripciones emergentes que indican de qué mod viene cada prenda.

Idiomas: inglés, alemán, chino, ruso, español, polaco (detección automática, cambiable en Opciones).

## Controles

* **B** – abrir / cerrar (cambiable en Opciones). **Esc** cierra.
* Clic izquierdo – seleccionar / ponerse / aplicar. Clic derecho – menú contextual. Rueda del ratón – desplazar.
* Mientras el panel está abierto Jodi no puede andar; arrastra sobre el fondo para girar la cámara, +/− acerca / aleja la cámara. Los dos botones redondos de encima abren una cámara libre (el ratón gira, W A S D / Q E mueven, Shift más rápido, rueda = velocidad, hasta 6 m de Jodi, se detiene en las paredes; Esc vuelve) y el modo foto del juego (Esc vuelve).

## Mods de cuerpo

Todos los paks que sustituyen el cuerpo sobrescriben el mismo archivo del juego, así que solo puede haber uno activo. **bodypak.pyz** (en el archivo; Python 3.8+, sin paquetes) transforma un sustituto en un pak de mod normal que guarda la malla en su propia ruta; se pueden instalar tantos cuerpos convertidos como quieras, uno junto a otro, y aparecen como chips en la pestaña Curvas.

```
python bodypak.pyz SomeBodyReplacer.pak --name Body_Some --title SomeBody
```

Copia el *Body_Some.pak* resultante en *TheKillingAntidote\Mods\* y quita el sustituto original (o déjalo en *~mods* – entonces se convierte en el chip «Estándar»).

Guía paso a paso con un ejemplo para Windows y otro para Linux (en inglés): [BODY_MODS.md](https://github.com/Zyiakk/AltUI/blob/main/BODY_MODS.md)

## Mods de armas

Los mods de armas sustituyen los mismos archivos del juego para cada arma, así que dos para la misma arma se excluyen y en el juego no hay forma de cambiar entre ellos. **weaponpak.pyz** (en el archivo; Python 3.8+, sin paquetes) transforma un sustituto así en su propio pak de mod; se pueden instalar tantos como quieras, uno junto a otro, y el modelo y el skin de cada arma se eligen en la pestaña Armas y se recuerdan.

```
python weaponpak.pyz SomeWeaponReplacer.pak --name SomeGun --title "Some gun"
```

*--name* pasa a formar parte del nombre del archivo (letras, cifras y _), *--title* es el texto del chip, y *--weapon* solo hace falta cuando el nombre de la carpeta del mod no dice para qué arma es. Un pak puede traer un skin, un modelo o ambos. Copia el *WeaponAltUI_SomeGun.pak* resultante en *TheKillingAntidote\Mods\* y quita el sustituto original; si no, sigue sobrescribiendo el arma, elijas lo que elijas en el panel.

Guía paso a paso con un ejemplo para Windows y otro para Linux (en inglés): [WEAPON_MODS.md](https://github.com/Zyiakk/AltUI/blob/main/WEAPON_MODS.md)

## Ajustes de otros mods

Los mods que se manejan dentro del juego – una lámpara, por ejemplo – pueden poner sus ajustes en AltUI en lugar de ocupar teclas propias. Una pestaña **Mods** los muestra entonces con interruptores, deslizadores, números, opciones, colores, campos de texto y botones al estilo de AltUI. La pestaña solo aparece cuando hay un mod así instalado.

Para autores de mods (en inglés): [MOD_UI.md](https://github.com/Zyiakk/AltUI/blob/main/MOD_UI.md) describe las dos tablas de datos y la interfaz que necesita un mod; un mod de ejemplo terminado, para instalar y reconstruir, está en [examples/AltUIMod_Example](https://github.com/Zyiakk/AltUI/tree/main/examples/AltUIMod_Example).

## Compatibilidad

Hecho para la versión 0.6.x del juego. Funciona con mods de ropa, peinados, maquillaje y mapas de Nexus y del Workshop – simplemente aparecen en las listas.

## Actualizaciones

Una versión nueva es un archivo nuevo; copia AltUI.pak encima del antiguo. El Blueprint Loader en sí no necesita nada – es un mod aparte y se actualiza en su propia página. Pero un AltUI_Hook_P.pak antiguo no puede quedarse en ~mods. Es el archivo que se queda con la clase del gestor de cámara, y uno anterior a 1.5.0 no lanza el cargador – entonces el panel se abre sin que la vista se aparte, y los mods hechos para el cargador no arrancan. Bórralo o sustitúyelo por el actual. Con el pak hook: cambia rara vez, porque solo lanza el panel y todo lo demás está en AltUI.pak. Cada entrada del registro de cambios indica si el hook ha cambiado; si dice «unchanged», puedes conservar el que tienes. Solo hace falta un hook nuevo cuando lo dice el registro de cambios o cuando una actualización del juego sustituye el gestor de cámara del jugador.

No se incluye ningún recurso del juego; todo lo que hay en el pak está generado.

## Qué hace cada combinación

AltUI.pak es el mod; hace falta un segundo archivo que lo arranque. El resultado:

* **Sólo AltUI.pak** – nada arranca el panel: B no hace nada.
* **AltUI.pak + Blueprint Loader** – el cargador lee la tabla de AltUI y abre el panel. AltUI en sí no reemplaza nada del juego; el cargador sí reemplaza la clase del gestor de cámara, que es como funciona.
* **AltUI.pak + AltUI_Hook_P.pak** – el hook reemplaza el gestor de cámara del juego y abre el panel.
* **AltUI.pak + ambos** – funciona y no se pierde nada. Ambos reemplazan la misma clase del juego, así que sólo uno de los dos paks la gana, y sea cual sea, AltUI arranca: por la tabla del cargador o por el hook, que además arranca el cargador para que los mods hechos para él sigan funcionando.
* **El hook o el cargador sin AltUI.pak** – nada: falta el mod en sí.

## Lo que no puede hacer

Tres límites que conviene conocer:

* **El maquillaje se tiñe, no se recolorea.** El color se multiplica sobre el dibujo existente: uno pálido o neutro lo toma casi por completo, uno oscuro sólo puede oscurecerse o desplazarse. El blanco significa «sin cambios», no maquillaje blanco.
* **Los colores se ven en el juego, no en el menú principal.** AltUI los aplica a Jodi mientras estás en un nivel, que es donde se ejecuta. El menú principal la muestra con los colores de fábrica del juego.
* **Un cuerpo convertido puede asomar bajo la ropa ajustada.** El juego aplana esas zonas con morph targets que viven en la malla del cuerpo; si la malla no trae ninguno, no hay nada con qué aplanar. Es cosa del cuerpo, no de la conversión: el conversor conserva los que tenga el original, y si el original no tiene, nadie puede añadirlos.

## Código fuente e incidencias

[github.com/Zyiakk/AltUI](https://github.com/Zyiakk/AltUI) – código fuente (MIT), todas las descargas, informes de errores.
