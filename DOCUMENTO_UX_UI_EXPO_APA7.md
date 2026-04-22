# Diseño de Experiencia de Usuario (UX) e Interfaces (UI) para Soluciones Móviles

## Proyecto

**Título del proyecto:** Sistema móvil para toma y gestión de pedidos en restaurante con sincronización en tiempo real con backend Django REST

**Programa / curso:**  
[Espacio para completar]

**Aprendiz / autores:**  
[Espacio para completar]

**Instructor:**  
[Espacio para completar]

**Institución:**  
[Espacio para completar]

**Fecha:**  
[Espacio para completar]

---

## Resumen

El presente documento describe el diseño de experiencia de usuario (UX) y de interfaces de usuario (UI) de una aplicación móvil desarrollada con Expo, React Native y Expo Router, orientada a la toma y gestión de pedidos en un entorno de restaurante. La solución fue construida en coherencia con un backend desarrollado en Django REST Framework, el cual centraliza la autenticación, la administración de pedidos, la consulta del menú del día, la edición de detalles y la validación de reglas de negocio. El propósito de la aplicación es optimizar el flujo operativo del personal del restaurante, permitiendo abrir pedidos por mesa, agregar productos, gestionar corrientes y desayunos, editar pedidos, marcar productos como servidos y consultar el estado actualizado de las órdenes desde un dispositivo móvil. El diseño visual prioriza claridad operativa, rapidez de uso y control de acceso, incluyendo restricciones visuales y funcionales para acciones no permitidas. El documento presenta dieciséis funcionalidades desde la perspectiva del usuario final, indicando la interfaz diseñada, la descripción funcional, el comportamiento esperado y la relación con las rutas del backend.

**Palabras clave:** Expo, React Native, UX, UI, pedidos, restaurante, Django REST Framework.

---

## Introducción

Una vez construida la lógica de servicios en el backend, la siguiente fase del proyecto consiste en materializar la interacción del usuario con el sistema móvil. En este contexto, la interfaz no se limita a una capa estética, sino que se convierte en la manifestación funcional de los requerimientos del sistema. Cada pantalla, componente visual y transición entre vistas debe responder directamente a una necesidad operativa del restaurante.

La aplicación móvil desarrollada permite que el personal autorizado pueda iniciar sesión, abrir pedidos por mesa, visualizar órdenes activas, gestionar productos, registrar menús corrientes y desayunos, actualizar estados y consultar la información sincronizada con el backend. Esto garantiza una experiencia de uso coherente con los procesos reales del negocio y una operación más ágil en escenarios de atención diaria.

---

## Descripción General del Sistema

La solución móvil fue construida con las siguientes tecnologías:

- **Expo** como framework base para desarrollo móvil.
- **React Native** para la construcción de interfaces nativas.
- **Expo Router** para la navegación entre pantallas.
- **Axios** para consumo de la API REST.
- **Django REST Framework** como backend principal.

La app móvil está orientada al proceso operativo del restaurante y actualmente cuenta con las siguientes pantallas base:

- Pantalla de inicio de sesión.
- Pantalla de listado de pedidos.
- Pantalla de detalle del pedido.
- Modales para agregar productos, editar pedido, editar detalle, confirmar acciones y asistente por voz.

Además del flujo operativo tradicional, la aplicación incorpora una capa de asistencia inteligente para interpretación de pedidos por texto o por voz, lo cual amplía la experiencia de usuario al permitir una captura más natural del pedido y una posterior traducción al flujo normal del sistema.

---

## Patrón de Diseño Aplicado

El diseño de la aplicación se apoya principalmente en principios de **Material Design para Android**, debido a que la solución fue pensada para una experiencia móvil operativa, con jerarquías visuales claras, botones de acción destacados, tarjetas informativas, chips de estado, navegación consistente y retroalimentación visual inmediata ante acciones del usuario. También se incorporan criterios de legibilidad, consistencia y visibilidad del estado del sistema, alineados con patrones modernos de interfaces móviles.

Elementos del patrón observables en la aplicación:

- Uso de tarjetas para agrupar información operativa.
- Botones prominentes para acciones críticas.
- Chips de estado para distinguir pedidos en curso, servidos o pagados.
- Modales y retroalimentación contextual para confirmar o bloquear acciones.
- Jerarquía visual clara mediante contraste, color y tipografía.

### Referencias del patrón

Google. (s. f.). *Material Design 3*. https://m3.material.io/

