## Acerca de AltUI {#about}

AltUI es una alternativa al armario y a la pantalla de apariencia de The Killing Antidote: un solo panel para todo, y las pantallas del juego siguen funcionando. Se abre en cualquier lugar de un nivel con B, sin ir al armario ni al espejo.

Cada prenda del juego y de todos los mods instalados está en una lista por ranura, con búsqueda, filtros, favoritos y ocultación. Peinado, maquillaje, cuerpo, rostro, poses, armas y los conjuntos y looks guardados están en el mismo panel, y también los ragdolls – copias de Jodi, zombis y personas para colocar y posar – y la velocidad de Jodi al andar y al correr.

El panel se abre en la pestaña en la que se cerró. Las pestañas que no uses se pueden desactivar en Opciones › Pestañas.

Una pestaña Inventario mueve objetos entre la mochila de Jodi y la hipercaja de almacenamiento, y los looks se convierten en seguidores y PNJ que caminan y luchan con ella.

## Instalación y actualizaciones {#install}

AltUI.pak contiene todo el mod y va en TheKillingAntidote/Mods/. Otro archivo lo pone en marcha:

- el Blueprint Loader (un mod pequeño aparte, TKA_BlueprintLoader.pak en TheKillingAntidote/Content/Paks/~mods/), o
- el gancho propio de AltUI, AltUI_Hook_P.pak en la misma carpeta ~mods/.

Basta con uno de los dos; los dos juntos también funcionan. Solo con AltUI.pak, B no hace nada.

Una actualización normalmente solo sustituye AltUI.pak. El registro de cambios indica cuándo cambia también el gancho; un gancho antiguo no debe quedarse en ~mods/.

Para quitar AltUI, borra los archivos que copiaste:

- TheKillingAntidote/Mods/AltUI.pak
- TheKillingAntidote/Content/Paks/~mods/AltUI_Hook_P.pak – si usas el gancho
- TheKillingAntidote/Content/Paks/~mods/TKA_BlueprintLoader.pak – solo si ningún otro mod lo necesita

AltUI guarda sus propios datos en la carpeta de partidas del juego, en Windows %LOCALAPPDATA%\TheKillingAntidote\Saved\SaveGames. Para quitarlo todo, borra allí también:

- AltUI.sav – ajustes y elecciones
- AltUI_Looks.sav – looks guardados
- AltUI_Faces.sav – rostros guardados
- AltUI_Names.sav – tus propios nombres
- AltUI_Ragdolls.sav – escenas y poses de ragdolls
- AltUI_Followers.sav – seguidores y PNJ
- AltUI_Drawers.sav – cajones de ropa
- la carpeta AltUI – fotos de looks, rostros y presets de apariencia
- la carpeta WeaponIcons – imágenes de armas

La ropa, los conjuntos, el maquillaje y el peinado se guardan en las partidas del propio juego y se conservan.

Tras una actualización del juego, o con un mod que reemplaza tablas del juego, AltUI puede encontrarse con un juego para el que no fue hecho. Entonces muestra un aviso antes de hacer nada: «Seguir de todos modos (bajo mi riesgo)» se recuerda para esta versión del juego, «AltUI desactivado por ahora» vuelve a preguntar en el siguiente nivel.

## Controles {#controls}

- B abre y cierra el panel (otra tecla en Opciones › Controles); Esc lo cierra.
- El clic izquierdo selecciona, viste o aplica; el clic derecho abre el menú contextual de una casilla, una fila o una pestaña.
- La rueda del ratón desplaza; la velocidad se ajusta en Opciones › Controles.
- Mientras el panel está abierto, Jodi no puede caminar. Arrastrar sobre el fondo gira la cámara; hacer clic en Jodi y arrastrar la gira a ella, y al cerrar el panel vuelve a su posición.
- + y − cambian la distancia de la cámara en pasos del 5 %, la rueda sobre Jodi en pasos del 4 %.
- Mientras juegas (panel cerrado), la rueda acerca o aleja la cámara de Jodi; con la entrada del menú rápido «Altura de la cámara (rueda)» la sube o la baja (clic izquierdo o Esc lo termina); al apuntar se mantiene la vista del juego. La distancia y la altura se guardan.
- Los botones redondos sobre + y − abren una cámara libre (el ratón gira, W A S D y Q E mueven, Mayús más rápido, la rueda ajusta la velocidad, Esc vuelve), el modo foto del juego (Esc vuelve) y el modo ragdoll (ver «Modo ragdoll»).
- El botón redondo de arriba (la bombilla) es la luz de cámara: ilumina lo que ve la cámara – junto al panel, en la cámara libre y en el modo foto. Un clic abre un pequeño menú: encender / apagar, el color de la luz (paleta) y un control de brillo. Solo aclara (sin brillos, sin haz en la niebla), está apagada mientras juegas y vuelve como la dejaste cuando se abre el panel.
- Deshacer y Rehacer (cinco pasos) están en la barra de estado de abajo.
- Mantén pulsado 4 para el menú rápido (ver «Menú rápido»).
- En el menú principal, B abre un pequeño menú: las tres escenas del menú y la escena de carga, la cámara siguiente, y ocultar el menú y los textos del juego (Esc los recupera).

## Vestimenta {#clothes}

A la izquierda las ranuras, a la derecha las prendas de la ranura elegida.

