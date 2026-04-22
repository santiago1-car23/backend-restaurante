# Sistema de Restaurante – Requerimientos y Documentación

## 1. Descripción general

Aplicación web de gestión para restaurante desarrollada con Django. Cubre:
- Gestión de usuarios y autenticación.
- Gestión de menú y productos.
- Gestión de mesas y pedidos.
- Módulo de caja (apertura, cierre, ventas, egresos/ingresos extra, reportes).
- Módulo de inventario de ingredientes y movimientos.

Estructura principal de apps Django:
- apps.core
- apps.usuarios
- apps.menu
- apps.mesas
- apps.pedidos
- apps.caja
- apps.inventario
 - apps.contactos
 - apps.estadisticas
 - apps.ajustes

---

## 2. Requerimientos funcionales (resumen)

1. **Usuarios y acceso**
   - Autenticación de usuarios (login/logout).
   - Perfiles de usuario para acceder a caja, inventario, pedidos, etc.

2. **Menú y productos**
   - CRUD de productos de menú (crear, editar, eliminar, listar).
   - Manejo de diferentes tipos de menú (desayuno, corriente, etc.).

3. **Mesas y pedidos**
   - Asignar pedidos a mesas.
   - Ver, editar y cerrar pedidos.
   - Detalle de pedido con productos, cantidades y totales.

4. **Caja**
   - Abrir sesión de caja con saldo inicial.
   - Registrar ventas (facturas) asociadas a pedidos y métodos de pago (efectivo, tarjeta, transferencia/Nequi).
   - Registrar salidas de dinero (egresos) y entradas adicionales.
   - Cerrar sesión de caja y generar resumen detallado.
   - Historial de sesiones de caja y filtros por fecha/estado.

5. **Inventario**
   - Gestión de ingredientes y existencias.
   - Registro de movimientos de entrada/salida de inventario.

6. **Contactos y proveedores**
   - Registro de proveedores y otros contactos del restaurante.
   - Gestión de teléfonos y datos de contacto.

7. **Estadísticas y reportes**
   - Resumen mensual de ventas y otros indicadores.
   - Filtros por fecha y otros criterios para análisis.

8. **Ajustes y configuración de usuario**
   - Modificación de datos de usuario (nombre, contraseña, etc.).
   - Configuración básica de parámetros del sistema.

---

## 3. Requerimientos no funcionales

- **Disponibilidad**: El sistema debe poder operar de forma estable durante la jornada completa del restaurante.
- **Seguridad**:
  - Acceso a módulos sensibles (caja, inventario) protegido por autenticación.
  - Contraseñas gestionadas por el sistema de auth de Django.
- **Usabilidad**: Interfaz web responsive orientada a uso en PC y tablet.
- **Mantenibilidad**: Código organizado en apps Django separadas por responsabilidad.
- **Rendimiento**: Capaz de manejar múltiples pedidos y operaciones de caja simultáneas en un local pequeño/mediano.

---

## 4. Requerimientos técnicos

### 4.1. Software

- Python 3.x (recomendado 3.10+).
- Django (versión indicada en el entorno virtual del proyecto).
- Motor de base de datos:
   - Desarrollo (por defecto actual): SQLite (`db.sqlite3`).
   - Alternativa: MySQL local (XAMPP, WAMP, etc.) descomentando y ajustando la sección MySQL en `restaurante/settings.py`.
   - Producción: instancia MySQL/MariaDB o PostgreSQL en servidor estable (según se configure).
- Servidor web para producción:
  - Opción típica: Nginx + Gunicorn/uvicorn en Linux.
  - Alternativas en Windows: IIS con reverse proxy.

### 4.2. Dependencias principales de Python

*(La lista exacta debe obtenerse desde el entorno virtual o un requirements.txt; como mínimo se requieren:)*

- django
- mysqlclient (u otro conector de MySQL compatible) **si se usa MySQL**
- gunicorn (u otro servidor WSGI) para despliegue en Linux
- python-decouple o similar para manejar variables de entorno (opcional pero recomendado)

Se recomienda generar un `requirements.txt` con:

```bash
pip freeze > requirements.txt
```

---

## 5. Configuración del proyecto (Django)

Archivo de configuración principal: `restaurante/settings.py`.

Puntos clave:
- `INSTALLED_APPS`: incluye las apps internas (`apps.core`, `apps.caja`, `apps.pedidos`, `apps.inventario`, `apps.contactos`, `apps.estadisticas`, `apps.ajustes`, etc.) y los módulos estándar de Django.
- `DATABASES` (estado actual):
   - `default`: base de datos SQLite (`db.sqlite3`) en el directorio del proyecto.
   - Existe una configuración alternativa para MySQL comentada en el archivo, que puede activarse y ajustarse para entornos donde se requiera MySQL.