Apple. (s. f.). *Human Interface Guidelines*. https://developer.apple.com/design/human-interface-guidelines/

---

## Control de Acceso y Restricción Visual

El sistema incorpora control de acceso desde la autenticación y desde la lógica de permisos definida en el backend. En la app móvil, este control se refleja visualmente de las siguientes formas:

- Redirección al login cuando no existe sesión activa.
- Ocultamiento del contenido operativo para usuarios no autenticados.
- Restricción de acciones cuando un pedido ya está pagado.
- Mensajes visuales de bloqueo cuando no se permite agregar, editar, eliminar o marcar productos.
- Sincronización con el backend para validar caja abierta, permisos de escritura y estados del pedido.

Aunque la aplicación móvil está enfocada en operación de pedidos, la gestión de permisos se encuentra alineada con los roles del backend, lo que garantiza coherencia entre lo que el usuario visualiza y lo que realmente puede ejecutar.

---

## Arquitectura de Navegación e Interfaz en Expo

La app fue estructurada con Expo Router y una organización modular por funcionalidades:

- `app/login`: acceso al sistema.
- `app/pedidos`: visualización y administración de pedidos activos.
- `app/detalle`: gestión detallada de una orden específica.
- `features/pedidos`: componentes y lógica de pedidos.
- `features/detalle`: componentes y lógica del detalle del pedido.
- `features/voice`: asistente de voz para captura asistida de pedidos.
- `features/ui`: componentes globales de interfaz.

Esta organización mejora la mantenibilidad del sistema y favorece el crecimiento futuro del proyecto.

---

## Integración de Asistencia Inteligente en la App

La aplicación móvil incorpora una funcionalidad de asistencia inteligente orientada al proceso de captura de pedidos. Esta capa no reemplaza la lógica principal del sistema, sino que actúa como un mecanismo de entrada alternativa para convertir frases naturales en acciones reales del pedido.

Desde la perspectiva UX/UI, esta integración se representa mediante:

- Un botón dedicado para “Agregar por voz”.
- Un modal de interpretación del pedido.
- Una vista previa del resultado detectado.
- Un proceso de confirmación antes de ejecutar la acción real.

Desde la perspectiva técnica, la IA o lógica inteligente se apoya en:

- El catálogo real recibido desde backend.
- Las opciones activas del menú corriente y desayuno.
- La comparación semántica entre lo dicho por el usuario y los productos configurados.
- La ejecución final sobre las mismas rutas REST ya existentes.

De esta manera, la experiencia inteligente se mantiene alineada con la arquitectura del sistema y no rompe la coherencia entre frontend y backend.

---

# Catálogo de Funcionalidades (16 Funciones)

## Función 1. Inicio de sesión

**Pantalla Expo:** `app/login`  
**Ruta backend relacionada:** `POST /api/auth/` y `GET /api/me/`

**Descripción funcional:**  
Permite que el usuario autenticado acceda al sistema móvil mediante credenciales válidas. La interfaz valida usuario y contraseña, muestra mensajes visuales de error y redirecciona al módulo principal cuando la autenticación es correcta.

**Comportamiento esperado:**  
Si las credenciales son correctas, el sistema guarda la sesión y permite el acceso. Si las credenciales son inválidas, el formulario resalta el error y muestra un mensaje dentro de la misma interfaz.

**Espacio para captura:**  
`[Insertar aquí imagen de la pantalla de login]`

---

## Función 2. Cierre de sesión

**Pantalla Expo:** botón global en layout principal  
**Ruta backend relacionada:** control local de sesión y redirección a `/login`

**Descripción funcional:**  
Permite salir del sistema desde cualquier pantalla autenticada, usando el botón de funcionalidades global.

**Comportamiento esperado:**  
Al cerrar sesión, se elimina el acceso del usuario y la aplicación regresa inmediatamente a la pantalla de inicio de sesión.

**Espacio para captura:**  
`[Insertar aquí imagen de cierre de sesión desde el botón global]`

---

## Función 3. Navegación global mediante botón de funcionalidades

**Pantalla Expo:** layout global  
**Ruta backend relacionada:** no aplica directamente; navegación interna

**Descripción funcional:**  
La aplicación incluye un botón flotante global que permite acceder a acciones rápidas como volver, ir a pedidos y cerrar sesión.

**Comportamiento esperado:**  
El usuario puede abrir el menú flotante desde cualquier pantalla autenticada y ejecutar las acciones disponibles sin interrumpir el flujo operativo.