- Un clic en una prenda la viste; un clic en una puesta la quita.
- Las fichas sobre la lista filtran por mod o grupo; «...» pliega las filas de fichas. Un campo de búsqueda reduce las fichas, y la búsqueda sobre la lista encuentra prendas por nombre, mod o grupo.
- Filtros: solo poseídos, solo favoritos, solo vanilla, solo puestos.
- Clic derecho en una prenda: favorito, mantener puesto, ocultar, color con la paleta del juego, restablecer color, meter en la mochila, renombrar, solo este grupo, ver contenido del mod, mostrar en la pestaña.
- Mantener puesto: una prenda marcada que te pusiste tú misma se queda puesta al ponerte un look o un conjunto. El look omite entonces las prendas de la misma ranura (o de una ranura incompatible) y las nombra en el aviso. Una prenda que puso un look o un conjunto no se queda en el siguiente cambio, aunque esté marcada; así probar conjuntos nunca acumula prendas. La casilla muestra «se mantiene». Deshacer restablece exactamente el estado anterior.
- Cajones: colecciones propias de ropa, en una barra sobre la lista. «Predeterminado» lo muestra todo; «+» crea un cajón nuevo («Cajón 1», «Cajón 2» …). Un cajón muestra la misma página – ranuras, fichas, búsqueda, filtros, favoritos – solo con sus prendas, y las ranuras cuentan solo esas. Clic derecho en una prenda › «Cajón ›» abre junto al menú la lista de cajones: una marca indica que la prenda está dentro; un clic la mete o la saca, «+ Nuevo cajón» crea uno con la prenda dentro. Una prenda puede estar en cualquier número de cajones; dentro de un cajón el menú tiene además «Quitar de este cajón». Clic derecho en un cajón: renombrar (Intro acepta, Esc cancela), mover a la izquierda / derecha, borrar (pregunta antes; las prendas se quedan). El cajón mostrado se mantiene tras reiniciar.
- La descripción emergente indica de qué mod viene una prenda.
- Daño (en el menú contextual): de 0 a 100 %, al instante en una prenda puesta; en cualquier otra se guarda hasta que se la ponga. Las prendas puestas sin texturas de daño no tienen control.
- Bajo la paleta de colores del juego, un campo muestra el color como #RRGGBB; escribe un código y pulsa Intro para aplicarlo. «Recordar» guarda el color en AltUI, «Usar» lo pone en otra prenda o ranura.
- La búsqueda también encuentra un mod por el nombre de su pak, aquí y en todas las demás pestañas.

## Conjuntos {#outfits}

Los conjuntos guardados del juego: los mismos que usan el armario y el espejo.

- La casilla «+» guarda lo que Jodi lleva puesto como un conjunto nuevo.
- Un clic en un conjunto lo viste.
- Clic derecho: vestir, ver contenido, añadir al menú rápido o quitar de él, renombrar, mover a la izquierda / a la derecha / al principio / al final, borrar.
- Un conjunto sin nombre propio aparece como «Conjunto» con su posición en la lista.
- El tamaño de las casillas y cuántas prendas muestra cada una se ajustan en Opciones › Casillas.
- Un conjunto guardado aquí conserva cada canal de color de sus prendas, tal como AltUI los coloreó; el juego en sí guarda un solo color por prenda. Un conjunto guardado en el espejo tiene solo ese.

## Looks {#looks}

Un look es todo a la vez: ropa con sus colores, peinado y color de pelo, maquillaje, ojos, piel, mutación, controles del cuerpo, mod de cuerpo y rostro.

- La casilla «+» guarda el look actual con una foto de cuerpo entero, de frente, o con la cámara libre: llévala adonde quieras y haz clic para tomar la foto (Esc: foto de frente en su lugar).
- Un clic en un look lo aplica.
- Clic derecho: ver contenido, renombrar, actualizar (foto de frente o con cámara libre), mover, borrar, añadir al menú rápido o quitar de él.
- Clic derecho también: «Crear como ragdoll», «Crear como seguidor», «Crear como PNJ» (ver «Ragdolls» y «Seguidores»).
- Clic derecho «Copia limpia (sin partes que faltan)»: solo aparece si el look contiene prendas de un mod ya no instalado o filas de maquillaje / ojos que ninguna tabla tiene; crea un look nuevo justo detrás sin esas entradas, con la misma foto. El original queda como está; volver a guardar un look nunca las quita por sí solo.

## Mochila {#bag}

Lo que Jodi lleva puesto y lo que lleva consigo.

- Un clic en una prenda puesta la quita; en una que lleva consigo, la viste.
- Clic derecho: vestir o quitar, reparar (necesita un kit de costura), quitar de la mochila, devolver al armario.
- «Ordenar la mochila» quita las prendas que no se llevan puestas y que también están en el armario.
- «Todo a la mochila» quita cada prenda puesta y la mete en la mochila.
- El menú contextual también tiene el control de daño (ver «Vestimenta»).

## Inventario {#inventory}

Los objetos de Jodi y la hipercaja de almacenamiento, una lista bajo la otra.

- Las fichas filtran por los grupos del juego (armas, munición, accesorios de armas, herramientas…). El peso muestra lo que lleva Jodi, lo que puede llevar y cuánto se ha sobrecargado.
- Un clic pone un objeto en la caja o saca uno. Clic derecho: la mitad o todos, usar, examinar, tirar, acceso rápido 1 o 2, descargar munición, «Accesorios…» (abre el arma en la pestaña Armas).
- El menú contextual de una pila termina con «Cantidad»: un control deslizante y un campo numérico, y debajo una entrada por destino con ese número («Guardar 5 en la caja», «Coger 5»). Enter en el campo ejecuta la primera entrada. En el catálogo el número cuenta unidades y el campo admite más de lo que alcanza el control. Las armas de fuego y los objetos sueltos no tienen cantidad.
- «Tirar todo» deja un objeto en el suelo por paquete. A partir de 100 objetos una ventana pregunta primero: «Cancelar», «Destruir en su lugar» (los objetos desaparecen, no cae nada) o «Tirar de todos modos»: tantos objetos con física a la vez pueden hacer que el juego se cierre. Esc cancela.
- Todo pasa por las funciones del propio juego, así que sus reglas se mantienen, sobrecarga incluida.
- «...» sobre una lista la pliega, ↑↓ le da toda la altura (otra vez: vuelve).
- En los mapas donde el juego nunca guarda la mochila (el campo de tiro, por ejemplo) la pestaña lo indica: guarda en la caja lo que quieras conservar.
- «Todos los objetos» está desactivado por defecto (Opciones › General): todos los objetos del juego como tercera lista, con su propia búsqueda. Un clic pone un paquete en la mochila; clic derecho: cinco, o a la caja.
  «Coleccionables» incluye también la Mano invisible del juego: mientras está en la mochila, trae a Jodi los objetos cercanos, uno tras otro, más rápido con más manos (una cada 2,5 s, desde seis cada 0,1 s). «Coleccionables» en la mochila muestra cuántas tiene Jodi.
