# 📋 Sistema de Gestión de Restaurante - Documentación Completa

## 🎯 Descripción General

**RestauranteDJ** es una aplicación web completa desarrollada con **Django** para la gestión integral de restaurantes. El sistema está diseñado para optimizar operaciones diarias incluyendo toma de órdenes, seguimiento de pedidos, gestión de mesas, control de caja, inventario y estadísticas.

### Objetivos Principales
- ✅ Facilitar la toma de pedidos por meseros
- ✅ Automatizar el control de mesas (libre/ocupada/reservada)
- ✅ Integrar un sistema de caja con apertura/cierre de sesiones
- ✅ Gestionar inventario de ingredientes
- ✅ Proporcionar reportes y estadísticas de ventas
- ✅ Administrar usuarios con roles específicos (Admin, Mesero, Cajero, Cocinero)
- ✅ Mantener control de proveedores y contactos

---

## 🏗️ Arquitectura y Tecnología

### Stack Tecnológico
- **Backend**: Django 4.2+
- **Base de Datos**: MySQL
- **Frontend**: HTML5, JavaScript (Vanilla)
- **Python**: 3.9+
- **Cliente MySQL**: mysqlclient 2.2+

### Estructura del Proyecto
```
restauranteDJ/
├── restaurante/              # Configuración global del proyecto
│   ├── settings.py          # Configuración de Django
│   ├── urls.py              # URLs principales
│   ├── wsgi.py              # WSGI para producción
│   └── asgi.py              # ASGI para WebSockets (futuro)
│
├── apps/                    # Aplicaciones modulares
│   ├── core/                # App base y templatetags
│   ├── usuarios/            # Autenticación y roles
│   ├── menu/                # Gestión de menú y productos
│   ├── mesas/               # Control de mesas
│   ├── pedidos/             # Órdenes y detalles
│   ├── caja/                # Sesiones de caja y facturas
│   ├── inventario/          # Stock e ingredientes
│   ├── contactos/           # Proveedores y teléfonos
│   ├── estadisticas/        # Reportes y análisis
│   └── ajustes/             # Configuraciones del sistema
│
├── templates/               # Plantillas HTML globales
├── static/                  # CSS, JS, imágenes
├── db.sqlite3               # Base de datos (desarrollo)
├── restaurante_db.sql       # Dump de la BD
└── manage.py                # Herramienta de gestión Django

```

---

## 📱 Aplicaciones Principales

### 1️⃣ **CORE** - Núcleo del Sistema
Proporciona funcionalidad base, modelos globales y utilidades compartidas.

#### Modelos
- **Restaurante**: Contiene datos de cada restaurante (permite multi-tenant)
  - `nombre`: Nombre del establecimiento
  - `nit`: NIT para facturación
  - `codigo_cliente`: ID único del restaurante
  - `fecha_inicio`, `fecha_fin_licencia`: Control de licencia

#### Características
- Dashboard inicial
- Plantillas base (base.html, navbar, sidebar)
- Service Worker para PWA
- TemplatesTags personalizados

---

### 2️⃣ **USUARIOS** - Gestión de Personal
Control de autenticación, roles y empleados.

#### Modelos

**Rol**
- Tipos: Admin, Mesero, Cajero, Cocinero
- Define permisos y responsabilidades

**Empleado**
- Extiende `django.contrib.auth.User`
- Datos: teléfono, dirección, horarios, fecha de contratación
- Vinculado a un `Rol` específico
- Auto-promoción a staff/superuser si es Admin

**Notificación**
- Mensajes para usuarios (ej: pedidos listos)
- Control de lectura
- Timestamps automáticos

#### Funcionalidades
- 🔐 Login/Logout seguro
- 👤 Perfil de usuario
- 📋 Registro de empleados
- 🔔 Sistema de notificaciones

---

### 3️⃣ **MENU** - Productos y Menú
Gestión del catálogo de productos y menú del día.

#### Modelos

**Categoría**
- Agrupa productos (Bebidas, Entradas, Platos Fuertes, etc.)
- Única por restaurante
- Control de activación

**Producto**
- Información: nombre, descripción, precio, imagen
- `tiempo_preparacion`: Tiempo estimado en minutos
- Control de disponibilidad
- Vinculado a `Categoría`

**MenuDiario**
- Menú especial para cada día
- Estructura de comida completa:
  - Sopa, caldos, principios, proteínas, acompañante
  - Limonada
  - Precios diferenciados (sopa, bandeja, completo)