**Espacio para captura:**  
`[Insertar aquí imagen del botón flotante y sus opciones]`

---

## Función 4. Reubicación del botón flotante

**Pantalla Expo:** layout global  
**Ruta backend relacionada:** no aplica

**Descripción funcional:**  
El botón flotante puede moverse por la pantalla para mejorar la comodidad del usuario y evitar que tape contenido importante.

**Comportamiento esperado:**  
El usuario arrastra el botón a la posición que prefiera y continúa usándolo normalmente.

**Espacio para captura:**  
`[Insertar aquí imagen del botón flotante en posición personalizada]`

---

## Función 5. Visualización de pedidos activos

**Pantalla Expo:** `app/pedidos`  
**Ruta backend relacionada:** `GET /api/pedidos/?archivado=0`

**Descripción funcional:**  
Permite ver la lista de pedidos activos del restaurante, mostrando mesa, estado, mesero, hora y total.

**Comportamiento esperado:**  
La pantalla debe listar los pedidos vigentes, mostrar cuántos se encuentran activos y reflejar cambios cuando se agregan productos o se modifica el estado del pedido.

**Espacio para captura:**  
`[Insertar aquí imagen del listado de pedidos]`

---

## Función 6. Creación de pedido por mesa

**Pantalla Expo:** modal de creación desde `app/pedidos`  
**Ruta backend relacionada:** `GET /api/mesas/?disponibles=1` y `POST /api/pedidos/abrir/`

**Descripción funcional:**  
Permite abrir un nuevo pedido seleccionando una mesa disponible.

**Comportamiento esperado:**  
El sistema consulta las mesas libres, permite seleccionar una y crea el pedido asociado si la caja está abierta y la mesa está disponible.

**Espacio para captura:**  
`[Insertar aquí imagen del modal de selección de mesa]`

---

## Función 7. Centro de notificaciones operativas

**Pantalla Expo:** `app/notificaciones` y banner superior en `app/pedidos`  
**Ruta backend relacionada:** `GET /api/usuarios/notificaciones/`, `POST /api/usuarios/notificaciones/{id}/marcar-leida/` y `POST /api/usuarios/notificaciones/marcar-todas-leidas/`

**Descripción funcional:**  
Permite visualizar avisos operativos del sistema, diferenciar notificaciones leídas/no leídas, abrir la notificación para ir al pedido relacionado y marcar una o todas como leídas.

**Comportamiento esperado:**  
La interfaz debe mostrar notificaciones recientes en tiempo de operación, permitir su gestión de lectura y mejorar el tiempo de respuesta del personal ante cambios del servicio.

**Espacio para captura:**  
`[Insertar aquí imagen de la pantalla de notificaciones y del banner superior en pedidos]`

---

## Función 8. Refresco manual y automático de pedidos

**Pantalla Expo:** `app/pedidos`  
**Ruta backend relacionada:** `GET /api/pedidos/`

**Descripción funcional:**  
La pantalla se refresca manualmente al deslizar o automáticamente cada cierto tiempo para mantener la información actualizada.

**Comportamiento esperado:**  
Los cambios realizados desde móvil o web deben reflejarse en la pantalla de pedidos sin necesidad de cerrar y abrir la app.

**Espacio para captura:**  
`[Insertar aquí imagen del refresco de pedidos]`

---

## Función 9. Visualización del detalle del pedido

**Pantalla Expo:** `app/detalle`  
**Ruta backend relacionada:** `GET /api/pedidos/{id}/`

**Descripción funcional:**  
Permite consultar la información detallada de un pedido, incluyendo productos, cantidades, precios, subtotal y total.

**Comportamiento esperado:**  
La pantalla debe mostrar el estado del pedido, los datos de la mesa, el mesero y todos los detalles asociados a la orden.

**Espacio para captura:**  
`[Insertar aquí imagen del detalle del pedido]`

---

## Función 10. Agregar producto normal al pedido

**Pantalla Expo:** modal `Agregar al pedido`  
**Ruta backend relacionada:** `POST /api/pedidos/{id}/agregar-detalle/`

**Descripción funcional:**  
Permite agregar productos unitarios o regulares desde el catálogo del pedido.

**Comportamiento esperado:**  
El usuario selecciona producto, cantidad y observaciones, y el sistema actualiza el detalle y el total del pedido.

**Espacio para captura:**  
`[Insertar aquí imagen del modal para agregar producto normal]`

---

## Función 11. Agregar menú corriente