- «Equipar armas automáticamente» (Opciones › General, activado por defecto): un arma de la caja o del catálogo pasa a la mano de Jodi como en el juego; desactivado, conserva lo que tiene en la mano.
- El tamaño de las casillas de esta pestaña se ajusta en Opciones › Casillas.

## Peinado {#hair}

Todos los peinados del juego y de los mods.

- Un clic en un peinado lo pone.
- El cuadro de búsqueda sobre las fichas encuentra peinados por nombre mostrado, identificador, nombre del mod y archivo pak; × lo vacía.
- «Color de pelo...» abre la paleta del juego; «Colores de pelo naturales» ofrece 14 colores listos.
- Clic derecho: añadir a / quitar de favoritos, restablecer color de pelo, renombrar, ver contenido del mod.
- Los favoritos están arriba, encima de todos los peinados.
- Clic derecho en un peinado de un mod: «Renombrar mod…».

## Poses {#poses}

Cada animación de acción que conocen el juego y tus mods de poses: la lista detrás de la app «ritmo» del teléfono.

- Un clic en una pose la reproduce; otro clic o «Detener pose» la detiene.
- Las poses están ordenadas por postura (de pie, sentada, tumbada) y por capítulo; las fichas filtran por mod y la búsqueda encuentra títulos.
- Clic derecho: favorito, ocultar, marcar como de pie / sentada / tumbada / en movimiento, renombrar, añadir al menú rápido.
- Clic derecho «Usar en reposo»: la pose empieza tras 1,5 s quieta y termina cuando Jodi anda, saca un arma o se agacha; «Ya no en reposo» lo desactiva.
- «Medir todas» reproduce una vez cada pose que aún no tiene postura y la ordena.
- Un altavoz en la esquina de una casilla marca una pose con sonido.
- «Medir todas» muestra el nombre de la pose que se está midiendo.
- «Repetir poses: sí» en la barra de estado vuelve a iniciar una pose que termina sola, hasta que Jodi se mueve, la tecla de usar o «Detener pose» la terminan o se elige otra pose. Muchos mods de poses repiten sus poses de todos modos.

## Armas {#weapons}

A la izquierda, una entrada por arma, incluidas las armas cuerpo a cuerpo. Para cada arma, el modelo, la skin y el sonido del disparo se eligen por separado.

- Arriba los modelos: el del juego y cada mod de modelo instalado.
- Abajo las skins: las pinturas de armas del juego (sin bote de pintura) y cada mod de skin instalado.
- Si un mod de modelo trae sus propias versiones de las pinturas del juego (hechas para su modelo), aparecen como skins adicionales junto a las del juego mientras ese modelo está elegido.
- Las casillas de modelo muestran cada modelo con el skin elegido; la pintura propia de un modelo, solo en ese modelo: en cualquier otro el arma se queda como está, y su casilla también. La casilla de un mod de skin aparece atenuada cuando el skin no hace nada en el modelo elegido; se sabe en cuanto el arma ha estado en la mano de Jodi con ese modelo. «Volver a tomar» en la barra de estado vuelve a tomar las imágenes de todas las casillas del arma.
- Sonido: el sonido de disparo propio del arma («Original») y cada sonido de disparo instalado para ella. Un clic elige el sonido y lo reproduce; las demás armas conservan el suyo. Un silenciador montado con sonido propio sigue teniendo prioridad.
- Las fichas de arriba filtran las tres secciones a la vez. Clic derecho en una casilla: favorito, ocultar, solo este mod.
- La elección se guarda y se vuelve a aplicar cuando se recoge el arma o se saca de la caja de almacenamiento.
- Una pintura aplicada en el juego con un bote de pintura se conserva: pasa a ser la skin elegida.
- Clic derecho en un modelo de mod: forzar skins en él, excluir el cargador, la mira, el silenciador o la empuñadura, mostrar la imagen propia del mod.
- Los mods de armas y de sonidos de disparo deben convertirse antes con weaponpak.pyz; consulta la guía WEAPON_MODS en la página del mod.
- Accesorios de armas: una fila por cada ranura del arma (mira, cañón, empuñadura, cargador), «Ninguno» primero. Las piezas salen de la mochila, o de la caja de almacenamiento y pasan a la mochila. Los accesorios solo van en armas que Jodi lleva; el arma conserva el modelo, la apariencia y el sonido elegidos aquí.
- «Mostrar imágenes de objeto» en la barra de estado pone en cada casilla la imagen propia del objeto o del mod en lugar de la renderizada.
- Clic derecho en un modelo, una apariencia o un sonido de un mod: «Renombrar mod…».

## Apariencia {#look}

Piel, cada tipo de maquillaje, ojos y los presets de apariencia del juego.

