# AltUI – panel de vestuario y apariencia

Versión en español de la descripción de la [página del Workshop de Steam](https://steamcommunity.com/sharedfiles/filedetails/?id=3802875867). El original en inglés de la página del Workshop es el que manda.

El vestuario del juego da a cada autor de mods su propia pestaña, así que con unos cuantos mods de ropa instalados el mismo tipo de prenda queda repartido por una docena de pestañas y no hay forma de buscar. AltUI ordena cada prenda del juego y de todos los mods instalados en **una lista por ranura** (tops, faldas, zapatos, …), con búsqueda, filtros, favoritos y ocultación – y mete peinado, maquillaje, cuerpo y conjuntos en el mismo panel. Se abre en cualquier punto de un nivel con **B**; no hace falta ir al vestuario ni al espejo.

También en [Nexus Mods](https://www.nexusmods.com/thekillingantidote/mods/988) (los dos archivos en un solo paquete). El mismo mod – elige una fuente, no las dos.

> ⚠️ **Aviso:** hecho para la versión 0.6.x del juego. Una actualización del juego que cambie las tablas de ropa / maquillaje o el gestor de cámara puede romper el mod. Steam solo actualiza automáticamente el pak del Workshop; el segundo archivo en `~mods` lo gestionas tú – véase «Actualizaciones del mod y el segundo archivo», más abajo.

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

El encuadre de cámara junto al panel abierto ya no depende del hook – se engancha al gestor de cámara que tenga el nivel, incluido el del propio juego.

Para desinstalar: cancela la suscripción y borra el archivo que copiaste. Los guardados propios del mod (*Saved\SaveGames\AltUI.sav*, *AltUI_Looks.sav*, *AltUI_Names.sav*, las fotos de looks en *Saved\SaveGames\AltUI\* y las imágenes de armas en *Saved\SaveGames\WeaponIcons\*) también se pueden borrar; no se toca nada más – ropa, conjuntos, maquillaje y peinado se escriben a través de los guardados del propio juego.

## Qué hace

* **Vestimenta** – cada prenda que conocen el juego y tus mods, agrupada por ranura, subpestañas por mod (plegables), búsqueda, filtros «solo poseídos» / «solo favoritos» / «solo vanilla», favoritos, color con la paleta del juego, restablecer color, meter en la mochila y sacar, ocultar prendas.
* **Conjuntos** – los conjuntos predefinidos del juego, con nombre (clic derecho → renombrar).
* **Looks** – un look completo (ropa con colores, peinado y su color, maquillaje, ojos, piel, deslizadores del cuerpo, mod de cuerpo) guardado con una foto de cuerpo entero hecha en el juego. Aplicar, actualizar, renombrar, borrar.
* **Mochila** – lo que Jodi lleva puesto y encima: ponerse, quitarse, reparar, devolver al vestuario, ordenar.
* **Peinado** – todos los peinados, color de pelo, 14 colores de pelo naturales, valores de fábrica.
* **Apariencia** – piel, todos los tipos de maquillaje, ojos, apariencias predefinidas con iconos.
* **Curvas** – deslizadores de pecho / cintura, un selector de los mods de cuerpo instalados y – para cuerpos convertidos – deslizadores de escala de huesos: escala, busto, cintura extra, glúteos/caderas, muslos, pantorrillas, brazos, manos, pies, guardados por cuerpo.
* **Opciones** – tecla del panel, idioma, velocidad de desplazamiento, tamaño de las casillas, longitud de los nombres de grupo y altura de la fila de grupos, parte de la pantalla reservada para Jodi, FOV / distancia / seguimiento de la cámara, esquema de colores y opacidad, «se puede quitar la ropa interior», «objetos no poseídos» bloqueado / atenuado / como poseído, liberar los conflictos de ranura del juego (sujetador y camisa …), fusionar grupos / mods con el mismo nombre, opciones de tooltips.
* **Gestión** – tus propios nombres para mods, grupos, prendas, peinados, piel y maquillaje – en todo el panel y en la búsqueda; «Renombrar…» en el menú contextual de cada casilla; exportables / importables como JSON con `altui_names.pyz`.
* Deshacer / rehacer (5 pasos), descripciones emergentes que indican de qué mod viene cada prenda.

Idiomas: inglés, alemán, chino, ruso, español, polaco (detección automática, cambiable en Opciones).

## Controles

* **B** – abrir / cerrar (cambiable en Opciones). **Esc** cierra.
* Clic izquierdo – seleccionar / ponerse / aplicar. Clic derecho – menú contextual. Rueda del ratón – desplazar.
* Mientras el panel está abierto Jodi no puede andar; arrastra sobre el fondo para girar la cámara, +/− acerca / aleja la cámara. Los dos botones redondos de encima abren una cámara libre (el ratón gira, W A S D / Q E mueven, Shift más rápido, rueda = velocidad, hasta 6 m de Jodi, se detiene en las paredes; Esc vuelve) y el modo foto del juego (Esc vuelve).

## Mods de cuerpo

Todos los paks que sustituyen el cuerpo sobrescriben el mismo archivo del juego, así que solo puede haber uno activo. Un pequeño conversor transforma un sustituto en un pak de mod normal que guarda la malla en su propia ruta; se pueden instalar tantos cuerpos convertidos como quieras, uno junto a otro, y aparecen como chips en la pestaña Curvas.

Conversor (Python 3.8+, sin paquetes): https://github.com/Zyiakk/AltUI/releases/latest/download/bodypak.pyz

```
python bodypak.pyz SomeBodyReplacer.pak --name Body_Some --title SomeBody
```

Copia el *Body_Some.pak* resultante en *TheKillingAntidote\Mods\* y quita el sustituto original (o déjalo en *~mods* – entonces se convierte en el chip «Estándar»).

Guía paso a paso con un ejemplo para Windows y otro para Linux (en inglés): [BODY_MODS.md](https://github.com/Zyiakk/AltUI/blob/main/BODY_MODS.md)

## Compatibilidad

Hecho para la versión 0.6.x del juego. Funciona con mods de ropa, peinados, maquillaje y mapas del Workshop y de Nexus – simplemente aparecen en las listas. Una actualización del juego que cambie las tablas de ropa / maquillaje o el gestor de cámara puede romper el mod.

## Actualizaciones del mod y el segundo archivo

Lo que lanza el panel está separado a propósito del panel en sí: todo lo que hace el mod vive en el pak del Workshop. Así que cuando este elemento se actualiza por Steam, **el archivo que pusiste en *~mods* normalmente sigue funcionando – no hace falta tocarlo**.

El Blueprint Loader en sí no necesita nada: es un mod aparte y se actualiza en su propia página. Pero un AltUI_Hook_P.pak antiguo no puede quedarse en ~mods. Es el archivo que se queda con la clase del gestor de cámara, y uno anterior a 1.5.0 no lanza el cargador – entonces el panel se abre sin que la vista se aparte, y los mods hechos para el cargador no arrancan. Bórralo o sustitúyelo por el actual.

Con el pak hook solo necesitas un **AltUI_Hook_P.pak** nuevo cuando

* lo dice el registro de cambios – eso ocurre cuando cambia la propia lógica de arranque, o
* una actualización del juego sustituye el gestor de cámara del jugador; entonces hay que reconstruir el hook para la nueva versión del juego (y el antiguo puede estropear la cámara hasta que lo borres o lo sustituyas).

Si el hook se queda anticuado: descarga el archivo actual desde el enlace de GitHub de arriba, sustituye el que está en *Content\Paks\~mods* y listo. Si lo que quieres es quitar el mod: cancela la suscripción y borra ese archivo.

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

https://github.com/Zyiakk/AltUI – código fuente (MIT), todas las descargas, informes de errores.
