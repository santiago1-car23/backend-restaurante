# Documento De Implementacion Del Backend

## Portada

**Institucion:** PENDIENTE_AGREGAR_NOMBRE_INSTITUCION  
**Programa:** Ingenieria De Software  
**Asignatura:** PENDIENTE_AGREGAR_ASIGNATURA  
**Actividad:** Implementacion Del Backend Del Proyecto De Generacion De Conocimiento  
**Proyecto:** RestauranteDJ  
**Integrantes:** PENDIENTE_AGREGAR_INTEGRANTES  
**Docente:** PENDIENTE_AGREGAR_NOMBRE_DOCENTE  
**Fecha:** PENDIENTE_AGREGAR_FECHA_DE_ENTREGA  

---

## Introduccion

El desarrollo de un backend funcional constituye una etapa esencial dentro de la construccion de productos de software modernos, ya que permite gestionar la logica del sistema, garantizar la persistencia de la informacion y establecer la comunicacion entre la base de datos, la interfaz y los servicios externos. En este contexto, el proyecto RestauranteDJ aborda la necesidad de digitalizar y optimizar los procesos operativos de un restaurante, integrando modulos para la administracion de mesas, pedidos, menu, inventario, caja, contactos y usuarios.

El presente documento expone la implementacion del backend del proyecto, desarrollado en Python mediante Django y Django REST Framework, evidenciando la aplicacion de conceptos de arquitectura de software, bases de datos relacionales, servicios REST, documentacion OpenAPI y manejo de respuestas HTTP. Asimismo, se presentan las rutas CRUD construidas, la organizacion general del sistema y los mecanismos de prueba utilizados para validar su funcionamiento.

## Objetivos

### Objetivo General

Desarrollar y documentar un backend funcional para el proyecto RestauranteDJ, implementado en Python, que exponga servicios RESTful para la gestion de la informacion del sistema, integrados con una base de datos relacional coherente con la problematica propuesta.

### Objetivos Especificos

- Describir la arquitectura de software implementada en el backend del proyecto.
- Identificar el framework de Python seleccionado y justificar su uso.
- Presentar el modelo de base de datos y su coherencia con el sistema de restaurante.
- Evidenciar la implementacion de rutas CRUD para los recursos principales del proyecto.
- Mostrar el uso adecuado de metodos HTTP y codigos de estado en las respuestas del backend.
- Documentar el funcionamiento de la API mediante Swagger/OpenAPI como evidencia de prueba.

---

## 1. Presentacion General

El presente documento describe la implementacion del backend del proyecto RestauranteDJ, desarrollado como parte del Proyecto de Generacion de Conocimiento del programa de Ingenieria de Software. El backend constituye el componente principal para la gestion de la informacion del sistema, permitiendo administrar mesas, pedidos, menu, caja, inventario, contactos y usuarios a traves de servicios web RESTful.

El proyecto fue desarrollado exclusivamente en Python usando Django como framework principal y Django REST Framework como capa para la exposicion de servicios REST. Adicionalmente, se incorporo documentacion interactiva con Swagger/OpenAPI mediante drf-yasg, lo que permite evidenciar el funcionamiento del backend y realizar pruebas directamente sobre los endpoints implementados.

La solucion construida responde a la necesidad de un sistema de restaurante con operaciones administrativas y operativas centralizadas, donde los diferentes roles del negocio puedan registrar, consultar, actualizar y eliminar informacion de manera controlada.

## 2. Descripcion General Del Backend

### 2.1 Arquitectura De Software Utilizada

El software utiliza una arquitectura modular basada en Django, organizada por aplicaciones funcionales. Cada modulo representa un dominio del negocio:

- Core: configuracion general y dashboard.
- Usuarios: autenticacion, roles y empleados.
- Menu: categorias, productos y menu diario.
- Mesas: gestion de disponibilidad y estados.
- Pedidos: ordenes y detalle de consumo.
- Caja: facturacion, sesiones de caja y movimientos operativos.
- Inventario: ingredientes y movimientos de inventario.
- Contactos: proveedores y telefonos del negocio.

La aplicacion sigue un estilo MVC propio de Django, donde:

- Los modelos representan la estructura de datos y relaciones.
- Las vistas controlan la logica de presentacion y respuesta.
- Las plantillas renderizan la interfaz HTML.
- Las vistas API exponen servicios JSON a traves de DRF.

### 2.2 Rol Del Backend En La Arquitectura General

El backend cumple las siguientes funciones dentro del sistema:

