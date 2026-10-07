## Acerca de AltUI {#about}

AltUI sustituye el armario y la pantalla de apariencia de The Killing Antidote por un solo panel. Se abre en cualquier lugar de un nivel con B, sin ir al armario ni al espejo.

Cada prenda del juego y de todos los mods instalados está en una lista por ranura, con búsqueda, filtros, favoritos y ocultación. Peinado, maquillaje, cuerpo, rostro, poses, armas y los conjuntos y looks guardados están en el mismo panel, y también los ragdolls – copias de Jodi, zombis y personas para colocar y posar – y la velocidad de Jodi al andar y al correr.

El panel se abre en la pestaña en la que se cerró. Las pestañas que no uses se pueden desactivar en Opciones › Pestañas.

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
- la carpeta AltUI – fotos de looks, rostros y presets de apariencia
- la carpeta WeaponIcons – imágenes de armas

La ropa, los conjuntos, el maquillaje y el peinado se guardan en las partidas del propio juego y se conservan.

## Controles {#controls}

- B abre y cierra el panel (otra tecla en Opciones › Controles); Esc lo cierra.
- El clic izquierdo selecciona, viste o aplica; el clic derecho abre el menú contextual de una casilla, una fila o una pestaña.
- La rueda del ratón desplaza; la velocidad se ajusta en Opciones › Controles.
- Mientras el panel está abierto, Jodi no puede caminar. Arrastrar sobre el fondo gira la cámara; hacer clic en Jodi y arrastrar la gira a ella, y al cerrar el panel vuelve a su posición.
- + y − cambian la distancia de la cámara en pasos del 5 %, la rueda sobre Jodi en pasos del 4 %.
- Los tres botones redondos sobre + y − abren una cámara libre (el ratón gira, W A S D y Q E mueven, Mayús más rápido, la rueda ajusta la velocidad, Esc vuelve), el modo foto del juego (Esc vuelve) y el modo ragdoll (ver «Modo ragdoll»).
- Deshacer y Rehacer (cinco pasos) están en la barra de estado de abajo.
- Mantén pulsado 4 para el menú rápido (ver «Menú rápido»).

## Vestimenta {#clothes}

A la izquierda las ranuras, a la derecha las prendas de la ranura elegida.

- Un clic en una prenda la viste; un clic en una puesta la quita.
- Las fichas sobre la lista filtran por mod o grupo; «...» pliega las filas de fichas. Un campo de búsqueda reduce las fichas, y la búsqueda sobre la lista encuentra prendas por nombre, mod o grupo.
- Filtros: solo poseídos, solo favoritos, solo vanilla, solo puestos.
- Clic derecho en una prenda: favorito, ocultar, color con la paleta del juego, restablecer color, meter en la mochila, renombrar, solo este grupo, ver contenido del mod, mostrar en la pestaña.
- La descripción emergente indica de qué mod viene una prenda.

## Conjuntos {#outfits}

Los conjuntos guardados del juego: los mismos que usan el armario y el espejo.

- La casilla «+» guarda lo que Jodi lleva puesto como un conjunto nuevo.
- Un clic en un conjunto lo viste.
- Clic derecho: vestir, ver contenido, añadir al menú rápido o quitar de él, renombrar, mover a la izquierda / a la derecha / al principio / al final, borrar.
- Un conjunto sin nombre propio aparece como «Conjunto» con su posición en la lista.
- El tamaño de las casillas y cuántas prendas muestra cada una se ajustan en Opciones › Casillas.

## Looks {#looks}

Un look es todo a la vez: ropa con sus colores, peinado y color de pelo, maquillaje, ojos, piel, controles del cuerpo, mod de cuerpo y rostro.

- La casilla «+» guarda el look actual con una foto de cuerpo entero, de frente o como la ves ahora.
- Un clic en un look lo aplica.
- Clic derecho: ver contenido, renombrar, actualizar (foto de frente o como se ve), mover, borrar, añadir al menú rápido o quitar de él.

## Mochila {#bag}

Lo que Jodi lleva puesto y lo que lleva consigo.

- Un clic en una prenda puesta la quita; en una que lleva consigo, la viste.
- Clic derecho: vestir o quitar, reparar (necesita un kit de costura), quitar de la mochila, devolver al armario.
- «Ordenar la mochila» quita las prendas que no se llevan puestas y que también están en el armario.
- «Todo a la mochila» quita cada prenda puesta y la mete en la mochila.

## Peinado {#hair}

Todos los peinados del juego y de los mods.

- Un clic en un peinado lo pone.
- «Color de pelo...» abre la paleta del juego; «Colores de pelo naturales» ofrece 14 colores listos.
- Clic derecho: restablecer color de pelo, renombrar, ver contenido del mod.

## Poses {#poses}

Cada animación de acción que conocen el juego y tus mods de poses: la lista detrás de la app «ritmo» del teléfono.