- Un clic en una entrada la aplica. Clic derecho en el maquillaje: teñir con la paleta del juego, restablecer el teñido.
- Ojos: color del iris y de las pestañas en el menú contextual.
- Piel: «Piel aceitada» encima de las pieles hace brillar la piel, como la piel mojada del juego (la piel mojada del juego = 50 %). Casilla marcada = tu valor, también frente a la historia; desmarcada = vuelve a decidir el juego. Solo en Jodi. Los looks y los presets de apariencia guardan este ajuste; los anteriores vuelven a «decide el juego».
- Mutación: el aspecto mutado de Jodi de la historia, por partes – color de piel y brillo como controles (casilla marcada = activo), venas y ojos como interruptores, «Restablecer» lo apaga todo. El maquillaje sigue visible sobre la piel descolorida y tu propio color de iris tiñe el ojo mutado. «Look de la historia» pone el aspecto de la cinemática: material de piel de la historia, todas las filas al máximo; después se puede bajar cada fila. Con él no se ven ni el maquillaje ni las cicatrices. Mientras la historia muta a la propia Jodi, se aplica su aspecto.
- Presets: la casilla «+» guarda la apariencia actual con una foto. Clic derecho: aplicar, ver contenido, renombrar, actualizar, mover, borrar, menú rápido.

## Curvas {#body}

- Los controles de pecho y cintura del juego.
- Las fichas cambian entre el cuerpo del juego y cada mod de cuerpo convertido.
- Los cuerpos convertidos tienen además controles de huesos: tamaño, busto, cintura, glúteos y caderas, muslos, pantorrillas, brazos, manos, pies. Se guardan por cuerpo; «Restablecer forma» los devuelve a su valor.
- Pecho y glúteos y caderas: rebote (0 % = solo animación) ajusta la física del juego y funciona con cualquier cuerpo; un sujetador sigue amortiguando como en el juego. El deslizador de pezones solo actúa mientras el pecho está descubierto. Ángulo y ancho de cadera solo existen en cuerpos convertidos; el ángulo se nota más cuanto menos rebote hay (al 100 % nada).
- Los mods que reemplazan el cuerpo deben convertirse antes con bodypak.pyz; consulta la guía BODY_MODS en la página del mod.

## Rostro {#face}

La expresión facial de Jodi.

- Controles para las expresiones del juego (relajada, concentrada, sonrisa, dolor, susto, cansada, sufrimiento), la mirada y las formas de la boca.
- «Ojos cerrados» (en Mirada) cierra los ojos, de abiertos a del todo cerrados; el parpadeo propio del juego sigue como siempre. Solo con cuerpos convertidos, como los controles del cuerpo. «Ojo izquierdo cerrado» y «Ojo derecho cerrado» cierran un solo ojo (izquierdo / derecho de Jodi), por ejemplo para guiñar; cada ojo se cierra tanto como el mayor valor entre su fila y «Ojos cerrados».
- Una entrada marcada conserva su valor, también en las poses; una sin marcar la decide la animación del juego. «Fijar todo» y «Todo al juego» cambian todas a la vez.
- Las expresiones se mezclan (juntas como máximo 100 %) o se suman.
- La casilla «+» guarda el rostro actual con una foto. Clic derecho: aplicar, ver contenido, renombrar, actualizar, mover, borrar.

## Mods {#mods}

Ajustes de otros mods que se registran en AltUI: a la izquierda sus entradas, a la derecha los interruptores, controles, números, opciones, colores, campos de texto, teclas y botones del elegido.

Encima de los campos: los preajustes de la página. La casilla «+» guarda los ajustes actuales con una foto (de frente o con cámara libre); un clic aplica un preajuste. Clic derecho: aplicar, ver contenido, renombrar, actualizar, mover, eliminar, menú rápido. «Ver contenido» lista los valores con una casilla cada uno: solo se aplican los marcados, los no marcados se conservan. Los preajustes que trae un mod van primero; se pueden aplicar, renombrar, darles una foto propia («Nueva foto») y marcar o desmarcar sus valores, no cambiar ni eliminar. Se guardan por mod en AltUI_ModPresets_<mod>.sav.

Esta pestaña solo aparece cuando hay un mod así instalado.

## Opciones {#options}

A la izquierda, las categorías.