- Gestionar la logica de negocio del restaurante.
- Controlar el acceso y autenticacion de usuarios.
- Administrar la persistencia y consulta de la informacion.
- Exponer endpoints REST para integraciones y pruebas.
- Retornar respuestas HTTP estructuradas y documentadas.

En la arquitectura general del sistema, el backend es el componente encargado de centralizar reglas de negocio, validaciones, acceso a base de datos y comunicacion con el frontend web y las herramientas de prueba como Swagger.

### 2.3 Framework De Python Seleccionado Y Justificacion

El framework utilizado es Django, complementado con Django REST Framework.

La eleccion de Django se justifica por:

- Rapidez de desarrollo para sistemas empresariales.
- Integracion nativa con ORM y manejo de base de datos.
- Sistema robusto de autenticacion y administracion.
- Buena organizacion por apps modulares.
- Facilidad para combinar vistas HTML tradicionales con servicios API.

La eleccion de Django REST Framework se justifica por:

- Facilitar la construccion de APIs REST sobre Django.
- Manejo estandarizado de metodos HTTP y respuestas JSON.
- Integracion directa con autenticacion, permisos y validaciones.
- Compatibilidad con Swagger/OpenAPI.

### 2.4 Tipo De Arquitectura Implementada

El backend implementa una arquitectura tipo API REST sobre HTTP. Las operaciones principales se exponen mediante endpoints que usan metodos GET, POST, PUT y DELETE, devolviendo respuestas en formato JSON con codigos de estado HTTP apropiados.

Ademas del enfoque REST, el sistema conserva vistas HTML para la operacion diaria del software, por lo que la arquitectura puede describirse como una solucion web hibrida: interfaz web con backend Django y capa API REST para consumo y pruebas.

## 3. Modelo De Base De Datos

### 3.1 Diseno Logico De La Base De Datos

El backend se conecta a una base de datos relacional gestionada a traves del ORM de Django. En entorno local se encuentra configurada con SQLite, segun la configuracion actual del proyecto.

Las tablas principales identificadas en el proyecto son:

- Restaurante
- Rol
- Empleado
- Notificacion
- Categoria
- Producto
- MenuDiario
- Mesa
- Pedido
- DetallePedido
- CajaSesion
- Factura
- MovimientoCaja
- Ingrediente
- MovimientoInventario
- Proveedor
- TelefonoNegocio

Adicionalmente, el proyecto utiliza tablas propias del sistema de autenticacion y administracion de Django, necesarias para el inicio de sesion, manejo de permisos y control de sesiones. Entre las mas relevantes se encuentran:

- User (`auth_user`): tabla base de usuarios utilizada para autenticacion.
- Group (`auth_group`): agrupacion de permisos por roles administrativos de Django.
- Permission (`auth_permission`): permisos internos del framework.
- ContentType (`django_content_type`): soporte para relacionar permisos con modelos.
- Session (`django_session`): almacenamiento de sesiones de usuarios autenticados.
- LogEntry (`django_admin_log`): registro de acciones realizadas desde el panel administrativo.

Por lo tanto, el modelo de base de datos del proyecto no solo contempla las tablas funcionales del sistema de restaurante, sino tambien las tablas estructurales de Django requeridas para el proceso de autenticacion, autorizacion y administracion del sistema.

### 3.2 Relaciones Principales Entre Tablas

- Restaurante se relaciona con mesas, productos, categorias, menues, pedidos, ingredientes, proveedores y telefonos.
- Rol se relaciona con Empleado.
- Empleado se relaciona con User y con Restaurante.
- Pedido se relaciona con Mesa, User y Restaurante.
- DetallePedido se relaciona con Pedido y Producto.
- Factura se relaciona con Pedido y CajaSesion.
- MovimientoCaja se relaciona con CajaSesion.
- MovimientoInventario se relaciona con Ingrediente y User.
- Producto se relaciona con Categoria.
- Proveedor y TelefonoNegocio se relacionan con Restaurante.

### 3.3 Normalizacion

La base de datos presenta una estructura relacional adecuada y separa las entidades principales del negocio, lo cual evidencia una normalizacion funcional. Se identifican correctamente claves primarias, claves foraneas y relaciones coherentes entre los modulos del sistema.

Sin embargo, desde un analisis estricto, la base no esta completamente normalizada al maximo nivel teorico, debido a algunos campos multivalor o derivados, por ejemplo:

- MenuDiario almacena algunas listas en campos de texto.
- Proveedor contiene telefono y telefono_secundario en la misma tabla.
- Pedido.total es un dato derivado del detalle del pedido.