- Desayuno del día con sus opciones
- Único por restaurante y fecha

#### Funcionalidades
- 📝 CRUD de productos
- 🍽️ Menú diario con precios
- 📸 Imágenes de platos
- ✓ Control de disponibilidad en tiempo real

---

### 4️⃣ **MESAS** - Control de Localización
Administración de mesas del restaurante.

#### Modelos

**Mesa**
- `numero`: ID de la mesa
- `capacidad`: Número de comensales
- `estado`: Libre, Ocupada, Reservada
- `ubicacion`: Terraza, Interior, VIP, etc.
- Única por restaurante

#### Estados de Mesa
| Estado | Significado |
|--------|-----------|
| Libre | Disponible para nuevo pedido |
| Ocupada | Clientes comiendo |
| Reservada | Reservada anticipadamente |

#### Funcionalidades
- 🎯 Vista de mesas disponibles
- 📊 Estado en tiempo real
- 🔄 Cambios rápidos de estado
- 📍 Ubicación dentro del establecimiento

---

### 5️⃣ **PEDIDOS** - Órdenes y Servicios
Núcleo de toma de pedidos y seguimiento.

#### Modelos

**Pedido**
- Encabezado de orden con:
  - `mesa`: Referencia a la mesa
  - `mesero`: Usuario que toma el pedido
  - `estado`: Pendiente → En prep. → Listo → Servido → Cancelado
  - `total`: Suma de detalles
  - `observaciones`: Notas especiales
  - `archivado`: Oculta pedidos cerrados

**DetallePedido**
- Cada producto en el pedido:
  - `producto`: Referencia al menú
  - `cantidad`: Número de unidades
  - `precio_unitario`: Precio al momento de pedir
  - `subtotal`: Cantidad × Precio (autocalculado)
  - `observaciones`: Modificaciones especiales
  - `servido`: Flag de entrega

#### Flujo de Estados
```
Pendiente (en cocina)
    ↓
En Preparación
    ↓
Listo (esperando para servir)
    ↓
Entregado/Servido
    ↓
Archivado (cerrado en caja)
```

#### Funcionalidades
- ➕ Agregar/quitar productos
- 🔄 Cambio de estados
- 📝 Observaciones por plato
- 💰 Cálculo automático de totales
- 🏗️ Seguimiento en cocina

---

### 6️⃣ **CAJA** - Sistema de Facturación y Control
Gestión completa de dinero y ventas.

#### Modelos

**CajaSesion**
- Sesión de caja: Apertura → Cierre
- Datos:
  - `usuario_apertura/cierre`: Quién abre y cierra
  - `saldo_inicial`: Dinero inicial
  - `entradas_extra`: Dinero adicional (recargas, ventas sueltas)
  - `salidas`: Dinero extraído
  - `saldo_final`: Dinero al cierre
  - `observaciones`: Notas del cierre

- Propiedades Calculadas:
  - `total_facturado`: Suma de todas las facturas
  - `resultado_neto`: Total facturado + entradas - salidas

**Factura**
- Documento de venta:
  - `numero_factura`: Auto-generado (F20260227XXXX)
  - `pedido`: Referencia a la orden
  - `cajero`: Usuario que emite
  - `metodo_pago`: Efectivo, Tarjeta, Transferencia, Mixto
  - `subtotal`, `impuesto`, `descuento`
  - `total`: Cálculo final
  - `cliente_nombre`, `cliente_nit`: Datos opcionales

**MovimientoCaja**
- Registro detallado:
  - Tipo: Entrada o Salida
  - Monto y concepto
  - Timestamp automático
  - Usuario responsable

#### Funcionalidades
- 🔓 Apertura de caja al inicio
- 💵 Registro de ventas automático
- 📊 Entradas y salidas manuales
- 🧾 Numeración secuencial de facturas
- 📝 Cierre con resumen
- 📈 Historial de movimientos
- 💾 Auditoría completa

---

### 7️⃣ **INVENTARIO** - Control de Stock
Gestión de ingredientes y consumos.

#### Modelos

**Ingrediente**
- Datos:
  - `nombre`: Ej: Arroz, Pollo, Aceite
  - `unidad`: kg, g, L, ml, unidades
  - `cantidad_actual`: Stock disponible
  - `cantidad_minima`: Umbral para alerta
  - `costo_unitario`: Precio de compra

