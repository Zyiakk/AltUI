# AltUI – panel de vestuario y apariencia

Versión en español de la descripción de la [página del Workshop de Steam](https://steamcommunity.com/sharedfiles/filedetails/?id=3802875867). El original en inglés de la página del Workshop es el que manda.

El vestuario del juego da a cada autor de mods su propia pestaña, así que con unos cuantos mods de ropa instalados el mismo tipo de prenda queda repartido por una docena de pestañas y no hay forma de buscar. AltUI ordena cada prenda del juego y de todos los mods instalados en **una lista por ranura** (tops, faldas, zapatos, …), con búsqueda, filtros, favoritos y ocultación – y mete peinado, maquillaje, cuerpo y conjuntos en el mismo panel. Se abre en cualquier punto de un nivel con **B**; no hace falta ir al vestuario ni al espejo.

También en [Nexus Mods](https://www.nexusmods.com/thekillingantidote/mods/988) (los dos archivos en un solo paquete). El mismo mod – elige una fuente, no las dos.

> ⚠️ **Aviso:** hecho para la versión 0.6.x del juego. Una actualización del juego que cambie las tablas de ropa / maquillaje o el gestor de cámara puede romper el mod.

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

* **Ropa** – cada prenda del juego y de tus mods, una lista por ranura, con búsqueda, filtros, favoritos y ocultación.
* **Conjuntos · Looks** – los ajustes del juego con nombres, y looks completos (ropa con colores, pelo, maquillaje, ojos, piel, cuerpo) guardados con una foto del juego.
* **Mochila · Peinados · Aspecto** – lo que Jodi lleva puesto y encima; peinados y colores de pelo; piel, maquillaje y ojos, todos coloreables.
* **Figura** – deslizadores de pecho y cintura, selector de cuerpos convertidos y deslizadores de huesos por cuerpo.
* **Armas** – un modelo y un skin por arma, juntos de todos los mods de armas, con una imagen renderizada en cada casilla.
* **Poses** – todas las animaciones de acción del juego y de los mods de poses, ordenadas en de pie, sentada y tumbada.
* **Opciones · Gestión** – tecla, idioma, colores, tamaño de casilla; tus propios nombres para mods, grupos y prendas.
* Deshacer / rehacer (5 pasos), descripciones emergentes que indican de qué mod viene cada prenda.

Idiomas: inglés, alemán, chino, ruso, español y polaco (detección automática, cambiable en Opciones).

## Controles

* **B** – abrir / cerrar (cambiable en Opciones). **Esc** cierra.
* Clic izquierdo – seleccionar / ponerse / aplicar. Clic derecho – menú contextual. Rueda del ratón – desplazar.

## Mods de cuerpo

Todos los paks que sustituyen el cuerpo sobrescriben el mismo archivo del juego, así que solo puede haber uno activo. Un pequeño conversor transforma un sustituto en un pak de mod normal que guarda la malla en su propia ruta; se pueden instalar tantos cuerpos convertidos como quieras, uno junto a otro, y aparecen como chips en la pestaña Curvas.

Conversor (Python 3.8+, sin paquetes): https://github.com/Zyiakk/AltUI/releases/latest/download/bodypak.pyz

Guía paso a paso con un ejemplo para Windows y otro para Linux (en inglés): [BODY_MODS.md](https://github.com/Zyiakk/AltUI/blob/main/BODY_MODS.md)

## Actualizaciones del mod y el segundo archivo

Lo que lanza el panel está separado a propósito del panel en sí: todo lo que hace el mod vive en el pak del Workshop. Así que cuando este elemento se actualiza por Steam, **el archivo que pusiste en *~mods* normalmente sigue funcionando – no hace falta tocarlo**.

El Blueprint Loader en sí no necesita nada: es un mod aparte y se actualiza en su propia página. Pero un AltUI_Hook_P.pak antiguo no puede quedarse en ~mods. Es el archivo que se queda con la clase del gestor de cámara, y uno anterior a 1.5.0 no lanza el cargador – entonces el panel se abre sin que la vista se aparte, y los mods hechos para el cargador no arrancan. Bórralo o sustitúyelo por el actual.

No se incluye ningún recurso del juego; todo lo que hay en el pak está generado.

## Qué hace cada combinación

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