- General: idioma, cuánto de la pantalla queda libre para Jodi, permitir quitar la ropa interior, cómo se muestran las prendas que no posees, el interruptor del Códice para la enciclopedia, el catálogo «Todos los objetos» y «Equipar armas automáticamente» para la pestaña Inventario. «Sin avisos» oculta todos los avisos de abajo, los de AltUI y los del propio juego.
- Casillas: tamaño de las casillas, tamaños propios para casillas de conjuntos, looks y ragdolls, prendas por casilla de conjunto, sin límite en listas largas, datos de las descripciones emergentes, el tamaño de las casillas de la pestaña Inventario.
- Grupos: unir grupos o mods con el mismo nombre, longitud de los nombres de grupo, altura de la zona de fichas, búsqueda de fichas.
- Cámara: campo de visión, distancia, altura, la cámara sigue la ranura elegida. Dos interruptores para la cámara libre (también en el modo ragdolls): sin colisión – atraviesa paredes y a Jodi – y a cualquier distancia de Jodi.
- Controles: tecla del panel, velocidad de desplazamiento, altura de la cámara con el botón derecho, cuánto levanta la rueda del ratón un ragdoll por paso.
- Movimiento: velocidad propia de Jodi al andar y al correr (del 50 al 200 %); agacharse y saltar no cambian. «Cámara lenta activada» enciende la cámara lenta, «Velocidad de la cámara lenta» (del 5 al 90 %, 25 % por defecto) fija lo lenta que va; la entrada del menú rápido «Cámara lenta sí / no» hace lo mismo que el interruptor. «Restablecer valores predeterminados» devuelve las velocidades de andar, correr y cámara lenta. «De pie» elige la animación en reposo de Jodi: las del juego (mirando alrededor, mirando las uñas, mirando la pierna, cautelosa, herida, posando) y las de los mods de reposo instalados (IdleAltUI_…). Los mods de andar/correr (WalkAltUI_…) añaden opciones a «Estilo al andar» y «Estilo al correr»; esas filas solo aparecen si hay elección. Un mod de andar gana a un mod de correr o de reposo elegido a la vez: ese lado se reproduce normal y lo indica bajo su fila.
- Tema: cada color del panel y su opacidad, una imagen de fondo (relleno, alineación, tono, sepia, invertir, opacidad propia) y una imagen para mosaicos y pestañas, esquemas de color guardados con un nombre; restablecer está en la barra de estado. Un tema guardado ahora conserva también las imágenes y sus ajustes. Imágenes propias: Background_1 … Background_30 y Button_1 … Button_30 (.png, .jpg o .jpeg) en la carpeta que indica la página. «Mostrar vistas previas» muestra las propias imágenes en sus chips; clic derecho en la vista previa de una imagen propia: «Rehacer vista previa».
- Conflictos de ranuras: separar los pares de ranuras del juego (por ejemplo sujetador y camisa) para poder llevar ambas prendas. Debajo: «Varias prendas en una ranura»: una ranura activada conserva sus prendas al ponerse otra (por ejemplo calcetines largos sobre unas medias), para Jodi, seguidores y looks.
- Pestañas: texto, iconos o ambos en la barra de pestañas; desactivar pestañas. «Intentar en una fila»: los textos se hacen más pequeños y luego más cortos, para que la barra quepa en una fila donde sea posible.

## Gestión {#manage}

Nombres propios para mods, grupos, ropa, peinados, pieles, maquillaje, poses y presets de apariencia.

- Los nombres se usan en todo el panel y la búsqueda los encuentra; el identificador original sigue siendo buscable y aparece en la descripción emergente.
- Fichas y una búsqueda filtran la lista; «solo mods» oculta las entradas del juego; ↺ vuelve al nombre predeterminado.
- Con altui_names.pyz los nombres se pueden exportar a un archivo de texto e importar de nuevo.
- Los mods de armas aparecen con los demás mods.
- «Uso» muestra qué mods están en uso ahora mismo: por mod, las piezas en uso y dónde están (Jodi ahora, conjuntos, looks, presets, favoritos, seguidores, escenas de ragdolls, de pie, armas, escenas y posiciones de objetos, cajones de ropa). Los mods sin usar aparecen debajo en gris, igual que los mods cuyo uso AltUI no puede detectar (mapas, mods de script). «Ver contenido» abre cualquiera de ellos. Lo que solo está en el armario no cuenta como uso. Cada mod es una ficha con su nombre visible y su archivo pak; los lugares de una pieza se resumen por tipo (p. ej. «Conjuntos 4–6, 8»). La lista se recopila al abrir «Uso»; en otros lugares el número de la izquierda es el de la última vez (ninguno antes de la primera).
- Las escenas de objetos y las posiciones de objetos guardadas también cuentan como uso (modelos de mods).

## Ragdolls {#ragdolls}

Figuras con física para colocar y posar en el nivel: copias de Jodi, zombis y personas.

- «+ Crear una copia de Jodi» pone una copia delante de ella, de pie y congelada en su pose actual, con todo lo que lleva puesto. Un look se convierte en figura con «Crear como ragdoll» en su menú contextual.
- «Zombis y personas»: una casilla con imagen por tipo de zombi, además de la enfermera y una superviviente. Un clic la crea; los enlaces bajo una casilla crean sus variantes.
- El mercenario también es un tipo de figura; conserva su fusil en las manos.
- Cada figura tiene una fila: activa (física, cae y se puede lanzar) o congelada (mantiene su pose), «articulaciones ›», bloquear todas, liberar todas, quitar. Abajo a la derecha, en la barra de estado: «Quitar todos» (quita todas las figuras) y «Esferas de articulación: sí/no».
- «articulaciones ›» despliega las 17 articulaciones de la figura, cada una con dos interruptores: bloqueada/libre y móvil/fija. Una articulación bloqueada queda rígida mientras la figura está activa; una móvil se puede posar en la figura congelada.
- Las esferas de articulación muestran dónde se puede agarrar: gris, rojo = bloqueada, verde = móvil, azul = fijada. Las ocultas brillan pálidas a través del cuerpo; un clic en una esfera agarra justo esa articulación. Solo aparecen en esta pestaña y en el modo ragdoll.
- Poses (en la fila desplegada): un nombre y «guardar pose» guardan cómo están colocadas las partes del cuerpo y qué articulaciones están bloqueadas o móviles. Una pose se carga en cualquier figura del mismo tipo, en cualquier nivel: clic carga, clic derecho: cargar / borrar. La figura se congela y queda de pie sobre el suelo.
- Escenas: «Guardar escena como» guarda cada figura del nivel con su aspecto, su lugar, su pose y sus articulaciones; el mismo nombre en el mismo nivel la sobrescribe. Solo se muestran las escenas del nivel actual. Un clic carga una escena y sustituye las figuras presentes; clic derecho: cargar / borrar.
- «Hacer atacable» (copias de Jodi, de NPC y del mercenario): los zombis atacan al ragdoll como a una figura; su cabecera muestra entonces «· atacable». Cada golpe empuja la parte del cuerpo más cercana al zombi; un ragdoll congelado vuelve a su pose alrededor de un segundo después del último golpe. Los ragdolls no mueren. El estado se guarda con la escena.