- Método:
  - `alerta_stock()`: Retorna True si stock < mínimo

**MovimientoInventario**
- Registra cada cambio:
  - Tipo: Entrada (compra), Salida (uso), Ajuste (corrección)
  - `cantidad`: Modificación
  - `motivo`: Por qué cambió
  - `usuario`: Quién realiza el cambio

#### Funcionalidades
- 📊 Dashboard de stock
- ⚠️ Alertas de bajo stock
- 📝 Registro de movimientos
- 📋 Historial completo
- 🧮 Cálculo automático de cantidades
- 💰 Control de costos unitarios

---

### 8️⃣ **CONTACTOS** - Proveedores y Teléfonos
Directorio de contactos externos.

#### Modelos

**Proveedor**
- Información:
  - `nombre`: Razón social
  - `tipo`: Alimentos, Bebidas, Limpieza, Tecnología, Otros
  - `telefono`, `telefono_secundario`
  - `email`
  - `direccion`
  - `notas`: Detalles importantes
  - `activo`: Control de estado

**TelefonoNegocio**
- Números importantes:
  - Teléfono principal
  - Línea de domicilios
  - WhatsApp
  - Reservas
  - Notas descriptivas

#### Funcionalidades
- 📞 Directorio de proveedores
- 📱 Números del negocio
- 🗂️ Clasificación por tipo
- 📝 Notas y observaciones
- ✓ Estado activo/inactivo

---

### 9️⃣ **ESTADÍSTICAS** - Reportes y Análisis
Información estratégica del negocio.

#### Funcionalidades Típicas
- 📈 Resumen de ventas diarias/mensuales
- 🏆 Productos más vendidos
- 💰 Ingresos por período
- 📊 Gráficos de tendencias
- 🕐 Horas pico
- 👥 Rendimiento de meseros
- 🍽️ Análisis de rotación de mesas

---

### 🔟 **AJUSTES** - Configuración del Sistema
Parámetros y configuración global.

#### Funcionalidades
- ⚙️ Configuración de impuestos
- 💵 Formatos de moneda
- 👤 Gestión de usuarios
- 🔑 Cambio de contraseñas
- 📋 Permisos y roles

---

## 🔐 Sistema de Roles y Permisos

El sistema implementa 4 roles principales:

### 🔴 ADMINISTRADOR
- Acceso completo al sistema
- Gestión de empleados y roles
- Control de configuración
- Ver todos los reportes
- Abrir/cerrar caja
- Emisión de facturas

### 🟡 MESERO
- Tomar pedidos en mesas
- Ver estado de mesas
- Modificar pedidos propios
- Ver órdenes en cocina
- No acceso a caja ni inventario

### 🟢 CAJERO
- Abrir/cerrar caja
- Registrar pagos de pedidos
- Emitir facturas
- Movimientos de caja
- Reportes de caja

### 🔵 COCINERO
- Ver órdenes pendientes
- Cambiar estado a "En Preparación"
- Marcar como "Listo"
- Ver observaciones especiales
- No acceso a ventas ni dinero

---

## 💾 Modelo de Datos - Relaciones

### Diagrama Conceptual

```
Restaurante (Multi-tenant)
    ├── Empleados
    │   ├── Usuario (Django Auth)
    │   └── Rol
    │
    ├── Mesas
    │   └── Mesa
    │       └── Pedidos
    │           ├── Pedido (estado, mesero)
    │           └── DetallePedido (producto, cantidad, precio)
    │
    ├── Menu
    │   ├── Categoría
    │   └── Producto
    │
    ├── MenuDiario
    │   └── Precios especiales del día
    │
    ├── Caja
    │   ├── CajaSesion
    │   │   ├── Factura
    │   │   └── MovimientoCaja
    │   └── Pedido → Factura (1:1)
    │
    ├── Inventario
    │   ├── Ingrediente
    │   └── MovimientoInventario
    │
    ├── Contactos
    │   ├── Proveedor
    │   └── TelefonoNegocio
    │
    └── Notificaciones
        └── Notificacion (a Usuario)
```

---

## 🚀 Flujo de Operación Diaria

### 1️⃣ **APERTURA DE CAJA**
```
Cajero inicia sesión
    ↓
Abre caja (CajaSesion.estado = 'abierta')
    ↓
Registra saldo inicial
    ↓
Sistema listo para vender
```