- Un clic en una pose la reproduce; otro clic o «Detener pose» la detiene.
- Las poses están ordenadas por postura (de pie, sentada, tumbada) y por capítulo; las fichas filtran por mod y la búsqueda encuentra títulos.
- Clic derecho: favorito, ocultar, marcar como de pie / sentada / tumbada / en movimiento, renombrar, añadir al menú rápido.
- «Medir todas» reproduce una vez cada pose que aún no tiene postura y la ordena.

## Armas {#weapons}

A la izquierda, una entrada por arma, incluidas las armas cuerpo a cuerpo. Para cada arma, el modelo, la skin y el sonido del disparo se eligen por separado.

- Arriba los modelos: el del juego y cada mod de modelo instalado.
- Abajo las skins: las pinturas de armas del juego (sin bote de pintura) y cada mod de skin instalado.
- Sonido: el sonido de disparo propio del arma («Original») y cada sonido de disparo instalado para ella. Un clic elige el sonido y lo reproduce; las demás armas conservan el suyo. Un silenciador montado con sonido propio sigue teniendo prioridad.
- Las fichas de arriba filtran las tres secciones a la vez. Clic derecho en una casilla: favorito, ocultar, solo este mod.
- La elección se guarda y se vuelve a aplicar cuando se recoge el arma o se saca de la caja de almacenamiento.
- Una pintura aplicada en el juego con un bote de pintura se conserva: pasa a ser la skin elegida.
- Clic derecho en un modelo de mod: forzar skins en él, excluir el cargador, la mira, el silenciador o la empuñadura, mostrar la imagen propia del mod.
- Los mods de armas y de sonidos de disparo deben convertirse antes con weaponpak.pyz; consulta la guía WEAPON_MODS en la página del mod.

## Apariencia {#look}

Piel, cada tipo de maquillaje, ojos y los presets de apariencia del juego.

- Un clic en una entrada la aplica. Clic derecho en el maquillaje: teñir con la paleta del juego, restablecer el teñido.
- Ojos: color del iris y de las pestañas en el menú contextual.
- Presets: la casilla «+» guarda la apariencia actual con una foto. Clic derecho: aplicar, ver contenido, renombrar, actualizar, mover, borrar, menú rápido.

## Curvas {#body}

- Los controles de pecho y cintura del juego.
- Las fichas cambian entre el cuerpo del juego y cada mod de cuerpo convertido.
- Los cuerpos convertidos tienen además controles de huesos: tamaño, busto, cintura, glúteos y caderas, muslos, pantorrillas, brazos, manos, pies. Se guardan por cuerpo; «Restablecer forma» los devuelve a su valor.
- Los mods que reemplazan el cuerpo deben convertirse antes con bodypak.pyz; consulta la guía BODY_MODS en la página del mod.

## Rostro {#face}

La expresión facial de Jodi.

- Controles para las expresiones del juego (relajada, concentrada, sonrisa, dolor, susto, cansada, sufrimiento), la mirada y las formas de la boca.
- Una entrada marcada conserva su valor, también en las poses; una sin marcar la decide la animación del juego. «Fijar todo» y «Todo al juego» cambian todas a la vez.
- Las expresiones se mezclan (juntas como máximo 100 %) o se suman.
- La casilla «+» guarda el rostro actual con una foto. Clic derecho: aplicar, ver contenido, renombrar, actualizar, mover, borrar.

## Mods {#mods}

Ajustes de otros mods que se registran en AltUI: a la izquierda sus entradas, a la derecha los interruptores, controles, números, opciones, colores, campos de texto, teclas y botones del elegido.

Esta pestaña solo aparece cuando hay un mod así instalado.

## Opciones {#options}

A la izquierda, las categorías.

- General: idioma, cuánto de la pantalla queda libre para Jodi, permitir quitar la ropa interior, cómo se muestran las prendas que no posees, el interruptor del Códice para la enciclopedia.
- Casillas: tamaño de las casillas, tamaños propios para casillas de conjuntos, looks y ragdolls, prendas por casilla de conjunto, sin límite en listas largas, datos de las descripciones emergentes.
- Grupos: unir grupos o mods con el mismo nombre, longitud de los nombres de grupo, altura de la zona de fichas, búsqueda de fichas.
- Cámara: campo de visión, distancia, altura, la cámara sigue la ranura elegida.
- Controles: tecla del panel, velocidad de desplazamiento, altura de la cámara con el botón derecho.
- Movimiento: velocidad propia de Jodi al andar y al correr (del 50 al 200 %, «Restablecer al 100 %»); agacharse y saltar no cambian.
- Menú rápido: su tecla, su opacidad, lo que hay en la rueda.
- Colores: cada color del panel, opacidades, esquemas de color guardados con un nombre.
- Conflictos de ranuras: separar los pares de ranuras del juego (por ejemplo sujetador y camisa) para poder llevar ambas prendas.
- Pestañas: texto, iconos o ambos en la barra de pestañas; desactivar pestañas.

## Gestión {#manage}

Nombres propios para mods, grupos, ropa, peinados, pieles, maquillaje, poses y presets de apariencia.

