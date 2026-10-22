# AltUI – panel de vestuario y apariencia

Versión en español de la descripción de la [página de AltUI en Nexus Mods](https://www.nexusmods.com/thekillingantidote/mods/988). El original en inglés de la página de Nexus es el que manda.

El vestuario del juego da a cada autor de mods su propia pestaña, así que con unos cuantos mods de ropa instalados el mismo tipo de prenda queda repartido por una docena de pestañas y no hay forma de buscar. AltUI ordena cada prenda del juego y de todos los mods instalados en **una lista por ranura** (tops, faldas, zapatos, …), con búsqueda, filtros, favoritos y ocultación – y mete peinado, maquillaje, cuerpo y conjuntos en el mismo panel. Se abre en cualquier punto de un nivel con **B**; no hace falta ir al vestuario ni al espejo.

También disponible en el [Workshop de Steam](https://steamcommunity.com/sharedfiles/filedetails/?id=3802875867). El mismo mod, los mismos archivos – elige una fuente, no las dos.

> ⚠ **Hecho para la versión 0.6.x del juego.** Una actualización del juego que cambie las tablas de ropa / maquillaje o el gestor de cámara puede romper el mod. Al arrancar, AltUI comprueba las tablas del juego y, si han cambiado, avisa antes de tocar nada.

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

Para desinstalar: borra los archivos que copiaste. AltUI guarda sus propios datos en la carpeta de partidas del juego, en Windows `%LOCALAPPDATA%\TheKillingAntidote\Saved\SaveGames\`; para quitarlo todo, borra allí también:

* `AltUI.sav` – ajustes y elecciones
* `AltUI_Looks.sav` – looks guardados
* `AltUI_Faces.sav` – rostros guardados
* `AltUI_Names.sav` – tus propios nombres
* `AltUI_Ragdolls.sav` – escenas y poses de ragdolls
* `AltUI_Followers.sav` – seguidores y PNJ
* `AltUI\` – fotos de looks, rostros y apariencias predefinidas
* `WeaponIcons\` – imágenes de armas de las casillas

No se toca nada más – ropa, conjuntos, maquillaje y peinado se escriben a través de los guardados del propio juego. Los colores por ranura de AltUI se guardan en la partida como entradas adicionales que empiezan por AltUI#; el juego las ignora.

## Qué hace

* **Menú rápido** – mantén **4** (cambiable) y se abre una rueda con lo que más usas: cámara libre, modo foto, un conjunto, look, rostro o preajuste guardado, una pose favorita, una pestaña y acciones de otros mods. Hasta 32 elementos, elegidos y ordenados en Opciones; suelta sobre uno para ejecutarlo. Un clic derecho en una casilla, una pestaña o la entrada de un mod la añade a la rueda o la quita. También cámara lenta, detener el tiempo, ocultar a Jodi y órdenes a los seguidores. Cualquier elemento puede tener también una tecla propia (Teclas propias).
* **Vestimenta** – cada prenda que conocen el juego y tus mods, agrupada por ranura, subpestañas por mod (plegables), búsqueda, filtros «solo poseídos» / «solo favoritos» / «solo vanilla», favoritos, color con la paleta del juego, restablecer color, meter en la mochila y sacar, ocultar prendas. Control de daño en el menú contextual; un color por ranura de material, joyas incluidas, guardado por partida. Cajones: tus propias colecciones de prendas, como pestañas sobre la lista.
* **Conjuntos** – los conjuntos predefinidos del juego, con nombre (clic derecho → renombrar). Un conjunto guardado en AltUI conserva los colores de cada canal de color.
* **Looks** – un look completo (ropa con colores, peinado y su color, maquillaje, ojos, piel, deslizadores del cuerpo, mod de cuerpo, rostro) guardado con una foto de cuerpo entero hecha en el juego, de frente o tal como la ves. Aplicar, actualizar, renombrar, borrar. Un look puede crearse como seguidor, PNJ o ragdoll. «Copia limpia» deja fuera lo que ya no está instalado.
* **Mochila** – lo que Jodi lleva puesto y encima: ponerse, quitarse, reparar, devolver al vestuario, ordenar.
* **Inventario** – los objetos de Jodi y la Hipercaja de almacenamiento, una lista bajo la otra: un clic mueve un objeto; clic derecho para usar, examinar, tirar o descargar; todo con las funciones propias del juego. Opcional: un catálogo «Todos los objetos». Un deslizador elige cualquier cantidad de una pila; antes de que caigan al suelo muchísimos objetos, un aviso pregunta primero. La Mano invisible del juego está en el catálogo: en la mochila trae a Jodi los objetos cercanos.
* **Peinado** – todos los peinados, color de pelo, 14 colores de pelo naturales, valores de fábrica. Peinados favoritos arriba. Búsqueda de peinados por nombre, mod o archivo pak.
* **Apariencia** – piel, todos los tipos de maquillaje, ojos, apariencias predefinidas con iconos (guardar, actualizar, renombrar, borrar). Mutación: el aspecto mutado de Jodi de la historia por partes – color de piel, venas brillantes, venas, ojos – o el aspecto de la historia completo.
* **Curvas** – deslizadores de pecho / cintura, un selector de los mods de cuerpo instalados y – para cuerpos convertidos – deslizadores de escala de huesos: escala, busto, cintura extra, glúteos/caderas, muslos, pantorrillas, brazos, manos, pies, guardados por cuerpo. Para pecho y glúteos: rebote, ángulo y anchura de cadera.
* **Rostro** – la expresión facial de Jodi: las expresiones del juego, la dirección de la mirada y las formas de la boca como deslizadores; una entrada marcada mantiene su valor, también en poses y al bailar, una sin marcar queda en manos del juego. Rostros guardados con foto. «Ver contenido» muestra sus valores. «Ojos cerrados» con cuerpos convertidos.
* **Armas** – un modelo, un skin y un sonido de disparo por arma, incluidas las armas cuerpo a cuerpo, juntos de todos los mods de armas, con una imagen renderizada en cada casilla; un clic en un sonido lo reproduce. Accesorios por ranura (mira, cañón, empuñadura, cargador) desde la mochila o la caja de almacenamiento. Las versiones propias de las pinturas del juego que trae un mod de modelo vienen con él.
* **Poses** – todas las animaciones de acción del juego y de los mods de poses, ordenadas en de pie, sentada y tumbada. «Repetir poses» para las poses que terminan solas.
* **Mods** – los ajustes de otros mods que se registran allí (solo visible si hay un mod así instalado).
* **Opciones** – por categorías, con una lista a la izquierda; las pestañas que no necesites se pueden desactivar; tecla del panel, idioma, velocidad de desplazamiento, tamaño de las casillas, longitud de los nombres de grupo y altura de la fila de grupos, parte de la pantalla reservada para Jodi, FOV / distancia / seguimiento de la cámara, esquema de colores y opacidad, «se puede quitar la ropa interior», «objetos no poseídos» bloqueado / atenuado / como poseído, liberar los conflictos de ranura del juego (sujetador y camisa …), varias prendas en una ranura (calcetines largos sobre medias), fusionar grupos / mods con el mismo nombre, opciones de tooltips; la barra de pestañas con iconos, texto o ambos, el icono a la izquierda o a la derecha del texto; esquemas de color guardados con un nombre; tamaño propio de las casillas de conjuntos y looks y cuántas prendas muestra una casilla de conjunto; opacidad del menú rápido. Una cámara libre sin colisión y a cualquier distancia; «Sin avisos» oculta los avisos de AltUI y del juego. Una luz de cámara (botón redondo junto al panel) ilumina lo que ve la cámara, con color y brillo.
* **Tema** – colores con su opacidad, una imagen de fondo tras el panel (rellenar, ajustar, estirar o en mosaico, alineada, con tono, sepia e invertir, opacidad propia) y una imagen para mosaicos y pestañas con esquinas redondeadas; imágenes de AltUI – entre ellas cartulinas blanco roto – o las tuyas; los temas guardados con un nombre lo conservan todo. Si quieres, vistas previas en los chips de imagen.
* **Gestión** – tus propios nombres para mods, grupos, prendas, peinados, piel y maquillaje – en todo el panel y en la búsqueda; «Renombrar…» en el menú contextual de cada casilla; exportables / importables como JSON con `altui_names.pyz`; como en Vestimenta, las subpestañas filtran la lista por mod o grupo y un campo de búsqueda acota las subpestañas; también se pueden renombrar poses y apariencias predefinidas. Uso: qué mods se usan y dónde (conjuntos, looks, seguidores, favoritos…) y cuáles no, para ver qué puede quitarse.
* **Ragdolls** – copias de Jodi, zombis y personas como figuras con física: colocarlas, posarlas articulación por articulación, congelarlas o dejarlas caer; se guardan poses por tipo de figura y escenas completas por nivel. Al arrastrar, un clic derecho fija una parte en el aire, como la pistola física; unas esferas en las articulaciones muestran dónde se puede agarrar una figura. Un modo ragdoll las mueve sin el panel. También el mercenario, con el fusil en la mano. Una extremidad bajo una articulación móvil gira arrastrando con el botón derecho.
* **Seguidores** – los looks se convierten en seguidores que caminan y luchan con Jodi, o en PNJ que se quedan en su sitio: órdenes, objetos y armas para dar, ropa que se daña como la de los PNJ del juego. Se guardan en un archivo propio, nunca en la partida del juego. Cada figura lleva el maquillaje de su look y tiene voz. «Todos los seguidores: venid aquí» desde el menú rápido. Munición infinita por figura; Jason, de la historia, se une como seguidor con su Glock.
* **Códice** – el manual de AltUI en los siete idiomas, la enciclopedia del juego y las cerraduras de código del nivel actual; cada código queda oculto hasta que lo pulsas.
* **TV** – en la oficina de Jodi, los vídeos del televisor en una lista: un clic reproduce uno, y se puede encender y apagar; tus propios .mp4 en `Videos/TV/` también aparecen.
* **Movimiento** – velocidad propia de Jodi al andar y al correr (50–200 %), en Opciones. Cámara lenta con su propia velocidad. Cómo está de pie Jodi: seis animaciones de reposo más del juego, mods de reposo o una pose como reposo.
* Deshacer / rehacer (5 pasos), descripciones emergentes que indican de qué mod viene cada prenda.

Idiomas: inglés, alemán, chino, ruso, español, polaco, francés (detección automática, cambiable en Opciones).

## Controles

* **B** – abrir / cerrar (cambiable en Opciones). **Esc** cierra.
* **4** – mantener para el menú rápido (cambiable en Opciones); suelta sobre un elemento para ejecutarlo, o en el centro para no hacer nada.
* **B en el menú principal** – un pequeño menú: las escenas del menú, la escena de carga, la siguiente cámara y ocultar el menú del juego.
* Clic izquierdo – seleccionar / ponerse / aplicar. Clic derecho – menú contextual. Rueda del ratón – desplazar.
* Mientras el panel está abierto Jodi no puede andar; arrastra sobre el fondo para girar la cámara, +/− acerca / aleja la cámara. Los tres botones redondos de encima abren una cámara libre (el ratón gira, W A S D / Q E mueven, Shift más rápido, rueda = velocidad, hasta 6 m de Jodi, se detiene en las paredes; Esc vuelve), el modo foto del juego (Esc vuelve) y el modo ragdoll (Esc vuelve).

## Mods de cuerpo

Todos los paks que sustituyen el cuerpo sobrescriben el mismo archivo del juego, así que solo puede haber uno activo. **bodypak.pyz** (en el archivo; Python 3.8+, sin paquetes) transforma un sustituto en un pak de mod normal que guarda la malla en su propia ruta; se pueden instalar tantos cuerpos convertidos como quieras, uno junto a otro, y aparecen como chips en la pestaña Curvas.

```
python bodypak.pyz SomeBodyReplacer.pak --name BodyAltUI_Some --title SomeBody
```

Copia el *BodyAltUI_Some.pak* resultante en *TheKillingAntidote\Mods\* y quita el sustituto original (o déjalo en *~mods* – entonces se convierte en el chip «Estándar»).

Guía paso a paso con un ejemplo para Windows y otro para Linux (en inglés): [BODY_MODS.md](https://github.com/Zyiakk/AltUI/blob/main/BODY_MODS.md)

## Mods de armas

Los mods de armas sustituyen los mismos archivos del juego para cada arma, así que dos para la misma arma se excluyen y en el juego no hay forma de cambiar entre ellos. **weaponpak.pyz** (en el archivo; Python 3.8+, sin paquetes) transforma un sustituto así en su propio pak de mod; se pueden instalar tantos como quieras, uno junto a otro, y el modelo y el skin de cada arma se eligen en la pestaña Armas y se recuerdan.

```
python weaponpak.pyz SomeWeaponReplacer.pak --name SomeGun --title "Some gun"
```

*--name* pasa a formar parte del nombre del archivo (letras, cifras y _), *--title* es el texto del chip, y *--weapon* solo hace falta cuando el nombre de la carpeta del mod no dice para qué arma es. Un pak puede traer un skin, un modelo o ambos. Copia el *WeaponAltUI_SomeGun.pak* resultante en *TheKillingAntidote\Mods\* y quita el sustituto original; si no, sigue sobrescribiendo el arma, elijas lo que elijas en el panel.

Guía paso a paso con un ejemplo para Windows y otro para Linux (en inglés): [WEAPON_MODS.md](https://github.com/Zyiakk/AltUI/blob/main/WEAPON_MODS.md)

## Mods de reposo

Los mods de reposo sustituyen la animación de Jodi de pie, así que solo puede haber uno activo. **idlepak.pyz** (en la versión publicada; Python 3.8+, sin paquetes) convierte un sustituto así en un pak de mod propio: el reposo del juego se mantiene y el mod pasa a ser una opción más en Opciones › Movimiento › De pie. AltUI debe estar instalado: el conversor construye el nuevo pak en parte a partir de AltUI.pak.

```
python idlepak.pyz SomeIdleReplacer.pak --name SomeIdle --title "Some idle"
```

Copia el IdleAltUI_SomeIdle.pak resultante en TheKillingAntidote\Mods\ y quita el sustituto original.

idlepak.pyz: https://github.com/Zyiakk/AltUI/releases/latest/download/idlepak.pyz · Detalles: [README](https://github.com/Zyiakk/AltUI#idle-mods)

## Ajustes de otros mods

Los mods que se manejan dentro del juego – una lámpara, por ejemplo – pueden poner sus ajustes en AltUI en lugar de ocupar teclas propias. Una pestaña **Mods** los muestra entonces con interruptores, deslizadores, números, opciones, colores, campos de texto, líneas de información, teclas y botones al estilo de AltUI. La pestaña solo aparece cuando hay un mod así instalado. Sus botones e interruptores también pueden ir al menú rápido, y un mod puede añadir acciones propias con un icono.

Para autores de mods (en inglés): [MOD_UI.md](https://github.com/Zyiakk/AltUI/blob/main/MOD_UI.md) describe las dos tablas de datos y la interfaz que necesita un mod; un mod de ejemplo terminado, para instalar y reconstruir, está en [examples/AltUIMod_Example](https://github.com/Zyiakk/AltUI/tree/main/examples/AltUIMod_Example).

## Compatibilidad

Hecho para la versión 0.6.x del juego. Funciona con mods de ropa, peinados, maquillaje y mapas de Nexus y del Workshop – simplemente aparecen en las listas.

## Actualizaciones

Una versión nueva es un archivo nuevo; copia AltUI.pak encima del antiguo. El Blueprint Loader en sí no necesita nada – es un mod aparte y se actualiza en su propia página. Pero un AltUI_Hook_P.pak antiguo no puede quedarse en ~mods. Es el archivo que se queda con la clase del gestor de cámara, y uno anterior a 1.5.0 no lanza el cargador – entonces el panel se abre sin que la vista se aparte, y los mods hechos para el cargador no arrancan. Bórralo o sustitúyelo por el actual. Con el pak hook: cambia rara vez, porque solo lanza el panel y todo lo demás está en AltUI.pak. Cada entrada del registro de cambios indica si el hook ha cambiado; si dice «unchanged», puedes conservar el que tienes. Solo hace falta un hook nuevo cuando lo dice el registro de cambios o cuando una actualización del juego sustituye el gestor de cámara del jugador.

**Con el hook y sin el Blueprint Loader:** Desde la 1.8.0 AltUI también pone tu look en Jodi en el menú principal y en la pantalla de carga. Solo con el hook hace falta el AltUI_Hook_P.pak actual: reemplaza el antiguo para tenerlo; en los niveles el antiguo sigue funcionando. Con el Blueprint Loader, AltUI.pak lo hace por sí mismo.

No se incluye ningún recurso del juego; todo lo que hay en el pak está generado.

## Qué hace cada combinación

AltUI.pak es el mod; hace falta un segundo archivo que lo arranque. El resultado:

* **Sólo AltUI.pak** – nada arranca el panel: B no hace nada.
* **AltUI.pak + Blueprint Loader** – el cargador lee la tabla de AltUI y abre el panel. AltUI en sí no reemplaza nada del juego; el cargador sí reemplaza la clase del gestor de cámara, que es como funciona.
* **AltUI.pak + AltUI_Hook_P.pak** – el hook reemplaza el gestor de cámara del juego y abre el panel.
* **AltUI.pak + ambos** – funciona y no se pierde nada. Ambos reemplazan la misma clase del juego, así que sólo uno de los dos paks la gana, y sea cual sea, AltUI arranca: por la tabla del cargador o por el hook, que además arranca el cargador para que los mods hechos para él sigan funcionando.
* **El hook o el cargador sin AltUI.pak** – nada: falta el mod en sí.

## Lo que no puede hacer

Dos límites que conviene conocer:

* **El maquillaje se tiñe, no se recolorea.** El color se multiplica sobre el dibujo existente: uno pálido o neutro lo toma casi por completo, uno oscuro sólo puede oscurecerse o desplazarse. El blanco significa «sin cambios», no maquillaje blanco.
* **Un cuerpo convertido puede asomar bajo la ropa ajustada.** El juego aplana esas zonas con morph targets que viven en la malla del cuerpo; si la malla no trae ninguno, no hay nada con qué aplanar. Es cosa del cuerpo, no de la conversión: el conversor conserva los que tenga el original, y si el original no tiene, nadie puede añadirlos.

## Código fuente e incidencias

[github.com/Zyiakk/AltUI](https://github.com/Zyiakk/AltUI) – código fuente (MIT), todas las descargas, informes de errores.
