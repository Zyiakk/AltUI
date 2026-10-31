# AltUI – panel de vestuario y apariencia

Versión en español de la descripción de la [página del Workshop de Steam](https://steamcommunity.com/sharedfiles/filedetails/?id=3802875867). La que manda es la [versión en inglés](description.en.md); la página del Workshop muestra una versión corta.

El vestuario del juego da a cada autor de mods su propia pestaña, así que con unos cuantos mods de ropa instalados el mismo tipo de prenda queda repartido por una docena de pestañas y no hay forma de buscar. AltUI ordena cada prenda del juego y de todos los mods instalados en **una lista por ranura** (tops, faldas, zapatos, …), con búsqueda, filtros, favoritos y ocultación – y mete peinado, maquillaje, cuerpo y conjuntos en el mismo panel. Se abre en cualquier punto de un nivel con **B**; no hace falta ir al vestuario ni al espejo.

También en [Nexus Mods](https://www.nexusmods.com/thekillingantidote/mods/988) (los dos archivos en un solo paquete). El mismo mod – elige una fuente, no las dos.

> ⚠️ **Aviso:** hecho para la versión 0.6.x del juego. Una actualización del juego que cambie las tablas de ropa / maquillaje o el gestor de cámara puede romper el mod. Al arrancar, AltUI comprueba las tablas del juego y, si han cambiado, avisa antes de tocar nada.

## ⚠ Instalación – léelo primero

Suscribirse instala el mod en sí, **AltUI.pak**. Hace falta un segundo archivo que lo ponga en marcha, y el Workshop no puede colocarlo por ti, porque va en una carpeta del juego que el Workshop no toca. Sin él, **B no hace nada**. Hay dos formas – elige una, y las dos juntas también funcionan.

**1. Con el Blueprint Loader (AltUI no sustituye nada del juego)**

1. Suscríbete a este elemento (eso instala **AltUI.pak**).
2. Consigue **TKA_BlueprintLoader.pak**: https://www.nexusmods.com/thekillingantidote/mods/994
3. Cópialo en
   `Steam\steamapps\common\TheKillingAntidote\TheKillingAntidote\Content\Paks\~mods\`
   Crea la carpeta **~mods** si no existe (el nombre empieza por una tilde ~). El nombre de la carpeta del juego aparece dos veces en la ruta – es correcto.
4. Inicia el juego y pulsa B en un nivel.

AltUI incluye una tabla que el cargador lee, y a partir de ella el cargador lanza el panel. Ese mismo cargador lanza cualquier otro mod que traiga una tabla así, por eso es la vía recomendable si usas más de uno.

**Si vienes de una versión anterior de AltUI: si aún hay un AltUI_Hook_P.pak en ~mods, bórralo. El hook se queda con la clase del gestor de cámara, y uno anterior a 1.5.0 no lanza el cargador: el panel se abriría sin que la vista se aparte y los mods hechos para el cargador no arrancarían.**

**2. Con el pak hook (un archivo, de la publicación de AltUI)**

1. Suscríbete a este elemento.
2. Descarga **AltUI_Hook_P.pak**: https://github.com/Zyiakk/AltUI/releases/latest/download/AltUI_Hook_P.pak
3. Cópialo en la misma carpeta *~mods* de arriba.
4. Inicia el juego y pulsa B en un nivel.

El hook sustituye *TKA_PlayerCameraManager* y lanza el panel desde ahí. Cualquier mod que sustituya ese mismo blueprint entra en conflicto con él – el Blueprint Loader es uno de ellos, y justo esa pareja es la excepción: con los dos instalados el hook se queda con la clase y lanza el cargador él mismo, así que los mods que necesitan el cargador siguen funcionando.

**«Me he suscrito pero B no hace nada»** → nada ha lanzado el panel: o falta el segundo archivo, o está en *Mods* o en la carpeta del Workshop en lugar de *Content\Paks\~mods*.

## Qué hace

* **Menú rápido** – mantén **4** (cambiable) y se abre una rueda con lo que más usas: cámara libre, modo foto, un conjunto, look, rostro o preajuste guardado, una pose favorita, una pestaña y acciones de otros mods. Hasta 32 elementos, elegidos y ordenados en la pestaña Acciones; suelta sobre uno para ejecutarlo. Un clic derecho en una casilla, una pestaña o la entrada de un mod la añade a la rueda o la quita. También cámara lenta, detener el tiempo, ocultar a Jodi y órdenes a los seguidores. Cualquier elemento puede tener también una tecla propia (Teclas propias).
* **Ropa** – cada prenda del juego y de tus mods, una lista por ranura, con búsqueda, filtros, favoritos y ocultación. Control de daño en el menú contextual; un color por ranura de material, joyas incluidas, guardado por partida. Cajones: tus propias colecciones de prendas, como pestañas sobre la lista. «Mantener puesto» deja puesta una prenda que te pones tú al cambiar de look o de conjunto.
* **Conjuntos · Looks** – los ajustes del juego con nombres, y looks completos (ropa con colores, pelo, maquillaje, ojos, piel, cuerpo, rostro) guardados con una foto del juego – de frente o desde donde vueles con la cámara libre. Un look puede crearse como seguidor, PNJ, enemigo o ragdoll. «Copia limpia» deja fuera lo que ya no está instalado. Un conjunto guardado en AltUI conserva los colores de cada canal de color.
* **Mochila · Peinados · Aspecto** – lo que Jodi lleva puesto y encima; peinados y colores de pelo; piel, maquillaje y ojos, todos coloreables. Peinados favoritos arriba. Mutación: el aspecto mutado de Jodi de la historia por partes – color de piel, venas brillantes, venas, ojos – o el aspecto de la historia completo. Búsqueda de peinados por nombre, mod o archivo pak.
* **Inventario** – los objetos de Jodi y la Hipercaja de almacenamiento, una lista bajo la otra: un clic mueve un objeto; clic derecho para usar, examinar, tirar o descargar; todo con las funciones propias del juego. Opcional: un catálogo «Todos los objetos». Un deslizador elige cualquier cantidad de una pila; antes de que caigan al suelo muchísimos objetos, un aviso pregunta primero. La Mano invisible del juego está en el catálogo: en la mochila trae a Jodi los objetos cercanos; en Opciones puede tener su propio alcance y recoger más objetos por ronda. «Equipar siempre automáticamente» en un objeto lo devuelve a la mochila tras cada carga de nivel, hasta la cantidad marcada.
* **Figura** – deslizadores de pecho y cintura, selector de cuerpos convertidos y deslizadores de huesos por cuerpo. Para pecho y glúteos: rebote, ángulo y anchura de cadera.
* **Rostro** – la expresión, la mirada y la boca de Jodi como deslizadores; el rostro se mantiene también en poses y al bailar; rostros guardados con foto, sus valores en «Ver contenido». «Ojos cerrados» con cuerpos convertidos.
* **Armas** – un modelo, un skin y un sonido de disparo por arma, incluidas las armas cuerpo a cuerpo, juntos de todos los mods de armas, con una imagen renderizada en cada casilla; un clic en un sonido lo reproduce. Accesorios por ranura (mira, cañón, empuñadura, cargador) desde la mochila o la caja de almacenamiento. Las versiones propias de las pinturas del juego que trae un mod de modelo vienen con él.
* **Poses** – todas las animaciones de acción del juego y de los mods de poses, ordenadas en de pie, sentada y tumbada. «Repetir poses» para las poses que terminan solas.
* **Mods** – los ajustes de otros mods que se registran allí: interruptores, deslizadores, números, opciones, colores, campos de texto, líneas de información, teclas y botones. Los números se pueden escribir. Preajustes por página: los ajustes guardados con una foto, aplicados con un clic, y por cada valor eliges qué aplica un preajuste; al menú rápido o a una tecla propia. Los mods pueden traer preajustes propios; esos se pueden ocultar. Solo visible si hay un mod así instalado.
* **Opciones** – ordenadas en categorías que eliges en una lista a la izquierda: tecla del panel, idioma, colores (los esquemas se pueden guardar con un nombre), barra de pestañas con iconos, texto o ambos, y tamaño de casilla, por separado para conjuntos y looks. Varias prendas pueden compartir una ranura (calcetines largos sobre medias). Las pestañas que no necesites se pueden desactivar. Una cámara libre sin colisión y a cualquier distancia; «Sin avisos» oculta los avisos de AltUI y del juego. Una luz de cámara (botón redondo junto al panel) ilumina lo que ve la cámara, con color y brillo.
* **Tema** – colores con su opacidad, una imagen de fondo tras el panel (rellenar, ajustar, estirar o en mosaico, alineada, con tono, sepia e invertir, opacidad propia) y una imagen para mosaicos y pestañas con esquinas redondeadas; imágenes de AltUI – entre ellas cartulinas blanco roto – o las tuyas; los temas guardados con un nombre lo conservan todo. Si quieres, vistas previas en los chips de imagen.
* **Acciones** – los ajustes del menú rápido, fuera de Opciones: los elementos de la rueda, las teclas propias y cada elemento por grupo, con búsqueda.
* **Gestión** – tus propios nombres para mods, grupos y prendas. Como en Vestimenta, las subpestañas filtran la lista por mod o grupo, y un campo de búsqueda acota las subpestañas. Uso: qué mods se usan y dónde (conjuntos, looks, seguidores, favoritos…) y cuáles no, para ver qué puede quitarse.
* **Ragdolls** – copias de Jodi, zombis y personas como figuras con física: colocarlas, posarlas articulación por articulación, congelarlas o dejarlas caer; se guardan poses por tipo de figura y escenas completas por nivel. Al arrastrar, un clic derecho fija una parte en el aire, como la pistola física; unas esferas en las articulaciones muestran dónde se puede agarrar una figura. Un modo ragdoll las mueve sin el panel. También el mercenario, con el fusil en la mano. Una extremidad bajo una articulación móvil gira arrastrando con el botón derecho. Dedos y ojos: posar las articulaciones de los dedos, dirigir la mirada, abrir y cerrar los párpados, poses de mano por mano. Los ragdolls se pueden hacer atacables para los zombis.
* **Seguidores** – los looks se convierten en seguidores que caminan y luchan con Jodi, o en PNJ que se quedan en su sitio: órdenes, objetos y armas para dar, ropa que se daña como la de los PNJ del juego. Se guardan en un archivo propio, nunca en la partida del juego. Cada figura lleva el maquillaje de su look y tiene voz. «Todos los seguidores: venid aquí» desde el menú rápido. Munición infinita por figura; Jason, de la historia, se une como seguidor con su Glock. Un interruptor «atacable» decide si los zombis van a por una figura. El menú rápido pone a la figura que miras en una de tus poses favoritas. «Restaurar atuendo (sin kit de costura)» vuelve a vestir a una figura con el conjunto de su look, cada prenda como nueva, también las arrancadas.
* **Enemigos** – zombis hostiles de todo tipo creados delante de Jodi: cantidad, distancia y comportamiento (cazar, acechar o pasivo); quitar, matar, todos pasivos / activos, una fila por cada enemigo vivo con sus propios enlaces. Un look también puede crearse como enemigo: lleva el look y caza a Jodi y a sus seguidores con una pistola.
* **Códice** – el manual de AltUI en los siete idiomas, la enciclopedia del juego y las cerraduras de código del nivel actual; cada código queda oculto hasta que lo pulsas.
* **TV** – en la oficina de Jodi, los vídeos del televisor en una lista: un clic reproduce uno, y se puede encender y apagar; tus propios .mp4 en `Videos/TV/` también aparecen.
* **Navegación** – las camas del nivel donde Jodi puede guardar, la más cercana primero: teletransportarse junto a una, y los seguidores vienen con ella. Volar / Aterrizar, con un deslizador de velocidad; también en el menú rápido.
* **Objetos** – modelos del juego, armas y accesorios de mods en el mundo, con imágenes que AltUI toma por sí mismo: deslizar, girar, levantar y escalar, con o sin física; se guardan las posiciones por modelo y escenas completas por nivel.
* **Movimiento** – velocidad propia de Jodi al andar y al correr (50–200 %), en Opciones. Cámara lenta con su propia velocidad. Cómo está de pie Jodi: seis animaciones de reposo más del juego, mods de reposo o una pose como reposo. Mods de andar y correr (convertidos con walkpak.pyz) como chips junto a los estilos de andar y correr incluidos.
* Deshacer / rehacer (5 pasos), descripciones emergentes que indican de qué mod viene cada prenda.

Idiomas: inglés, alemán, chino, ruso, español, polaco y francés (detección automática, cambiable en Opciones).

## Controles

* **B** – abrir / cerrar (cambiable en Opciones). **Esc** cierra.
* **4** – mantener para el menú rápido (cambiable en Opciones); suelta sobre un elemento para ejecutarlo, o en el centro para no hacer nada.
* **B en el menú principal** – un pequeño menú: las escenas del menú, la escena de carga, la siguiente cámara y ocultar el menú del juego.
* Clic izquierdo – seleccionar / ponerse / aplicar. Clic derecho – menú contextual. Rueda del ratón – desplazar.
* **Rueda del ratón al jugar** (panel cerrado) – la cámara más cerca o más lejos; «Altura de la cámara (rueda)» en el menú rápido la sube o la baja en su lugar.

## Mods de cuerpo

Todos los paks que sustituyen el cuerpo sobrescriben el mismo archivo del juego, así que solo puede haber uno activo. Un pequeño conversor transforma un sustituto en un pak de mod normal que guarda la malla en su propia ruta; se pueden instalar tantos cuerpos convertidos como quieras, uno junto a otro, y aparecen como chips en la pestaña Curvas.

Conversor (Python 3.8+, sin paquetes): https://github.com/Zyiakk/AltUI/releases/latest/download/bodypak.pyz

Guía paso a paso con un ejemplo para Windows y otro para Linux (en inglés): [BODY_MODS.md](https://github.com/Zyiakk/AltUI/blob/main/BODY_MODS.md)

## Mods de reposo

Los mods de reposo sustituyen la animación de Jodi de pie, así que solo puede haber uno activo. **idlepak.pyz** (en la versión publicada; Python 3.8+, sin paquetes) convierte un sustituto así en un pak de mod propio: el reposo del juego se mantiene y el mod pasa a ser una opción más en Opciones › Movimiento › De pie. AltUI debe estar instalado: el conversor construye el nuevo pak en parte a partir de AltUI.pak.

```
python idlepak.pyz SomeIdleReplacer.pak --name SomeIdle --title "Some idle"
```

Copia el IdleAltUI_SomeIdle.pak resultante en TheKillingAntidote\Mods\ y quita el sustituto original.

idlepak.pyz: https://github.com/Zyiakk/AltUI/releases/latest/download/idlepak.pyz · Detalles: [README](https://github.com/Zyiakk/AltUI#idle-mods)

## Mods de andar y correr

Los mods de andar sustituyen la animación de Jodi al andar o al correr, así que solo puede haber uno activo. **walkpak.pyz** (en la versión publicada; Python 3.8+, sin paquetes) convierte un sustituto así en un pak de mod propio: el andar del juego se queda, y el mod pasa a ser un chip en Opciones › Movimiento › Estilo al andar (y Estilo al correr, si trae una carrera). Como con idlepak, AltUI tiene que estar instalado.

```
python walkpak.pyz SomeWalkReplacer.pak --name Strut --title "Strut"
```

Copia el WalkAltUI_Strut.pak resultante a TheKillingAntidote\Mods\.

walkpak.pyz: https://github.com/Zyiakk/AltUI/releases/latest/download/walkpak.pyz · Detalles: [README](https://github.com/Zyiakk/AltUI#walk--run-mods)

## Actualizaciones del mod y el segundo archivo

Lo que lanza el panel está separado a propósito del panel en sí: todo lo que hace el mod vive en el pak del Workshop. Así que cuando este elemento se actualiza por Steam, **el archivo que pusiste en *~mods* normalmente sigue funcionando – no hace falta tocarlo**.

El Blueprint Loader en sí no necesita nada: es un mod aparte y se actualiza en su propia página. Un AltUI_Hook_P.pak anterior a 1.5.0 no puede quedarse en ~mods (ver la nota en Instalación): bórralo o sustitúyelo por el actual.

**Con el hook y sin el Blueprint Loader:** Desde la 1.8.0 AltUI también pone tu look en Jodi en el menú principal y en la pantalla de carga. Solo con el hook hace falta el AltUI_Hook_P.pak actual: reemplaza el antiguo para tenerlo; en los niveles el antiguo sigue funcionando. Con el Blueprint Loader, AltUI.pak lo hace por sí mismo.

No se incluye ningún recurso del juego; todo lo que hay en el pak está generado.

## Qué hace cada combinación

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

https://github.com/Zyiakk/AltUI – código fuente (MIT), todas las descargas, informes de errores.