**Pantalla Expo:** pestaña “Corriente” dentro del modal de agregar  
**Ruta backend relacionada:** `POST /api/pedidos/{id}/agregar-corriente/`

**Descripción funcional:**  
Permite agregar un menú corriente usando opciones del menú del día como sopa, principio, proteína y acompañante.

**Comportamiento esperado:**  
El sistema debe construir el pedido con base en las opciones seleccionadas y calcular correctamente el precio según la presencia de sopa o bandeja.

**Espacio para captura:**  
`[Insertar aquí imagen del flujo de agregar corriente]`

---

## Función 12. Agregar menú desayuno

**Pantalla Expo:** pestaña “Desayuno” dentro del modal de agregar  
**Ruta backend relacionada:** `POST /api/pedidos/{id}/agregar-desayuno/`

**Descripción funcional:**  
Permite registrar un desayuno usando principal, bebida y acompañante según el menú configurado.

**Comportamiento esperado:**  
La interfaz debe permitir construir el desayuno y enviarlo al backend manteniendo coherencia con el menú del día.

**Espacio para captura:**  
`[Insertar aquí imagen del flujo de agregar desayuno]`

---

## Función 13. Editar pedido general

**Pantalla Expo:** modal de edición de pedido  
**Ruta backend relacionada:** `PATCH /api/pedidos/{id}/`

**Descripción funcional:**  
Permite modificar el estado del pedido y las observaciones generales.

**Comportamiento esperado:**  
El usuario puede actualizar la información general del pedido siempre que este no esté pagado.

**Espacio para captura:**  
`[Insertar aquí imagen del modal editar pedido]`

---

## Función 14. Editar detalle o producto del pedido

**Pantalla Expo:** modal de edición de detalle  
**Ruta backend relacionada:** `PATCH /api/pedidos/detalles/{id}/`

**Descripción funcional:**  
Permite modificar cantidad, observaciones o el producto asociado a un detalle específico.

**Comportamiento esperado:**  
La interfaz debe actualizar el detalle, recalcular la información y reflejar el cambio de forma inmediata.

**Espacio para captura:**  
`[Insertar aquí imagen del modal editar detalle]`

---

## Función 15. Eliminar producto del pedido

**Pantalla Expo:** tarjeta del detalle del pedido  
**Ruta backend relacionada:** `DELETE /api/pedidos/detalles/{id}/`

**Descripción funcional:**  
Permite eliminar un producto del pedido mediante una confirmación visual personalizada.

**Comportamiento esperado:**  
El sistema elimina el detalle si el pedido no está pagado y bloquea la acción si la orden ya fue facturada.

**Espacio para captura:**  
`[Insertar aquí imagen del modal eliminar producto]`

---

## Función 16. Asistente de captura de pedido por voz

**Pantalla Expo:** modal de asistente por voz desde `app/detalle`  
**Ruta backend relacionada:** `POST /api/pedidos/{id}/agregar-detalle/`, `POST /api/pedidos/{id}/agregar-corriente/` y `POST /api/pedidos/{id}/agregar-desayuno/`

**Descripción funcional:**  
Permite interpretar una frase escrita o capturada por voz para convertirla en acciones reales del pedido, reutilizando el mismo flujo normal del sistema.

**Comportamiento esperado:**  
El sistema interpreta la frase, muestra una vista previa del pedido detectado y, tras confirmación del usuario, agrega productos, corrientes o desayunos al pedido real.

**Espacio para captura:**  
`[Insertar aquí imagen del asistente de pedido por voz]`

---

## Coherencia entre Frontend Móvil y Backend

El diseño de interfaces se encuentra directamente vinculado a la API del proyecto. Esto garantiza que cada pantalla tenga correspondencia con una operación real del sistema. Algunos ejemplos de coherencia implementada son:

- Login conectado con autenticación por token.
- Listado de pedidos conectado al endpoint de pedidos activos.
- Creación de pedidos vinculada a mesas disponibles.
- Detalle sincronizado con información del pedido en backend.
- Agregado de corrientes y desayunos conectado al menú del día.
- Restricción visual y funcional cuando el pedido se encuentra pagado.

Esta coherencia asegura que la app móvil no sea un prototipo aislado, sino una interfaz funcional sobre el sistema backend real.

Adicionalmente, el módulo de asistencia por voz o interpretación inteligente no crea rutas paralelas para registrar pedidos, sino que reutiliza las rutas ya existentes de detalle, corriente y desayuno. Esto fortalece la consistencia del sistema y garantiza que toda acción inteligente siga siendo trazable dentro del backend principal.