Con el ratón sobre una figura, junto al panel y en el modo ragdoll:

- Arrastrar con el botón izquierdo una figura congelada la mueve por el suelo; la rueda la sube o la baja mientras arrastras.
- Arrastrar con el botón izquierdo una figura activa agarra la parte del cuerpo bajo el ratón; al soltarla, cae. La rueda sube o baja entretanto el punto agarrado.
- Un clic derecho mientras arrastras fija la parte donde está; el resto de la figura cuelga de ella. Si la vuelves a agarrar, queda libre. «soltar todas» en la fila de la figura las libera todas.
- Arrastrar con el botón derecho gira la figura sobre sus caderas.
- Mayús + clic izquierdo bloquea o libera la articulación pulsada.
- Mayús + clic derecho en una figura congelada hace móvil la articulación. Arrastrar entonces con el botón izquierdo una parte del cuerpo bajo una articulación móvil mueve solo esa parte; se queda donde la sueltas: así se posa una figura.
- Arrastrar con el botón derecho una parte del cuerpo bajo una articulación móvil de una figura congelada gira ese miembro sobre la articulación: el punto agarrado sigue al ratón y la mano y los dedos giran con él. Mientras tanto, la rueda del ratón lo tuerce sobre su propio eje. El giro queda en la pose y se guarda con poses y escenas; los límites de las articulaciones solo cuentan cuando la figura se activa.
- Dedos y ojos (figuras congeladas con el cuerpo de Jodi): de cerca (a menos de 1 m aprox.) aparecen pequeñas esferas en las falanges y en los párpados. Arrastrar con el botón derecho una esfera de dedo gira esa falange, la rueda la tuerce; arrastrar con el izquierdo flexiona todo el dedo (tirar de la punta hacia el nudillo). Arrastrar con el izquierdo una esfera de párpado dirige la mirada de ambos ojos; la rueda abre y cierra mientras tanto los párpados (con Mayús al agarrar: solo ese párpado).
- En una figura desplegada, «Mano izquierda» y «Mano derecha» aplican poses de mano (abierta, relajada, puño, pulgar arriba, paz, señalar, sujetar, pose base); «Ojos: restablecer» abre los párpados y mira al frente. Las poses y escenas guardan dedos, párpados y mirada.

Sin el panel, el menú rápido activa o congela figuras: «Ragdoll: activar / congelar la del centro» toma la figura del centro de la pantalla, «Ragdolls: activos / congelados» las cambia todas.

## Modo ragdoll {#ragmode}

Mover y posar las figuras sin el panel, con la cámara libre en la sala. Se inicia con el tercer botón redondo sobre + y − o desde el menú rápido.

- El puntero del ratón sigue visible; sobre una figura todo funciona como junto al panel (ver «Ragdolls»).
- W A S D y Q E mueven la cámara, Mayús más rápido; Mayús + rueda ajusta la velocidad.
- Arrastrar en el vacío gira la cámara.
- Mantén pulsado el botón central para girar la cámara sin que lo detengan los bordes de la pantalla; luego el puntero vuelve a su sitio.
- Esc o B termina el modo.

## Navegación {#navigation}

- Volar / Aterrizar: Jodi vuela. Moverse como siempre, Espacio sube, Ctrl baja, Mayús va tres veces más rápido; el control deslizante fija la velocidad. Las paredes la detienen. Aterrizar la deja caer al suelo: una caída alta hace daño como en el juego. También en el menú rápido, así que también con una tecla propia (Acciones › Teclas propias).
- Muestra las camas del nivel actual donde Jodi puede guardar, la más cercana primero, con el nombre de la sala y la distancia.
- «Teletransportar» coloca a Jodi junto a esa cama, mirándola; se guarda como siempre usando la cama. Los seguidores que la siguen vienen con ella; los que esperan se quedan.
- Un teletransporte se salta todo lo que hay en el camino: los pasos de la historia que el juego inicia cuando Jodi cruza una zona no ocurren por el camino, solo cuando entra en ella más tarde. La oficina de Jodi, el nivel 3 y el campo de tiro no tienen estas camas.

## Objetos {#objects}

Colocar en el mundo modelos del juego, armas y modelos de mods (p. ej. accesorios de mods de poses), moverlos y guardarlos como escena.

- A la izquierda, CATÁLOGO: Todos, ★ Favoritos, las carpetas del juego, «Del nivel: …», Armas y Mods (+ despliega cada mod). A la derecha una búsqueda y los modelos en mosaicos, ordenados por nombre; «Mostrar más» carga más. AltUI toma las imágenes y las guarda.
- Un clic en un mosaico pone el modelo en el suelo delante de Jodi, fijo. Clic derecho: favorito, «Aparecer con física».
- AltUI encuentra los modelos de mods recorriendo los mods una vez, carpeta por carpeta (el contador se ve arriba), y guarda el resultado; después solo se recorren los mods nuevos. «Volver a buscar en los mods» empieza de nuevo. Algunos mods guardan modelos en carpetas que no se llaman como su pak; «Buscar en todas las carpetas de mods» los encuentra (el juego se detiene unos treinta segundos).
- Abajo el bloque «Seleccionado»: imagen, nombre, fijo o con física, deseleccionar, activar/desactivar física, al suelo, copiar, quitar; campos para posición, giro (guiñada, cabeceo, alabeo) y tamaño – Intro aplica. El objeto seleccionado tiene un marco amarillo.
- MUNDO › En el mundo: una fila por objeto con seleccionar (en el seleccionado: deseleccionar), física sí/no, copiar, quitar. «Posiciones» abre un bloque: un nombre y «Guardar posición» guardan lugar, giro, tamaño y física. La posición aparece en cada objeto del mismo modelo en el mismo nivel – un clic lo coloca allí, clic derecho: aplicar / borrar.
- MUNDO › Escenas: un nombre y «Guardar escena» guardan todos los objetos del nivel; el mismo nombre en el mismo nivel sobrescribe. Solo se muestran las escenas del nivel actual. Un clic carga una escena y reemplaza los objetos; clic derecho: cargar / borrar. Un modelo que falta (mod no instalado) se omite y se avisa.
- Los objetos desaparecen con el nivel; una escena los trae de vuelta.