- `TEMPLATES`: carpeta de plantillas en `templates/`.
- `STATIC_URL = 'static/'`: falta definir `STATIC_ROOT` para producción.
- `LOGIN_URL = 'login'` y `LOGIN_REDIRECT_URL = 'dashboard'`.

### 5.1. Ajustes recomendados para producción

Crear una configuración separada para producción (por ejemplo `settings_prod.py`) con:

- `DEBUG = False`.
- `ALLOWED_HOSTS = ['midominio.com', 'mi-ip-publica']`.
- `SECRET_KEY` obtenido de variables de entorno (no hardcodeado).
- Credenciales de base de datos configuradas por variables de entorno.
- Parámetros de seguridad adicionales:
  - `SECURE_SSL_REDIRECT = True` (si hay HTTPS).
  - `SESSION_COOKIE_SECURE = True`.
  - `CSRF_COOKIE_SECURE = True`.
  - HSTS (`SECURE_HSTS_SECONDS`, etc.) según el entorno.

---

## 6. Despliegue de archivos estáticos

En producción se recomienda:

1. Definir en `settings.py`:

   ```python
   STATIC_URL = 'static/'
   STATIC_ROOT = BASE_DIR / 'staticfiles'
   ```

2. Ejecutar en el servidor de producción:

   ```bash
   python manage.py collectstatic
   ```

3. Configurar el servidor web (Nginx/IIS/Apache) para servir la carpeta `staticfiles/` directamente.

Si se manejan archivos subidos por usuarios, también definir:

```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

y configurar las rutas y servidor web para servir `MEDIA_ROOT`.

---

## 7. Guía de instalación (entorno de desarrollo)

1. **Clonar/copiar el proyecto** en una carpeta, por ejemplo:

   ```bash
   C:\Users\santi\OneDrive\Escritorio\restauranteDJ
   ```

2. **Crear entorno virtual (opcional pero recomendado)**:

   ```bash
   python -m venv .venv
   .venv\\Scripts\\activate
   ```

3. **Instalar dependencias** (si ya hay `requirements.txt`):

   ```bash
   pip install -r requirements.txt
   ```

   Si no existe, instalar manualmente como mínimo:

   ```bash
   pip install django mysqlclient
   ```

4. **Configurar base de datos**:
   - **Opción rápida (recomendada para empezar)**: usar la base de datos SQLite que ya viene configurada en `restaurante/settings.py` (no requiere pasos adicionales).
   - **Opción MySQL**:
     - Crear base de datos `restaurante_db` (o el nombre que se defina).
     - Descomentar el bloque MySQL en `restaurante/settings.py` y ajustar `NAME`, `USER`, `PASSWORD`, `HOST` y `PORT`.

5. **Aplicar migraciones**:

   ```bash
   python manage.py migrate
   ```

6. **Crear superusuario** (para acceder al admin de Django):

   ```bash
   python manage.py createsuperuser
   ```

7. **Levantar servidor de desarrollo**:

   - Usando manage.py:

     ```bash
     python manage.py runserver 0.0.0.0:8000
     ```

   - O usando el script `levantar_servicios` (si se ejecuta como script de Windows/PowerShell).

8. Acceder en el navegador a:

   - Panel principal: `http://localhost:8000/`

---

## 8. Checklist para producción

- [ ] Crear entorno virtual y instalar dependencias desde `requirements.txt`.
- [ ] Configurar base de datos en servidor (MySQL/MariaDB/PostgreSQL) y ajustar `DATABASES`.
- [ ] Configurar settings de producción (`DEBUG = False`, `ALLOWED_HOSTS`, `SECRET_KEY` en variables de entorno).
- [ ] Definir `STATIC_ROOT` y ejecutar `collectstatic`.
- [ ] Configurar servidor de aplicaciones (Gunicorn/uvicorn) y servidor web frontal (Nginx/IIS/Apache).
- [ ] Activar HTTPS (certificado SSL) y aplicar cabeceras de seguridad.
- [ ] Configurar LOGGING en Django para guardar errores en archivos o sistema externo (Sentry, etc.).
- [ ] Crear usuarios administrativos y revisar permisos/roles para caja, inventario, pedidos.
- [ ] Probar flujo completo: login → crear pedido → cobrar → ver caja → cerrar caja.

---

## 9. Notas finales

- Para listar exactamente las dependencias utilizadas en el entorno actual, se recomienda ejecutar `pip freeze > requirements.txt` dentro del entorno virtual.
- Se sugiere añadir tests automatizados para los flujos críticos (caja, pedidos, inventario) y ejecutarlos antes de cada despliegue a producción.
- El proyecto incluye un archivo `restaurante_db.sql` con una base de datos de ejemplo que puede importarse en MySQL para cargar datos iniciales (por ejemplo en entornos de prueba o producción).