---

## Evidencia Visual Requerida

Para la entrega final se recomienda insertar, al menos, las siguientes capturas:

- Pantalla de login.
- Pantalla principal de pedidos.
- Modal de creación de pedido.
- Pantalla de detalle del pedido.
- Modal para agregar producto.
- Modal para agregar corriente.
- Modal para agregar desayuno.
- Modal de edición de pedido.
- Modal de edición de detalle.
- Modal de confirmación de eliminación.
- Ejemplo de restricción visual por pedido pagado.
- Ejemplo del botón global de funcionalidades.
- Ejemplo del asistente por voz.

---

## Conclusiones

El diseño UX/UI de la aplicación móvil desarrollada con Expo responde directamente a las necesidades operativas del restaurante y se integra de manera coherente con la lógica de negocio definida en el backend. La solución demuestra control de acceso, sincronización con servicios reales, diferenciación visual de estados y una estructura modular que facilita su mantenimiento y crecimiento.

El sistema no solo presenta interfaces visualmente funcionales, sino que traduce el proceso operativo del restaurante a una experiencia móvil clara, consistente y eficiente. La incorporación de funciones como el pedido por voz, la edición de pedidos y el control de bloqueo para pedidos pagados fortalece el valor práctico de la aplicación y evidencia una solución alineada con un entorno real de uso.

---

## Referencias

Apple. (s. f.). *Human Interface Guidelines*. https://developer.apple.com/design/human-interface-guidelines/

Google. (s. f.). *Material Design 3*. https://m3.material.io/

Expo. (s. f.). *Expo documentation*. https://docs.expo.dev/

Django Software Foundation. (s. f.). *Django documentation*. https://docs.djangoproject.com/

---

## Anexos

### Anexo A. Capturas del sistema Expo

`[Insertar aquí las imágenes finales organizadas por función]`

### Anexo B. Rutas principales consumidas por la app

- `POST /api/auth/`
- `GET /api/me/`
- `GET /api/usuarios/me/`
- `GET /api/pedidos/`
- `POST /api/pedidos/abrir/`
- `GET /api/pedidos/{id}/`
- `PATCH /api/pedidos/{id}/`
- `DELETE /api/pedidos/{id}/`
- `GET /api/pedidos/{id}/catalogo/`
- `GET /api/pedidos/{id}/menu-dia/`
- `POST /api/pedidos/{id}/agregar-detalle/`
- `POST /api/pedidos/{id}/agregar-corriente/`
- `POST /api/pedidos/{id}/agregar-desayuno/`
- `GET /api/pedidos/detalles/?pedido={id}`
- `PATCH /api/pedidos/detalles/{id}/`
- `DELETE /api/pedidos/detalles/{id}/`
- `POST /api/pedidos/detalles/{id}/marcar-servido/`
- `GET /api/mesas/`
- `GET /api/menu-dia/`
- `GET /api/menu/categorias/`
- `GET /api/menu/productos/`
- `GET /api/menu/recetas/`
- `GET /api/menu/recetas-ingredientes/`
- `GET /api/menu/opciones-consumo/`
- `GET /api/caja/sesion/activa/`
- `GET /api/caja/sesiones/`
- `GET /api/caja/facturas/`
- `GET /api/caja/movimientos/`
- `GET /api/inventario/ingredientes/`
- `GET /api/inventario/movimientos/`
- `GET /api/contactos/proveedores/`
- `GET /api/contactos/telefonos/`
- `GET /api/ajustes/empleados/`
- `GET /api/ajustes/roles/`
- `GET /api/restaurantes/`
- `GET /api/usuarios/notificaciones/`
- `GET /api/estadisticas/resumen/`
- `GET /api/resumen-mensual/`

### Anexo C. Relación entre IA y servicios REST

El módulo de asistencia inteligente no posee una ruta REST independiente en el backend para “pedido por voz”. En su lugar, la aplicación implementa la lógica de interpretación del lado móvil y luego reutiliza las rutas principales del sistema:

- Si el pedido detectado corresponde a un producto normal: `POST /api/pedidos/{id}/agregar-detalle/`
- Si corresponde a menú corriente: `POST /api/pedidos/{id}/agregar-corriente/`
- Si corresponde a menú desayuno: `POST /api/pedidos/{id}/agregar-desayuno/`

Esto significa que la funcionalidad de IA se comporta como una capa de apoyo a la experiencia del usuario, manteniendo intacto el modelo operativo central del backend.