### 2️⃣ **TOMA DE PEDIDO**
```
Mesero verifica mesas disponibles
    ↓
Selecciona mesa (estado = 'libre')
    ↓
Crea Pedido asociado a mesa
    ↓
Agrega DetallePedidos (productos + observaciones)
    ↓
Cambia estado a 'pendiente'
    ↓
Mesa pasa a 'ocupada'
    ↓
Orden va a cocina
```

### 3️⃣ **SEGUIMIENTO EN COCINA**
```
Cocinero ve orden pendiente
    ↓
Cambia estado a 'en_preparacion'
    ↓
Prepara platos
    ↓
Marca como 'listo' cuando termina
    ↓
Mesero es notificado
    ↓
Mesero sirve en mesa
    ↓
Marca DetallePedido como 'servido'
```

### 4️⃣ **PAGO Y FACTURACIÓN**
```
Cliente solicita cuenta
    ↓
Mesero solicita cierre en caja
    ↓
Cajero genera Factura:
    - Número auto-generado
    - Subtotal, impuesto, descuento
    - Total final
    ↓
Selecciona método de pago
    ↓
Registra transacción
    ↓
Pedido se marca como 'entregado'
    ↓
Crea MovimientoCaja (entrada)
    ↓
Mesa vuelve a estado 'libre'
```

### 5️⃣ **CIERRE DE CAJA**
```
Fin del turno
    ↓
Cajero inicia cierre (CajaSesion.estado = 'cerrada')
    ↓
Sistema calcula:
    - Total facturado
    - Entradas/Salidas
    - Resultado neto
    ↓
Registra saldo final
    ↓
Archivo caja de forma segura
    ↓
Reportes disponibles
```

---

## 📊 Flujos Secundarios

### Gestión de Inventario
```
Compra de ingredientes
    ↓
Crea MovimientoInventario (entrada)
    ↓
Incrementa cantidad_actual
    ↓
Sistema verifica vs cantidad_minima
    ↓
Si stock bajo → Alerta
```

### Menú del Día
```
Admin crea MenuDiario para fecha X
    ↓
Define sopa, caldos, principios, proteínas
    ↓
Establece precios especiales
    ↓
Meseros solo pueden vender menú del día
    ↓
Próximo día genera nuevo menú
```

### Reportes y Estadísticas
```
Selecciona rango de fechas
    ↓
Sistema agrega datos de:
    - Facturas (ventas)
    - Pedidos (cantidad, productos)
    - Mesas (rotación)
    - Empleados (ventas por mesero)
    ↓
Genera gráficos y tablas
```

---

## 🔧 Configuración del Proyecto

### Archivo: `settings.py`

```python
# Aplicaciones instaladas
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'apps.core',
    'apps.usuarios',
    'apps.menu',
    'apps.mesas',
    'apps.pedidos',
    'apps.caja',
    'apps.inventario',
    'apps.contactos',
    'apps.estadisticas',
    'apps.ajustes',
]

# DEBUG = False (Producción)
DEBUG = False
ALLOWED_HOSTS = ['*']

# Base de datos MySQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'restaurante_db',
        'USER': 'usuario',
        'PASSWORD': 'contraseña',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### URLs Principales

```
/                           → Dashboard (core)
/admin/                     → Panel de administración Django
/usuarios/login/            → Login
/usuarios/logout/           → Logout
/menu/                      → Catálogo de productos
/mesas/                     → Control de mesas
/pedidos/                   → Órdenes
/caja/abrir/               → Apertura de caja
/caja/cobrar/              → Registro de pagos
/caja/cierre/              → Cierre de sesión
/inventario/               → Stock de ingredientes
/contactos/                → Proveedores
/estadisticas/             → Reportes
/ajustes/                  → Configuración
```

---

## 📦 Dependencias del Proyecto

```
Django>=4.2,<5.0       # Framework web
mysqlclient>=2.2       # Driver para MySQL
```

### Cómo instalar:
```bash
pip install -r requirements.txt
```

---

## 🎮 Comandos Útiles

```bash
# Activar entorno virtual
.\.venv\Scripts\Activate

# Ejecutar servidor de desarrollo
python manage.py runserver

# Crear usuario superadmin
python manage.py createsuperuser

# Ejecutar migraciones
python manage.py migrate

# Crear migraciones
python manage.py makemigrations

# Exportar datos
python manage.py dumpdata > backup.json