Por lo tanto, puede afirmarse que la base de datos se encuentra mayormente normalizada y es coherente con la problematica del proyecto, aunque aun existen oportunidades de mejora para una normalizacion mas estricta.

### 3.4 Coherencia Con La Problematica Del Proyecto

El modelo de datos responde directamente a la operacion de un restaurante, ya que permite:

- Controlar las mesas y su estado.
- Registrar pedidos y sus productos asociados.
- Administrar caja y facturacion.
- Gestionar inventario e insumos.
- Organizar personal por roles.
- Mantener informacion de proveedores y telefonos del negocio.

## 4. Implementacion De Rutas CRUD

### 4.1 Rutas CRUD Implementadas En La API

Actualmente el backend expone rutas CRUD REST para las tablas operativas principales del sistema. Las rutas identificadas son las siguientes:

| Modulo | Recurso | Ruta | Metodo HTTP | Operacion CRUD | Descripcion funcional |
|---|---|---|---|---|---|
| Mesas | Mesa | `/mesas/api/mesas/` | GET | Read | Ruta para consultar las mesas registradas |
| Mesas | Mesa | `/mesas/api/mesas/` | POST | Create | Ruta para registrar una nueva mesa |
| Mesas | Mesa | `/mesas/api/mesas/{mesa_id}/` | GET | Read | Ruta para consultar una mesa especifica |
| Mesas | Mesa | `/mesas/api/mesas/{mesa_id}/` | PUT | Update | Ruta para actualizar una mesa |
| Mesas | Mesa | `/mesas/api/mesas/{mesa_id}/` | DELETE | Delete | Ruta para eliminar una mesa |
| Pedidos | Pedido | `/pedidos/api/ordenes/` | GET | Read | Ruta para consultar los pedidos activos |
| Pedidos | Pedido | `/pedidos/api/ordenes/` | POST | Create | Ruta para registrar un pedido |
| Pedidos | Pedido | `/pedidos/api/ordenes/{orden_id}/` | GET | Read | Ruta para consultar un pedido especifico |
| Pedidos | Pedido | `/pedidos/api/ordenes/{orden_id}/` | PUT | Update | Ruta para actualizar un pedido |
| Pedidos | Pedido | `/pedidos/api/ordenes/{orden_id}/` | DELETE | Delete | Ruta para eliminar un pedido |
| Menu | Categoria | `/menu/api/categorias/` | GET | Read | Ruta para consultar categorias del menu |
| Menu | Categoria | `/menu/api/categorias/` | POST | Create | Ruta para crear una categoria |
| Menu | Categoria | `/menu/api/categorias/{categoria_id}/` | PUT | Update | Ruta para actualizar una categoria |
| Menu | Categoria | `/menu/api/categorias/{categoria_id}/` | DELETE | Delete | Ruta para eliminar una categoria |
| Menu | Producto | `/menu/api/productos/` | GET | Read | Ruta para consultar productos |
| Menu | Producto | `/menu/api/productos/` | POST | Create | Ruta para crear un producto |
| Menu | Producto | `/menu/api/productos/{producto_id}/` | PUT | Update | Ruta para actualizar un producto |
| Menu | Producto | `/menu/api/productos/{producto_id}/` | DELETE | Delete | Ruta para eliminar un producto |
| Menu | MenuDiario | `/menu/api/menus-diarios/` | GET | Read | Ruta para consultar el menu diario |
| Menu | MenuDiario | `/menu/api/menus-diarios/` | POST | Create | Ruta para crear menu diario |
| Menu | MenuDiario | `/menu/api/menus-diarios/{menu_id}/` | PUT | Update | Ruta para actualizar menu diario |
| Menu | MenuDiario | `/menu/api/menus-diarios/{menu_id}/` | DELETE | Delete | Ruta para eliminar menu diario |
| Inventario | Ingrediente | `/inventario/api/ingredientes/` | GET | Read | Ruta para consultar ingredientes |
| Inventario | Ingrediente | `/inventario/api/ingredientes/` | POST | Create | Ruta para crear ingredientes |
| Inventario | Ingrediente | `/inventario/api/ingredientes/{ingrediente_id}/` | PUT | Update | Ruta para actualizar ingredientes |
| Inventario | Ingrediente | `/inventario/api/ingredientes/{ingrediente_id}/` | DELETE | Delete | Ruta para eliminar ingredientes |
| Inventario | MovimientoInventario | `/inventario/api/movimientos/` | GET | Read | Ruta para consultar movimientos de inventario |
| Inventario | MovimientoInventario | `/inventario/api/movimientos/` | POST | Create | Ruta para registrar movimiento de inventario |
| Inventario | MovimientoInventario | `/inventario/api/movimientos/{movimiento_id}/` | PUT | Update | Ruta para actualizar movimiento de inventario |
| Inventario | MovimientoInventario | `/inventario/api/movimientos/{movimiento_id}/` | DELETE | Delete | Ruta para eliminar movimiento de inventario |
| Caja | CajaSesion | `/caja/api/sesiones/` | GET | Read | Ruta para consultar sesiones de caja |
| Caja | CajaSesion | `/caja/api/sesiones/` | POST | Create | Ruta para abrir o registrar una sesion de caja |
| Caja | CajaSesion | `/caja/api/sesiones/{sesion_id}/` | PUT | Update | Ruta para actualizar una sesion de caja |
| Caja | CajaSesion | `/caja/api/sesiones/{sesion_id}/` | DELETE | Delete | Ruta para eliminar una sesion de caja |
| Caja | Factura | `/caja/api/facturas/` | GET | Read | Ruta para consultar facturas |
| Caja | Factura | `/caja/api/facturas/` | POST | Create | Ruta para registrar una factura |
| Caja | Factura | `/caja/api/facturas/{factura_id}/` | PUT | Update | Ruta para actualizar una factura |
| Caja | Factura | `/caja/api/facturas/{factura_id}/` | DELETE | Delete | Ruta para eliminar una factura |
| Usuarios | Empleado | `/usuarios/api/empleados/` | GET | Read | Ruta para consultar empleados |
| Usuarios | Empleado | `/usuarios/api/empleados/` | POST | Create | Ruta para registrar empleados |
| Usuarios | Empleado | `/usuarios/api/empleados/{empleado_id}/` | PUT | Update | Ruta para actualizar empleados |
| Usuarios | Empleado | `/usuarios/api/empleados/{empleado_id}/` | DELETE | Delete | Ruta para eliminar empleados |
| Usuarios | Rol | `/usuarios/api/roles/` | GET | Read | Ruta para consultar roles |
| Usuarios | Rol | `/usuarios/api/roles/` | POST | Create | Ruta para crear roles |
| Usuarios | Rol | `/usuarios/api/roles/{rol_id}/` | PUT | Update | Ruta para actualizar roles |
| Usuarios | Rol | `/usuarios/api/roles/{rol_id}/` | DELETE | Delete | Ruta para eliminar roles |
| Contactos | Proveedor | `/contactos/api/proveedores/` | GET | Read | Ruta para consultar proveedores |
| Contactos | Proveedor | `/contactos/api/proveedores/` | POST | Create | Ruta para registrar proveedores |
| Contactos | Proveedor | `/contactos/api/proveedores/{proveedor_id}/` | PUT | Update | Ruta para actualizar proveedores |
| Contactos | Proveedor | `/contactos/api/proveedores/{proveedor_id}/` | DELETE | Delete | Ruta para eliminar proveedores |
| Contactos | TelefonoNegocio | `/contactos/api/telefonos/` | GET | Read | Ruta para consultar telefonos del negocio |
| Contactos | TelefonoNegocio | `/contactos/api/telefonos/` | POST | Create | Ruta para registrar telefonos del negocio |
| Contactos | TelefonoNegocio | `/contactos/api/telefonos/{telefono_id}/` | PUT | Update | Ruta para actualizar telefonos del negocio |
| Contactos | TelefonoNegocio | `/contactos/api/telefonos/{telefono_id}/` | DELETE | Delete | Ruta para eliminar telefonos del negocio |