Con el ratón sobre un objeto, junto al panel y en el modo ragdoll:

- Clic lo selecciona.
- Arrastrar con el izquierdo desliza un objeto fijo a su altura; un objeto con física se agarra y al soltarlo se lanza.
- Arrastrar con el derecho lo gira sobre su eje vertical, Shift + arrastrar con el derecho lo gira libremente. Un objeto con física se queda quieto mientras tanto y luego vuelve a caer.
- La rueda al arrastrar lo sube o baja (también agarrado con física); Ctrl + rueda cambia su tamaño.

## Seguidores {#followers}

Looks convertidos en personas del juego: un seguidor acompaña a Jodi, lucha y obedece órdenes; un PNJ se queda donde está y se defiende.

- En la pestaña Looks, clic derecho en un look: «Crear como seguidor» o «Crear como PNJ». La figura aparece delante de Jodi con ese look.
- La pestaña «Seguidores» muestra todas las figuras con su estado (sigue, espera, PNJ, inactivo, caído) y chips: «Sígueme», «Espera aquí», «Traer aquí», → PNJ / → Seguidor, «Activo», ∞ con un corazón (invulnerable), ∞ con cartuchos (munición infinita) y el engranaje (atacable / no atacable, renombrar, cambiar look, revivir, eliminar). «...» pliega y despliega las fichas de la figura (ropa y mochila); se queda así por figura, también tras reiniciar.
- Los seguidores aparecen encima de los PNJ, con una línea entre los dos grupos. Los chips sobre las filas muestran todos, solo seguidores o solo PNJ (se mantiene tras reiniciar).
- Un clic en una fila selecciona la figura. Arriba están la mochila (izquierda) y la caja (derecha): un clic da un objeto a la figura seleccionada, un arma con su pintura y accesorios. Un clic en una casilla de la figura la devuelve a la mochila; clic derecho: todo, o a la caja. «...» sobre una lista la pliega.
- El menú contextual de una pila – de Jodi o de la figura – tiene la fila de cantidad como en la pestaña Inventario: «Dar 5», «Coger 5», a la caja.
- La ropa son prendas reales de la figura, como con los PNJ del juego: se daña, puede romperse y aparece en el inventario de PNJ del propio juego, donde también se puede intercambiar. Bajo una figura, sus prendas son casillas (las dañadas, marcadas): un clic se quita una y la deja en la mochila de Jodi; clic derecho: reparar con un kit de costura de la mochila de Jodi, o reparar todo. En la columna de la mochila, «Ropa» muestra las prendas de Jodi: un clic da una a la figura seleccionada, que se la pone (el daño y los colores van con ella).
- «Activo» desactivado saca a la figura del mundo con todo lo que lleva; al activarla vuelve delante de Jodi.
- «Munición infinita»: la figura recarga sus armas de fuego una y otra vez sin necesitar munición en su bolsa. Las armas con cargador no tocan su munición; la escopeta y el lanzagranadas gastan primero la que lleva.
- Una figura que no es invulnerable puede caer. Sigue en la lista y «Revivir» la devuelve con sus cosas. Las figuras nunca se convierten en zombis.
- «Invulnerable» (∞ con un corazón): la figura no puede morir, su salud se rellena tras cada golpe. Aun así muestra las reacciones a los golpes y su ropa sufre daño.
- «Atacable» (engranaje): los zombis solo eligen como objetivo figuras atacables, sean invulnerables o no. Tras «Hacer no atacable» los zombis la dejan en paz y tampoco recibe daño. El ajuste se guarda; las figuras nuevas son atacables.
- «+ Jason» (abajo a la derecha de la pestaña) añade a Jason de la historia como seguidor, con su Glock. Obedece órdenes, te acompaña y se guarda. Solo lucha con su propia Glock: una Glock que le des pasa a ser suya; otras armas no las acepta. No tiene look, ropa ni maquillaje; si cae, no se le puede curar: «Revivir» lo trae de vuelta.
- «Eliminar» pide confirmación; los objetos y armas de la figura van a la caja y su ropa a la mochila de Jodi.
- «Cambiar look» pasa a la pestaña Looks: haz clic en el look que debe llevar la figura.
- Cada figura lleva el maquillaje de su look y tiene una de las voces de PNJ del juego. Una figura creada con AltUI antes de la 2.2.0 muestra el maquillaje de Jodi hasta que «Cambiar look…» le da el suyo.

AltUI guarda las figuras en una partida propia (AltUI_Followers.sav); la partida del juego nunca las contiene. Los seguidores que siguen vienen a cada nivel y tras cargar; los que esperan y los PNJ se quedan en su nivel, en su sitio.

Menú rápido: «Seguidor: sígueme / espera aquí» se dirige al seguidor que tienes a la vista, «Todos los seguidores: seguir / esperar» a todos. «Todos los seguidores: venid aquí» trae a cada seguidor activo a los puestos delante de Jodi, también a uno que espera en otro nivel.