# Importar datos
python manage.py loaddata backup.json
```

---

## 💡 Características Destacadas

✅ **Multi-Tenant**: Soporte para múltiples restaurantes en uma BD
✅ **Control de Roles**: 4 tipos de usuario con permisos específicos
✅ **Seguimiento en Tiempo Real**: Estado de pedidos y mesas
✅ **Auditoría Completa**: Registro de todas las transacciones
✅ **Cálculos Automáticos**: Totales, impuestos, subtotales
✅ **Inventario Dinámico**: Alertas de stock bajo
✅ **Numeración Secuencial**: Facturas con formato FAAAAMMDDNNNN
✅ **Interface Responsiva**: Compatible con celulares (PWA ready)
✅ **Dashboard Intuitivo**: Información de un vistazo

---

## 🔒 Seguridad

- ✅ Autenticación con Django Auth
- ✅ Protección CSRF en formularios
- ✅ Encriptación de contraseñas (bcrypt)
- ✅ Validación en servidor
- ✅ SQL Injection prevention (ORM)
- ✅ Registro de auditoría de operaciones
- ✅ Restricción por roles y permisos

---

## 📱 Características PWA (Progressive Web App)

- 📲 Funciona en navegador móvil
- 💾 Se puede instalar como app
- 🔄 Service Worker para caché
- 📡 Funcionalidad offline (parcial)
- ⚡ Carga rápida

---

## 📈 Posibles Mejoras Futuras

- 🔔 Push notifications en tiempo real
- 📊 Dashboard con gráficos interactivos
- 🤖 Integración con sistemas de pago
- 📧 Email de confirmación de órdenes
- 📱 Aplicación móvil nativa
- 🎯 Sistema de mesas interactivo
- 💬 Chat entre cocina y meseros
- 🔗 APIs REST para integraciones

---

## 👨‍💻 Estructura de Carpetas de Templates

```
templates/
├── base.html                    # Layout principal
├── ajustes/
│   ├── usuario_form.html
│   └── usuarios_list.html
├── caja/
│   ├── abrir_caja.html
│   ├── caja.html
│   ├── cerrar_caja.html
│   ├── cobrar_pedido.html
│   ├── factura_detalle.html
│   ├── historial_caja.html
│   ├── resumen_caja.html
│   └── venta_rapida.html
├── contactos/
│   ├── contactos_list.html
│   ├── proveedor_form.html
│   └── telefono_form.html
├── core/
│   ├── inicio.html
│   └── service-worker.js
├── estadisticas/
│   └── resumen_mensual.html
├── inventario/
│   ├── ingrediente_confirm_delete.html
│   ├── ingrediente_form.html
│   ├── inventario_list.html
│   ├── movimiento_form.html
│   └── movimientos_list.html
├── menu/
│   └── [templates de menú]
├── mesas/
│   └── [templates de mesas]
├── pedidos/
│   └── [templates de pedidos]
└── usuarios/
    └── [templates de autenticación]
```

---

## 📝 Notas Importantes

1. **Restaurante Principal**: El sistema está diseñado para soportar múltiples restaurantes a través de una sola BD.

2. **Sesión de Caja**: Solo puede existir UNA caja abierta por restaurante al mismo tiempo.

3. **Estados de Pedidos**: Los pedidos solo avanzan estados, no retroceden (por auditoría).

4. **Archivado de Pedidos**: Los pedidos se marcan como archivados después de facturados para mantener limpia la vista activa.

5. **Cálculos**: Todos los cálculos se hacen automáticamente en modelos para garantizar consistencia.

6. **Seguridad CSRF**: Todos los formularios incluyen el token CSRF obligatorio.

7. **Base de Datos**: Se incluye dump SQL para restaurar datos (`restaurante_db.sql`).

---

## 🎓 Conclusión

RestauranteDJ es un sistema **modular, escalable y completo** para la gestión operativa de restaurantes. Implementa mejores prácticas Django con:

- ✅ Modelos bien estructurados
- ✅ Separación de responsabilidades
- ✅ Control de acceso por roles
- ✅ Auditoría integrada
- ✅ Interface intuitiva

Es ideal para restaurantes medianos que necesitan control de mesas, pedidos, caja e inventario en una sola plataforma.

---

**Versión del Documento**: 1.0  
**Última Actualización**: Febrero 2026  
**Autor**: Equipo de Desarrollo