- Los nombres se usan en todo el panel y la búsqueda los encuentra; el identificador original sigue siendo buscable y aparece en la descripción emergente.
- Fichas y una búsqueda filtran la lista; «solo mods» oculta las entradas del juego; ↺ vuelve al nombre predeterminado.
- Con altui_names.pyz los nombres se pueden exportar a un archivo de texto e importar de nuevo.

## Ragdolls {#ragdolls}

Figuras con física para colocar y posar en el nivel: copias de Jodi, zombis y personas.

- «+ Crear una copia de Jodi» pone una copia delante de ella, de pie y congelada en su pose actual, con todo lo que lleva puesto. Un look se convierte en figura con «Crear como ragdoll» en su menú contextual.
- «Zombis y personas»: una casilla con imagen por tipo de zombi, además de la enfermera y una superviviente. Un clic la crea; los enlaces bajo una casilla crean sus variantes.
- Cada figura tiene una fila: activa (física, cae y se puede lanzar) o congelada (mantiene su pose), «articulaciones ›», bloquear todas, liberar todas, quitar. «Quitar todos» quita todas las figuras.
- «articulaciones ›» despliega las 17 articulaciones de la figura, cada una bloqueada, libre o móvil. Una articulación bloqueada queda rígida mientras la figura está activa.
- Poses (en la fila desplegada): un nombre y «guardar pose» guardan cómo están colocadas las partes del cuerpo. Una pose se carga en cualquier figura del mismo tipo, en cualquier nivel: clic carga, clic derecho: cargar / borrar. La figura se congela y queda de pie sobre el suelo.
- Escenas: «Guardar escena como» guarda cada figura del nivel con su aspecto, su lugar, su pose y sus articulaciones; el mismo nombre en el mismo nivel la sobrescribe. Solo se muestran las escenas del nivel actual. Un clic carga una escena y sustituye las figuras presentes; clic derecho: cargar / borrar.

Con el ratón sobre una figura, junto al panel y en el modo ragdoll:

- Arrastrar con el botón izquierdo una figura congelada la mueve por el suelo; la rueda la sube o la baja mientras arrastras.
- Arrastrar con el botón izquierdo una figura activa agarra la parte del cuerpo bajo el ratón; al soltarla, cae.
- Arrastrar con el botón derecho gira la figura sobre sus caderas.
- Mayús + clic izquierdo bloquea o libera la articulación pulsada.
- Mayús + clic derecho en una figura congelada hace móvil la articulación. Arrastrar entonces con el botón izquierdo una parte del cuerpo bajo una articulación móvil mueve solo esa parte; se queda donde la sueltas: así se posa una figura.

Sin el panel, el menú rápido activa o congela figuras: «Ragdoll: activar / congelar la del centro» toma la figura del centro de la pantalla, «Ragdolls: activos / congelados» las cambia todas.

## Modo ragdoll {#ragmode}

Mover y posar las figuras sin el panel, con la cámara libre en la sala. Se inicia con el tercer botón redondo sobre + y − o desde el menú rápido.

- El puntero del ratón sigue visible; sobre una figura todo funciona como junto al panel (ver «Ragdolls»).
- W A S D y Q E mueven la cámara, Mayús más rápido; Mayús + rueda ajusta la velocidad.
- Arrastrar en el vacío gira la cámara.
- Esc o B termina el modo.

## Códice {#kodex}

- Enciclopedia: las entradas del archivo del ordenador de la oficina de Jodi, con imagen y texto. Solo se muestran las que el juego ha desbloqueado, o todas con el interruptor de Opciones › General.
- Contraseñas: las cerraduras con código del nivel actual, la más cercana primero, con su distancia y si están cerradas. Cada código queda oculto hasta que haces clic en él.
- Manual de AltUI: este texto.

## Menú rápido {#quick}

Mantén pulsado 4 (otra tecla en Opciones › Menú rápido) y se abre una rueda alrededor del ratón. Suelta sobre una entrada para ejecutarla; suelta en el centro para no hacer nada.

- Entradas: conjuntos, looks, rostros, presets de apariencia, poses, pestañas, ajustes de otros mods y acciones: cámara libre, modo foto, modo ragdoll, una copia de Jodi como ragdoll, cambiar todos los ragdolls entre activos y congelados, activar / congelar el del centro, quitar todos los ragdolls, velocidad propia sí / no.
- Se añaden en Opciones › Menú rápido, o con clic derecho en una casilla, una pestaña o la entrada de un mod («Añadir al menú rápido»).
- El orden en la rueda es el orden de la lista en Opciones › Menú rápido.

## Para autores de mods {#modding}

- Los mods de ropa no necesitan nada especial: AltUI lee las tablas del juego y coloca cada prenda en su ranura.
- Los mods que reemplazan el cuerpo o un arma pueden convertirse con bodypak.pyz y weaponpak.pyz para instalar varios a la vez; también pueden hacerse para AltUI directamente en el Unreal Editor.
- Los mods pueden mostrar sus ajustes en la pestaña Mods mediante dos tablas de datos y una interfaz; MOD_UI.md en el repositorio del código fuente explica cómo.