### 4.2 Estado Actual Del Alcance CRUD

El backend ya implementa CRUD completo para las tablas operativas principales del proyecto. No obstante, existen algunas tablas del modelo general que aun no cuentan con endpoints REST especificos dedicados, entre ellas:

- Restaurante
- DetallePedido
- MovimientoCaja
- Notificacion

Estas tablas hacen parte del modelo de datos, pero actualmente su manipulacion se realiza desde logica interna del sistema o desde otros modulos relacionados. Para un cumplimiento total y estricto de la actividad, seria recomendable exponer tambien sus rutas CRUD de forma explicita.

## 5. Manejo De Respuestas HTTP Y Errores

El backend demuestra el uso de respuestas HTTP adecuadas conforme a la operacion ejecutada.

### 5.1 Codigos De Exito Utilizados

- 200 OK: usado para consultas y actualizaciones exitosas.
- 201 Created: usado para creacion exitosa de recursos.
- 204 No Content: usado para eliminaciones sin contenido de respuesta.

### 5.2 Manejo De Errores

El proyecto incorpora manejo basico de errores y validaciones, por ejemplo:

- 400 Bad Request: cuando faltan datos requeridos o existen validaciones de negocio.
- 403 Forbidden: cuando un usuario intenta acceder a recursos de otro restaurante o sin permiso.
- 404 Not Found: cuando el recurso solicitado no existe.
- 500 Internal Server Error: error no deseado que se ha venido corrigiendo durante las pruebas.