Figura en una pose: el grupo del menú rápido «Figura: poses favoritas» contiene cada una de tus poses favoritas como «Figura: <pose>». La entrada pone a la figura seguidora o PNJ que tienes a la vista en esa pose (Jason no). Entonces ni camina ni lucha, mantiene la pose incluso tras recibir golpes y no se gira. Si es atacable, los zombis la atacan, y una figura que no es invulnerable puede morir: así se montan escenas. «Figura: terminar pose» la hace levantarse; después sigue o espera como antes. Un cambio de nivel termina la pose.

## Códice {#kodex}

- Enciclopedia: las entradas del archivo del ordenador de la oficina de Jodi, con imagen y texto. Solo se muestran las que el juego ha desbloqueado, o todas con el interruptor de Opciones › General.
- Contraseñas: las cerraduras con código del nivel actual, la más cercana primero, con su distancia y si están cerradas. Cada código queda oculto hasta que haces clic en él.
- Manual de AltUI: este texto.

## TV {#tv}

- Solo aparece cuando el nivel actual tiene un televisor (la oficina de Jodi), o siempre con el interruptor de Opciones › General. Con varios televisores se controla el más cercano a Jodi.
- Encender / Apagar funcionan como la tecla E en el televisor. El televisor lee su lista de vídeos la primera vez que se enciende; hasta entonces la pestaña pide encenderlo una vez.
- Haz clic en un vídeo para reproducirlo. Un vídeo ya empezado continúa donde se quedó, como en el propio televisor.
- Tus propios vídeos: pon archivos .mp4 en la carpeta del juego TheKillingAntidote/Videos/TV/. Aparecen después de volver a cargar el nivel.

## Menú rápido {#quick}

Mantén pulsado 4 (otra tecla en Acciones) y se abre una rueda alrededor del ratón. Suelta sobre una entrada para ejecutarla; suelta en el centro para no hacer nada.

- Entradas: conjuntos, looks, rostros, presets de apariencia, poses, pestañas, ajustes de otros mods y acciones: cámara libre, modo foto, modo ragdoll, una copia de Jodi como ragdoll, cambiar todos los ragdolls entre activos y congelados, activar / congelar el del centro, quitar todos los ragdolls, velocidad propia sí / no.
- Más acciones: «Cámara lenta sí / no», «Detener el tiempo / seguir» (todo se queda quieto; el panel y las cámaras siguen funcionando; también la cámara del modo foto del juego), «Ocultar / mostrar a Jodi» (con ropa, pelo y arma; en el siguiente nivel vuelve a estar) y las órdenes a los seguidores (ver «Seguidores»).
- «Ocultar / mostrar la interfaz del juego» apaga y enciende el HUD del juego, como hace su modo foto.
- «+1 Mano invisible» pone una Mano invisible en la mochila (ver Inventario › Todos los objetos).
- «Altura de la cámara (rueda)»: aparecen dos flechas en el centro de la pantalla y la rueda sube o baja la cámara en lugar de acercarla o alejarla. Un clic izquierdo o Esc lo termina. La altura se guarda.
- Teclas propias: en Acciones, clic derecho en un elemento de «Disponible» y pulsa una tecla: el elemento se ejecuta con esa tecla, con el panel cerrado, también en la cámara libre y en el modo foto del juego. Un clic en la tecla de una fila asigna otra, ✕ la quita. La tecla del panel, la del menú rápido y una tecla ya asignada se rechazan; una tecla que el juego ya usa activa ambas cosas.
- Se añaden en Acciones, o con clic derecho en una casilla, una pestaña o la entrada de un mod («Añadir al menú rápido»).
- La pestaña Acciones: a la izquierda «En la rueda» (tecla, opacidad, orden con ↑ ↓ ✕), «Teclas propias», luego «Todos» y cada grupo con entradas – conjuntos, looks, caras, preajustes, poses, pestañas, entradas de mods – y una fila por cada mod con acciones. A la derecha, las entradas de ese grupo con una casilla (en la rueda o no) y una búsqueda encima. Cada grupo recuerda su posición de desplazamiento.
- El orden en la rueda es el orden de la lista en Acciones › En la rueda.

## Para autores de mods {#modding}

- Los mods de ropa no necesitan nada especial: AltUI lee las tablas del juego y coloca cada prenda en su ranura.
- Los mods que reemplazan el cuerpo o un arma pueden convertirse con bodypak.pyz y weaponpak.pyz para instalar varios a la vez; también pueden hacerse para AltUI directamente en el Unreal Editor.
- Los mods de reposo (un pak que sustituye la animación de reposo de Jodi) se pueden convertir con idlepak.pyz: python3 idlepak.pyz <mod>.pak. El nuevo IdleAltUI_….pak va en Mods/ y aparece en Opciones › Movimiento › «De pie»; el reposo propio del juego se mantiene. AltUI debe estar instalado: el conversor construye el nuevo pak en parte a partir de AltUI.pak y lo busca en las carpetas habituales de Steam; si está en otro sitio, indica la ruta con --altui <ruta a AltUI.pak>.
- Los mods de andar/correr (un pak que sustituye la animación de andar o correr de Jodi) se convierten con walkpak.pyz: python3 walkpak.pyz <mod>.pak. El nuevo WalkAltUI_….pak va a Mods/ y aparece en Opciones › Movimiento › «Estilo al andar» (y «Estilo al correr» si trae carrera); el andar propio del juego se mantiene. walkpak rechaza una animación sin las curvas de movimiento del juego (MoveData_Speed, Rotation Speed) e indica cuál falta. Como idlepak, necesita AltUI.pak (--altui <ruta> si no está en las carpetas habituales de Steam).
- Los mods pueden mostrar sus ajustes en la pestaña Mods mediante dos tablas de datos y una interfaz; MOD_UI.md en el repositorio del código fuente explica cómo.