### 5.3 Formato De Respuesta

Las respuestas de la API se entregan en formato JSON, con estructuras comprensibles para el consumidor del servicio. Ejemplos:

```json
{
  "mesas": [
    {
      "id": 1,
      "numero": 5,
      "capacidad": 4,
      "estado": "libre",
      "estado_display": "Libre"
    }
  ]
}
```

```json
{
  "error": "La mesa #5 ya existe para este restaurante."
}
```

## 6. Pruebas Del Backend

### 6.1 Herramienta De Evidencia Utilizada

La principal evidencia de funcionamiento del backend se encuentra en Swagger/OpenAPI, accesible desde las rutas:

- `http://127.0.0.1:8000/swagger/`
- `http://127.0.0.1:8000/redoc/`

Swagger permite:

- Consultar los endpoints disponibles.
- Ejecutar peticiones GET, POST, PUT y DELETE.
- Ver los codigos de estado retornados.
- Comprobar la estructura JSON de las respuestas.

### 6.2 Evidencias De Funcionamiento Observadas En El Proyecto

Durante el desarrollo y validacion del backend se comprobaron los siguientes escenarios:

- Peticiones exitosas sobre endpoints de lectura con codigo 200.
- Creacion de recursos via POST con codigo 201.
- Actualizacion de registros via PUT con codigo 200.
- Eliminacion de registros via DELETE con codigo 204.
- Casos de error controlado, por ejemplo validaciones de duplicado en mesas y validacion de campos obligatorios.

### 6.3 Caso De Error Controlado

Un caso representativo corregido en el proyecto fue la gestion de mesas duplicadas. Inicialmente, al crear una mesa repetida se presentaba un IntegrityError por restriccion unica de base de datos. Posteriormente se implemento validacion previa y manejo controlado del error, devolviendo una respuesta o mensaje comprensible en lugar de dejar fallar el sistema.

Este caso evidencia que el backend no solo responde a operaciones exitosas, sino que tambien incorpora validaciones y control de errores de forma progresiva.

## 7. Conclusiones

El backend de RestauranteDJ cumple con los lineamientos fundamentales de la actividad, al estar desarrollado en Python, usar un framework valido, conectarse a una base de datos relacional, exponer servicios RESTful, documentarse con Swagger/OpenAPI y manejar codigos de estado HTTP acordes a las operaciones realizadas.

Desde la perspectiva tecnica, el proyecto presenta una base funcional solida, con modulos claramente identificados y una API REST operativa para los recursos principales del sistema. Asimismo, se identifican oportunidades de mejora en dos frentes:

- Exponer CRUD completo para todas las tablas restantes del modelo de datos.
- Reducir la concentracion de logica en las vistas, migrando progresivamente hacia una arquitectura mas profesional basada en servicios, serializadores y separacion entre vistas web y vistas API.

En conclusion, el backend implementado es coherente con la problematica del proyecto y evidencia un avance significativo en la construccion de un producto de software real para el sector restaurantero.

## 8. Producto A Entregar

### 8.1 Repositorio Del Proyecto

- URL del repositorio GitHub: `PENDIENTE_AGREGAR_URL_REPOSITORIO`

### 8.2 Video De Sustentacion O Evidencia

- URL del video: `PENDIENTE_AGREGAR_URL_VIDEO`

### 8.3 Evidencia De Commits

El proyecto se encuentra versionado en GitHub y debe presentarse con el historial de commits que evidencie el avance del desarrollo del backend, incluyendo:

- configuracion del framework,
- conexion a la base de datos,
- implementacion de modelos,
- construccion de endpoints,
- integracion de Swagger,
- pruebas y correccion de errores.

## 9. Recomendacion Final Para La Entrega

Antes de entregar el documento final se recomienda completar:

1. La URL real del repositorio de GitHub.
2. La URL del video de presentacion.
3. Capturas o anexos visuales de Swagger mostrando pruebas exitosas y un caso de error controlado.
4. Si el docente exige cobertura total por tabla, completar endpoints REST para Restaurante, DetallePedido, MovimientoCaja y Notificacion.
